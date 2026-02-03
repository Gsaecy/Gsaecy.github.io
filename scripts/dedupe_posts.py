#!/usr/bin/env python3
"""Remove duplicate Hugo posts under content/posts.

Strategy:
- Parse front matter (YAML/TOML/JSON not fully supported; we target YAML '---').
- Determine dedupe key by (slug) if present, else (title), else filename stem.
- Keep the newest by date (front matter date) else by filesystem mtime.
- Move duplicates to a trash folder under content/posts/.duplicates/ (safer than delete).

Exit code 0 always; prints summary.
"""

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple

try:
    import yaml
except Exception:
    yaml = None

POSTS_DIR = Path("content/posts")
DUP_DIR = POSTS_DIR / ".duplicates"

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n" , re.S)

@dataclass
class Post:
    path: Path
    title: str
    slug: str
    date: Optional[datetime]
    mtime: float


def parse_yaml_front_matter(text: str) -> Dict:
    if yaml is None:
        return {}
    m = FM_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    try:
        return yaml.safe_load(block) or {}
    except Exception:
        return {}


def parse_date(v) -> Optional[datetime]:
    if not v:
        return None
    if isinstance(v, datetime):
        return v
    s = str(v)
    # allow RFC3339-ish
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            pass
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None


def load_post(path: Path) -> Post:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_yaml_front_matter(text)
    title = str(fm.get("title") or "").strip()
    slug = str(fm.get("slug") or fm.get("url") or "").strip()
    if slug.startswith("/"):
        slug = slug.strip("/")
    dt = parse_date(fm.get("date"))
    mtime = path.stat().st_mtime
    if not title:
        title = path.stem
    return Post(path=path, title=title, slug=slug, date=dt, mtime=mtime)


def sort_key(p: Post) -> Tuple:
    # Newer first
    if p.date:
        return (0, p.date.timestamp())
    return (1, p.mtime)


def main():
    if not POSTS_DIR.exists():
        print("[dedupe] content/posts not found; skip")
        return

    posts = [load_post(p) for p in POSTS_DIR.glob("*.md")]
    if not posts:
        print("[dedupe] no posts; skip")
        return

    groups: Dict[str, list[Post]] = {}
    for p in posts:
        key = (p.slug or p.title or p.path.stem).lower()
        groups.setdefault(key, []).append(p)

    DUP_DIR.mkdir(parents=True, exist_ok=True)

    moved = 0
    for key, items in groups.items():
        if len(items) <= 1:
            continue
        items_sorted = sorted(items, key=sort_key, reverse=True)
        keep = items_sorted[0]
        dups = items_sorted[1:]
        for d in dups:
            target = DUP_DIR / d.path.name
            # avoid overwrite
            if target.exists():
                target = DUP_DIR / f"{d.path.stem}-{int(d.mtime)}{d.path.suffix}"
            shutil.move(str(d.path), str(target))
            moved += 1
        print(f"[dedupe] key={key} keep={keep.path.name} moved={len(dups)}")

    print(f"[dedupe] done. moved_duplicates={moved} dir={DUP_DIR}")


if __name__ == "__main__":
    main()
