#!/usr/bin/env python3
"""
AI自动化博客系统 v3.0 - 集成微信公众号发布
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from scripts.utils.logger import setup_logger
from scripts.utils.config_loader import load_config
from scripts.collectors.collector_runner import CollectorRunner
from scripts.analyzers.trend_analyzer import TrendAnalyzer
from scripts.generators.article_generator import ArticleGenerator
from scripts.publishers.hugo_publisher import HugoPublisher
from scripts.publishers.wechat_publisher import WeChatPublisher
from scripts.monitoring.system_monitor import SystemMonitor


class AIBlogAutomationV3:
    """AI博客自动化系统 v3.0"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化系统"""
        self.config = load_config(config_path)
        self.logger = setup_logger("automation_v3")
        
        # 初始化各模块
        self.collector_runner = CollectorRunner(self.config)
        self.trend_analyzer = TrendAnalyzer(self.config)
        self.article_generator = ArticleGenerator(self.config)
        self.hugo_publisher = HugoPublisher(self.config)
        self.wechat_publisher = WeChatPublisher(config_path)
        self.system_monitor = SystemMonitor(self.config)
        
        # 运行统计
        self.stats = {
            'start_time': None,
            'end_time': None,
            'articles_collected': 0,
            'articles_analyzed': 0,
            'articles_generated': 0,
            'articles_published': 0,
            'wechat_drafts_created': 0,
            'errors': []
        }
    
    async def run_pipeline(self) -> Dict:
        """运行完整流水线"""
        self.stats['start_time'] = datetime.now().isoformat()
        self.logger.info("🚀 启动AI博客自动化流水线 v3.0")
        
        try:
            # 1. 系统健康检查
            self.logger.info("🔍 步骤1: 系统健康检查")
            health_status = await self.system_monitor.check_system_health()
            if not health_status['healthy']:
                self.logger.error(f"系统健康检查失败: {health_status['issues']}")
                return self._generate_error_report("系统健康检查失败")
            
            # 2. 数据采集
            self.logger.info("📥 步骤2: 数据采集")
            collected_data = await self.collector_runner.run_all_collectors()
            self.stats['articles_collected'] = len(collected_data)
            self.logger.info(f"采集完成: {self.stats['articles_collected']} 条数据")
            
            if not collected_data:
                self.logger.warning("未采集到数据，使用模拟数据继续")
                collected_data = self._get_sample_data()
            
            # 3. AI趋势分析
            self.logger.info("🧠 步骤3: AI趋势分析")
            analysis_results = []
            for industry, articles in collected_data.items():
                if articles:
                    self.logger.info(f"分析 {industry} 行业数据...")
                    analysis = await self.trend_analyzer.analyze_trends(articles, industry)
                    if analysis:
                        analysis_results.append({
                            'industry': industry,
                            'analysis': analysis,
                            'source_count': len(articles)
                        })
                        self.stats['articles_analyzed'] += len(articles)
            
            # 4. 内容生成
            self.logger.info("📝 步骤4: 内容生成")
            generated_articles = []
            for result in analysis_results:
                article = self.article_generator.generate_article(
                    analysis=result['analysis'],
                    industry=result['industry'],
                    source_count=result['source_count']
                )
                if article:
                    generated_articles.append(article)
                    self.stats['articles_generated'] += 1
            
            # 5. 发布到Hugo博客
            self.logger.info("🌐 步骤5: 发布到Hugo博客")
            published_articles = []
            for article in generated_articles:
                publish_result = self.hugo_publisher.publish_article(article)
                if publish_result['success']:
                    published_articles.append({
                        'file_path': publish_result['file_path'],
                        'metadata': article['metadata']
                    })
                    self.stats['articles_published'] += 1
            
            # 6. 微信公众号发布（如果启用）
            wechat_results = []
            if self.config.get('publishing', {}).get('wechat', {}).get('enabled', False):
                self.logger.info("📱 步骤6: 微信公众号发布")
                for article_info in published_articles:
                    wechat_result = self.wechat_publisher.publish_to_wechat(
                        article_info['file_path'],
                        article_info['metadata']
                    )
                    wechat_results.append(wechat_result)
                    if wechat_result.get('media_id'):
                        self.stats['wechat_drafts_created'] += 1
            
            # 7. 生成报告
            self.logger.info("📊 步骤7: 生成报告")
            report = self._generate_report(
                collected_data=collected_data,
                analysis_results=analysis_results,
                published_articles=published_articles,
                wechat_results=wechat_results
            )
            
            self.stats['end_time'] = datetime.now().isoformat()
            self.logger.info("✅ AI博客自动化流水线完成")
            
            return report
            
        except Exception as e:
            self.logger.error(f"流水线执行失败: {e}")
            self.stats['errors'].append(str(e))
            return self._generate_error_report(str(e))
    
    def _get_sample_data(self) -> Dict:
        """获取示例数据（当采集失败时使用）"""
        return {
            '科技': [
                {
                    'title': 'AI芯片技术新突破',
                    'content': '最新研究显示，新一代AI芯片能效比提升40%',
                    'source': '模拟数据',
                    'url': 'https://example.com'
                }
            ],
            '金融': [
                {
                    'title': '数字人民币试点扩大',
                    'content': '数字人民币在更多城市开展试点应用',
                    'source': '模拟数据', 
                    'url': 'https://example.com'
                }
            ]
        }
    
    def _generate_report(self, **kwargs) -> Dict:
        """生成执行报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'success': True,
            'pipeline_version': '3.0',
            'config_used': {
                'wechat_enabled': self.config.get('publishing', {}).get('wechat', {}).get('enabled', False),
                'auto_publish': self.config.get('publishing', {}).get('auto_publish', True)
            }
        }
        
        # 添加各阶段结果
        for key, value in kwargs.items():
            if isinstance(value, dict) or isinstance(value, list):
                report[key] = value
        
        # 保存报告到文件
        report_dir = self.config.get('storage', {}).get('reports_dir', './data/reports')
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"报告已保存: {report_file}")
        return report
    
    def _generate_error_report(self, error_message: str) -> Dict:
        """生成错误报告"""
        self.stats['end_time'] = datetime.now().isoformat()
        
        error_report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'success': False,
            'error': error_message,
            'pipeline_version': '3.0'
        }
        
        # 保存错误报告
        report_dir = self.config.get('storage', {}).get('reports_dir', './data/reports')
        os.makedirs(report_dir, exist_ok=True)
        
        error_file = os.path.join(report_dir, f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_report, f, ensure_ascii=False, indent=2)
        
        self.logger.error(f"错误报告已保存: {error_file}")
        return error_report


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI博客自动化系统 v3.0')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--test', action='store_true', help='测试模式')
    args = parser.parse_args()
    
    print("🤖 AI博客自动化系统 v3.0")
    print("=" * 50)
    
    # 初始化系统
    automation = AIBlogAutomationV3(args.config)
    
    if args.test:
        print("🧪 测试模式: 仅检查配置和依赖")
        # 这里可以添加测试逻辑
        print("✅ 系统初始化成功")
        return
    
    # 运行流水线
    print("🚀 开始执行自动化流水线...")
    result = await automation.run_pipeline()
    
    # 输出结果摘要
    print("\n" + "=" * 50)
    print("📊 执行结果摘要")
    print("-" * 30)
    
    if result['success']:
        print(f"✅ 流水线执行成功!")
        print(f"   采集文章: {result['stats']['articles_collected']}")
        print(f"   分析文章: {result['stats']['articles_analyzed']}")
        print(f"   生成文章: {result['stats']['articles_generated']}")
        print(f"   发布文章: {result['stats']['articles_published']}")
        
        if result['config_used']['wechat_enabled']:
            print(f"   微信草稿: {result['stats']['wechat_drafts_created']}")
        
        print(f"\n⏱️  开始时间: {result['stats']['start_time']}")
        print(f"   结束时间: {result['stats']['end_time']}")
        
        print("\n🎯 下一步:")
        print("   1. 访问博客: https://gsaecy.github.io")
        if result['config_used']['wechat_enabled']:
            print("   2. 检查微信公众号草稿箱")
        print("   3. 查看详细报告: data/reports/")
        
    else:
        print(f"❌ 流水线执行失败!")
        print(f"   错误: {result['error']}")
        print(f"\n🔧 建议:")
        print("   1. 检查配置文件")
        print("   2. 验证API密钥")
        print("   3. 查看错误日志")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(main())