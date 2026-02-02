#!/usr/bin/env python3
"""趋势分析器"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.analyzers.deepseek_client import AsyncDeepSeekClient
from scripts.utils.logger import setup_logger


class TrendAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = AsyncDeepSeekClient(config)
        self.logger = setup_logger(
            "trend_analyzer",
            level=config.get("logging", {}).get("level", "INFO"),
        )

    async def analyze_industry(self, industry: Dict[str, Any], articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """对单一行业做趋势分析"""
        text_chunks: List[str] = []
        for a in articles[:20]:
            text_chunks.append(
                f"标题：{a.get('title','')}\n"
                f"摘要：{a.get('summary','') or ''}\n"
                f"内容：{(a.get('content','') or '')[:1200]}\n"
                f"来源：{a.get('source','')}\n"
                f"链接：{a.get('url','')}\n"
            )
        corpus = "\n\n".join(text_chunks)

        instructions = (
            f"行业：{industry.get('name')}。"
            "请给出结构化趋势洞察，要求包含可执行建议与风险预警，并尽量引用原文标题来佐证。"
        )
        result = await self.client.analyze_text(corpus, analysis_type="trend", instructions=instructions)
        result["industry"] = industry.get("name")
        result["article_count"] = len(articles)
        result["generated_at"] = datetime.now().isoformat()
        return result

    async def analyze_all(self, industry_articles: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        outputs: Dict[str, Any] = {}
        for ind in self.config.get("analysis", {}).get("industries", []):
            name = ind.get("name")
            arts = industry_articles.get(name, [])
            if not arts:
                continue
            try:
                outputs[name] = await self.analyze_industry(ind, arts)
            except Exception as e:
                self.logger.error(f"行业分析失败 {name}: {e}")
                outputs[name] = {
                    "industry": name,
                    "error": str(e),
                    "generated_at": datetime.now().isoformat(),
                }
        return {
            "type": "trend_analysis_batch",
            "results": outputs,
            "generated_at": datetime.now().isoformat(),
        }
