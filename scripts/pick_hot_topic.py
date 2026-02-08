#!/usr/bin/env python3
"""Pick a fallback (industry, topic) from a hot-topic pool.

Used when RSS collection returns 0 items.

Selection strategy:
- filter by safe=true
- filter out deny_keywords
- take top_k by weight, then weighted-random pick

Outputs:
- default: two lines: INDUSTRY=... and TOPIC=...
- --shell: prints: <industry>\t<topic>

Env:
- optional SEED for reproducibility
"""

from __future__ import annotations

import argparse
import os
import random
import re
from pathlib import Path

import yaml


def contains_any(s: str, words: list[str]) -> bool:
    s = s or ""
    return any(w and w in s for w in words)


def weighted_choice(items: list[dict]) -> dict:
    total = sum(int(x.get("weight", 0)) for x in items)
    if total <= 0:
        return random.choice(items)
    r = random.uniform(0, total)
    acc = 0.0
    for x in items:
        acc += int(x.get("weight", 0))
        if r <= acc:
            return x
    return items[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="scripts/hot_topic_pool.yaml")
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument(
        "--avoid-recent",
        type=int,
        default=20,
        help="Avoid topics that already appeared in the most recent N posts' titles.",
    )
    ap.add_argument("--shell", action="store_true")
    args = ap.parse_args()

    seed = os.getenv("SEED")
    if seed:
        random.seed(seed)

    doc = yaml.safe_load(Path(args.pool).read_text(encoding="utf-8")) or {}
    pool = list(doc.get("pool", []) or [])
    deny = list(doc.get("deny_keywords", []) or [])

    # Collect recent post titles to avoid repeating topics
    recent_titles: list[str] = []
    try:
        posts_dir = Path("content/posts")
        if posts_dir.exists() and args.avoid_recent > 0:
            paths = sorted(posts_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[: args.avoid_recent]
            for p in paths:
                txt = p.read_text(encoding="utf-8")
                m = re.match(r"^---\n(.*?)\n---\n", txt, flags=re.S)
                if not m:
                    continue
                fm = m.group(1)
                for line in fm.splitlines():
                    if line.startswith("title:"):
                        recent_titles.append(line.split(":", 1)[1].strip().strip('"'))
                        break
    except Exception:
        pass

    candidates = []
    for x in pool:
        if not x.get("safe", True):
            continue
        topic = (x.get("topic") or "").strip()
        industry = (x.get("industry") or "").strip()
        if not topic or not industry:
            continue
        if contains_any(topic, deny):
            continue
        if recent_titles and any(topic in (t or "") for t in recent_titles):
            continue
        candidates.append(x)

    if not candidates:
        raise SystemExit("no safe candidates")

    candidates.sort(key=lambda z: int(z.get("weight", 0)), reverse=True)
    top = candidates[: max(1, args.top_k)]
    pick = weighted_choice(top)

    industry = pick["industry"].strip()
    topic = pick["topic"].strip()

    if args.shell:
        print(f"{industry}\t{topic}")
    else:
        print(f"INDUSTRY={industry}")
        print(f"TOPIC={topic}")


if __name__ == "__main__":
    main()
