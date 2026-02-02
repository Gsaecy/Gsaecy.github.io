#!/usr/bin/env python3
"""
DeepSeek API客户端
封装DeepSeek API调用，提供统一的AI分析接口
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import httpx
from openai import OpenAI

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.utils.logger import setup_logger
from scripts.utils.cache import CacheManager


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化DeepSeek客户端
        
        Args:
            config: 配置字典，包含DeepSeek API配置
        """
        self.config = config.get('deepseek', {})
        
        # 设置日志
        self.logger = setup_logger("deepseek_client", 
                                  level=config.get('logging', {}).get('level', 'INFO'))
        
        # 初始化缓存
        cache_dir = config.get('storage', {}).get('cache_dir', './data/cache')
        self.cache = CacheManager(cache_dir, prefix="deepseek")
        
        # 获取API密钥
        api_key = self.config.get('api_key', '')
        if api_key.startswith('${') and api_key.endswith('}'):
            # 从环境变量读取
            env_var = api_key[2:-1]
            api_key = os.environ.get(env_var, '')
        
        if not api_key:
            self.logger.warning("DeepSeek API密钥未配置")
        
        # 初始化OpenAI客户端（兼容DeepSeek API）
        base_url = self.config.get('base_url', 'https://api.deepseek.com')
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 模型配置
        self.model = self.config.get('model', 'deepseek-chat')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 4000)
        self.timeout = self.config.get('timeout', 30)
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens_used': 0,
            'last_request_time': None,
            'average_response_time': 0
        }
        
        self.logger.info(f"DeepSeek客户端初始化完成 - 模型: {self.model}")
    
    async def chat_completion(self, 
                            messages: List[Dict[str, str]],
                            model: Optional[str] = None,
                            temperature: Optional[float] = None,
                            max_tokens: Optional[int] = None,
                            use_cache: bool = True) -> Dict[str, Any]:
        """
        调用DeepSeek聊天补全API
        
        Args:
            messages: 消息列表
            model: 模型名称（可选）
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）
            use_cache: 是否使用缓存
            
        Returns:
            API响应字典
        """
        # 生成缓存键
        cache_key = self._generate_cache_key(messages, model, temperature, max_tokens)
        
        # 检查缓存
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                self.logger.debug("从缓存获取AI响应")
                return cached
        
        # 准备请求参数
        request_params = {
            'model': model or self.model,
            'messages': messages,
            'temperature': temperature or self.temperature,
            'max_tokens': max_tokens or self.max_tokens,
            'stream': False
        }
        
        # 移除None值
        request_params = {k: v for k, v in request_params.items() if v is not None}
        
        try:
            self.stats['total_requests'] += 1
            start_time = time.time()
            
            # 调用API
            response = await self._make_request(request_params)
            
            # 更新统计
            duration = time.time() - start_time
            self.stats['successful_requests'] += 1
            self.stats['last_request_time'] = datetime.now().isoformat()
            self.stats['average_response_time'] = (
                self.stats['average_response_time'] * (self.stats['successful_requests'] - 1) + duration
            ) / self.stats['successful_requests']
            
            # 提取token使用量
            if 'usage' in response:
                self.stats['total_tokens_used'] += response['usage'].get('total_tokens', 0)
            
            self.logger.debug(f"API调用成功 - 耗时: {duration:.2f}s - Token使用: {response.get('usage', {}).get('total_tokens', 'N/A')}")
            
            # 保存到缓存
            if use_cache:
                cache_ttl = self.config.get('cache_ttl', 3600)  # 默认缓存1小时
                self.cache.set(cache_key, response, ttl=cache_ttl)
            
            return response
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.logger.error(f"API调用失败: {str(e)}")
            raise
    
    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行API请求"""
        try:
            # 使用OpenAI客户端
            response = await self.client.chat.completions.create(**params)
            
            # 转换为字典格式
            result = {
                'id': response.id,
                'object': response.object,
                'created': response.created,
                'model': response.model,
                'choices': [],
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
            for choice in response.choices:
                result['choices'].append({
                    'index': choice.index,
                    'message': {
                        'role': choice.message.role,
                        'content': choice.message.content
                    },
                    'finish_reason': choice.finish_reason
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"API请求异常: {str(e)}")
            raise
    
    def _generate_cache_key(self, 
                          messages: List[Dict[str, str]],
                          model: Optional[str],
                          temperature: Optional[float],
                          max_tokens: Optional[int]) -> str:
        """生成缓存键"""
        import hashlib
        
        # 创建可哈希的字符串
        cache_str = json.dumps({
            'messages': messages,
            'model': model or self.model,
            'temperature': temperature or self.temperature,
            'max_tokens': max_tokens or self.max_tokens
        }, sort_keys=True, ensure_ascii=False)
        
        # 生成MD5哈希
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    async def analyze_text(self, 
                          text: str,
                          analysis_type: str = "general",
                          instructions: Optional[str] = None,
                          **kwargs) -> Dict[str, Any]:
        """
        分析文本
        
        Args:
            text: 要分析的文本
            analysis_type: 分析类型
            instructions: 自定义指令
            **kwargs: 额外参数
            
        Returns:
            分析结果
        """
        # 根据分析类型选择提示词
        if analysis_type == "trend":
            prompt = self._get_trend_analysis_prompt(text, instructions)
        elif analysis_type == "summary":
            prompt = self._get_summary_prompt(text, instructions)
        elif analysis_type == "sentiment":
            prompt = self._get_sentiment_analysis_prompt(text, instructions)
        elif analysis_type == "industry":
            prompt = self._get_industry_analysis_prompt(text, instructions)
        else:
            prompt = self._get_general_analysis_prompt(text, instructions)
        
        # 添加额外参数
        if 'temperature' not in kwargs:
            kwargs['temperature'] = 0.3 if analysis_type in ['summary', 'sentiment'] else 0.7
        
        # 调用API
        response = await self.chat_completion(prompt, **kwargs)
        
        # 解析响应
        if response and response.get('choices'):
            content = response['choices'][0]['message']['content']
            
            # 尝试解析JSON响应
            try:
                result = json.loads(content)
                result['raw_response'] = content
            except json.JSONDecodeError:
                # 如果不是JSON，返回文本
                result = {
                    'analysis': content,
                    'raw_response': content
                }
            
            # 添加元数据
            result['analysis_type'] = analysis_type
            result['model'] = response.get('model', self.model)
            result['usage'] = response.get('usage', {})
            result['timestamp'] = datetime.now().isoformat()
            
            return result
        
        return {'error': 'No response from AI', 'timestamp': datetime.now().isoformat()}
    
    def _get_general_analysis_prompt(self, text: str, instructions: Optional[str] = None) -> List[Dict[str, str]]:
        """获取通用分析提示词"""
        system_prompt = """你是一个专业的行业分析师。请分析以下文本，提取关键信息并进行深入分析。"""
        
        if instructions:
            system_prompt += f"\n额外要求：{instructions}"
        
        user_prompt = f"""请分析以下文本：

{text}

请以JSON格式返回分析结果，包含以下字段：
1. key_points: 关键要点列表
2. summary: 文本摘要（200字以内）
3. insights: 深入洞察和分析
4. recommendations: 建议和行动项
5. confidence_score: 分析置信度（0-1）
6. tags: 相关标签列表

请确保分析专业、准确、有深度。"""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _get_trend_analysis_prompt(self, text: str, instructions: Optional[str] = None) -> List[Dict[str, str]]:
        """获取趋势分析提示词"""
        system_prompt = """你是一个专业的趋势分析师。请分析以下文本中的趋势、模式和未来发展方向。"""
        
        if instructions:
            system_prompt += f"\n额外要求：{instructions}"
        
        user_prompt = f"""请分析以下文本中的趋势：

{text}

请以JSON格式返回趋势分析结果，包含以下字段：
1. identified_trends: 识别出的趋势列表（每个趋势包含名称、描述、强度）
2. trend_drivers: 趋势驱动因素
3. timeline: 趋势时间线（短期、中期、长期）
4. impact_analysis: 影响分析（对行业、企业、个人的影响）
5. opportunities: 机会识别
6. risks: 风险预警
7. confidence_score: 分析置信度（0-1）

请确保分析具有前瞻性和实用性。"""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _get_summary_prompt(self, text: str, instructions: Optional[str] = None) -> List[Dict[str, str]]:
        """获取摘要提示词"""
        system_prompt = """你是一个专业的文本摘要专家。请为以下文本生成准确、简洁的摘要。"""
        
        if instructions:
            system_prompt += f"\n额外要求：{instructions}"
        
        user_prompt = f"""请为以下文本生成摘要：

{text}

请以JSON格式返回摘要结果，包含以下字段：
1. summary: 文本摘要（100-200字）
2. key_points: 关键要点列表（3-5个）
3. main_topics: 主要主题
4. tone: 文本语气
5. length_original: 原文长度（字符数）
6. length_summary: 摘要长度（字符数）
7. compression_ratio: 压缩比

摘要应保持原文的核心信息和关键细节。"""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _get_sentiment_analysis_prompt(self, text: str, instructions: Optional[str] = None) -> List[Dict[str, str]]:
        """获取情感分析提示词"""
        system_prompt = """你是一个专业的情感分析师。请分析以下文本的情感倾向和情绪强度。"""
        
        if instructions:
            system_prompt += f"\n额外要求：{instructions}"
        
        user_prompt = f"""请分析以下文本的情感：

{text}

请以JSON格式返回情感分析结果，包含以下字段：
1. overall_sentiment: 整体情感（positive/negative/neutral）
2. sentiment_score: 情感分数（-1到1，-1为极端负面，1为极端正面）
3. emotion_breakdown: 情绪细分（如anger, joy, sadness, fear, surprise等）
4. intensity: 情感强度（0-1）
5. key_phrases: 关键情感短语
6. confidence: 分析置信度（0-1）
7. recommendations: 基于情感分析的建议

请确保分析准确、细致。"""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _get_industry_analysis_prompt(self, text: str, instructions: Optional[str] = None) -> List[Dict[str, str]]:
        """获取行业分析提示词"""
        system_prompt = """你是一个专业的行业分析师。请分析以下文本中的行业动态、竞争格局和发展机会。"""
        
        if instructions:
            system_prompt += f"\n额外要求：{instructions}"
        
        user_prompt = f"""请分析以下文本中的行业信息：

{text}

请以JSON格式返回行业分析结果，包含以下字段：
1. industry: 所属行业
2. market_size: 市场规模分析
3. growth_rate: 增长率分析
4. competitive_landscape: 竞争格局分析
5. key_players: 主要参与者
6. trends: 行业趋势
7. opportunities: 机会识别
8. challenges: 挑战分析
9. swot_analysis: SWOT分析
10. recommendations: 战略建议
11. confidence_score: 分析置信度（0-1）

请确保分析全面、深入、实用。"""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    async def batch_analyze(self, 
                          texts: List[str],
                          analysis_type: str = "general",
                          **kwargs) -> List[Dict[str, Any]]:
        """
        批量分析文本
        
        Args:
            texts: 文本列表
            analysis_type: 分析类型
            **kwargs: 额外参数
            
        Returns:
            分析结果列表
        """
        results = []
        
        for i, text in enumerate(texts):
            try:
                self.logger.info(f"分析文本 {i+1}/{len(texts)}")
                result = await self.analyze_text(text, analysis_type, **kwargs)
                results.append(result)
                
                # 避免速率限制
                if i < len(texts) - 1:
                    await asyncio.sleep(1)  # 1秒间隔
                    
            except Exception as e:
                self.logger.error(f"分析文本失败 {i+1}: {str(e)}")
                results.append({
                    'error': str(e),
                    'text_index': i,
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            'model': self.model,
            'timestamp': datetime.now().isoformat()
        }
    
    def cleanup(self):
        """清理资源"""
        pass


# 异步支持
import asyncio

class AsyncDeepSeekClient(DeepSeekClient):
    """异步DeepSeek客户端"""
    
    async def chat_completion(self, *args, **kwargs):
        """异步聊天补全"""
        return await super().chat_completion(*args, **kwargs)
    
    async def analyze_text(self, *args, **kwargs):
        """异步分析文本"""
        return await super().analyze_text(*args, **kwargs)
    
    async def batch_analyze(self, *args, **kwargs):
        """异步批量分析"""
        return await super().batch_analyze(*args, **kwargs)