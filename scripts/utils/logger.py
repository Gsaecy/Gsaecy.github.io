#!/usr/bin/env python3
"""统一日志配置"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(name: str,
                 level: str = "INFO",
                 log_file: Optional[str] = None,
                 fmt: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = fmt or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File
    if log_file:
        Path(os.path.dirname(log_file)).mkdir(parents=True, exist_ok=True)
        fh = RotatingFileHandler(log_file, maxBytes=50 * 1024 * 1024, backupCount=5, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    logger.propagate = False
    return logger