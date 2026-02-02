#!/usr/bin/env python3
"""简单文件缓存"""

import os
import json
import time
from pathlib import Path
from typing import Any, Optional


class CacheManager:
    def __init__(self, cache_dir: str, prefix: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{self.prefix}_{key}.json"

    def get(self, key: str) -> Optional[Any]:
        p = self._path(key)
        if not p.exists():
            return None
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
            exp = payload.get("expires_at")
            if exp and time.time() > exp:
                p.unlink(missing_ok=True)
                return None
            return payload.get("value")
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        p = self._path(key)
        payload = {"value": value, "expires_at": time.time() + ttl if ttl else None}
        p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")