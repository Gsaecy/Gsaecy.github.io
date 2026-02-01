#!/usr/bin/env python3
"""
DeepSeek AI分析器
专门针对DeepSeek API优化的行业分析模块
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

class DeepSeekAnalyzer:
    """DeepSeek AI分析器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 配置DeepSeek API
        self.setup_deepseek_api()
        
        # 加载分析配置
        self.analysis_config = config.get('analysis', {})
        self.prompts = config.get('prompts', {})
        
        self.logger.info("DeepSeek分析器初始化完成")
    
    def setup_deepseek_api(self):
        """配置DeepSeek API"""
        api_config = self.config.get('analysis', {}).get('ai_model', {})
        
        # 从环境变量或配置获取API Key
        api_key = os.getenv('DEEPSEEK_API_KEY') or api_config.get('api_key')
        api_base = api_config.get('api_base', 'https://api.deepseek.com')
        model = api_config.get('model', 'deepseek-chat')
        
        if not api_key:
            raise ValueError("DeepSeek API Key未配置")
        
        # 配置OpenAI客户端（兼容DeepSeek）
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        self.model = model
        self.temperature = api_config.get('temperature', 0.7)
        self.max_tokens = api_config.get('max_tokens', 2000)
        
        self.logger.info(f"DeepSeek API配置完成，模型: {model}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def call_deepseek_api(self, messages: List[Dict], **kwargs) -> str:
        """调用DeepSeek API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                stream=False
            )
            
            content = response.choices[0].message.content
            usage = response.usage
            
            self.logger.debug(f"DeepSeek API调用成功，使用token: {usage.total_tokens}")
            return content
            
        except Exception as e:
            self.logger.error(f"DeepSeek API调用失败: {e}")
            raise
    
    def analyze_industry_trends(self, industry_data: Dict) -> Dict:
        """分析行业趋势"""
        self.logger.info(f"开始分析行业趋势: {industry_data.get('industry', '未知')}")
        
        prompt = self.prompts.get('trend_analysis', '').format(
            data=json.dumps(industry_data, ensure_ascii=False, indent=2)
        )
        
        messages = [
            {"role": "system", "content": "你是一个资深的行业分析师，擅长发现趋势和机会。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            analysis_result = self.call_deepseek_api(messages)
            
            # 解析分析结果
            result = {
                "industry": industry_data.get("industry"),
                "analysis_date": datetime.now().isoformat(),
                "trends": self.extract_trends(analysis_result),
                "opportunities": self.extract_opportunities(analysis_result),
                "risks": self.extract_risks(analysis_result),
                "recommendations": self.extract_recommendations(analysis_result),
                "raw_analysis": analysis_result
            }
            
            self.logger.info(f"行业趋势分析完成: {industry_data.get('industry')}")
            return result
            
        except Exception as e:
            self.logger.error(f"行业趋势分析失败: {e}")
            return {
                "industry": industry_data.get("industry"),
                "error": str(e),
                "analysis_date": datetime.now().isoformat()
            }
    
    def generate_daily_summary(self, daily_data: List[Dict]) -> Dict:
        """生成每日摘要"""
        self.logger.info("开始生成每日摘要")
        
        # 整理数据
        formatted_data = self.format_daily_data(daily_data)
        
        prompt = self.prompts.get('daily_summary', '').format(
            content=formatted_data
        )
        
        messages = [
            {"role": "system", "content": "你是一个专业的财经科技记者，擅长撰写行业日报。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            summary = self.call_deepseek_api(messages, max_tokens=1500)
            
            result = {
                "summary_date": datetime.now().strftime("%Y-%m-%d"),
                "sections": self.parse_summary_sections(summary),
                "key_events": self.extract_key_events(summary),
                "market_sentiment": self.analyze_sentiment(summary),
                "full_summary": summary
            }
            
            self.logger.info("每日摘要生成完成")
            return result
            
        except Exception as e:
            self.logger.error(f"每日摘要生成失败: {e}")
            return {
                "summary_date": datetime.now().strftime("%Y-%m-%d"),
                "error": str(e)
            }
    
    def generate_article(self, analysis_data: Dict, article_type: str = "analysis") -> Dict:
        """生成分析文章"""
        self.logger.info(f"生成{article_type}类型文章")
        
        prompt_template = self.prompts.get('article_generation', '')
        prompt = prompt_template.format(
            analysis=json.dumps(analysis_data, ensure_ascii=False, indent=2)
        )
        
        # 根据文章类型调整系统提示
        if article_type == "daily":
            system_prompt = "你是一个专业的行业日报编辑，擅长撰写简洁明了的每日行业报告。"
        elif article_type == "deep":
            system_prompt = "你是一个资深的行业分析师，擅长撰写深度分析报告。"
        else:
            system_prompt = "你是一个专业的行业内容创作者。"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            article_content = self.call_deepseek_api(messages, max_tokens=2500)
            
            # 提取文章结构
            article_structure = self.parse_article_structure(article_content)
            
            result = {
                "title": article_structure.get("title", "未命名文章"),
                "content": article_content,
                "type": article_type,
                "generated_date": datetime.now().isoformat(),
                "sections": article_structure.get("sections", []),
                "keywords": self.extract_keywords(article_content),
                "estimated_reading_time": self.calculate_reading_time(article_content)
            }
            
            self.logger.info(f"文章生成完成: {result['title']}")
            return result
            
        except Exception as e:
            self.logger.error(f"文章生成失败: {e}")
            return {
                "type": article_type,
                "error": str(e),
                "generated_date": datetime.now().isoformat()
            }
    
    def format_daily_data(self, data: List[Dict]) -> str:
        """格式化每日数据"""
        formatted = []
        
        for item in data:
            source = item.get("source", "未知来源")
            title = item.get("title", "无标题")
            content = item.get("content", "")[:200]  # 截取前200字符
            category = item.get("category", "未分类")
            
            formatted.append(f"[{source}] {category} - {title}\n{content}...")
        
        return "\n\n".join(formatted)
    
    def extract_trends(self, analysis_text: str) -> List[Dict]:
        """从分析文本中提取趋势"""
        # 这里可以更复杂地解析，暂时返回简单结果
        return [
            {
                "name": "AI技术普及",
                "strength": "强",
                "duration": "中长期",
                "description": "AI技术在各行业加速应用"
            }
        ]
    
    def extract_opportunities(self, analysis_text: str) -> List[Dict]:
        """提取机会"""
        return [
            {
                "area": "跨境电商",
                "potential": "高",
                "timeline": "6-12个月",
                "description": "东南亚市场增长迅速"
            }
        ]
    
    def extract_risks(self, analysis_text: str) -> List[Dict]:
        """提取风险"""
        return [
            {
                "type": "政策风险",
                "probability": "中",
                "impact": "高",
                "description": "国际贸易政策可能变化"
            }
        ]
    
    def extract_recommendations(self, analysis_text: str) -> List[Dict]:
        """提取建议"""
        return [
            {
                "action": "关注东南亚市场",
                "priority": "高",
                "rationale": "增长潜力大，竞争相对较小"
            }
        ]
    
    def parse_summary_sections(self, summary_text: str) -> Dict:
        """解析摘要章节"""
        # 简单解析，实际可以更复杂
        lines = summary_text.split('\n')
        sections = {}
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('##'):
                current_section = line.replace('##', '').strip()
                sections[current_section] = []
            elif current_section and line:
                sections[current_section].append(line)
        
        return sections
    
    def extract_key_events(self, summary_text: str) -> List[str]:
        """提取关键事件"""
        # 简单实现
        import re
        events = re.findall(r'[•\-*]\s*(.+?)(?=[•\-*]|$)', summary_text)
        return events[:5]  # 返回前5个
    
    def analyze_sentiment(self, text: str) -> str:
        """分析市场情绪"""
        # 简单情绪分析
        positive_words = ['增长', '利好', '机会', '突破', '创新']
        negative_words = ['风险', '下跌', '挑战', '压力', '下滑']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "积极"
        elif negative_count > positive_count:
            return "谨慎"
        else:
            return "中性"
    
    def parse_article_structure(self, article_text: str) -> Dict:
        """解析文章结构"""
        lines = article_text.split('\n')
        title = ""
        sections = []
        current_section = {"title": "", "content": []}
        
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                title = line.replace('# ', '')
            elif line.startswith('## '):
                if current_section["title"]:
                    sections.append(current_section.copy())
                current_section = {"title": line.replace('## ', ''), "content": []}
            elif line and current_section["title"]:
                current_section["content"].append(line)
        
        if current_section["title"]:
            sections.append(current_section)
        
        return {"title": title, "sections": sections}
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """提取关键词"""
        # 简单关键词提取
        import jieba.analyse
        try:
            keywords = jieba.analyse.extract_tags(text, topK=top_n)
            return keywords
        except:
            # 如果jieba不可用，使用简单方法
            words = text.split()
            from collections import Counter
            common_words = Counter(words).most_common(top_n)
            return [word for word, count in common_words]
    
    def calculate_reading_time(self, text: str, words_per_minute: int = 200) -> int:
        """计算阅读时间（分钟）"""
        word_count = len(text.split())
        return max(1, word_count // words_per_minute)
    
    def analyze(self, data: List[Dict]) -> Dict:
        """主分析接口"""
        self.logger.info(f"开始分析{len(data)}条数据")
        
        # 按行业分组
        industry_groups = {}
        for item in data:
            industry = item.get("industry", "其他")
            if industry not in industry_groups:
                industry_groups[industry] = []
            industry_groups[industry].append(item)
        
        # 分析每个行业
        industry_analyses = {}
        for industry, items in industry_groups.items():
            if len(items) >= 3:  # 至少有3条数据才分析
                industry_data = {
                    "industry": industry,
                    "data_count": len(items),
                    "items": items[:10]  # 最多10条
                }
                analysis = self.analyze_industry_trends(industry_data)
                industry_analyses[industry] = analysis
        
        # 生成每日摘要
        daily_summary = self.generate_daily_summary(data[:20])  # 最多20条
        
        result = {
            "analysis_date": datetime.now().isoformat(),
            "total_data_points": len(data),
            "industries_analyzed": list(industry_analyses.keys()),
            "industry_analyses": industry_analyses,
            "daily_summary": daily_summary,
            "market_overview": self.generate_market_overview(industry_analyses)
        }
        
        self.logger.info(f"分析完成，处理了{len(data)}条数据")
        return result
    
    def generate_market_overview(self, industry_analyses: Dict) -> Dict:
        """生成市场概览"""
        overview = {
            "total_industries": len(industry_analyses),
            "positive_industries": 0,
            "neutral_industries": 0,
            "cautious_industries": 0,
            "key_themes": [],
            "overall_sentiment": "中性"
        }
        
        # 分析各行业情绪
        for industry, analysis in industry_analyses.items():
            sentiment = analysis.get("market_sentiment", "中性")
            if sentiment == "积极":
                overview["positive_industries"] += 1
            elif sentiment == "谨慎":
                overview["cautious_industries"] += 1
            else:
                overview["neutral_industries"] += 1
        
        # 确定整体情绪
        if overview["positive_industries"] > overview["cautious_industries"]:
            overview["overall_sentiment"] = "积极"
        elif overview["cautious_industries"] > overview["positive_industries"]:
            overview["overall_sentiment"] = "谨慎"
        
        # 提取关键主题
        all_keywords = []
        for industry, analysis in industry_analyses.items():
            keywords = analysis.get("keywords", [])
            all_keywords.extend(keywords)
        
        # 找出最常见的关键词
        from collections import Counter
        if all_keywords:
            common_keywords = Counter(all_keywords).most_common(5)
            overview["key_themes"] = [word for word, count in common_keywords]
        
        return overview

if __name__ == "__main__":
    # 测试代码
    import yaml
    
    test_config = {
        "analysis": {
            "ai_model": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "api_key": "test_key",
                "api_base": "https://api.deepseek.com",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        },
        "prompts": {
            "trend_analysis": "分析数据：{data}",
            "daily_summary": "总结：{content}",
            "article_generation": "生成文章：{analysis}"
        }
    }
    
    analyzer = DeepSeekAnalyzer(test_config)
    
    # 测试数据
    test_data = [
        {
            "title": "AI芯片市场增长",
            "content": "AI芯片市场需求持续增长",
            "industry": "科技",
            "source": "测试源"
        }
    ]
    
    print("DeepSeek分析器测试完成")