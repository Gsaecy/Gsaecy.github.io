#!/usr/bin/env python3
"""
科技新闻采集器
"""

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from typing import List, Dict
import json

class TechNewsCollector:
    """科技新闻采集器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.sources = config.get('sources', {}).get('tech', [])
        
    def collect(self) -> List[Dict]:
        """采集科技新闻"""
        all_news = []
        
        for source in self.sources:
            try:
                news = self.collect_from_source(source)
                all_news.extend(news)
                self.logger.info(f"从 {source.get('name')} 采集到 {len(news)} 条新闻")
            except Exception as e:
                self.logger.error(f"采集 {source.get('name')} 失败: {e}")
        
        return all_news
    
    def collect_from_source(self, source: Dict) -> List[Dict]:
        """从单个源采集"""
        url = source.get('url', '')
        source_type = source.get('type', 'news')
        source_name = source.get('name', '未知源')
        
        if not url:
            return []
        
        # 这里简化处理，实际需要根据不同的网站编写解析逻辑
        # 示例：模拟采集一些数据
        sample_news = [
            {
                'title': 'AI芯片公司发布新一代处理器',
                'content': '某AI芯片公司今日发布新一代处理器，性能提升50%，功耗降低30%。',
                'source': source_name,
                'url': f'{url}/news/1',
                'publish_time': datetime.now().isoformat(),
                'category': '科技',
                'tags': ['AI芯片', '处理器', '半导体'],
                'importance': 'high'
            },
            {
                'title': '云计算市场竞争加剧',
                'content': '各大云服务商纷纷降价，市场竞争进入白热化阶段。',
                'source': source_name,
                'url': f'{url}/news/2',
                'publish_time': datetime.now().isoformat(),
                'category': '科技',
                'tags': ['云计算', '市场竞争', '云服务'],
                'importance': 'medium'
            },
            {
                'title': '自动驾驶技术新突破',
                'content': '某公司宣布其自动驾驶系统在复杂城市道路测试中表现优异。',
                'source': source_name,
                'url': f'{url}/news/3',
                'publish_time': datetime.now().isoformat(),
                'category': '科技',
                'tags': ['自动驾驶', '智能交通', 'AI'],
                'importance': 'medium'
            }
        ]
        
        return sample_news
    
    def parse_36kr(self, html: str) -> List[Dict]:
        """解析36氪网站（示例）"""
        # 实际实现需要根据网站结构编写
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []
        
        # 示例解析逻辑
        articles = soup.find_all('article', class_='article-item')[:10]
        
        for article in articles:
            try:
                title_elem = article.find('h3')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.find('a')
                url = link['href'] if link else ''
                
                summary_elem = article.find('p', class_='summary')
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                time_elem = article.find('time')
                publish_time = time_elem['datetime'] if time_elem else datetime.now().isoformat()
                
                news_items.append({
                    'title': title,
                    'content': summary,
                    'source': '36氪',
                    'url': f'https://36kr.com{url}' if url.startswith('/') else url,
                    'publish_time': publish_time,
                    'category': '科技',
                    'tags': self.extract_tags(summary),
                    'importance': self.calculate_importance(title, summary)
                })
            except Exception as e:
                self.logger.warning(f"解析文章失败: {e}")
                continue
        
        return news_items
    
    def extract_tags(self, text: str) -> List[str]:
        """从文本中提取标签"""
        # 简化实现，实际可以使用NLP技术
        common_tags = ['AI', '人工智能', '大数据', '云计算', '区块链', '物联网', '5G']
        tags = []
        
        for tag in common_tags:
            if tag in text:
                tags.append(tag)
        
        return tags[:3]  # 最多返回3个标签
    
    def calculate_importance(self, title: str, content: str) -> str:
        """计算新闻重要性"""
        important_keywords = ['重大', '突破', '首次', '革命性', '颠覆']
        
        text = title + content
        for keyword in important_keywords:
            if keyword in text:
                return 'high'
        
        return 'medium'

if __name__ == "__main__":
    # 测试代码
    import yaml
    
    config = {
        'sources': {
            'tech': [
                {'name': '36氪', 'url': 'https://36kr.com', 'type': 'news'},
                {'name': '虎嗅', 'url': 'https://huxiu.com', 'type': 'news'}
            ]
        }
    }
    
    collector = TechNewsCollector(config)
    news = collector.collect()
    print(f"采集到 {len(news)} 条新闻")
    for item in news[:2]:
        print(f"- {item['title']}")