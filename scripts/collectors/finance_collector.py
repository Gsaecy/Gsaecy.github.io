#!/usr/bin/env python3
"""
金融数据采集器
采集金融新闻、市场数据、行业报告等
"""

import os
import sys
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.collectors.base_collector import NewsCollector


class FinanceCollector(NewsCollector):
    """金融数据采集器基类"""
    
    def __init__(self, config: Dict[str, Any], source_config: Dict[str, Any]):
        super().__init__(config, source_config)
        
        # 金融数据特定配置
        self.market_data_enabled = source_config.get('market_data', True)
        self.include_stock_data = source_config.get('include_stock_data', False)
        self.include_forex_data = source_config.get('include_forex_data', False)
        self.include_crypto_data = source_config.get('include_crypto_data', False)
    
    async def collect(self) -> List[Dict[str, Any]]:
        """
        采集金融数据
        
        Returns:
            金融数据列表
        """
        self.logger.info(f"开始采集金融数据: {self.source_name}")
        
        data = []
        
        # 采集新闻数据
        news_data = await super().collect()
        data.extend(news_data)
        
        # 采集市场数据（如果启用）
        if self.market_data_enabled:
            market_data = await self.collect_market_data()
            data.extend(market_data)
        
        # 采集行业报告（如果适用）
        if self.source_type == 'report':
            report_data = await self.collect_reports()
            data.extend(report_data)
        
        return data
    
    async def collect_market_data(self) -> List[Dict[str, Any]]:
        """采集市场数据"""
        market_data = []
        
        try:
            # 股票市场数据
            if self.include_stock_data:
                stock_data = await self.collect_stock_data()
                market_data.extend(stock_data)
            
            # 外汇数据
            if self.include_forex_data:
                forex_data = await self.collect_forex_data()
                market_data.extend(forex_data)
            
            # 加密货币数据
            if self.include_crypto_data:
                crypto_data = await self.collect_crypto_data()
                market_data.extend(crypto_data)
            
        except Exception as e:
            self.logger.error(f"采集市场数据失败: {str(e)}")
        
        return market_data
    
    async def collect_stock_data(self) -> List[Dict[str, Any]]:
        """采集股票数据"""
        # 基础实现，子类可重写
        return []
    
    async def collect_forex_data(self) -> List[Dict[str, Any]]:
        """采集外汇数据"""
        # 基础实现，子类可重写
        return []
    
    async def collect_crypto_data(self) -> List[Dict[str, Any]]:
        """采集加密货币数据"""
        # 基础实现，子类可重写
        return []
    
    async def collect_reports(self) -> List[Dict[str, Any]]:
        """采集行业报告"""
        # 基础实现，子类可重写
        return []
    
    def extract_financial_metrics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """提取财务指标"""
        metrics = {}
        
        # 尝试提取表格数据
        tables = soup.find_all('table')
        for table in tables:
            # 查找包含财务数据的表格
            headers = table.find_all('th')
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = self.extract_text(cells[0]).strip()
                    value = self.extract_text(cells[1]).strip()
                    
                    if key and value:
                        # 清理键名
                        key = re.sub(r'[:：]', '', key)
                        metrics[key] = value
        
        return metrics


class WallStreetCNCollector(FinanceCollector):
    """华尔街见闻采集器"""
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """提取文章链接"""
        links = []
        
        # 华尔街见闻首页文章
        for article in soup.find_all('a', href=re.compile(r'/articles/\d+')):
            href = article.get('href', '')
            if href:
                if not href.startswith('http'):
                    href = f"https://wallstreetcn.com{href}"
                if href not in links:
                    links.append(href)
        
        # 新闻列表
        for article in soup.find_all('div', class_=re.compile(r'article-item')):
            link = article.find('a')
            if link:
                href = link.get('href', '')
                if href:
                    if not href.startswith('http'):
                        href = f"https://wallstreetcn.com{href}"
                    if href not in links:
                        links.append(href)
        
        # 热门文章
        for article in soup.find_all('a', class_=re.compile(r'hot-article')):
            href = article.get('href', '')
            if href:
                if not href.startswith('http'):
                    href = f"https://wallstreetcn.com{href}"
                if href not in links:
                    links.append(href)
        
        return links[:self.max_articles]
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        # 华尔街见闻标题选择器
        title_elem = soup.select_one('h1.article-title') or \
                    soup.select_one('h1.title') or \
                    soup.select_one('.article-header h1')
        
        if title_elem:
            title = self.extract_text(title_elem)
            if title:
                return title
        
        return super().extract_title(soup)
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """提取内容"""
        # 华尔街见闻内容区域
        content_elem = soup.select_one('.article-content') or \
                      soup.select_one('.content-body') or \
                      soup.select_one('article')
        
        if content_elem:
            # 清理不需要的元素
            for elem in content_elem.select('script, style, .ad-container, .related-articles'):
                elem.decompose()
            
            content = self.extract_text(content_elem)
            if content and len(content) > self.min_content_length:
                return content
        
        return super().extract_content(soup)
    
    def extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """提取发布日期"""
        # 华尔街见闻日期格式
        date_elem = soup.select_one('.publish-time') or \
                   soup.select_one('.article-meta time') or \
                   soup.select_one('meta[property="article:published_time"]')
        
        if date_elem:
            if date_elem.name == 'meta':
                return date_elem.get('content', '')
            else:
                date_text = self.extract_text(date_elem)
                if date_text:
                    # 尝试提取日期
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_text)
                    if date_match:
                        return date_match.group()
        
        return super().extract_publish_date(soup)
    
    async def collect_market_data(self) -> List[Dict[str, Any]]:
        """采集市场数据"""
        market_data = []
        
        try:
            # 采集A股数据
            ashare_data = await self.collect_ashare_data()
            market_data.extend(ashare_data)
            
            # 采集美股数据
            usstock_data = await self.collect_usstock_data()
            market_data.extend(usstock_data)
            
        except Exception as e:
            self.logger.error(f"采集市场数据失败: {str(e)}")
        
        return market_data
    
    async def collect_ashare_data(self) -> List[Dict[str, Any]]:
        """采集A股数据"""
        # 这里可以调用第三方API或解析相关页面
        # 示例：返回模拟数据
        return [
            {
                'type': 'market_data',
                'market': 'A股',
                'index': '上证指数',
                'value': '3200.00',
                'change': '+1.5%',
                'timestamp': datetime.now().isoformat()
            }
        ]
    
    async def collect_usstock_data(self) -> List[Dict[str, Any]]:
        """采集美股数据"""
        # 这里可以调用第三方API或解析相关页面
        # 示例：返回模拟数据
        return [
            {
                'type': 'market_data',
                'market': '美股',
                'index': '道琼斯指数',
                'value': '35000.00',
                'change': '+0.8%',
                'timestamp': datetime.now().isoformat()
            }
        ]


class IndustryReportCollector(FinanceCollector):
    """行业报告采集器"""
    
    async def collect(self) -> List[Dict[str, Any]]:
        """采集行业报告"""
        self.logger.info(f"开始采集行业报告: {self.source_name}")
        
        reports = []
        
        try:
            # 获取报告列表页
            list_html = await self.fetch_url(self.source_url)
            if not list_html:
                return []
            
            # 解析报告列表
            soup = self.parse_html(list_html, self.source_url)
            report_links = self.extract_report_links(soup)
            
            # 采集每份报告
            for link in report_links[:self.max_articles]:
                try:
                    report = await self.collect_report(link)
                    if report:
                        reports.append(report)
                        self.stats['articles_collected'] += 1
                except Exception as e:
                    self.logger.error(f"采集报告失败 {link}: {str(e)}")
                    continue
            
            # 保存数据
            if reports:
                self.save_raw_data(reports, 'raw')
            
            self.logger.info(f"采集完成: {self.source_name} - 共采集{len(reports)}份报告")
            
            return reports
            
        except Exception as e:
            self.logger.error(f"采集过程失败: {str(e)}")
            return []
    
    def extract_report_links(self, soup: BeautifulSoup) -> List[str]:
        """提取报告链接"""
        links = []
        
        # 通用报告链接模式
        patterns = [
            r'/report/\d+',
            r'/research/\d+',
            r'/analysis/\d+',
            r'\.pdf$',
            r'\.docx?$'
        ]
        
        for pattern in patterns:
            for link in soup.find_all('a', href=re.compile(pattern, re.I)):
                href = link.get('href', '')
                if href:
                    if not href.startswith('http'):
                        href = urljoin(self.source_url, href)
                    if href not in links:
                        links.append(href)
        
        return links
    
    async def collect_report(self, url: str) -> Optional[Dict[str, Any]]:
        """采集单份报告"""
        try:
            # 检查是否为PDF文件
            if url.lower().endswith('.pdf'):
                return await self.collect_pdf_report(url)
            
            # HTML报告
            html = await self.fetch_url(url)
            if not html:
                return None
            
            soup = self.parse_html(html, url)
            
            report = {
                'url': url,
                'title': self.extract_report_title(soup),
                'summary': self.extract_report_summary(soup),
                'publish_date': self.extract_publish_date(soup),
                'author': self.extract_author(soup),
                'industry': self.extract_industry(soup),
                'pages': self.extract_page_count(soup),
                'file_type': 'html',
                'source': self.source_name,
                'collected_at': datetime.now().isoformat()
            }
            
            # 提取报告内容（摘要）
            content = self.extract_report_content(soup)
            if content:
                report['content'] = content[:1000]  # 只保存前1000字符作为摘要
            
            # 提取关键数据
            metrics = self.extract_financial_metrics(soup)
            if metrics:
                report['metrics'] = metrics
            
            return report
            
        except Exception as e:
            self.logger.error(f"解析报告失败 {url}: {str(e)}")
            return None
    
    async def collect_pdf_report(self, url: str) -> Optional[Dict[str, Any]]:
        """采集PDF报告"""
        # 基础实现，实际项目中可能需要使用PDF解析库
        return {
            'url': url,
            'title': os.path.basename(url),
            'file_type': 'pdf',
            'source': self.source_name,
            'collected_at': datetime.now().isoformat(),
            'note': 'PDF报告需要额外处理'
        }
    
    def extract_report_title(self, soup: BeautifulSoup) -> str:
        """提取报告标题"""
        # 报告特定标题选择器
        title_elem = soup.select_one('h1.report-title') or \
                    soup.select_one('.report-header h1') or \
                    soup.select_one('h1')
        
        if title_elem:
            title = self.extract_text(title_elem)
            if title:
                return title
        
        return "未命名报告"
    
    def extract_report_summary(self, soup: BeautifulSoup) -> Optional[str]:
        """提取报告摘要"""
        # 报告摘要选择器
        summary_elem = soup.select_one('.report-summary') or \
                      soup.select_one('.executive-summary') or \
                      soup.select_one('.abstract')
        
        if summary_elem:
            summary = self.extract_text(summary_elem)
            if summary:
                return summary
        
        return None
    
    def extract_industry(self, soup: BeautifulSoup) -> Optional[str]:
        """提取所属行业"""
        # 尝试从各种位置提取行业信息
        industry_selectors = [
            '.industry-tag', '.sector', '.category',
            'meta[name="industry"]', 'meta[property="article:section"]'
        ]
        
        for selector in industry_selectors:
            if selector.startswith('meta'):
                meta_elem = soup.find('meta', {'name': 'industry'}) or \
                           soup.find('meta', {'property': 'article:section'})
                if meta_elem and meta_elem.get('content'):
                    return meta_elem['content']
            else:
                industry_elem = soup.select_one(selector)
                if industry_elem:
                    industry = self.extract_text(industry_elem)
                    if industry:
                        return industry
        
        return None
    
    def extract_page_count(self, soup: BeautifulSoup) -> Optional[int]:
        """提取页数"""
        # 查找页数信息
        page_text = None
        
        # 从文本中查找
        text = soup.get_text()
        page_match = re.search(r'(\d+)\s*页', text)
        if page_match:
            page_text = page_match.group(1)
        
        # 从特定元素查找
        if not page_text:
            page_elem = soup.select_one('.page-count') or \
                       soup.select_one('.total-pages')
            if page_elem:
                page_text = self.extract_text(page_elem)
        
        if page_text:
            try:
                return int(re.search(r'\d+', page_text).group())
            except:
                pass
        
        return None
    
    def extract_report_content(self, soup: BeautifulSoup) -> str:
        """提取报告内容（摘要）"""
        # 报告内容区域
        content_elem = soup.select_one('.report-content') or \
                      soup.select_one('.research-content') or \
                      soup.select_one('article')
        
        if content_elem:
            # 清理不需要的元素
            for elem in content_elem.select('script, style, .references, .appendix'):
                elem.decompose()
            
            content = self.extract_text(content_elem)
            if content:
                return content
        
        return ""