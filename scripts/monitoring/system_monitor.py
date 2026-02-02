#!/usr/bin/env python3
"""系统监控与健康检查"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from scripts.utils.logger import setup_logger


class SystemMonitor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logger("system_monitor", level=config.get("logging", {}).get("level", "INFO"))
        self.status_dir = Path("./status")
        self.status_dir.mkdir(parents=True, exist_ok=True)

    def disk_status(self) -> Dict[str, Any]:
        total, used, free = shutil.disk_usage(".")
        return {"total": total, "used": used, "free": free, "free_gb": round(free/1024/1024/1024, 2)}

    def write_status(self, status: Dict[str, Any]) -> Path:
        fp = self.status_dir / "latest.json"
        status["timestamp"] = datetime.now().isoformat()
        fp.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
        return fp

    def health_check(self) -> Dict[str, Any]:
        st = {"disk": self.disk_status(), "ok": True}
        min_free_gb = 1.0
        if st["disk"]["free_gb"] < min_free_gb:
            st["ok"] = False
            st["warning"] = f"磁盘剩余空间不足: {st['disk']['free_gb']} GB"
        self.write_status(st)
        return st