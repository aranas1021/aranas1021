"""
Generates live-updating SVG stat badges for CodeChef and GeeksforGeeks.

Run daily by .github/workflows/update-stats.yml, which commits the
resulting SVGs in /profile/ back to the repo. Reference them in your
README like:

    ![CodeChef](./profile/codechef.svg)
    ![GFG](./profile/gfg.svg)

Both platforms lack an official public API, so this script scrapes their
public profile pages directly. If CodeChef or GFG change their page
structure, the relevant selectors below will need updating — the script
is written to fail gracefully (keeps the last known SVG) rather than
commit a broken/blank badge.
"""

import re
import sys
import requests
from bs4 import BeautifulSoup

CODECHEF_USERNAME = "gazianas"
GFG_USERNAME = "gazianas"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def make_badge(label: str, value: str, color: str) -> str:
    """Minimal flat shields.io-style SVG badge (no external calls needed)."""
    label_w = 10 * len(label) + 20
    value_w = 10 * len(value) + 20
    total_w = label_w + value_w
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="28" role="img" aria-label="{label}: {value}">
  <rect width="{label_w}" height="28" fill="#555"/>
  <rect x="{label_w}" width="{value_w}" height="28" fill="{color}"/>
  <g fill="#fff" font-family="Verdana,Geneva,sans-serif" font-size="13">
    <text x="{label_w/2}" y="18" text-anchor="middle">{label}</text>
    <text x="{label_w + value_w/2}" y="18" text-anchor="middle">{value}</text>
  </g>
</svg>'''


def fetch_codechef(username: str):
    url = f"https://www.codechef.com/users/{username}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rating_tag = soup.find("div", class_="rating-number")
    rating = rating_tag.text.strip() if rating_tag else "N/A"

    star_tag = soup.find("span", class_=re.compile(r"rating(-star|__stars)?"))
    stars = star_tag.text.strip().count("★") if star_tag else 0

    fully_solved = "N/A"
    problems_tag = soup.find("section", class_="rating-data-section problems-solved")
    if problems_tag:
        match = re.search(r"Fully Solved\s*\((\d+)\)", problems_tag.text)
        if match:
            fully_solved = match.group(1)

    return rating, stars, fully_solved


def fetch_gfg(username: str):
    # Unofficial GFG data endpoint (community-maintained, may go down —
    # see fallback below).
    api_url = f"https://geeks-for-geeks-api.vercel.app/{username}"
    try:
        resp = requests.get(api_url, timeout=15)
        data = resp.json()
        if "info" in data:
            return str(data["info"].get("totalProblemsSolved", "N/A"))
    except Exception:
        pass

    # Fallback: scrape the profile page directly.
    url = f"https://www.geeksforgeeks.org/profile/{username}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    match = re.search(r'"totalProblemsSolved"\s*:\s*"?(\d+)"?', resp.text)
    if match:
        return match.group(1)
    return "N/A"


def main():
    exit_code = 0

    try:
        rating, stars, solved = fetch_codechef(CODECHEF_USERNAME)
        cc_svg = make_badge("CodeChef", f"{stars}\u2605 | {rating}", "#5B4638")
        with open("profile/codechef.svg", "w") as f:
            f.write(cc_svg)
        print(f"CodeChef OK: {stars} stars, rating {rating}, solved {solved}")
    except Exception as e:
        print(f"CodeChef fetch failed, leaving previous badge in place: {e}", file=sys.stderr)
        exit_code = 1

    try:
        gfg_solved = fetch_gfg(GFG_USERNAME)
        gfg_svg = make_badge("GFG", f"{gfg_solved}+ Solved", "#2F8D46")
        with open("profile/gfg.svg", "w") as f:
            f.write(gfg_svg)
        print(f"GFG OK: {gfg_solved} solved")
    except Exception as e:
        print(f"GFG fetch failed, leaving previous badge in place: {e}", file=sys.stderr)
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
