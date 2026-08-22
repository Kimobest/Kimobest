# 🛠️ Automated Profile README System — Developer & Operations Manual

Welcome to your automated GitHub profile README architecture. This repository is structured as a modular, self-updating system powered by **GitHub Actions** and lightweight **Python 3 scripts** with **zero external dependencies**.

---

## 🏗️ Architecture & Pipeline Overview

```
Kimobest/ (Profile Repository)
│
├── .github/workflows/
│   ├── snake.yml               # Generates daily animated snake eating contribution grid -> 'output' branch
│   └── update-profile.yml      # Master pipeline: Custom Stats SVG + Activity Feed + README Assembly (Every 6h)
│
├── scripts/
│   ├── generate_stats.py       # Queries GraphQL API, calculates streaks & language bytes, renders self-hosted SVG
│   ├── fetch_activity.py       # Parses RSS feed or GitHub public events fallback
│   └── build_readme.py         # Assembles partials/ into root README.md & injects dynamic feed
│
├── partials/                   # Modular Markdown components (Edit these to customize content)
│   ├── 01_header.md            # Animated banner, Typing SVG title, social shields
│   ├── 02_about.md             # About Me (Data Science & ML focus)
│   ├── 03_skills.md            # Modern Skillicons grid & categorized badges
│   ├── 04_stats.md             # Custom self-hosted SVG stats card & activity wave graph
│   ├── 05_snake.md             # Contribution snake animation wrapper
│   ├── 06_activity.md          # Dynamic activity feed markers <!--LATEST-ACTIVITY:START-->
│   ├── 07_projects.md          # Featured Data Science portfolio showcase table
│   └── 08_footer.md            # Let's connect links & bottom wave footer
│
├── assets/
│   └── github-stats.svg        # 100% self-hosted, custom-rendered SVG stats card
│
├── README.md                   # The final compiled README rendered by GitHub
└── README-DEV.md               # This maintenance and developer documentation
```

---

## ⚡ How the Automated Modules Work

### 1. Custom SVG Stats Generator (`scripts/generate_stats.py`)
- **First-Party & Self-Hosted:** No reliance on 3rd-party services (e.g. `github-readme-stats.vercel.app`), guaranteeing 100% uptime with zero 503 errors.
- **GraphQL API Authentication:** Authenticates securely using the built-in `${{ secrets.GITHUB_TOKEN }}`.
- **Calculated Metrics:**
  - `Total Contributions`: Calendar sum across the current contribution year.
  - `Current & Longest Streak`: Chronologically computed from contribution calendar days.
  - `Total Stars Earned`: Real-time sum of stargazers across all owned repositories.
  - `Top Languages`: Exact byte-weighted calculation with a proportional neon progress bar.
  - `Latest Active Repository`: Identifies the most recently updated project.
- **Output:** Renders and commits directly to `assets/github-stats.svg`.

### 2. Live Activity & Blog Feed (`scripts/fetch_activity.py`)
- **RSS Blog Feed (Optional):** If you configure a secret or env var `BLOG_RSS_URL` (e.g. Medium, Dev.to, or Hashnode), the script parses the top 3 latest articles.
- **GitHub Public Activity (Fallback):** If no RSS URL is provided, it automatically fetches your latest 4 public GitHub contributions (Pushed commits, Merged Pull Requests, Created Repositories, Starred projects).

### 3. README Modular Assembly System (`scripts/build_readme.py`)
- **Partials Compilation:** Reads files in `partials/` sorted in alphanumeric order (`01_header.md` through `08_footer.md`).
- **Dynamic In-Place Replacement:** Locates `<!--LATEST-ACTIVITY:START-->` and `<!--LATEST-ACTIVITY:END-->` in `partials/06_activity.md` and injects live markdown.
- **Idempotency:** Generates `README.md`. If no content has changed, git skips committing to prevent empty commit pollution.

---

## 🚀 Step-by-Step Setup & Verification Instructions

### Step 1: Verify GitHub Workflow Permissions
Ensure GitHub Actions can push updates back to your repository:
1. Navigate to: **Settings** > **Actions** > **General**
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions** ✅.
4. Check **Allow GitHub Actions to create and approve pull requests** ✅.
5. Click **Save**.

### Step 2: (Optional) Add Blog RSS Feed URL
If you want the activity feed to display your personal blog posts:
1. Go to: **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**.
3. Name: `BLOG_RSS_URL`
4. Value: `https://medium.com/feed/@yourusername` (or your custom RSS link).
5. Click **Add secret**.

### Step 3: Test Workflows Manually (`workflow_dispatch`)
Before waiting for the cron schedule, trigger both workflows to verify:
1. Open the **Actions** tab: `https://github.com/Kimobest/Kimobest/actions`
2. **Test 3D / Snake Action:**
   - Select **Generate Snake Animation** > Click **Run workflow**.
3. **Test Profile Build Pipeline:**
   - Select **Automated Profile README & Stats Update** > Click **Run workflow**.
4. Check that both workflows finish with a green checkmark (**✔**).

---

## 💻 Local Development & Customization

To edit your profile locally on your machine:

```bash
# 1. Edit any component inside partials/
# e.g., edit partials/07_projects.md to add new Data Science repositories

# 2. Test and re-compile README.md locally
python scripts/generate_stats.py
python scripts/build_readme.py

# 3. Commit and push your updates
git add partials/ README.md assets/
git commit -m "docs: update featured projects in profile"
git push origin main
```

When you push to `main`, GitHub Actions will automatically re-run the pipeline and keep all stats in sync.

---

## 🔒 Security & Performance Best Practices

- **Zero Token Leakage:** All API tokens are read from environment variables; zero hardcoded secrets.
- **Loop Prevention:** Automated commits append `[skip ci]` to prevent endless workflow triggers.
- **Free Quota Friendly:** Workflows run every 6 hours and take less than 5 seconds each, consuming less than 20 minutes/month out of your 2,000 free monthly GitHub Actions minutes.
