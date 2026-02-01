#!/usr/bin/env python3
"""
文章生成器
将分析结果转换为Hugo格式的Markdown文章
"""

import os
import yaml
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List

class ArticleGenerator:
    """文章生成器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(config.get('publish', {}).get('blog_path', './content/posts'))
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, analysis_results: List[Dict]) -> List[Dict]:
        """生成文章"""
        articles = []
        
        for result in analysis_results:
            try:
                article = self.generate_article(result)
                articles.append(article)
                
                # 保存到文件
                self.save_article(article)
                
            except Exception as e:
                self.logger.error(f"生成文章失败: {e}")
        
        return articles
    
    def generate_article(self, analysis: Dict) -> Dict:
        """生成单篇文章"""
        # 从分析结果中提取信息
        industry = analysis.get('industry', '综合')
        date_str = datetime.now().strftime('%Y-%m-%d')
        time_str = datetime.now().strftime('%H:%M')
        
        # 生成标题
        title = self.generate_title(industry, analysis)
        
        # 生成内容
        content = self.generate_content(analysis)
        
        # 生成元数据
        metadata = self.generate_metadata(title, industry, analysis)
        
        # 完整文章
        article = {
            'title': title,
            'content': content,
            'metadata': metadata,
            'filename': self.generate_filename(title),
            'filepath': self.output_dir / self.generate_filename(title)
        }
        
        return article
    
    def generate_title(self, industry: str, analysis: Dict) -> str:
        """生成文章标题"""
        trends = analysis.get('trends', [])
        key_events = analysis.get('key_events', [])
        
        if key_events:
            # 如果有重大事件，以事件为主题
            main_event = key_events[0].get('title', '')
            if main_event:
                return f"{industry}日报：{main_event}"
        
        if trends:
            # 以主要趋势为主题
            main_trend = trends[0].get('description', '')[:20]
            if main_trend:
                return f"{industry}趋势分析：{main_trend}"
        
        # 默认标题
        date_str = datetime.now().strftime('%m月%d日')
        return f"{industry}行业观察 - {date_str}"
    
    def generate_content(self, analysis: Dict) -> str:
        """生成文章内容"""
        industry = analysis.get('industry', '综合')
        trends = analysis.get('trends', [])
        key_events = analysis.get('key_events', [])
        insights = analysis.get('insights', [])
        data_points = analysis.get('data_points', [])
        
        content = f"# {industry}行业分析报告\n\n"
        content += f"*分析时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}*\n\n"
        
        # 执行摘要
        content += "## 📊 执行摘要\n\n"
        if analysis.get('summary'):
            content += f"{analysis['summary']}\n\n"
        
        # 关键事件
        if key_events:
            content += "## 🔥 关键事件\n\n"
            for i, event in enumerate(key_events[:5], 1):
                content += f"{i}. **{event.get('title', '')}**\n"
                content += f"   - {event.get('description', '')}\n"
                if event.get('impact'):
                    content += f"   - 影响：{event['impact']}\n"
                content += "\n"
        
        # 趋势分析
        if trends:
            content += "## 📈 趋势分析\n\n"
            for trend in trends[:5]:
                content += f"### {trend.get('name', '趋势')}\n"
                content += f"- **描述**：{trend.get('description', '')}\n"
                content += f"- **强度**：{trend.get('strength', '中等')}\n"
                content += f"- **持续时间**：{trend.get('duration', '短期')}\n"
                if trend.get('drivers'):
                    content += f"- **驱动因素**：{', '.join(trend['drivers'][:3])}\n"
                content += "\n"
        
        # 数据洞察
        if data_points:
            content += "## 📊 数据洞察\n\n"
            for data in data_points[:5]:
                content += f"- **{data.get('metric', '指标')}**：{data.get('value', '')}"
                if data.get('change'):
                    change = data['change']
                    arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                    content += f" ({arrow} {abs(change)}%)"
                content += "\n"
                if data.get('interpretation'):
                    content += f"  *{data['interpretation']}*\n"
                content += "\n"
        
        # 投资建议
        if insights:
            content += "## 💡 投资建议\n\n"
            for insight in insights[:3]:
                content += f"### {insight.get('category', '建议')}\n"
                content += f"{insight.get('content', '')}\n\n"
                if insight.get('confidence'):
                    content += f"*置信度：{insight['confidence']}*\n\n"
        
        # 风险提示
        content += "## ⚠️ 风险提示\n\n"
        content += "1. 市场波动风险：行业政策变化可能影响市场表现\n"
        content += "2. 技术风险：新技术发展不确定性\n"
        content += "3. 竞争风险：新进入者可能改变竞争格局\n\n"
        
        # 明日展望
        content += "## 🔮 明日展望\n\n"
        content += "1. 关注政策动向对行业的影响\n"
        content += "2. 跟踪关键技术突破进展\n"
        content += "3. 监测市场竞争格局变化\n\n"
        
        # 数据来源
        content += "---\n"
        content += "*本报告由AI行业观察站自动生成*\n"
        content += f"*分析模型：{analysis.get('model', 'GPT-4')}*\n"
        content += f"*数据来源：{', '.join(analysis.get('sources', ['公开数据']))}*\n"
        content += "*更新时间：{}*\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return content
    
    def generate_metadata(self, title: str, industry: str, analysis: Dict) -> str:
        """生成文章元数据（YAML front matter）"""
        date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
        
        # 提取标签
        tags = analysis.get('tags', [])
        if not tags:
            tags = [industry, 'AI分析', '行业报告']
        
        # 提取分类
        categories = analysis.get('categories', [industry])
        
        metadata = {
            'title': title,
            'date': date_str,
            'draft': False,
            'tags': tags[:5],
            'categories': categories[:2],
            'description': analysis.get('summary', f'{industry}行业最新分析和趋势洞察')[:150],
            'author': 'AI行业观察站'
        }
        
        # 转换为YAML格式
        yaml_str = yaml.dump(metadata, allow_unicode=True, sort_keys=False)
        return f"---\n{yaml_str}---\n"
    
    def generate_filename(self, title: str) -> str:
        """生成文件名"""
        # 清理标题，只保留字母数字和中文字符
        import re
        clean_title = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', title)
        clean_title = re.sub(r'-+', '-', clean_title).strip('-')
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"{date_str}-{clean_title[:50]}.md"
    
    def save_article(self, article: Dict):
        """保存文章到文件"""
        filepath = article['filepath']
        
        # 组合完整内容
        full_content = article['metadata'] + "\n" + article['content']
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        self.logger.info(f"文章已保存：{filepath}")
        
        # 返回保存的信息
        return {
            'filepath': str(filepath),
            'title': article['title'],
            'size': len(full_content)
        }

if __name__ == "__main__":
    # 测试代码
    config = {
        'publish': {
            'blog_path': './content/posts'
        }
    }
    
    # 模拟分析结果
    analysis = {
        'industry': '科技',
        'summary': '科技行业今日表现活跃，AI芯片和云计算领域有重要进展。',
        'trends': [
            {
                'name': 'AI芯片竞争加剧',
                'description': '国内外厂商纷纷推出新一代AI芯片',
                'strength': '强',
                'duration': '中长期'
            }
        ],
        'key_events': [
            {
                'title': '某公司发布新一代AI处理器',
                'description': '性能提升显著，引起行业关注',
                'impact': '可能改变竞争格局'
            }
        ],
        'tags': ['科技', 'AI芯片', '云计算'],
        'categories': ['科技'],
        'model': 'GPT-4',
        'sources': ['36氪', '虎嗅']
    }
    
    generator = ArticleGenerator(config)
    article = generator.generate([analysis])
    print(f"生成文章：{article[0]['title']}")