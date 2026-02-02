#!/usr/bin/env python3
"""将分析结果生成Hugo Markdown文章"""

import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from scripts.utils.logger import setup_logger


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-\u4e00-\u9fff]", "", text)
    return text[:80]


class ArticleGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logger("article_generator", level=config.get("logging", {}).get("level", "INFO"))

    def _front_matter(self, title: str, tags: List[str], categories: List[str], date: Optional[str] = None) -> str:
        date = date or datetime.now().astimezone().isoformat()
        tags_yaml = "[" + ", ".join([f"\"{t}\"" for t in tags]) + "]"
        cats_yaml = "[" + ", ".join([f"\"{c}\"" for c in categories]) + "]"
        return (
            "---\n"
            f"title: \"{title}\"\n"
            f"date: {date}\n"
            "draft: false\n"
            f"tags: {tags_yaml}\n"
            f"categories: {cats_yaml}\n"
            "---\n\n"
        )

    def generate_daily_industry_post(self, industry: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        date_str = datetime.now().strftime("%Y-%m-%d")
        title = f"【行业日报】{date_str} - {industry}行业动态分析"
        tags = ["AI分析", "行业趋势", industry]
        categories = ["行业分析"]

        body = []
        body.append(f"# {title}\n")

        if isinstance(analysis, dict) and analysis.get("error"):
            body.append("## 生成失败\n")
            body.append(f"错误信息：{analysis.get('error')}\n")
        else:
            summary = analysis.get("summary") or analysis.get("analysis", "")
            body.append("## 摘要\n")
            body.append(f"{summary}\n")

            body.append("## 趋势解读\n")
            trends = analysis.get("identified_trends") or []
            if isinstance(trends, list) and trends:
                for t in trends[:5]:
                    if isinstance(t, dict):
                        body.append(f"- **{t.get('name','趋势')}**：{t.get('description','')}（强度：{t.get('strength','')}）")
                    else:
                        body.append(f"- {t}")
                body.append("")
            else:
                body.append(analysis.get("insights", "（无）"))

            body.append("## 机会与风险\n")
            opp = analysis.get("opportunities") or []
            risk = analysis.get("risks") or []
            if opp:
                body.append("### 机会\n")
                for x in opp[:5]:
                    body.append(f"- {x}")
                body.append("")
            if risk:
                body.append("### 风险\n")
                for x in risk[:5]:
                    body.append(f"- {x}")
                body.append("")

            body.append("## 结论与建议\n")
            rec = analysis.get("recommendations") or []
            if isinstance(rec, list) and rec:
                for r in rec[:6]:
                    body.append(f"- {r}")
            else:
                body.append(str(rec) if rec else "（无）")

        content = self._front_matter(title, tags=tags, categories=categories) + "\n".join(body) + "\n"
        slug = slugify(f"daily-{industry}-{date_str}")
        return {"title": title, "slug": slug, "content": content}