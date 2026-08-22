#!/usr/bin/env python3
"""
build_readme.py
Compiles modular markdown partials from partials/ into the root README.md.
Dynamically injects the narrative Contribution Activity Timeline.
Zero external dependencies - Uses pure Python 3 standard library.
"""

import os
import re
import sys
from generate_timeline import fetch_timeline_data, generate_timeline_markdown

TIMELINE_START = "<!--ACTIVITY-TIMELINE:START-->"
TIMELINE_END = "<!--ACTIVITY-TIMELINE:END-->"

def assemble_readme(partials_dir: str, output_path: str, username: str, token: str):
    if not os.path.exists(partials_dir):
        print(f"[Error] Partials directory not found: {partials_dir}", file=sys.stderr)
        sys.exit(1)

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

    # Inject Narrative Contribution Activity Timeline
    if TIMELINE_START in assembled_text and TIMELINE_END in assembled_text:
        print("[*] Computing and injecting Contribution Activity Timeline...")
        user_data = fetch_timeline_data(token, username)
        timeline_md = generate_timeline_markdown(user_data, username)
        
        pattern = re.compile(
            f"{re.escape(TIMELINE_START)}.*?{re.escape(TIMELINE_END)}",
            re.DOTALL
        )
        replacement = f"{TIMELINE_START}\n{timeline_md}\n{TIMELINE_END}"
        assembled_text = pattern.sub(replacement, assembled_text)

    # Write final README.md
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(assembled_text)

    print(f"[OK] Successfully compiled {output_path} ({len(assembled_text)} bytes)")

def main():
    username = os.environ.get("GITHUB_USERNAME", "Kimobest")
    token = os.environ.get("GITHUB_TOKEN", "")
    partials_dir = os.environ.get("PARTIALS_DIR", "partials")
    output_path = os.environ.get("README_OUTPUT_PATH", "README.md")

    assemble_readme(partials_dir, output_path, username, token)

if __name__ == "__main__":
    main()
