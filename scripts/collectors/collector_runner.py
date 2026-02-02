#!/usr/bin/env python3
"""根据配置运行采集器并按行业聚合"""

import os
import sys
import asyncio
from typing import Any, Dict, List

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.utils.logger import setup_logger
from scripts.collectors.tech_news_collector import Kr36Collector, HuxiuCollector, TMTPostCollector
from scripts.collectors.finance_collector import WallStreetCNCollector


class CollectorRunner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logger("collector_runner", level=config.get("logging", {}).get("level", "INFO"))

    def _make_collector(self, src: Dict[str, Any]):
        url = src.get("url", "")
        if "36kr.com" in url:
            return Kr36Collector(self.config, src)
        if "huxiu.com" in url:
            return HuxiuCollector(self.config, src)
        if "tmtpost.com" in url:
            return TMTPostCollector(self.config, src)
        if "wallstreetcn.com" in url:
            return WallStreetCNCollector(self.config, src)
        # fallback
        return Kr36Collector(self.config, src)

    async def collect_all(self) -> Dict[str, List[Dict[str, Any]]]:
        industry_articles: Dict[str, List[Dict[str, Any]]] = {}

        sources = self.config.get("collectors", {}).get("sources", {})
        all_sources = []
        for group in sources.values():
            if isinstance(group, list):
                for src in group:
                    if src.get("enabled", True):
                        all_sources.append(src)

        collectors = [self._make_collector(s) for s in all_sources]
        results = await asyncio.gather(*[c.collect() for c in collectors], return_exceptions=True)

        # 归类：简单按source_type映射行业（可扩展为关键词匹配）
        for src, res in zip(all_sources, results):
            if isinstance(res, Exception):
                self.logger.error(f"采集失败 {src.get('name')}: {res}")
                continue
            for a in res:
                # 根据关键词粗略归到行业
                assigned = None
                for ind in self.config.get("analysis", {}).get("industries", []):
                    for kw in ind.get("keywords", []):
                        if kw in (a.get("title", "") + a.get("content", "")):
                            assigned = ind.get("name")
                            break
                    if assigned:
                        break
                assigned = assigned or "科技"
                industry_articles.setdefault(assigned, []).append(a)

        return industry_articles