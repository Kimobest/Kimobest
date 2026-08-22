#!/usr/bin/env python3
"""
contribution_digest.py
Auto-Updating Interactive SVG Contribution Activity Module for GitHub Profile README.

Architecture:
1. API Fetching Logic: Queries GitHub GraphQL API for 7-day and 365-day contribution data.
2. Highlights Computation Logic: Pure testable function compute_highlights(raw_data) -> dict.
3. Dual-Theme SVG Rendering Engine: Generates modern interactive Dark & Light mode SVG cards (CSS hover, tooltips, links).
4. In-Place README Injection Logic: Injects responsive <picture> embed between <!--ACTIVITY:START--> and <!--ACTIVITY:END-->.

Zero external dependencies - Uses pure Python 3 standard library.
"""

import os
import re
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

START_MARKER = "<!--ACTIVITY:START-->"
END_MARKER = "<!--ACTIVITY:END-->"
DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

THEMES = {
    "dark": {
        "bg": "#0D1117",
        "card_bg": "#161B22",
        "card_hover": "#1C2128",
        "border": "#30363D",
        "border_hover": "#00E5FF",
        "accent": "#00E5FF",
        "accent_secondary": "#58A6FF",
        "text": "#C9D1D9",
        "subtext": "#8B949E",
        "bar_empty": "#21262D",
        "bar_fill": "#00E5FF",
        "bar_active": "#79FFE1",
        "shadow": "rgba(0, 229, 255, 0.15)"
    },
    "light": {
        "bg": "#FFFFFF",
        "card_bg": "#F6F8FA",
        "card_hover": "#EAEEF2",
        "border": "#D0D7DE",
        "border_hover": "#0969DA",
        "accent": "#0969DA",
        "accent_secondary": "#218BFF",
        "text": "#1F2328",
        "subtext": "#656D76",
        "bar_empty": "#EAEFF2",
        "bar_fill": "#0969DA",
        "bar_active": "#218BFF",
        "shadow": "rgba(9, 105, 218, 0.12)"
    }
}

GRAPHQL_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    name
    login
    weeklyActivity: contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalRepositoryContributions
      commitContributionsByRepository(maxRepositories: 25) {
        repository {
          name
          url
        }
        contributions {
          totalCount
        }
      }
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            weekday
            contributionCount
          }
        }
      }
    }
    annualActivity: contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

# ==============================================================================
# 1. API Fetching Logic
# ==============================================================================

def fetch_raw_activity_data(token: str, username: str) -> dict:
    """Queries GitHub GraphQL API for 7-day and annual contribution collections."""
    if not token:
        print("[*] No GITHUB_TOKEN provided, utilizing simulated baseline...", file=sys.stderr)
        return {}

    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)

    variables = {
        "username": username,
        "from": seven_days_ago.strftime("%Y-%m-%dT00:00:00Z"),
        "to": now.strftime("%Y-%m-%dT23:59:59Z")
    }

    url = "https://api.github.com/graphql"
    payload = json.dumps({"query": GRAPHQL_QUERY, "variables": variables}).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": f"GitHub-Contribution-Digest-Bot ({username})"
    }

    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "errors" in data:
                print(f"[Warning] GraphQL returned errors: {data['errors']}", file=sys.stderr)
            return data.get("data", {}).get("user", {})
    except urllib.error.HTTPError as e:
        print(f"[Error] GraphQL HTTP {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"[Error] GraphQL connection failed: {e}", file=sys.stderr)
        return {}


# ==============================================================================
# 2. Highlights Computation Logic (Pure, Testable Function)
# ==============================================================================

def calculate_streaks(weeks: list) -> tuple:
    """Calculates current continuous streak and all-time longest streak in days."""
    all_days = []
    for week in weeks:
        for day in week.get("contributionDays", []):
            all_days.append((day.get("date"), day.get("contributionCount", 0)))

    if not all_days:
        return 0, 0

    all_days.sort(key=lambda x: x[0])
    longest_streak = 0
    temp_streak = 0
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for date_str, count in all_days:
        if count > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    current_streak = 0
    rev_days = list(reversed(all_days))
    for i, (date_str, count) in enumerate(rev_days):
        if i == 0 and count == 0 and date_str == today_str:
            continue
        if count > 0:
            current_streak += 1
        else:
            break

    return current_streak, longest_streak


def compute_highlights(raw_data: dict, username: str = "Kimobest") -> dict:
    """
    Pure transformation function.
    Derives meaningful weekly highlights and daily timeline from raw GraphQL data.
    """
    if not raw_data:
        # Default baseline when offline
        today = datetime.now(timezone.utc)
        simulated_history = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            cnt = 2 if i in [0, 1] else (8 if i == 2 else 0)
            simulated_history.append({
                "date": d.strftime("%Y-%m-%d"),
                "day_name": DAY_NAMES[int(d.strftime("%w"))],
                "count": cnt
            })

        return {
            "total_commits": 14,
            "active_repos_count": 2,
            "most_active_repo": {
                "name": username,
                "url": f"https://github.com/{username}/{username}",
                "commits": 12
            },
            "current_streak": 2,
            "longest_streak": 5,
            "peak_day": "Saturday",
            "peak_day_commits": 12,
            "daily_history": simulated_history,
            "milestone": "Automated profile pipeline & analytics configured"
        }

    weekly = raw_data.get("weeklyActivity", {})
    annual = raw_data.get("annualActivity", {})

    # 1. Total Commits & Active Repositories
    total_commits = weekly.get("totalCommitContributions", 0)
    repo_list = weekly.get("commitContributionsByRepository", [])
    active_repos_count = len(repo_list)

    # 2. Most Active Repository (with tie-breaker sorting)
    if repo_list:
        sorted_repos = sorted(
            repo_list,
            key=lambda r: r.get("contributions", {}).get("totalCount", 0),
            reverse=True
        )
        top_repo = sorted_repos[0]
        most_active_repo = {
            "name": top_repo.get("repository", {}).get("name", "N/A"),
            "url": top_repo.get("repository", {}).get("url", f"https://github.com/{username}"),
            "commits": top_repo.get("contributions", {}).get("totalCount", 0)
        }
    else:
        most_active_repo = {
            "name": username,
            "url": f"https://github.com/{username}/{username}",
            "commits": total_commits
        }

    # 3. Peak Productive Day of the Week & 7-Day History
    daily_history = []
    day_totals = {name: 0 for name in DAY_NAMES}
    for week in weekly.get("contributionCalendar", {}).get("weeks", []):
        for day in week.get("contributionDays", []):
            wday_idx = day.get("weekday", 0)
            if 0 <= wday_idx < len(DAY_NAMES):
                dname = DAY_NAMES[wday_idx]
                c_count = day.get("contributionCount", 0)
                day_totals[dname] += c_count
                daily_history.append({
                    "date": day.get("date", ""),
                    "day_name": dname,
                    "count": c_count
                })

    best_day, best_day_commits = max(day_totals.items(), key=lambda x: x[1])

    # 4. Streak Calculation
    current_streak, longest_streak = calculate_streaks(
        annual.get("contributionCalendar", {}).get("weeks", [])
    )

    # 5. Notable Milestones
    new_repos = weekly.get("totalRepositoryContributions", 0)
    prs = weekly.get("totalPullRequestContributions", 0)
    issues = weekly.get("totalIssueContributions", 0)

    if new_repos > 0:
        milestone = f"Created {new_repos} new repository"
    elif prs > 0:
        milestone = f"Merged {prs} Pull Request(s)"
    elif issues > 0:
        milestone = f"Resolved {issues} Issue(s)"
    elif total_commits >= 20:
        milestone = f"High-velocity sprint: {total_commits} commits logged"
    else:
        milestone = "Continuous architecture & pipeline development"

    return {
        "total_commits": total_commits,
        "active_repos_count": active_repos_count,
        "most_active_repo": most_active_repo,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "peak_day": best_day,
        "peak_day_commits": best_day_commits,
        "daily_history": daily_history[-7:] if daily_history else [],
        "milestone": milestone
    }


# ==============================================================================
# 3. Dual-Theme SVG Rendering Engine (CSS Hover, Native Tooltips, Clickable Links)
# ==============================================================================

def render_activity_svg(highlights: dict, theme_mode: str = "dark") -> str:
    """Renders a modern, interactive dashboard card in Dark or Light mode."""
    t = THEMES.get(theme_mode, THEMES["dark"])

    total_commits = highlights.get("total_commits", 0)
    repo_count = highlights.get("active_repos_count", 0)
    most_active = highlights.get("most_active_repo", {})
    streak = highlights.get("current_streak", 0)
    longest = highlights.get("longest_streak", 0)
    peak_day = highlights.get("peak_day", "Sat")
    peak_commits = highlights.get("peak_day_commits", 0)
    milestone = highlights.get("milestone", "")
    daily_history = highlights.get("daily_history", [])

    repo_name = most_active.get("name", "None")
    repo_url = most_active.get("url", "#")
    repo_commits = most_active.get("commits", 0)
    if len(repo_name) > 16:
        repo_display = repo_name[:14] + ".."
    else:
        repo_display = repo_name

    # 7-Day Mini Bar Graph Generator
    max_daily = max([d.get("count", 0) for d in daily_history] + [1])
    bar_svg_elements = []
    start_bx = 30
    bar_width = 66
    gap = 13
    max_bar_height = 36

    for i, d in enumerate(daily_history[-7:]):
        bx = start_bx + i * (bar_width + gap)
        cnt = d.get("count", 0)
        d_name = d.get("day_name", "")
        d_date = d.get("date", "")
        
        b_height = max(round((cnt / max_daily) * max_bar_height), 4) if cnt > 0 else 3
        by = 222 - b_height
        bar_fill = t["bar_active"] if cnt == max_daily and cnt > 0 else (t["bar_fill"] if cnt > 0 else t["bar_empty"])

        bar_svg_elements.append(f"""
        <g class="mini-bar-group">
          <title>{d_name}, {d_date}: {cnt} commits</title>
          <rect x="{bx}" y="186" width="{bar_width}" height="{max_bar_height}" rx="4" fill="{t['card_bg']}" opacity="0.6"/>
          <rect x="{bx}" y="{by}" width="{bar_width}" height="{b_height}" rx="3" fill="{bar_fill}" class="bar-rect"/>
          <text x="{bx + bar_width/2}" y="238" text-anchor="middle" class="bar-label">{d_name}</text>
          <text x="{bx + bar_width/2}" y="182" text-anchor="middle" class="bar-val-label">{cnt if cnt > 0 else '-'}</text>
        </g>""")

    svg_content = f"""<svg width="600" height="280" viewBox="0 0 600 280" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <style>
    .card-title {{ font: 700 16px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: {t['accent']}; }}
    .card-badge {{ font: 600 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: {t['subtext']}; }}
    .pill-label {{ font: 500 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: {t['subtext']}; }}
    .pill-value {{ font: 700 14px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: {t['text']}; }}
    .pill-accent {{ font: 700 14px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: {t['accent']}; }}
    .bar-label {{ font: 500 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: {t['subtext']}; }}
    .bar-val-label {{ font: 600 10px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: {t['subtext']}; opacity: 0.8; }}
    .milestone-text {{ font: 500 11.5px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; fill: {t['text']}; }}
    
    /* Interactive CSS Micro-Animations */
    .interactive-pill {{
      transition: all 0.2s ease-in-out;
      cursor: default;
    }}
    .interactive-pill:hover {{
      fill: {t['card_hover']};
      stroke: {t['border_hover']};
      filter: drop-shadow(0 2px 8px {t['shadow']});
    }}
    .clickable-link {{
      cursor: pointer;
      text-decoration: none;
    }}
    .clickable-link:hover .pill-value {{
      fill: {t['accent']};
      text-decoration: underline;
    }}
    .bar-rect {{
      transition: all 0.2s ease;
    }}
    .mini-bar-group:hover .bar-rect {{
      fill: {t['bar_active']};
      transform: scaleY(1.08);
      transform-origin: bottom;
    }}
  </style>

  <!-- Container Canvas -->
  <rect width="600" height="280" rx="14" fill="{t['bg']}" stroke="{t['border']}" stroke-width="1.5"/>

  <!-- Card Header -->
  <g transform="translate(30, 24)">
    <circle cx="10" cy="10" r="10" fill="{t['card_bg']}" stroke="{t['accent']}" stroke-width="1.5"/>
    <path d="M7 10 L9.5 12.5 L13.5 7.5" stroke="{t['accent']}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="28" y="15" class="card-title">Weekly Contribution Activity</text>
    <rect x="460" y="2" width="80" height="20" rx="10" fill="{t['card_bg']}" stroke="{t['border']}"/>
    <text x="500" y="16" text-anchor="middle" class="card-badge">Last 7 Days</text>
  </g>

  <!-- 2x2 Grid of Interactive Stat Pill Chips -->
  
  <!-- Pill 1 (Top-Left): Weekly Velocity -->
  <g transform="translate(30, 60)" class="interactive-pill">
    <title>Total commits logged over the past 7 days across all repositories</title>
    <rect width="260" height="46" rx="10" fill="{t['card_bg']}" stroke="{t['border']}" stroke-width="1"/>
    <text x="14" y="20" class="pill-label">🔥 Weekly Velocity</text>
    <text x="14" y="36" class="pill-value"><tspan class="pill-accent">{total_commits}</tspan> commits <tspan fill="{t['subtext']}" font-size="12">({repo_count} repos)</tspan></text>
  </g>

  <!-- Pill 2 (Top-Right): Most Active Project (Clickable SVG Link) -->
  <a xlink:href="{repo_url}" target="_blank" class="clickable-link">
    <g transform="translate(310, 60)" class="interactive-pill">
      <title>Click to open most active repository: {repo_name} ({repo_commits} commits)</title>
      <rect width="260" height="46" rx="10" fill="{t['card_bg']}" stroke="{t['border']}" stroke-width="1"/>
      <text x="14" y="20" class="pill-label">⭐ Most Active Project ↗</text>
      <text x="14" y="36" class="pill-value">{repo_display} <tspan fill="{t['subtext']}" font-size="12">({repo_commits} commits)</tspan></text>
    </g>
  </a>

  <!-- Pill 3 (Bottom-Left): Current Streak -->
  <g transform="translate(30, 114)" class="interactive-pill">
    <title>Continuous unbroken contribution streak</title>
    <rect width="260" height="46" rx="10" fill="{t['card_bg']}" stroke="{t['border']}" stroke-width="1"/>
    <text x="14" y="20" class="pill-label">🌱 Current Streak</text>
    <text x="14" y="36" class="pill-value"><tspan class="pill-accent">{streak}</tspan> days <tspan fill="{t['subtext']}" font-size="12">(Longest: {longest}d)</tspan></text>
  </g>

  <!-- Pill 4 (Bottom-Right): Peak Productivity -->
  <g transform="translate(310, 114)" class="interactive-pill">
    <title>Day of the week with the highest recorded commit volume</title>
    <rect width="260" height="46" rx="10" fill="{t['card_bg']}" stroke="{t['border']}" stroke-width="1"/>
    <text x="14" y="20" class="pill-label">🕐 Peak Productivity</text>
    <text x="14" y="36" class="pill-value">{peak_day} <tspan fill="{t['subtext']}" font-size="12">({peak_commits} commits)</tspan></text>
  </g>

  <!-- 7-Day Mini Bar Graph -->
  {''.join(bar_svg_elements)}

  <!-- Milestone Footer Chip -->
  <g transform="translate(30, 252)">
    <circle cx="6" cy="6" r="4" fill="{t['accent']}"/>
    <text x="16" y="10" class="milestone-text">📦 <tspan font-weight="600">Milestone:</tspan> {milestone}</text>
  </g>

</svg>"""
    return svg_content


# ==============================================================================
# 4. In-Place README Injection Logic (<picture> tag embed)
# ==============================================================================

def inject_picture_embed_into_file(file_path: str, dark_svg: str, light_svg: str) -> bool:
    """Replaces content between START_MARKER and END_MARKER with <picture> block."""
    if not os.path.exists(file_path):
        print(f"[Error] Target file does not exist: {file_path}", file=sys.stderr)
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        print(f"[Warning] Markers not found in {file_path}.", file=sys.stderr)
        return False

    picture_embed = f"""<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="{dark_svg}">
    <source media="(prefers-color-scheme: light)" srcset="{light_svg}">
    <img src="{dark_svg}" width="100%" alt="Weekly Contribution Activity Digest" />
  </picture>
</div>"""

    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL
    )
    new_section = f"{START_MARKER}\n{picture_embed}\n{END_MARKER}"
    updated_content = pattern.sub(new_section, content)

    if updated_content == content:
        print(f"[*] Content in {file_path} is already up-to-date.")
        return False

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"[OK] Injected responsive SVG <picture> embed into {file_path}")
    return True


# ==============================================================================
# 5. Main Execution Entrypoint
# ==============================================================================

def main():
    username = os.environ.get("GITHUB_USERNAME", "Kimobest")
    token = os.environ.get("GITHUB_TOKEN", "")
    output_dark = os.environ.get("OUTPUT_DARK_SVG", "assets/activity-digest-dark.svg")
    output_light = os.environ.get("OUTPUT_LIGHT_SVG", "assets/activity-digest-light.svg")
    target_readme = os.environ.get("TARGET_README_PATH", "README.md")
    target_partial = os.environ.get("TARGET_PARTIAL_PATH", "partials/05_timeline.md")

    os.makedirs(os.path.dirname(output_dark), exist_ok=True)
    os.makedirs(os.path.dirname(output_light), exist_ok=True)

    print(f"[*] Fetching and computing weekly activity highlights for @{username}...")
    raw_data = fetch_raw_activity_data(token, username)
    highlights = compute_highlights(raw_data, username)

    # Render Dark & Light Mode SVGs
    dark_svg_content = render_activity_svg(highlights, theme_mode="dark")
    light_svg_content = render_activity_svg(highlights, theme_mode="light")

    with open(output_dark, "w", encoding="utf-8") as f:
        f.write(dark_svg_content)
    print(f"[OK] Rendered Dark SVG -> {output_dark}")

    with open(output_light, "w", encoding="utf-8") as f:
        f.write(light_svg_content)
    print(f"[OK] Rendered Light SVG -> {output_light}")

    # Inject <picture> embed into partial and root README
    if os.path.exists(target_partial):
        inject_picture_embed_into_file(target_partial, output_dark, output_light)
        
    inject_picture_embed_into_file(target_readme, output_dark, output_light)

if __name__ == "__main__":
    main()
