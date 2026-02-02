#!/usr/bin/env python3
"""
科技新闻采集器
采集36氪、虎嗅、钛媒体等科技新闻网站
"""

import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.collectors.base_collector import NewsCollector


class TechNewsCollector(NewsCollector):
    """科技新闻采集器"""
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """提取文章链接"""
        links = []
        
        # 36氪网站
        if '36kr.com' in self.source_url:
            # 36氪首页文章链接
            for article in soup.find_all('a', href=re.compile(r'/p/\d+')):
                href = article.get('href', '')
                if href and not href.startswith('http'):
                    href = f"https://36kr.com{href}"
                if href and href not in links:
                    links.append(href)
            
            # 36氪热门文章
            for article in soup.find_all('a', class_=re.compile(r'article-item-title')):
                href = article.get('href', '')
                if href and not href.startswith('http'):
                    href = f"https://36kr.com{href}"
                if href and href not in links:
                    links.append(href)
        
        # 虎嗅网站
        elif 'huxiu.com' in self.source_url:
            # 虎嗅首页文章
            for article in soup.find_all('a', href=re.compile(r'/article/\d+\.html')):
                href = article.get('href', '')
                if href and not href.startswith('http'):
                    href = f"https://www.huxiu.com{href}"
                if href and href not in links:
                    links.append(href)
            
            # 虎嗅推荐文章
            for article in soup.find_all('div', class_='article-item'):
                link = article.find('a')
                if link:
                    href = link.get('href', '')
                    if href and not href.startswith('http'):
                        href = f"https://www.huxiu.com{href}"
                    if href and href not in links:
                        links.append(href)
        
        # 钛媒体网站
        elif 'tmtpost.com' in self.source_url:
            # 钛媒体首页文章
            for article in soup.find_all('a', href=re.compile(r'/\d+\.html')):
                href = article.get('href', '')
                if href and not href.startswith('http'):
                    href = f"https://www.tmtpost.com{href}"
                if href and href not in links:
                    links.append(href)
            
            # 钛媒体列表文章
            for article in soup.find_all('div', class_=re.compile(r'post-item')):
                link = article.find('a')
                if link:
                    href = link.get('href', '')
                    if href and not href.startswith('http'):
                        href = f"https://www.tmtpost.com{href}"
                    if href and href not in links:
                        links.append(href)
        
        # 通用提取规则
        if not links:
            # 提取所有可能的文章链接
            for link in soup.find_all('a', href=True):
                href = link['href']
                # 过滤掉非文章链接
                if (href.startswith('http') and 
                    not any(x in href for x in ['javascript:', '#', 'mailto:', 'tel:']) and
                    not any(x in href for x in ['.jpg', '.png', '.gif', '.css', '.js']) and
                    len(href) > 20):  # 相对较长的链接可能是文章
                    if href not in links:
                        links.append(href)
        
        # 去重并返回
        return list(set(links))[:self.max_articles]
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """提取文章标题"""
        # 尝试多种选择器
        selectors = [
            'h1', 'h1.article-title', 'h1.title', 
            '.article-title', '.title', 'header h1',
            'h1.post-title', 'h1.entry-title'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = self.extract_text(title_elem)
                if title and len(title) > 5:
                    return title
        
        # 尝试meta标签
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title['content']
        
        # 尝试title标签
        if soup.title:
            return self.extract_text(soup.title)
        
        return "未找到标题"
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """提取文章内容"""
        # 尝试多种内容选择器
        content_selectors = [
            'article', '.article-content', '.content', 
            '.post-content', '.entry-content', '.main-content',
            'div[class*="content"]', 'div[class*="article"]',
            'div[class*="post"]', 'div[class*="entry"]'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 清理不需要的元素
                for elem in content_elem.select('script, style, nav, footer, aside, .ad, .ads'):
                    elem.decompose()
                
                content = self.extract_text(content_elem)
                if content and len(content) > self.min_content_length:
                    return content
        
        # 如果找不到特定内容区域，尝试提取所有段落
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = ' '.join([self.extract_text(p) for p in paragraphs])
            if len(content) > self.min_content_length:
                return content
        
        return ""
    
    def extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """提取发布日期"""
        # 尝试多种日期选择器
        date_selectors = [
            'time', '.publish-date', '.post-date', '.date',
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[name="date"]'
        ]
        
        for selector in date_selectors:
            if selector.startswith('meta'):
                meta_elem = soup.find('meta', {'property': 'article:published_time'}) or \
                           soup.find('meta', {'name': 'publish_date'}) or \
                           soup.find('meta', {'name': 'date'})
                if meta_elem and meta_elem.get('content'):
                    return meta_elem['content']
            else:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_text = self.extract_text(date_elem)
                    if date_text:
                        # 尝试解析日期
                        try:
                            # 常见日期格式
                            date_patterns = [
                                r'\d{4}-\d{2}-\d{2}',
                                r'\d{4}/\d{2}/\d{2}',
                                r'\d{4}年\d{2}月\d{2}日',
                                r'\d{2}-\d{2} \d{2}:\d{2}'
                            ]
                            
                            for pattern in date_patterns:
                                match = re.search(pattern, date_text)
                                if match:
                                    return match.group()
                        except:
                            pass
        
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """提取作者"""
        # 尝试多种作者选择器
        author_selectors = [
            '.author', '.post-author', '.article-author',
            'meta[name="author"]', 'meta[property="article:author"]',
            'span[class*="author"]', 'a[class*="author"]'
        ]
        
        for selector in author_selectors:
            if selector.startswith('meta'):
                meta_elem = soup.find('meta', {'name': 'author'}) or \
                           soup.find('meta', {'property': 'article:author'})
                if meta_elem and meta_elem.get('content'):
                    return meta_elem['content']
            else:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = self.extract_text(author_elem)
                    if author and len(author) > 1:
                        return author
        
        return None
    
    def extract_summary(self, soup: BeautifulSoup) -> Optional[str]:
        """提取摘要"""
        # 尝试meta描述
        meta_desc = soup.find('meta', {'name': 'description'}) or \
                   soup.find('meta', {'property': 'og:description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        
        # 尝试提取第一段作为摘要
        first_paragraph = soup.find('p')
        if first_paragraph:
            summary = self.extract_text(first_paragraph)
            if summary and len(summary) > 50:
                return summary[:200] + '...' if len(summary) > 200 else summary
        
        return None
    
    def extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """提取标签"""
        tags = []
        
        # 尝试多种标签选择器
        tag_selectors = [
            '.tags', '.post-tags', '.article-tags',
            'meta[name="keywords"]', 'a[rel="tag"]'
        ]
        
        for selector in tag_selectors:
            if selector.startswith('meta'):
                meta_elem = soup.find('meta', {'name': 'keywords'})
                if meta_elem and meta_elem.get('content'):
                    keywords = meta_elem['content'].split(',')
                    tags.extend([k.strip() for k in keywords if k.strip()])
            else:
                tag_elems = soup.select(selector)
                for elem in tag_elems:
                    tag_text = self.extract_text(elem)
                    if tag_text:
                        # 分割标签
                        tag_parts = re.split(r'[,，、\s]+', tag_text)
                        tags.extend([t.strip() for t in tag_parts if t.strip()])
        
        # 去重并返回
        return list(set(tags))[:10]
    
    def extract_images(self, soup: BeautifulSoup) -> List[str]:
        """提取图片"""
        images = []
        
        # 提取文章中的图片
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and not src.startswith('data:'):  # 排除base64图片
                images.append(src)
        
        # 提取Open Graph图片
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            images.append(og_image['content'])
        
        return images[:5]  # 只返回前5张图片


class Kr36Collector(TechNewsCollector):
    """36氪专用采集器"""
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """36氪专用文章链接提取"""
        links = []
        
        # 36氪新版首页
        for article in soup.find_all('a', class_=re.compile(r'feed-item-title')):
            href = article.get('href', '')
            if href:
                if not href.startswith('http'):
                    href = f"https://36kr.com{href}"
                if href not in links:
                    links.append(href)
        
        # 36氪热门文章
        for article in soup.find_all('div', class_='hotlist-item'):
            link = article.find('a')
            if link:
                href = link.get('href', '')
                if href:
                    if not href.startswith('http'):
                        href = f"https://36kr.com{href}"
                    if href not in links:
                        links.append(href)
        
        return links[:self.max_articles]
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """36氪专用内容提取"""
        # 36氪文章内容区域
        content_elem = soup.select_one('.articleDetailContent')
        if not content_elem:
            content_elem = soup.select_one('.article-content')
        
        if content_elem:
            # 清理不需要的元素
            for elem in content_elem.select('script, style, .recommend-article, .ad-box'):
                elem.decompose()
            
            content = self.extract_text(content_elem)
            if content and len(content) > self.min_content_length:
                return content
        
        return super().extract_content(soup)


class HuxiuCollector(TechNewsCollector):
    """虎嗅专用采集器"""
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """虎嗅专用文章链接提取"""
        links = []
        
        # 虎嗅首页文章
        for article in soup.find_all('div', class_='article-item'):
            link = article.find('a', class_='article-item-title')
            if link:
                href = link.get('href', '')
                if href:
                    if not href.startswith('http'):
                        href = f"https://www.huxiu.com{href}"
                    if href not in links:
                        links.append(href)
        
        # 虎嗅推荐
        for article in soup.find_all('a', class_='rec-article-title'):
            href = article.get('href', '')
            if href:
                if not href.startswith('http'):
                    href = f"https://www.huxiu.com{href}"
                if href not in links:
                    links.append(href)
        
        return links[:self.max_articles]
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """虎嗅专用内容提取"""
        # 虎嗅文章内容区域
        content_elem = soup.select_one('#article_content')
        if not content_elem:
            content_elem = soup.select_one('.article-content')
        
        if content_elem:
            # 清理不需要的元素
            for elem in content_elem.select('script, style, .article-share, .article-tags'):
                elem.decompose()
            
            content = self.extract_text(content_elem)
            if content and len(content) > self.min_content_length:
                return content
        
        return super().extract_content(soup)


class TMTPostCollector(TechNewsCollector):
    """钛媒体专用采集器"""
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """钛媒体专用文章链接提取"""
        links = []
        
        # 钛媒体首页文章
        for article in soup.find_all('div', class_='post-item'):
            link = article.find('a')
            if link:
                href = link.get('href', '')
                if href:
                    if not href.startswith('http'):
                        href = f"https://www.tmtpost.com{href}"
                    if href not in links:
                        links.append(href)
        
        # 钛媒体列表
        for article in soup.find_all('a', class_='post-title'):
            href = article.get('href', '')
            if href:
                if not href.startswith('http'):
                    href = f"https://www.tmtpost.com{href}"
                if href not in links:
                    links.append(href)
        
        return links[:self.max_articles]
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """钛媒体专用内容提取"""
        # 钛媒体文章内容区域
        content_elem = soup.select_one('.post-article')
        if not content_elem:
            content_elem = soup.select_one('.article-content')
        
        if content_elem:
            # 清理不需要的元素
            for elem in content_elem.select('script, style, .related-posts, .ad-container'):
                elem.decompose()
            
            content = self.extract_text(content_elem)
            if content and len(content) > self.min_content_length:
                return content
        
        return super().extract_content(soup)