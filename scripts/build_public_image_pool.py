#!/usr/bin/env python3
"""Build/refresh the public image pool via Openverse API.

This script updates scripts/public_image_pool.yaml by filling missing url/image_url/license fields.
It keeps existing entries stable (id/tags/weight) and only fills blanks.

Why: make cover selection controllable + low-cost; Jimeng is fallback.

Usage:
  python3 scripts/build_public_image_pool.py --pool scripts/public_image_pool.yaml
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import yaml

from openverse_fetch import fetch


QUERY_HINTS = {
    "technology": ["AI circuit board", "data center servers", "machine learning abstract"],
    "finance": ["fintech dashboard", "risk management chart", "banking technology"],
    "healthcare": ["medical technology AI", "hospital digital", "diagnostic imaging"],
    "education": ["online learning", "education technology", "classroom technology"],
    "automotive": ["electric vehicle charging", "EV battery", "autonomous driving"],
    "retail": ["retail store", "ecommerce warehouse", "inventory management"],
    "manufacturing": ["smart factory", "industrial automation", "robotic arm factory"],
    "foreign_trade": ["shipping containers port", "logistics supply chain", "cargo ship"],
    "scientific_instruments": ["laboratory microscope", "scientific instrument lab", "research laboratory equipment"],
    "reagents": ["biotechnology laboratory", "PCR lab", "reagent bottles"],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="scripts/public_image_pool.yaml")
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args()

    path = Path(args.pool)
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    pool = list(doc.get("pool") or [])

    changed = 0

    for item in pool:
        if (item.get("image_url") or "").strip() and (item.get("license") or "").strip():
            continue
        industry = item.get("industry")
        hints = QUERY_HINTS.get(industry) or []
        if not hints:
            continue

        picked = None
        for q in hints:
            res = fetch(q, limit=args.limit)
            # Prefer permissive licenses (Openverse often reports as BY/BY-SA/CC0)
            for it in res:
                lic = (it.get("license") or "").upper()
                if lic in {"CC0", "BY", "BY-SA", "CC-BY", "CC-BY-SA"}:
                    picked = it
                    break
            if picked:
                break

        if not picked:
            # fall back to first available
            res = fetch(hints[0], limit=1)
            picked = res[0] if res else None

        if not picked:
            continue

        if not (item.get("url") or "").strip():
            item["url"] = picked.get("url") or ""
        if not (item.get("image_url") or "").strip():
            item["image_url"] = picked.get("image_url") or ""
        if not (item.get("license") or "").strip():
            item["license"] = picked.get("license") or ""
        if not (item.get("license_url") or "").strip():
            item["license_url"] = picked.get("license_url") or ""
        item["provider"] = picked.get("provider") or "openverse"

        changed += 1
        time.sleep(0.2)

    doc["pool"] = pool
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"updated {changed} items -> {path}")


if __name__ == "__main__":
    main()
