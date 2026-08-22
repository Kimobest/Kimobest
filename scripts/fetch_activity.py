#!/usr/bin/env python3
"""
fetch_activity.py
Fetches recent activity from an RSS feed OR falls back to recent public GitHub events.
Zero external dependencies - Uses pure Python 3 standard library.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_rss_feed(feed_url: str, max_items: int = 3) -> list:
    """Fetches and parses top items from an RSS/Atom feed."""
    try:
        req = urllib.request.Request(feed_url, headers={"User-Agent": "GitHub-Profile-Activity-Fetcher"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            root = ET.fromstring(resp.read())

        items = []
        # Support RSS 2.0 (<channel><item>)
        for item in root.findall(".//item")[:max_items]:
            title = item.findtext("title", "Untitled Post").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "")
            if pub_date:
                try:
                    # Clean RFC 822 date format to simple YYYY-MM-DD
                    dt = datetime.strptime(pub_date[:16].strip(), "%a, %d %b %Y")
                    pub_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    pub_date = pub_date[:10]
            items.append((title, link, pub_date))

        # Support Atom (<feed><entry>)
        if not items:
            for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry")[:max_items]:
                title = entry.findtext("{http://www.w3.org/2005/Atom}title", "Untitled Post").strip()
                link_elem = entry.find("{http://www.w3.org/2005/Atom}link")
                link = link_elem.attrib.get("href", "") if link_elem is not None else ""
                published = entry.findtext("{http://www.w3.org/2005/Atom}published", "")[:10]
                items.append((title, link, published))

        return items
    except Exception as e:
        print(f"[Warning] RSS feed fetch failed: {e}", file=sys.stderr)
        return []

def fetch_github_activity(username: str, token: str = "", max_items: int = 4) -> list:
    """Fetches recent public events (commits, PRs, releases) for a user."""
    url = f"https://api.github.com/users/{username}/events/public?per_page=15"
    headers = {"User-Agent": f"GitHub-Profile-Activity-Fetcher ({username})"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            events = json.loads(resp.read().decode("utf-8"))

        activity_lines = []
        seen = set()

        for ev in events:
            ev_type = ev.get("type")
            repo_name = ev.get("repo", {}).get("name", "")
            repo_url = f"https://github.com/{repo_name}"
            created_at = ev.get("created_at", "")[:10]

            if not repo_name:
                continue

            if ev_type == "PushEvent":
                commits = ev.get("payload", {}).get("commits", [])
                msg = commits[0].get("message", "").split("\n")[0] if commits else "Code update"
                if len(msg) > 60:
                    msg = msg[:57] + "..."
                key = f"push-{repo_name}"
                if key not in seen:
                    activity_lines.append(f"- 🚀 **Pushed to** [{repo_name}]({repo_url}) — `{msg}` *({created_at})*")
                    seen.add(key)

            elif ev_type == "PullRequestEvent":
                action = ev.get("payload", {}).get("action")
                pr = ev.get("payload", {}).get("pull_request", {})
                pr_title = pr.get("title", "")
                pr_url = pr.get("html_url", repo_url)
                key = f"pr-{pr_url}"
                if key not in seen:
                    activity_lines.append(f"- 🔀 **{action.capitalize()} PR** [{pr_title}]({pr_url}) on [{repo_name}]({repo_url}) *({created_at})*")
                    seen.add(key)

            elif ev_type == "CreateEvent":
                ref_type = ev.get("payload", {}).get("ref_type")
                if ref_type == "repository":
                    key = f"create-{repo_name}"
                    if key not in seen:
                        activity_lines.append(f"- ✨ **Created repository** [{repo_name}]({repo_url}) *({created_at})*")
                        seen.add(key)

            elif ev_type == "WatchEvent":
                key = f"star-{repo_name}"
                if key not in seen:
                    activity_lines.append(f"- ⭐ **Starred** [{repo_name}]({repo_url}) *({created_at})*")
                    seen.add(key)

            if len(activity_lines) >= max_items:
                break

        return activity_lines
    except Exception as e:
        print(f"[Warning] GitHub public activity fetch failed: {e}", file=sys.stderr)
        return []

def get_activity_markdown(username: str, token: str = "", rss_url: str = "") -> str:
    """Returns final formatted markdown for the activity feed."""
    if rss_url:
        print(f"[*] Fetching blog posts from RSS: {rss_url}")
        posts = fetch_rss_feed(rss_url, max_items=3)
        if posts:
            lines = [f"- 📝 **[{title}]({link})** — *{date}*" if date else f"- 📝 **[{title}]({link})**" for title, link, date in posts]
            return "\n".join(lines)

    # Fallback to GitHub Activity
    print(f"[*] Fetching latest public GitHub activity for @{username}...")
    activity = fetch_github_activity(username, token, max_items=4)
    if activity:
        return "\n".join(activity)

    # Clean default fallback
    return "- 🔭 Exploring and training new Data Science & Machine Learning models.\n- 💡 Working on open-source predictive analytics and end-to-end pipelines."

if __name__ == "__main__":
    uname = os.environ.get("GITHUB_USERNAME", "Kimobest")
    tok = os.environ.get("GITHUB_TOKEN", "")
    feed = os.environ.get("RSS_FEED_URL", "")
    print(get_activity_markdown(uname, tok, feed))
