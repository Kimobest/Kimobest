# 🛠️ Auto-Updating Profile System & Contribution Activity Module — Developer Manual

Welcome to the official developer documentation for the **Auto-Updating Contribution Activity & Profile System** of **Kareem Alaa (@Kimobest)**.

---

## 🏗️ Architecture & Component Overview

```text
Kimobest/ (Special Profile Repository)
│
├── .github/workflows/
│   └── update-profile.yml          # Daily cron & on-push workflow: runs stats generator, builds README, and injects weekly digest
│
├── scripts/
│   ├── contribution_digest.py      # GraphQL API client -> compute_highlights() -> in-place README injector
│   ├── generate_stats.py           # First-party custom SVG stats generator (Total contributions, streaks, languages)
│   └── build_readme.py             # Modular partials compiler
│
├── partials/                       # 🧩 Modular Markdown blocks
│   ├── 01_header.md                # Banner, typing animation, contact badges
│   ├── 02_about.md                 # Data Science profile card
│   ├── 03_skills.md                # Skillicons grid & categorized badges
│   ├── 04_stats.md                 # Custom SVG stats card embed
│   ├── 05_timeline.md              # Target container with <!--ACTIVITY:START--> and <!--ACTIVITY:END-->
│   └── 08_footer.md                # Contact links and wave footer
│
├── assets/
│   └── github-stats.svg            # 100% self-hosted, custom-rendered dark/neon SVG stats card
│
├── README.md                       # Compiled root README rendered on GitHub profile
└── README-DEV.md                   # This operations and maintenance manual
```

---

## ⚡ How the Contribution Activity Module Works

### 1. GraphQL API Query (`scripts/contribution_digest.py`)
Queries the GitHub GraphQL API in a single request:
- **`weeklyActivity` (Past 7 days):** Commits grouped by repository, daily contribution counts, new repositories created, PRs and issues.
- **`annualActivity` (Past 365 days):** Full contribution calendar for calculating uninterrupted contribution streaks.

### 2. Pure Highlights Computation Logic (`compute_highlights(rawData)`)
Derives actionable intelligence from raw GraphQL arrays:
- **Total Commits & Repositories:** Aggregates commits made across unique repositories in the last 7 days.
- **Most Active Project:** Identifies the top repository by commit volume with repository URL and exact commit count.
- **Commit Streak:** Chronologically calculates current continuous streak and all-time longest streak in days.
- **Peak Productivity Day:** Groups commits by day of the week to highlight the most productive workday/weekend.
- **Milestones:** Detects new repositories, merged PRs, resolved issues, or high-velocity sprints.

### 3. In-Place Markdown Injection
The script scans `README.md` and `partials/05_timeline.md` for:
```markdown
<!--ACTIVITY:START-->
- 🔥 **14 commits** across **2 repos**
- ⭐ **Most active:** [Kimobest](https://github.com/Kimobest/Kimobest) (12 commits)
- 🌱 **Current streak:** 2 days *(Longest: 5 days)*
- 🕐 **Most productive day:** Saturday (12 commits)
- 📦 **Milestone:** Automated developer pipeline and developer metrics configured
<!--ACTIVITY:END-->
```
It updates strictly the contents between these markers without altering any other section of the file.

---

## 🤖 GitHub Actions Workflow (`.github/workflows/update-profile.yml`)

- **Schedule:** `cron: "0 0 * * *"` (Daily at midnight UTC).
- **Manual Trigger:** Supports `workflow_dispatch` button in the GitHub UI.
- **Push Trigger:** Re-runs automatically when you edit any file in `partials/**` or `scripts/**`.
- **Permissions:** `contents: write` (least privilege).
- **Identity:** Commits as `github-actions[bot]` with message `chore: update contribution activity [skip ci]`.
- **Idempotency:** Checks `git diff --staged --quiet` and skips committing if content has not changed.

---

## 🚀 Step-by-Step Testing & Verification

1. **Verify Workflow Permissions on GitHub:**
   - Go to: **Settings** > **Actions** > **General**
   - Scroll down to **Workflow permissions**.
   - Select **Read and write permissions** ✅ and save.

2. **Trigger Workflow Manually:**
   - Go to: **Actions** tab (`https://github.com/Kimobest/Kimobest/actions`).
   - Click **Auto-Update Contribution Activity & Profile**.
   - Click **Run workflow** ⬇️.

3. **Local Testing:**
   ```bash
   python scripts/generate_stats.py
   python scripts/build_readme.py
   python scripts/contribution_digest.py
   ```
