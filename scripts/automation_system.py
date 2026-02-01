#!/usr/bin/env python3
"""
AI智汇观察 - 全自动博客系统
集成信息采集、AI分析、内容生成、自动发布全流程
"""

import os
import sys
import yaml
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import schedule
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.collectors.news_collector import NewsCollector
from scripts.collectors.finance_collector import FinanceCollector
from scripts.collectors.social_collector import SocialCollector
from scripts.analyzers.trend_analyzer import TrendAnalyzer
from scripts.analyzers.industry_analyzer import IndustryAnalyzer
from scripts.generators.report_generator import ReportGenerator
from scripts.publishers.hugo_publisher import HugoPublisher
from scripts.monitoring.system_monitor import SystemMonitor

class AIBlogAutomationSystem:
    """AI博客自动化系统主控制器"""
    
    def __init__(self, config_path="config/config.yaml"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化时间
        self.start_time = datetime.now()
        self.last_run = None
        
        # 初始化组件
        self.collectors = []
        self.analyzers = []
        self.generators = []
        self.publishers = []
        self.monitor = None
        
        self.init_components()
        self.logger.info(f"AI博客自动化系统初始化完成 - 版本 {self.config.get('version', '1.0')}")
    
    def load_config(self, config_path):
        """加载配置文件"""
        config_file = project_root / config_path
        if not config_file.exists():
            self.create_default_config(config_file)
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def create_default_config(self, config_file):
        """创建默认配置文件"""
        default_config = {
            "version": "1.0",
            "system": {
                "name": "AI智汇观察",
                "description": "AI驱动的自动化行业分析博客",
                "author": "AI智汇观察系统"
            },
            "schedule": {
                "daily_analysis": "10:00",
                "weekly_summary": "sunday 20:00",
                "monthly_report": "last_day 22:00"
            },
            "analysis": {
                "industries": ["科技", "金融", "教育", "医疗", "电商", "制造"],
                "depth": "medium",
                "include_forecast": True,
                "include_risk": True
            },
            "publishing": {
                "blog_path": "./content/posts",
                "max_posts_per_day": 5,
                "auto_deploy": True,
                "deploy_time": "10:30"
            },
            "monitoring": {
                "enabled": True,
                "check_interval": 3600,
                "alert_email": None,
                "performance_log": "./logs/performance.json"
            }
        }
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True, sort_keys=False)
        
        self.logger.info(f"创建默认配置文件: {config_file}")
    
    def setup_logging(self):
        """设置日志系统"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        # 创建日志目录
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 配置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 文件处理器
        file_handler = logging.FileHandler(log_dir / "system.log", encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        
        # 配置根日志
        logging.basicConfig(
            level=log_level,
            handlers=[file_handler, console_handler]
        )
    
    def init_components(self):
        """初始化所有组件"""
        self.logger.info("初始化系统组件...")
        
        # 初始化采集器
        collector_config = self.config.get('collectors', {})
        if collector_config.get('news', {}).get('enabled', True):
            self.collectors.append(NewsCollector(self.config))
        
        if collector_config.get('finance', {}).get('enabled', True):
            self.collectors.append(FinanceCollector(self.config))
        
        if collector_config.get('social', {}).get('enabled', True):
            self.collectors.append(SocialCollector(self.config))
        
        # 初始化分析器
        analyzer_config = self.config.get('analyzers', {})
        if analyzer_config.get('trend', {}).get('enabled', True):
            self.analyzers.append(TrendAnalyzer(self.config))
        
        if analyzer_config.get('industry', {}).get('enabled', True):
            self.analyzers.append(IndustryAnalyzer(self.config))
        
        # 初始化生成器
        generator_config = self.config.get('generators', {})
        if generator_config.get('reports', {}).get('enabled', True):
            self.generators.append(ReportGenerator(self.config))
        
        # 初始化发布器
        publisher_config = self.config.get('publishers', {})
        if publisher_config.get('hugo', {}).get('enabled', True):
            self.publishers.append(HugoPublisher(self.config))
        
        # 初始化监控器
        monitor_config = self.config.get('monitoring', {})
        if monitor_config.get('enabled', True):
            self.monitor = SystemMonitor(self.config)
        
        self.logger.info(f"组件初始化完成: {len(self.collectors)}采集器, "
                        f"{len(self.analyzers)}分析器, {len(self.generators)}生成器, "
                        f"{len(self.publishers)}发布器")
    
    def run_daily_analysis(self):
        """运行每日分析任务"""
        self.logger.info("=" * 60)
        self.logger.info(f"开始每日分析任务 - {datetime.now()}")
        self.logger.info("=" * 60)
        
        try:
            # 1. 数据采集
            collected_data = self.run_data_collection()
            if not collected_data:
                self.logger.warning("数据采集为空，跳过分析")
                return False
            
            # 2. 数据分析
            analysis_results = self.run_data_analysis(collected_data)
            if not analysis_results:
                self.logger.warning("分析结果为空，跳过生成")
                return False
            
            # 3. 报告生成
            generated_reports = self.run_report_generation(analysis_results)
            if not generated_reports:
                self.logger.warning("报告生成为空，跳过发布")
                return False
            
            # 4. 内容发布
            publish_results = self.run_content_publishing(generated_reports)
            
            # 5. 记录运行状态
            self.record_run_status(success=True, reports=len(generated_reports))
            
            self.logger.info(f"每日分析任务完成，生成 {len(generated_reports)} 篇报告")
            return True
            
        except Exception as e:
            self.logger.error(f"每日分析任务失败: {e}", exc_info=True)
            self.record_run_status(success=False, error=str(e))
            return False
    
    def run_data_collection(self):
        """运行数据采集"""
        self.logger.info("开始数据采集...")
        all_data = []
        
        for collector in self.collectors:
            try:
                collector_name = collector.__class__.__name__
                self.logger.info(f"运行采集器: {collector_name}")
                
                data = collector.collect()
                if data:
                    all_data.extend(data)
                    self.logger.info(f"{collector_name} 采集到 {len(data)} 条数据")
                    
                    # 保存原始数据
                    self.save_raw_data(collector_name, data)
                else:
                    self.logger.warning(f"{collector_name} 未采集到数据")
                    
            except Exception as e:
                self.logger.error(f"采集器 {collector.__class__.__name__} 运行失败: {e}")
        
        self.logger.info(f"数据采集完成，总计 {len(all_data)} 条数据")
        return all_data
    
    def run_data_analysis(self, data):
        """运行数据分析"""
        self.logger.info("开始数据分析...")
        analysis_results = []
        
        for analyzer in self.analyzers:
            try:
                analyzer_name = analyzer.__class__.__name__
                self.logger.info(f"运行分析器: {analyzer_name}")
                
                result = analyzer.analyze(data)
                if result:
                    analysis_results.append(result)
                    self.logger.info(f"{analyzer_name} 分析完成")
                    
                    # 保存分析结果
                    self.save_analysis_result(analyzer_name, result)
                else:
                    self.logger.warning(f"{analyzer_name} 未生成分析结果")
                    
            except Exception as e:
                self.logger.error(f"分析器 {analyzer.__class__.__name__} 运行失败: {e}")
        
        self.logger.info(f"数据分析完成，生成 {len(analysis_results)} 个分析结果")
        return analysis_results
    
    def run_report_generation(self, analysis_results):
        """运行报告生成"""
        self.logger.info("开始报告生成...")
        generated_reports = []
        
        for generator in self.generators:
            try:
                generator_name = generator.__class__.__name__
                self.logger.info(f"运行生成器: {generator_name}")
                
                reports = generator.generate(analysis_results)
                if reports:
                    generated_reports.extend(reports)
                    self.logger.info(f"{generator_name} 生成 {len(reports)} 篇报告")
                else:
                    self.logger.warning(f"{generator_name} 未生成报告")
                    
            except Exception as e:
                self.logger.error(f"生成器 {generator.__class__.__name__} 运行失败: {e}")
        
        self.logger.info(f"报告生成完成，总计 {len(generated_reports)} 篇报告")
        return generated_reports
    
    def run_content_publishing(self, reports):
        """运行内容发布"""
        self.logger.info("开始内容发布...")
        publish_results = []
        
        for publisher in self.publishers:
            try:
                publisher_name = publisher.__class__.__name__
                self.logger.info(f"运行发布器: {publisher_name}")
                
                result = publisher.publish(reports)
                if result:
                    publish_results.append(result)
                    self.logger.info(f"{publisher_name} 发布完成: {result}")
                else:
                    self.logger.warning(f"{publisher_name} 发布失败")
                    
            except Exception as e:
                self.logger.error(f"发布器 {publisher.__class__.__name__} 运行失败: {e}")
        
        self.logger.info(f"内容发布完成，{len(publish_results)} 个发布器执行成功")
        return publish_results
    
    def save_raw_data(self, source, data):
        """保存原始数据"""
        data_dir = project_root / "data" / "raw" / datetime.now().strftime("%Y-%m-%d")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        filename = data_dir / f"{source}_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_analysis_result(self, analyzer, result):
        """保存分析结果"""
        result_dir = project_root / "data" / "analysis" / datetime.now().strftime("%Y-%m-%d")
        result_dir.mkdir(parents=True, exist_ok=True)
        
        filename = result_dir / f"{analyzer}_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def record_run_status(self, success=True, reports=0, error=None):
        """记录运行状态"""
        status_dir = project_root / "status"
        status_dir.mkdir(exist_ok=True)
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "reports_generated": reports,
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "components": {
                "collectors": len(self.collectors),
                "analyzers": len(self.analyzers),
                "generators": len(self.generators),
                "publishers": len(self.publishers)
            }
        }
        
        if error:
            status["error"] = error
        
        # 保存状态文件
        status_file = status_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        
        # 更新最新状态
        latest_file = status_dir / "latest.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        
        self.last_run = status
    
    def setup_schedule(self):
        """设置定时任务"""
        schedule_config = self.config.get('schedule', {})
        
        # 每日分析任务
        daily_time = schedule_config.get('daily_analysis', '10:00')
        schedule.every().day.at(daily_time).do(self.run_daily_analysis)
        self.logger.info(f"设置每日分析任务: {daily_time}")
        
        # 每周总结任务
        weekly_schedule = schedule_config.get('weekly_summary', 'sunday 20:00')
        if weekly_schedule:
            # 解析周计划
            if weekly_schedule.startswith('sunday'):
                schedule.every().sunday.at(weekly_schedule.split()[1]).do(self.run_weekly_summary)
                self.logger.info(f"设置每周总结任务: {weekly_schedule}")
        
        # 监控任务
        if self.monitor:
            check_interval = self.config.get('monitoring', {}).get('check_interval', 3600)
            schedule.every(check_interval).seconds.do(self.monitor.check_system_status)
            self.logger.info(f"设置系统监控，间隔: {check_interval}秒")
    
    def run_weekly_summary(self):
        """运行每周总结"""
        self.logger.info("开始每周总结任务...")
        # 实现每周总结逻辑
        pass
    
    def run(self, daemon=False):
        """运行系统"""
        self.logger.info("=" * 60)
        self.logger.info(f"AI博客自动化系统启动 - {datetime.now()}")
        self.logger.info("=" * 60)
        
        # 设置定时任务
        self.setup_schedule()
        
        if daemon:
            # 守护进程模式
            self.logger.info("进入守护进程模式，等待定时任务...")
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # 每分钟检查一次
            except KeyboardInterrupt:
                self.logger.info("系统收到停止信号，正在关闭...")
        else:
            # 立即运行一次
            self.logger.info("立即执行分析任务...")
            success = self.run_daily_analysis()
            
            if success:
                self.logger.info("分析任务执行成功")
            else:
                self.logger.error("分析任务执行失败")
            
            self.logger.info("系统运行完成")
    
    def get_status(self):
        """获取系统状态"""
        if not self.last_run:
            return {"status": "not_run", "message": "系统尚未运行"}
        
        return {
            "status": "running" if self.last_run.get("success") else "error",
            "last_run": self.last_run.get("timestamp"),
            "reports_generated": self.last_run.get("reports_generated", 0),
            "duration": self.last_run.get("duration", 0)
        }

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI博客自动化系统')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--daemon', action='store_true', help='守护进程模式')
    parser.add_argument('--test', action='store_true', help='测试模式')
    parser.add_argument('--status', action='store_true', help='查看系统状态')
    
    args = parser.parse_args()
    
    try:
        system = AIBlogAutomationSystem(args.config)
        
        if args.status:
            status = system.get_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))
        elif args.test:
            print("测试模式运行...")
            # 简化测试逻辑
            success = system.run_daily_analysis()
            print(f"测试结果: {'成功' if success else '失败'}")
        else:
            system.run(daemon=args.daemon)
            
    except Exception as e:
        print(f"系统启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()