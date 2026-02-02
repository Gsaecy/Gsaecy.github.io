#!/usr/bin/env python3
"""AI自动化博客系统 v2 - 采集->分析->生成->发布->监控"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(project_root))

from scripts.utils.config_loader import load_config
from scripts.utils.logger import setup_logger
from scripts.collectors.collector_runner import CollectorRunner
from scripts.analyzers.trend_analyzer import TrendAnalyzer
from scripts.generators.article_generator import ArticleGenerator
from scripts.publishers.hugo_publisher import HugoPublisher
from scripts.monitoring.system_monitor import SystemMonitor


async def run_pipeline(config_path: str = "config/config.yaml"):
    cfg = load_config(config_path)
    logger = setup_logger("pipeline", level=cfg.get("logging", {}).get("level", "INFO"), log_file=cfg.get("logging", {}).get("file"))

    monitor = SystemMonitor(cfg)
    health = monitor.health_check()
    if not health.get("ok"):
        logger.warning(f"健康检查未通过: {health}")

    runner = CollectorRunner(cfg)
    industry_articles = await runner.collect_all()

    analyzer = TrendAnalyzer(cfg)
    analysis_batch = await analyzer.analyze_all(industry_articles)

    out_dir = Path(cfg.get("storage", {}).get("analysis_data_dir", "./data/analysis"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_file.write_text(json.dumps(analysis_batch, ensure_ascii=False, indent=2), encoding="utf-8")

    generator = ArticleGenerator(cfg)
    publisher = HugoPublisher(cfg)

    published = []
    for industry, analysis in analysis_batch.get("results", {}).items():
        post = generator.generate_daily_industry_post(industry, analysis)
        fp = publisher.publish_markdown(post)
        published.append(str(fp))

    logger.info(f"发布完成: {len(published)} 篇")
    monitor.write_status({"ok": True, "published": published, "analysis_file": str(out_file)})


def main():
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()