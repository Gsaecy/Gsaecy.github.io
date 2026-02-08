#!/usr/bin/env python3
"""Pick a public cover image from a tagged industry pool (and download it).

Used by workflow as primary cover source to reduce paid image generation.
If no match is found or download fails, workflow falls back to Jimeng.

Usage:
  python3 scripts/pick_public_cover.py --pool scripts/public_image_pool.yaml \
    --industry technology --title "..." --slug xxx --out static/images/posts/<slug>/cover.jpg

Exit codes:
  0: success (cover downloaded and attribution printed)
  2: no suitable candidate
  3: download failed
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import requests
import yaml


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def score_item(item: dict, title: str) -> float:
    title = title or ""
    tags = item.get("tags") or []
    score = float(item.get("weight", 0))
    for t in tags:
        if t and t in title:
            score += 50
    # small bonus if AI appears and item has AI tag
    if ("AI" in title or "人工智能" in title) and any(x in ["AI", "人工智能"] for x in tags):
        score += 20
    return score


def download(url: str, out_path: Path) -> bool:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        r.raise_for_status()
        out_path.write_bytes(r.content)
        return True
    except Exception:
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="scripts/public_image_pool.yaml")
    ap.add_argument("--industry", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    doc = yaml.safe_load(Path(args.pool).read_text(encoding="utf-8")) or {}
    pool = list(doc.get("pool") or [])

    title = norm(args.title)

    candidates = [x for x in pool if x.get("industry") == args.industry and (x.get("image_url") or "").strip()]
    if not candidates:
        raise SystemExit(2)

    candidates.sort(key=lambda x: score_item(x, title), reverse=True)
    pick = candidates[0]

    img_url = (pick.get("image_url") or "").strip()
    if not img_url:
        raise SystemExit(2)

    ok = download(img_url, Path(args.out))
    if not ok:
        raise SystemExit(3)

    # Write sidecar meta for attribution
    meta = {
        "mode": "public_pool",
        "picked": pick,
        "slug": args.slug,
    }
    meta_path = Path(args.out).with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "cover_rel": f"/images/posts/{args.slug}/{Path(args.out).name}",
                "source": pick.get("url", ""),
                "license": pick.get("license", ""),
                "license_url": pick.get("license_url", ""),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
