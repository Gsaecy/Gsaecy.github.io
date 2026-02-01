#!/usr/bin/env python3
"""
AI行业观察站 - 主控制脚本
自动采集、分析、生成和发布行业分析文章
"""

import os
import sys
import yaml
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.collectors.tech_news import TechNewsCollector
from scripts.collectors.finance_data import FinanceDataCollector
from scripts.collectors.social_trends import SocialTrendsCollector
from scripts.analyzers.summarizer import Summarizer
from scripts.analyzers.analyzer import IndustryAnalyzer
from scripts.generators.article_generator import ArticleGenerator
from scripts.publishers.hugo_publisher import HugoPublisher

class AIIndustryObserver:
    """AI行业观察站主控制器"""
    
    def __init__(self, config_path="config/config.yaml"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.collectors = []
        self.analyzers = []
        self.generators = []
        self.publishers = []
        
        self.init_components()
    
    def load_config(self, config_path):
        """加载配置文件"""
        config_file = project_root / config_path
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', './logs/app.log')),
                logging.StreamHandler()
            ]
        )
    
    def init_components(self):
        """初始化各个组件"""
        self.logger.info("初始化组件...")
        
        # 初始化采集器
        if 'tech' in self.config.get('sources', {}):
            self.collectors.append(TechNewsCollector(self.config))
        
        if 'finance' in self.config.get('sources', {}):
            self.collectors.append(FinanceDataCollector(self.config))
        
        if 'social' in self.config.get('sources', {}):
            self.collectors.append(SocialTrendsCollector(self.config))
        
        # 初始化分析器
        self.analyzers.append(Summarizer(self.config))
        self.analyzers.append(IndustryAnalyzer(self.config))
        
        # 初始化生成器
        self.generators.append(ArticleGenerator(self.config))
        
        # 初始化发布器
        self.publishers.append(HugoPublisher(self.config))
        
        self.logger.info(f"初始化完成: {len(self.collectors)}个采集器, "
                        f"{len(self.analyzers)}个分析器, "
                        f"{len(self.generators)}个生成器, "
                        f"{len(self.publishers)}个发布器")
    
    def run_collection(self):
        """运行信息采集"""
        self.logger.info("开始信息采集...")
        all_data = []
        
        for collector in self.collectors:
            try:
                data = collector.collect()
                all_data.extend(data)
                self.logger.info(f"{collector.__class__.__name__} 采集到 {len(data)} 条数据")
            except Exception as e:
                self.logger.error(f"采集器 {collector.__class__.__name__} 出错: {e}")
        
        return all_data
    
    def run_analysis(self, data):
        """运行数据分析"""
        self.logger.info("开始数据分析...")
        analysis_results = []
        
        for analyzer in self.analyzers:
            try:
                result = analyzer.analyze(data)
                analysis_results.append(result)
                self.logger.info(f"{analyzer.__class__.__name__} 分析完成")
            except Exception as e:
                self.logger.error(f"分析器 {analyzer.__class__.__name__} 出错: {e}")
        
        return analysis_results
    
    def run_generation(self, analysis_results):
        """运行文章生成"""
        self.logger.info("开始文章生成...")
        articles = []
        
        for generator in self.generators:
            try:
                article = generator.generate(analysis_results)
                articles.append(article)
                self.logger.info(f"{generator.__class__.__name__} 生成文章: {article.get('title', '未知标题')}")
            except Exception as e:
                self.logger.error(f"生成器 {generator.__class__.__name__} 出错: {e}")
        
        return articles
    
    def run_publishing(self, articles):
        """运行文章发布"""
        self.logger.info("开始文章发布...")
        
        for publisher in self.publishers:
            try:
                result = publisher.publish(articles)
                self.logger.info(f"{publisher.__class__.__name__} 发布完成: {result}")
            except Exception as e:
                self.logger.error(f"发布器 {publisher.__class__.__name__} 出错: {e}")
    
    def run(self, test_mode=False):
        """运行完整流程"""
        self.logger.info("=" * 50)
        self.logger.info(f"AI行业观察站开始运行 - {datetime.now()}")
        self.logger.info("=" * 50)
        
        try:
            # 1. 信息采集
            collected_data = self.run_collection()
            if not collected_data:
                self.logger.warning("没有采集到数据，跳过后续步骤")
                return False
            
            # 2. 数据分析
            analysis_results = self.run_analysis(collected_data)
            if not analysis_results:
                self.logger.warning("没有分析结果，跳过生成步骤")
                return False
            
            # 3. 文章生成
            articles = self.run_generation(analysis_results)
            if not articles:
                self.logger.warning("没有生成文章，跳过发布步骤")
                return False
            
            # 4. 文章发布
            if not test_mode:
                self.run_publishing(articles)
            
            self.logger.info(f"运行完成，生成 {len(articles)} 篇文章")
            return True
            
        except Exception as e:
            self.logger.error(f"运行过程中出错: {e}", exc_info=True)
            return False
        finally:
            self.logger.info("=" * 50)
            self.logger.info(f"AI行业观察站运行结束 - {datetime.now()}")
            self.logger.info("=" * 50)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI行业观察站')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--test', action='store_true', help='测试模式，不实际发布')
    parser.add_argument('--collect-only', action='store_true', help='仅采集数据')
    parser.add_argument('--analyze-only', action='store_true', help='仅分析数据')
    
    args = parser.parse_args()
    
    try:
        observer = AIIndustryObserver(args.config)
        
        if args.collect_only:
            data = observer.run_collection()
            print(f"采集到 {len(data)} 条数据")
        elif args.analyze_only:
            # 这里需要先有数据，简化处理
            print("分析模式需要先采集数据")
        else:
            success = observer.run(test_mode=args.test)
            if success:
                print("运行成功！")
            else:
                print("运行失败，请查看日志")
                sys.exit(1)
                
    except Exception as e:
        print(f"程序出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()