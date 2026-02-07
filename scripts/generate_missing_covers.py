#!/usr/bin/env python3
"""Generate missing Jimeng cover images for changed posts.

Triggered in CI. It:
- finds changed content/posts/*.md between BEFORE_SHA..AFTER_SHA
- reads YAML front matter, expecting fields: title, slug, image
- if image == /images/posts/<slug>/cover.jpg and cover file doesn't exist,
  call scripts/jimeng_generate_cover.py to create it.

Env:
- BEFORE_SHA, AFTER_SHA
- VOLC_ACCESS_KEY_ID, VOLC_SECRET_ACCESS_KEY
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


def sh(cmd: str) -> str:
    return subprocess.check_output(["bash", "-lc", cmd], text=True)


def parse_front_matter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not m:
        return None
    fm = m.group(1)
    out = {"title": None, "slug": None, "image": None}
    for line in fm.splitlines():
        if line.startswith("title:"):
            out["title"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("slug:"):
            out["slug"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("image:"):
            out["image"] = line.split(":", 1)[1].strip().strip('"')
    return out


def main() -> None:
    before = os.getenv("BEFORE_SHA")
    after = os.getenv("AFTER_SHA")
    if not before or not after:
        print("BEFORE_SHA/AFTER_SHA not set; skip", file=sys.stderr)
        return

    changed = sh(f"git diff --name-only {before} {after} | grep '^content/posts/.*\\.md$' || true")
    paths = [p.strip() for p in changed.splitlines() if p.strip()]
    if not paths:
        print("No changed posts")
        return

    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        meta = parse_front_matter(path.read_text(encoding="utf-8"))
        if not meta:
            continue
        title, slug, image = meta.get("title"), meta.get("slug"), meta.get("image")
        if not title or not slug:
            continue
        target = f"/images/posts/{slug}/cover.jpg"
        if image != target:
            continue

        out_file = Path("static/images/posts") / slug / "cover.jpg"
        if out_file.exists():
            print(f"cover exists: {out_file}")
            continue

        print(f"Generating cover for {slug} -> {out_file}")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(
            [
                "python3",
                "scripts/jimeng_generate_cover.py",
                "--slug",
                slug,
                "--title",
                title,
                "--industry",
                "综合",
                "--out",
                str(out_file),
            ]
        )


if __name__ == "__main__":
    main()
