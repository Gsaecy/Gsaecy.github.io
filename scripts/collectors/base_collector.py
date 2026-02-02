#!/usr/bin/env python3
"""
基础数据采集器
提供通用的采集功能，包括HTTP请求、数据解析、错误处理等
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import httpx
from urllib.parse import urljoin, urlparse
import hashlib

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.utils.logger import setup_logger
from scripts.utils.cache import CacheManager


class BaseCollector(ABC):
    """基础数据采集器抽象类"""
    
    def __init__(self, config: Dict[str, Any], source_config: Dict[str, Any]):
        """
        初始化采集器
        
        Args:
            config: 系统配置
            source_config: 数据源配置
        """
        self.config = config
        self.source_config = source_config
        self.source_name = source_config.get('name', 'unknown')
        self.source_url = source_config.get('url', '')
        self.source_type = source_config.get('type', 'unknown')
        
        # 设置日志
        self.logger = setup_logger(f"collector.{self.source_name}", 
                                  level=config.get('logging', {}).get('level', 'INFO'))
        
        # 初始化缓存
        cache_dir = config.get('storage', {}).get('cache_dir', './data/cache')
        self.cache = CacheManager(cache_dir, prefix=f"collector_{self.source_name}")
        
        # HTTP客户端配置
        self.timeout = config.get('collectors', {}).get('timeout', 30)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
        }
        
        # 采集参数
        self.max_articles = config.get('collectors', {}).get('parameters', {}).get('max_articles_per_source', 20)
        self.min_content_length = config.get('collectors', {}).get('parameters', {}).get('min_content_length', 100)
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'articles_collected': 0,
            'articles_filtered': 0,
            'last_collection_time': None,
            'collection_duration': 0
        }
    
    @abstractmethod
    async def collect(self) -> List[Dict[str, Any]]:
        """
        执行数据采集
        
        Returns:
            采集到的文章列表
        """
        pass
    
    async def fetch_url(self, url: str, method: str = 'GET', 
                       params: Optional[Dict] = None, 
                       data: Optional[Dict] = None,
                       use_cache: bool = True) -> Optional[str]:
        """
        获取URL内容
        
        Args:
            url: 目标URL
            method: HTTP方法
            params: 查询参数
            data: 请求数据
            use_cache: 是否使用缓存
            
        Returns:
            响应内容或None
        """
        # 生成缓存键
        cache_key = hashlib.md5(f"{url}_{method}_{str(params)}_{str(data)}".encode()).hexdigest()
        
        # 检查缓存
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                self.logger.debug(f"从缓存获取: {url}")
                return cached
        
        try:
            self.stats['total_requests'] += 1
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                if method.upper() == 'GET':
                    response = await client.get(url, params=params)
                elif method.upper() == 'POST':
                    response = await client.post(url, params=params, data=data)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                
                # 记录成功
                self.stats['successful_requests'] += 1
                duration = time.time() - start_time
                self.logger.debug(f"获取成功: {url} - 状态码: {response.status_code} - 耗时: {duration:.2f}s")
                
                content = response.text
                
                # 保存到缓存
                if use_cache:
                    cache_ttl = self.source_config.get('update_interval', 3600)
                    self.cache.set(cache_key, content, ttl=cache_ttl)
                
                return content
                
        except httpx.TimeoutException:
            self.stats['failed_requests'] += 1
            self.logger.warning(f"请求超时: {url}")
        except httpx.HTTPStatusError as e:
            self.stats['failed_requests'] += 1
            self.logger.warning(f"HTTP错误: {url} - 状态码: {e.response.status_code}")
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.logger.error(f"请求失败: {url} - 错误: {str(e)}")
        
        return None
    
    def parse_html(self, html: str, url: str = '') -> BeautifulSoup:
        """
        解析HTML内容
        
        Args:
            html: HTML内容
            url: 原始URL（用于相对路径转换）
            
        Returns:
            BeautifulSoup对象
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # 更新所有相对链接为绝对链接
            if url:
                for tag in soup.find_all(['a', 'img', 'link', 'script']):
                    for attr in ['href', 'src']:
                        if tag.has_attr(attr):
                            tag[attr] = urljoin(url, tag[attr])
            
            return soup
        except Exception as e:
            self.logger.error(f"HTML解析失败: {str(e)}")
            # 回退到html.parser
            return BeautifulSoup(html, 'html.parser')
    
    def extract_text(self, element, strip: bool = True) -> str:
        """
        提取元素的文本内容
        
        Args:
            element: BeautifulSoup元素
            strip: 是否去除空白字符
            
        Returns:
            提取的文本
        """
        if not element:
            return ''
        
        text = element.get_text()
        if strip:
            text = ' '.join(text.split())
        
        return text
    
    def filter_article(self, article: Dict[str, Any]) -> bool:
        """
        过滤文章，检查是否符合要求
        
        Args:
            article: 文章数据
            
        Returns:
            是否通过过滤
        """
        # 检查必要字段
        required_fields = ['title', 'content', 'url']
        for field in required_fields:
            if not article.get(field):
                self.logger.debug(f"文章缺少必要字段: {field}")
                return False
        
        # 检查内容长度
        content = article.get('content', '')
        if len(content) < self.min_content_length:
            self.logger.debug(f"文章内容过短: {len(content)} 字符")
            return False
        
        # 检查重复内容（简单检查）
        if self.is_duplicate(article):
            self.logger.debug(f"检测到重复文章: {article.get('title')}")
            return False
        
        return True
    
    def is_duplicate(self, article: Dict[str, Any]) -> bool:
        """
        检查文章是否重复
        
        Args:
            article: 文章数据
            
        Returns:
            是否重复
        """
        # 使用标题和内容生成唯一标识
        content_hash = hashlib.md5(
            f"{article.get('title', '')}_{article.get('content', '')[:100]}".encode()
        ).hexdigest()
        
        # 检查缓存中是否存在
        duplicate_key = f"duplicate_{content_hash}"
        if self.cache.get(duplicate_key):
            return True
        
        # 标记为已处理
        self.cache.set(duplicate_key, '1', ttl=86400)  # 24小时
        return False
    
    def save_raw_data(self, data: List[Dict[str, Any]], data_type: str = 'raw'):
        """
        保存原始数据
        
        Args:
            data: 要保存的数据
            data_type: 数据类型（raw, processed等）
        """
        if not data:
            return
        
        try:
            # 创建数据目录
            data_dir = self.config.get('storage', {}).get(f'{data_type}_data_dir', f'./data/{data_type}')
            os.makedirs(data_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            source_safe = self.source_name.replace('/', '_').replace('\\', '_')
            filename = f"{source_safe}_{timestamp}.json"
            filepath = os.path.join(data_dir, filename)
            
            # 保存数据
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'source': self.source_name,
                    'type': self.source_type,
                    'collection_time': timestamp,
                    'data': data,
                    'stats': self.stats
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"保存{data_type}数据到: {filepath} - 共{len(data)}条记录")
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取采集统计信息
        
        Returns:
            统计信息字典
        """
        return {
            **self.stats,
            'source_name': self.source_name,
            'source_url': self.source_url,
            'source_type': self.source_type,
            'timestamp': datetime.now().isoformat()
        }
    
    def cleanup(self):
        """清理资源"""
        pass


class NewsCollector(BaseCollector):
    """新闻采集器基类"""
    
    async def collect(self) -> List[Dict[str, Any]]:
        """
        采集新闻数据
        
        Returns:
            新闻文章列表
        """
        self.logger.info(f"开始采集新闻: {self.source_name}")
        start_time = time.time()
        
        try:
            # 获取新闻列表页
            list_html = await self.fetch_url(self.source_url)
            if not list_html:
                self.logger.error(f"无法获取新闻列表页: {self.source_url}")
                return []
            
            # 解析新闻列表
            soup = self.parse_html(list_html, self.source_url)
            article_links = self.extract_article_links(soup)
            
            # 限制文章数量
            article_links = article_links[:self.max_articles]
            
            # 采集每篇文章
            articles = []
            for link in article_links:
                try:
                    article = await self.collect_article(link)
                    if article and self.filter_article(article):
                        articles.append(article)
                        self.stats['articles_collected'] += 1
                    else:
                        self.stats['articles_filtered'] += 1
                except Exception as e:
                    self.logger.error(f"采集文章失败 {link}: {str(e)}")
                    continue
            
            # 保存原始数据
            if articles and self.config.get('collectors', {}).get('parameters', {}).get('save_raw_data', True):
                self.save_raw_data(articles, 'raw')
            
            # 更新统计
            duration = time.time() - start_time
            self.stats['collection_duration'] = duration
            self.stats['last_collection_time'] = datetime.now().isoformat()
            
            self.logger.info(f"采集完成: {self.source_name} - 共采集{len(articles)}篇文章 - 耗时{duration:.2f}s")
            
            return articles
            
        except Exception as e:
            self.logger.error(f"采集过程失败: {str(e)}")
            return []
    
    @abstractmethod
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """
        从列表页提取文章链接
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            文章链接列表
        """
        pass
    
    async def collect_article(self, url: str) -> Optional[Dict[str, Any]]:
        """
        采集单篇文章
        
        Args:
            url: 文章URL
            
        Returns:
            文章数据字典
        """
        try:
            # 获取文章内容
            html = await self.fetch_url(url)
            if not html:
                return None
            
            # 解析文章
            soup = self.parse_html(html, url)
            
            # 提取文章信息
            article = {
                'url': url,
                'title': self.extract_title(soup),
                'content': self.extract_content(soup),
                'publish_date': self.extract_publish_date(soup),
                'author': self.extract_author(soup),
                'summary': self.extract_summary(soup),
                'tags': self.extract_tags(soup),
                'images': self.extract_images(soup),
                'source': self.source_name,
                'source_url': self.source_url,
                'collected_at': datetime.now().isoformat()
            }
            
            return article
            
        except Exception as e:
            self.logger.error(f"解析文章失败 {url}: {str(e)}")
            return None
    
    @abstractmethod
    def extract_title(self, soup: BeautifulSoup) -> str:
        """提取文章标题"""
        pass
    
    @abstractmethod
    def extract_content(self, soup: BeautifulSoup) -> str:
        """提取文章内容"""
        pass
    
    def extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """提取发布日期"""
        # 默认实现，子类可重写
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """提取作者"""
        return None
    
    def extract_summary(self, soup: BeautifulSoup) -> Optional[str]:
        """提取摘要"""
        return None
    
    def extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """提取标签"""
        return []
    
    def extract_images(self, soup: BeautifulSoup) -> List[str]:
        """提取图片"""
        return []