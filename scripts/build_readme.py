#!/usr/bin/env python3
"""
build_readme.py
Compiles modular markdown partials from partials/ into the root README.md.
Dynamically injects live activity feed data between marker tags.
Zero external dependencies - Uses pure Python 3 standard library.
"""

import os
import re
import sys
from fetch_activity import get_activity_markdown

START_MARKER = "<!--LATEST-ACTIVITY:START-->"
END_MARKER = "<!--LATEST-ACTIVITY:END-->"

def assemble_readme(partials_dir: str, output_path: str, username: str, token: str, rss_url: str):
    if not os.path.exists(partials_dir):
        print(f"[Error] Partials directory not found: {partials_dir}", file=sys.stderr)
        sys.exit(1)

    # 1. Collect all .md partials in sorted order
    partial_files = sorted([
        f for f in os.listdir(partials_dir) if f.endswith(".md")
    ])

    if not partial_files:
        print(f"[Error] No markdown files found in {partials_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Assembling README from {len(partial_files)} partials:")
    content_blocks = [
        "<!-- ================================================================= -->\n"
        "<!-- ⚠️ AUTO-GENERATED FILE — DO NOT EDIT DIRECTLY                     -->\n"
        "<!-- Edit files in partials/ and run: python scripts/build_readme.py   -->\n"
        "<!-- ================================================================= -->\n"
    ]

    for p in partial_files:
        print(f"    - Reading {p}")
        p_path = os.path.join(partials_dir, p)
        with open(p_path, "r", encoding="utf-8") as f:
            content_blocks.append(f.read().strip())

    assembled_text = "\n\n".join(content_blocks) + "\n"

    # 2. Inject Dynamic Activity between markers
    if START_MARKER in assembled_text and END_MARKER in assembled_text:
        print("[*] Injecting live activity feed between markers...")
        activity_md = get_activity_markdown(username, token, rss_url)
        pattern = re.compile(
            f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
            re.DOTALL
        )
        replacement = f"{START_MARKER}\n{activity_md}\n{END_MARKER}"
        assembled_text = pattern.sub(replacement, assembled_text)

    # 3. Write final README.md
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(assembled_text)

    print(f"[OK] Successfully compiled {output_path} ({len(assembled_text)} bytes)")

def main():
    username = os.environ.get("GITHUB_USERNAME", "Kimobest")
    token = os.environ.get("GITHUB_TOKEN", "")
    rss_url = os.environ.get("RSS_FEED_URL", "")
    partials_dir = os.environ.get("PARTIALS_DIR", "partials")
    output_path = os.environ.get("README_OUTPUT_PATH", "README.md")

    assemble_readme(partials_dir, output_path, username, token, rss_url)

if __name__ == "__main__":
    main()
