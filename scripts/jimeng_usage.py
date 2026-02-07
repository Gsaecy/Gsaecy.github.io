#!/usr/bin/env python3
"""Lightweight usage counter for Jimeng image generation.

We don't have official remaining quota in API, so we track usage ourselves.

File format (JSON):
{
  "month": "YYYY-MM",
  "by_day": {"YYYY-MM-DD": {"success": 0, "fail": 0}},
  "total": {"success": 0, "fail": 0}
}

Usage:
  python3 scripts/jimeng_usage.py --file data/usage/jimeng_usage.json --mark success
  python3 scripts/jimeng_usage.py --file data/usage/jimeng_usage.json --mark fail
  python3 scripts/jimeng_usage.py --file data/usage/jimeng_usage.json --print
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


def now_cn_date() -> str:
    cn = timezone(timedelta(hours=8))
    return datetime.now(cn).strftime("%Y-%m-%d")


def month_of(d: str) -> str:
    return d[:7]


def load(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def ensure_month(doc: dict, month: str) -> dict:
    if doc.get("month") != month:
        # reset for new month
        return {"month": month, "by_day": {}, "total": {"success": 0, "fail": 0}}
    doc.setdefault("by_day", {})
    doc.setdefault("total", {"success": 0, "fail": 0})
    doc["total"].setdefault("success", 0)
    doc["total"].setdefault("fail", 0)
    return doc


def mark(doc: dict, day: str, kind: str) -> dict:
    doc.setdefault("by_day", {})
    doc.setdefault("total", {"success": 0, "fail": 0})
    doc["by_day"].setdefault(day, {"success": 0, "fail": 0})
    if kind not in ("success", "fail"):
        raise SystemExit("kind must be success|fail")
    doc["by_day"][day][kind] += 1
    doc["total"][kind] += 1
    return doc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--mark", choices=["success", "fail"], default=None)
    ap.add_argument("--print", dest="do_print", action="store_true")
    args = ap.parse_args()

    path = Path(args.file)
    path.parent.mkdir(parents=True, exist_ok=True)

    day = now_cn_date()
    doc = ensure_month(load(path), month_of(day))

    if args.mark:
        doc = mark(doc, day, args.mark)
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.do_print:
        print(json.dumps(doc, ensure_ascii=False))


if __name__ == "__main__":
    main()
