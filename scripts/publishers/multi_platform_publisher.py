#!/usr/bin/env python3
"""
多平台发布器 - 集成微信公众号、小红书、微博等
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from pathlib import Path

from scripts.utils.logger import setup_logger
from scripts.utils.config_loader import load_config
from scripts.design.figma_client import FigmaClient
from scripts.publishers.wechat_publisher import WeChatPublisher

logger = setup_logger("multi_platform_publisher")


class MultiPlatformPublisher:
    """多平台发布器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化发布器"""
        self.config = load_config(config_path)
        self.publishing_config = self.config.get('publishing', {})
        
        # 初始化各平台发布器
        self.wechat_publisher = WeChatPublisher(config_path)
        self.figma_client = FigmaClient(config_path)
        
        # 平台配置
        self.platforms = {
            'wechat': {
                'enabled': self.publishing_config.get('wechat', {}).get('enabled', False),
                'publisher': self.wechat_publisher,
                'requires_design': True
            },
            'xiaohongshu': {
                'enabled': False,  # 需要单独配置
                'requires_design': True
            },
            'weibo': {
                'enabled': False,  # 需要单独配置
                'requires_design': True
            },
            'zhihu': {
                'enabled': False,  # 需要单独配置
                'requires_design': False  # 知乎支持Markdown
            },
            'twitter': {
                'enabled': False,  # 需要单独配置
                'requires_design': True
            }
        }
        
        # 输出目录
        self.output_dir = self.config.get('storage', {}).get('exports_dir', './data/exports')
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("多平台发布器初始化完成")
    
    def prepare_content(self, article_data: Dict) -> Dict[str, Any]:
        """准备多平台内容"""
        content_versions = {}
        
        # 基础内容
        base_content = {
            'title': article_data.get('title', ''),
            'content': article_data.get('content', ''),
            'author': article_data.get('author', 'AI智汇观察'),
            'date': article_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'tags': article_data.get('tags', []),
            'summary': article_data.get('summary', ''),
            'images': article_data.get('images', [])
        }
        
        # 微信公众号版本
        content_versions['wechat'] = {
            **base_content,
            'optimized': self._optimize_for_wechat(base_content)
        }
        
        # 小红书版本
        content_versions['xiaohongshu'] = {
            **base_content,
            'optimized': self._optimize_for_xiaohongshu(base_content)
        }
        
        # 微博版本
        content_versions['weibo'] = {
            **base_content,
            'optimized': self._optimize_for_weibo(base_content)
        }
        
        # 知乎版本
        content_versions['zhihu'] = {
            **base_content,
            'optimized': self._optimize_for_zhihu(base_content)
        }
        
        # Twitter版本
        content_versions['twitter'] = {
            **base_content,
            'optimized': self._optimize_for_twitter(base_content)
        }
        
        return content_versions
    
    def _optimize_for_wechat(self, content: Dict) -> Dict:
        """优化为微信公众号格式"""
        optimized = content.copy()
        
        # 添加引导语
        guide = f"大家好，我是{content['author']}。今天为大家带来最新的行业分析："
        optimized['content'] = guide + '\n\n' + content['content']
        
        # 添加关注引导
        footer = f"\n\n---\n关注微信公众号，每日获取最新行业分析"
        optimized['content'] += footer
        
        return optimized
    
    def _optimize_for_xiaohongshu(self, content: Dict) -> Dict:
        """优化为小红书格式"""
        optimized = content.copy()
        
        # 小红书喜欢短句、emoji、分段清晰
        lines = content['content'].split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                # 添加适当的emoji
                if any(keyword in line for keyword in ['关键', '重要', '核心']):
                    formatted_lines.append(f"🔑 {line}")
                elif any(keyword in line for keyword in ['建议', '推荐', '技巧']):
                    formatted_lines.append(f"💡 {line}")
                elif any(keyword in line for keyword in ['数据', '统计', '数字']):
                    formatted_lines.append(f"📊 {line}")
                elif any(keyword in line for keyword in ['警告', '注意', '风险']):
                    formatted_lines.append(f"⚠️  {line}")
                else:
                    formatted_lines.append(line)
        
        optimized['content'] = '\n\n'.join(formatted_lines)
        
        # 添加标签
        tags = content.get('tags', [])
        if tags:
            tag_str = ' '.join([f"#{tag}" for tag in tags[:5]])
            optimized['content'] += f"\n\n{tag_str}"
        
        return optimized
    
    def _optimize_for_weibo(self, content: Dict) -> Dict:
        """优化为微博格式"""
        optimized = content.copy()
        
        # 微博适合短平快，重点突出
        sentences = content['content'].split('。')
        key_sentences = []
        
        keywords = ['突破', '增长', '下降', '创新', '首次', '最高', '最低', '重要']
        for sentence in sentences:
            if any(keyword in sentence for keyword in keywords):
                key_sentences.append(sentence.strip())
                if len(key_sentences) >= 5:  # 微博不宜过长
                    break
        
        optimized['content'] = '。'.join(key_sentences)
        
        # 添加话题标签
        tags = content.get('tags', [])
        if tags:
            hashtags = ' '.join([f"#{tag}" for tag in tags[:3]])
            optimized['content'] += f"\n\n{hashtags}"
        
        return optimized
    
    def _optimize_for_zhihu(self, content: Dict) -> Dict:
        """优化为知乎格式"""
        optimized = content.copy()
        
        # 知乎喜欢深度、专业、有数据支持的内容
        # 保持Markdown格式，添加适当的标题和引用
        lines = content['content'].split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            if i == 0 and line.strip():
                # 第一行作为摘要
                formatted_lines.append(f"**{line}**")
            elif '数据' in line or '统计' in line:
                # 数据行加粗
                formatted_lines.append(f"**{line}**")
            else:
                formatted_lines.append(line)
        
        optimized['content'] = '\n'.join(formatted_lines)
        
        return optimized
    
    def _optimize_for_twitter(self, content: Dict) -> Dict:
        """优化为Twitter格式"""
        optimized = content.copy()
        
        # Twitter有字符限制，需要精简
        summary = content.get('summary', '')
        if len(summary) > 280:
            summary = summary[:277] + '...'
        
        optimized['content'] = summary
        
        # 添加话题标签（英文）
        tags = content.get('tags', [])
        if tags:
            # 简单翻译或使用通用标签
            english_tags = ['Tech', 'AI', 'Analysis', 'Trends']
            hashtags = ' '.join([f"#{tag}" for tag in english_tags[:3]])
            optimized['content'] += f"\n\n{hashtags}"
        
        return optimized
    
    def create_designs(self, content_versions: Dict) -> Dict[str, Any]:
        """为各平台创建设计"""
        if not self.config.get('figma', {}).get('enabled', False):
            logger.warning("Figma设计功能未启用")
            return {}
        
        designs = {}
        
        # 微信公众号设计
        if self.platforms['wechat']['enabled'] and self.platforms['wechat']['requires_design']:
            wechat_design = self.figma_client.create_wechat_design(content_versions['wechat'])
            if wechat_design:
                designs['wechat'] = wechat_design
        
        # 小红书设计
        if self.platforms['xiaohongshu']['enabled'] and self.platforms['xiaohongshu']['requires_design']:
            xiaohongshu_design = self.figma_client.create_xiaohongshu_design(content_versions['xiaohongshu'])
            if xiaohongshu_design:
                designs['xiaohongshu'] = xiaohongshu_design
        
        # 微博设计
        if self.platforms['weibo']['enabled'] and self.platforms['weibo']['requires_design']:
            weibo_design = self.figma_client.create_weibo_design(content_versions['weibo'])
            if weibo_design:
                designs['weibo'] = weibo_design
        
        return designs
    
    def export_designs(self, designs: Dict) -> Dict[str, Any]:
        """导出设计为图片"""
        exports = {}
        
        for platform, design in designs.items():
            if 'file_key' in design:
                # 获取需要导出的节点ID
                node_ids = list(design.get('node_map', {}).values())
                if node_ids:
                    platform_exports = self.figma_client.export_design(
                        design['file_key'],
                        node_ids,
                        formats=self.config.get('figma', {}).get('export', {}).get('formats', ['png'])
                    )
                    
                    if platform_exports:
                        exports[platform] = platform_exports
                        
                        # 保存图片到文件
                        self._save_exports(platform, platform_exports)
        
        return exports
    
    def _save_exports(self, platform: str, exports: Dict):
        """保存导出的图片"""
        platform_dir = os.path.join(self.output_dir, platform)
        os.makedirs(platform_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for format, images in exports.items():
            for node_id, image_url in images.items():
                if image_url:
                    try:
                        # 下载图片
                        response = requests.get(image_url, timeout=30)
                        if response.status_code == 200:
                            # 生成文件名
                            filename = f"{platform}_{timestamp}_{node_id}.{format}"
                            filepath = os.path.join(platform_dir, filename)
                            
                            # 保存文件
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            
                            logger.info(f"图片保存成功: {filepath}")
                    except Exception as e:
                        logger.error(f"图片保存失败 {image_url}: {e}")
    
    def publish_to_platforms(self, article_path: str, metadata: Dict) -> Dict[str, Any]:
        """发布到多个平台"""
        results = {}
        
        try:
            # 读取文章内容
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 准备多平台内容
            metadata['content'] = content
            content_versions = self.prepare_content(metadata)
            
            # 创建设计（如果启用Figma）
            designs = {}
            exports = {}
            
            if self.config.get('figma', {}).get('enabled', False):
                designs = self.create_designs(content_versions)
                exports = self.export_designs(designs)
            
            # 发布到各平台
            for platform, config in self.platforms.items():
                if config['enabled']:
                    platform_result = self._publish_to_platform(
                        platform, 
                        content_versions.get(platform, {}),
                        designs.get(platform),
                        exports.get(platform)
                    )
                    results[platform] = platform_result
            
            # 生成综合报告
            report = self._generate_report(results, designs, exports)
            
            logger.info("多平台发布完成")
            return report
            
        except Exception as e:
            logger.error(f"多平台发布失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _publish_to_platform(self, platform: str, content: Dict, 
                           design: Optional[Dict], exports: Optional[Dict]) -> Dict:
        """发布到单个平台"""
        result = {
            'platform': platform,
            'success': False,
            'message': '',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if platform == 'wechat':
                # 使用微信公众号发布器
                publish_result = self.wechat_publisher.publish_to_wechat(
                    content.get('optimized', {}).get('content', ''),
                    content
                )
                result.update(publish_result)
                
            elif platform == 'xiaohongshu':
                # 小红书发布（需要实现）
                result['message'] = '小红书发布功能待实现'
                result['success'] = False
                
            elif platform == 'weibo':
                # 微博发布（需要实现）
                result['message'] = '微博发布功能待实现'
                result['success'] = False
                
            elif platform == 'zhihu':
                # 知乎发布（需要实现）
                result['message'] = '知乎发布功能待实现'
                result['success'] = False
                
            elif platform == 'twitter':
                # Twitter发布（需要实现）
                result['message'] = 'Twitter发布功能待实现'
                result['success'] = False
            
            else:
                result['message'] = f'未知平台: {platform}'
                result['success'] = False
            
        except Exception as e:
            result['message'] = f'发布异常: {str(e)}'
            result['success'] = False
        
        return result
    
    def _generate_report(self, results: Dict, designs: Dict, exports: Dict) -> Dict:
        """生成发布报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'success': any(r.get('success', False) for r in results.values()),
            'platform_results': results,
            'designs_created': len(designs) > 0,
            'exports_generated': len(exports) > 0,
            'summary': {
                'total_platforms': len(results),
                'successful_platforms': sum(1 for r in results.values() if r.get('success', False)),
                'failed_platforms': sum(1 for r in results.values() if not r.get('success', False))
            }
        }
        
        # 保存报告
        report_dir = self.config.get('storage', {}).get('reports_dir', './data/reports')
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, f"multi_platform_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"发布报告已保存: {report_file}")
        return report


def main():
    """测试函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python multi_platform_publisher.py <文章路径>")
        return
    
    article_path = sys.argv[1]
    
    # 模拟文章元数据
    metadata = {
        'title': '科技行业日报：AI芯片竞争加剧与云计算价格战',
        'author': 'AI智汇观察',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'tags': ['科技', 'AI芯片', '云计算'],
        'summary': '今日科技行业三大趋势分析'
    }
    
    publisher = MultiPlatformPublisher()
    result = publisher.publish_to_platforms(article_path, metadata)
    
    print(f"发布结果: {json.dumps(result, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    main()