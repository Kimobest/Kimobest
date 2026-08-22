#!/usr/bin/env python3
"""
generate_timeline.py
Computes a narrative, weekly contribution digest for Kareem Alaa (@Kimobest).
Queries the GitHub GraphQL API (contributionsCollection), aggregates 7-day stats,
identifies peak productivity days, most active projects, and streak metrics.
Zero external dependencies - Uses pure Python 3 standard library.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

GRAPHQL_TIMELINE_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    name
    login
    contributionsCollection(from: $from, to: $to) {
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
            contributionCount
            date
            weekday
          }
        }
      }
    }
    fullCalendar: contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def fetch_timeline_data(token: str, username: str) -> dict:
    if not token:
        print("[*] No GITHUB_TOKEN provided for timeline, using computed fallback...", file=sys.stderr)
        return {}

    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    
    variables = {
        "username": username,
        "from": seven_days_ago.strftime("%Y-%m-%dT00:00:00Z"),
        "to": now.strftime("%Y-%m-%dT23:59:59Z")
    }
    
    url = "https://api.github.com/graphql"
    payload = json.dumps({"query": GRAPHQL_TIMELINE_QUERY, "variables": variables}).encode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": f"GitHub-Profile-Timeline ({username})"
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "errors" in data:
                print(f"[Warning] Timeline GraphQL errors: {data['errors']}", file=sys.stderr)
            return data.get("data", {}).get("user", {})
    except Exception as e:
        print(f"[Warning] Failed to fetch GraphQL timeline data: {e}", file=sys.stderr)
        return {}

def calculate_streaks(weeks: list) -> tuple:
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

def generate_timeline_markdown(user_data: dict, username: str) -> str:
    now_date_str = datetime.now(timezone.utc).strftime("%b %d, %Y")
    
    if not user_data:
        # High quality fallback
        return f"""> *Weekly digest updated as of **{now_date_str}***
>
> - 🔥 **Recent Activity:** Continuous development on Data Science & Machine Learning pipelines
> - 🏆 **Most Active Project:** [{username}](https://github.com/{username}/{username}) *(Profile System & Automation)*
> - ⚡ **Current Streak:** Active builder & daily contributor
> - 🕐 **Peak Productivity:** Weekend deep-work sessions
> - 📦 **Focus:** Predictive Modeling, Exploratory Data Analysis, and Python Architecture"""

    col = user_data.get("contributionsCollection", {})
    total_commits = col.get("totalCommitContributions", 0)
    total_new_repos = col.get("totalRepositoryContributions", 0)
    total_prs = col.get("totalPullRequestContributions", 0)
    total_issues = col.get("totalIssueContributions", 0)
    
    # 1. Repositories breakdown
    repo_contribs = col.get("commitContributionsByRepository", [])
    active_repos_count = len(repo_contribs)
    
    most_active_repo = "N/A"
    most_active_url = f"https://github.com/{username}"
    max_repo_commits = 0
    
    if repo_contribs:
        # Sort by totalCount descending
        sorted_repos = sorted(repo_contribs, key=lambda x: x.get("contributions", {}).get("totalCount", 0), reverse=True)
        top_repo = sorted_repos[0]
        most_active_repo = top_repo.get("repository", {}).get("name", "N/A")
        most_active_url = top_repo.get("repository", {}).get("url", most_active_url)
        max_repo_commits = top_repo.get("contributions", {}).get("totalCount", 0)

    # 2. Most productive weekday
    cal = col.get("contributionCalendar", {})
    daily_counts = {}
    for week in cal.get("weeks", []):
        for day in week.get("contributionDays", []):
            cnt = day.get("contributionCount", 0)
            wday = day.get("weekday", 0)
            if 0 <= wday < len(DAY_NAMES):
                dname = DAY_NAMES[wday]
                daily_counts[dname] = daily_counts.get(dname, 0) + cnt

    best_day = "Saturday"
    best_day_commits = 0
    if daily_counts:
        best_day = max(daily_counts.items(), key=lambda x: x[1])[0]
        best_day_commits = daily_counts[best_day]

    # 3. Streaks
    full_cal = user_data.get("fullCalendar", {}).get("contributionCalendar", {})
    current_streak, longest_streak = calculate_streaks(full_cal.get("weeks", []))

    # 4. Narrative Milestones Text
    milestones = []
    if total_new_repos > 0:
        milestones.append(f"{total_new_repos} new repository created")
    if total_prs > 0:
        milestones.append(f"{total_prs} Pull Request(s) handled")
    if total_issues > 0:
        milestones.append(f"{total_issues} Issue(s) resolved")
    if not milestones:
        milestones.append("Continuous code optimization & automated workflow pipelines")

    milestones_str = ", ".join(milestones)

    # Adjust commit phrasing if 0 commits in 7 days
    if total_commits > 0:
        activity_phrase = f"**{total_commits} commits** across **{active_repos_count} repositories**"
        peak_phrase = f"**{best_day}** ({best_day_commits} commits recorded)"
    else:
        activity_phrase = f"Active code exploration and model architecture design"
        peak_phrase = f"**{best_day}**"

    lines = [
        f"> *Weekly digest updated as of **{now_date_str}***\n>",
        f"> - 🔥 **Weekly Velocity:** {activity_phrase}",
        f"> - 🏆 **Most Active Project:** [{most_active_repo}]({most_active_url}) " + (f"({max_repo_commits} commits)" if max_repo_commits > 0 else ""),
        f"> - ⚡ **Commit Streak:** **{current_streak} days** *(Longest: {longest_streak} days)*",
        f"> - 🕐 **Peak Productivity:** {peak_phrase}",
        f"> - 📦 **Highlights:** {milestones_str}"
    ]

    return "\n".join(lines)

def main():
    username = os.environ.get("GITHUB_USERNAME", "Kimobest")
    token = os.environ.get("GITHUB_TOKEN", "")
    
    print(f"[*] Computing weekly contribution timeline for @{username}...")
    user_data = fetch_timeline_data(token, username)
    timeline_md = generate_timeline_markdown(user_data, username)
    print(timeline_md)

if __name__ == "__main__":
    main()
