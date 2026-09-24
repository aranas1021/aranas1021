# Setup instructions

These files add a daily GitHub Action that scrapes your CodeChef and
GeeksforGeeks profiles and commits updated SVG badges to your repo, so
they show real, auto-refreshing numbers on your README instead of a
static badge.

## 1. Add the files to your repo

In `Anas-Gazi/Anas-Gazi`, add these three items exactly at these paths:

```
.github/workflows/update-stats.yml
scripts/generate_stats.py
profile/.gitkeep
```

You can do this by uploading them through the GitHub web UI ("Add file"
→ "Upload files", recreating the folder structure) or via git:

```bash
git clone https://github.com/Anas-Gazi/Anas-Gazi.git
cd Anas-Gazi
# copy the 3 files/folders into place here, then:
git add .
git commit -m "Add auto-updating CodeChef & GFG stats action"
git push
```

## 2. Run it once manually

Go to your repo → **Actions** tab → **Update CodeChef & GFG Stats** →
**Run workflow**. This generates `profile/codechef.svg` and
`profile/gfg.svg` for the first time (don't wait for the daily cron).

## 3. Add the badges to your README

```html
<img src="./profile/codechef.svg" alt="CodeChef Stats" />
<img src="./profile/gfg.svg" alt="GFG Stats" />
```

Because these are files inside your own repo (not hosted elsewhere),
they'll always load — no dependence on a third-party server staying up.

## 4. If a scrape fails

CodeChef and GFG occasionally change their page layout, which can break
the scraper's selectors. When that happens the workflow logs an error
(visible in the Actions tab) but leaves your last successful badge in
place, rather than breaking the image. If you see stale numbers for a
while, check the Action logs — you (or I, if you paste me the error)
can update the relevant selector in `scripts/generate_stats.py`.
