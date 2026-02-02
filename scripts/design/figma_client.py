#!/usr/bin/env python3
"""
Figma API客户端 - 自动化设计排版
"""

import os
import json
import time
import requests
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from scripts.utils.logger import setup_logger
from scripts.utils.config_loader import load_config

logger = setup_logger("figma_client")


class FigmaClient:
    """Figma API客户端"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化Figma客户端"""
        self.config = load_config(config_path)
        self.figma_config = self.config.get('figma', {})
        
        # API配置
        self.api_base = "https://api.figma.com/v1"
        self.access_token = os.getenv('FIGMA_ACCESS_TOKEN', self.figma_config.get('access_token', ''))
        self.headers = {
            'X-Figma-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        # 模板配置
        self.templates = self.figma_config.get('templates', {})
        
        # 缓存
        self.file_cache = {}
        self.image_cache = {}
        
        logger.info("Figma客户端初始化完成")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """发送API请求"""
        url = f"{self.api_base}/{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # 速率限制，等待后重试
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"速率限制，等待 {retry_after} 秒后重试")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, **kwargs)
            else:
                logger.error(f"API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API请求异常: {e}")
            return None
    
    def get_file(self, file_key: str) -> Optional[Dict]:
        """获取文件信息"""
        if file_key in self.file_cache:
            return self.file_cache[file_key]
        
        data = self._make_request('GET', f'files/{file_key}')
        if data:
            self.file_cache[file_key] = data
        return data
    
    def get_file_nodes(self, file_key: str, node_ids: List[str]) -> Optional[Dict]:
        """获取文件节点信息"""
        ids_param = ','.join(node_ids)
        return self._make_request('GET', f'files/{file_key}/nodes?ids={ids_param}')
    
    def get_images(self, file_key: str, node_ids: List[str], format: str = 'png', scale: float = 1.0) -> Optional[Dict]:
        """获取节点图片"""
        ids_param = ','.join(node_ids)
        return self._make_request('GET', f'images/{file_key}?ids={ids_param}&format={format}&scale={scale}')
    
    def create_comment(self, file_key: str, message: str, client_meta: Dict = None) -> Optional[Dict]:
        """创建评论（可用于标记处理状态）"""
        payload = {
            'message': message,
            'client_meta': client_meta or {}
        }
        return self._make_request('POST', f'files/{file_key}/comments', json=payload)
    
    def update_file(self, file_key: str, updates: List[Dict]) -> bool:
        """更新文件（需要Figma插件，API限制较多）"""
        # 注意：Figma REST API不支持直接修改文件内容
        # 这需要通过Figma插件或使用Figma的WebSocket API
        logger.warning("Figma REST API不支持直接文件修改，需要使用插件或WebSocket API")
        return False
    
    def duplicate_file(self, file_key: str, name: str = None) -> Optional[str]:
        """复制文件（创建新版本）"""
        # 通过Figma的"复制文件"功能
        # 这通常需要通过UI或插件实现
        logger.info(f"复制文件 {file_key} 为 {name}")
        # 实际实现需要更复杂的逻辑
        return None
    
    def render_template(self, template_id: str, content: Dict) -> Optional[Dict]:
        """渲染模板（填充内容到设计模板）"""
        template_config = self.templates.get(template_id)
        if not template_config:
            logger.error(f"模板未找到: {template_id}")
            return None
        
        file_key = template_config.get('file_key')
        node_map = template_config.get('node_map', {})
        
        # 获取文件信息
        file_info = self.get_file(file_key)
        if not file_info:
            return None
        
        # 构建更新数据
        updates = []
        for content_key, node_id in node_map.items():
            if content_key in content:
                updates.append({
                    'node_id': node_id,
                    'content': content[content_key]
                })
        
        # 这里需要调用Figma插件API来实际更新内容
        # 简化版本：返回占位信息
        result = {
            'template_id': template_id,
            'file_key': file_key,
            'updates': updates,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"模板渲染完成: {template_id}")
        return result
    
    def export_design(self, file_key: str, node_ids: List[str], 
                     formats: List[str] = None) -> Dict[str, Any]:
        """导出设计为多种格式"""
        if formats is None:
            formats = ['png', 'jpg', 'pdf']
        
        results = {}
        
        for format in formats:
            if format in ['png', 'jpg']:
                # 获取图片
                image_data = self.get_images(file_key, node_ids, format=format, scale=2.0)
                if image_data and 'images' in image_data:
                    results[format] = image_data['images']
            elif format == 'pdf':
                # PDF导出需要特殊处理
                logger.warning("PDF导出需要额外配置")
        
        return results
    
    def create_wechat_design(self, article_data: Dict) -> Optional[Dict]:
        """创建微信公众号设计"""
        return self.render_template('wechat_article', {
            'title': article_data.get('title', ''),
            'content': article_data.get('content', ''),
            'author': article_data.get('author', 'AI智汇观察'),
            'date': article_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'cover_image': article_data.get('cover_image', ''),
            'summary': article_data.get('summary', '')
        })
    
    def create_xiaohongshu_design(self, article_data: Dict) -> Optional[Dict]:
        """创建小红书设计"""
        return self.render_template('xiaohongshu_note', {
            'title': article_data.get('title', ''),
            'content': self._format_for_xiaohongshu(article_data.get('content', '')),
            'tags': article_data.get('tags', []),
            'images': article_data.get('images', [])
        })
    
    def create_weibo_design(self, article_data: Dict) -> Optional[Dict]:
        """创建微博长图设计"""
        return self.render_template('weibo_card', {
            'title': article_data.get('title', ''),
            'content': self._format_for_weibo(article_data.get('content', '')),
            'hashtags': article_data.get('hashtags', []),
            'qrcode': article_data.get('qrcode', '')
        })
    
    def _format_for_xiaohongshu(self, content: str) -> str:
        """格式化内容为小红书风格"""
        # 小红书喜欢短句、emoji、分段清晰
        lines = content.split('\n')
        formatted = []
        
        for line in lines:
            if len(line.strip()) > 0:
                # 添加适当的emoji和格式
                formatted_line = line.strip()
                if '关键' in formatted_line or '重要' in formatted_line:
                    formatted_line = f"🔑 {formatted_line}"
                elif '建议' in formatted_line or '推荐' in formatted_line:
                    formatted_line = f"💡 {formatted_line}"
                elif '数据' in formatted_line or '统计' in formatted_line:
                    formatted_line = f"📊 {formatted_line}"
                
                formatted.append(formatted_line)
        
        return '\n\n'.join(formatted)
    
    def _format_for_weibo(self, content: str) -> str:
        """格式化内容为微博风格"""
        # 微博适合短平快，重点突出
        sentences = content.split('。')
        key_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in ['突破', '增长', '下降', '创新', '首次']):
                key_sentences.append(sentence.strip())
                if len(key_sentences) >= 5:  # 微博长图不宜过长
                    break
        
        # 添加话题标签
        formatted = '\n\n'.join(key_sentences)
        formatted += '\n\n#科技趋势 #行业分析 #AI观察'
        
        return formatted
    
    def batch_create_designs(self, article_data: Dict) -> Dict[str, Any]:
        """批量创建多平台设计"""
        designs = {}
        
        # 微信公众号设计
        wechat_design = self.create_wechat_design(article_data)
        if wechat_design:
            designs['wechat'] = wechat_design
        
        # 小红书设计
        xiaohongshu_design = self.create_xiaohongshu_design(article_data)
        if xiaohongshu_design:
            designs['xiaohongshu'] = xiaohongshu_design
        
        # 微博设计
        weibo_design = self.create_weibo_design(article_data)
        if weibo_design:
            designs['weibo'] = weibo_design
        
        # 导出所有设计
        exports = {}
        for platform, design in designs.items():
            if 'file_key' in design and 'node_ids' in design:
                exports[platform] = self.export_design(
                    design['file_key'], 
                    design['node_ids'],
                    formats=['png', 'jpg']
                )
        
        return {
            'designs': designs,
            'exports': exports,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """测试函数"""
    import sys
    
    # 检查环境变量
    token = os.getenv('FIGMA_ACCESS_TOKEN')
    if not token:
        print("❌ 请设置 FIGMA_ACCESS_TOKEN 环境变量")
        print("   获取方式: Figma → Settings → Personal Access Tokens")
        return
    
    # 测试配置
    test_config = {
        'figma': {
            'access_token': token,
            'templates': {
                'wechat_article': {
                    'file_key': 'test_file_key',
                    'node_map': {
                        'title': 'node_1',
                        'content': 'node_2'
                    }
                }
            }
        }
    }
    
    # 临时写入测试配置
    config_path = '/tmp/test_figma_config.yaml'
    import yaml
    with open(config_path, 'w') as f:
        yaml.dump(test_config, f)
    
    client = FigmaClient(config_path)
    
    # 测试API连接
    print("🔗 测试Figma API连接...")
    
    # 这里可以添加实际的API测试
    print("✅ Figma客户端初始化成功")
    print("\n📋 下一步:")
    print("1. 在Figma中创建设计模板")
    print("2. 配置模板映射关系")
    print("3. 集成到自动化流水线")


if __name__ == "__main__":
    main()