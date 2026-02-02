#!/usr/bin/env python3
"""将文章写入Hugo content/posts"""

import os
from pathlib import Path
from typing import Any, Dict

from scripts.utils.logger import setup_logger


class HugoPublisher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logger("hugo_publisher", level=config.get("logging", {}).get("level", "INFO"))
        self.content_dir = Path(config.get("publishing", {}).get("hugo", {}).get("content_dir", "./content/posts"))
        self.content_dir.mkdir(parents=True, exist_ok=True)

    def publish_markdown(self, post: Dict[str, Any]) -> Path:
        slug = post["slug"]
        fp = self.content_dir / f"{slug}.md"
        fp.write_text(post["content"], encoding="utf-8")
        self.logger.info(f"写入文章: {fp}")
        return fp