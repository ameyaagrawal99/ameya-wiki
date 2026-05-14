"""
Weekly wiki updater for Ameya Agrawal's personal wiki.
Fetches public sources and updates wiki/pages/*.md files.
Runs via GitHub Actions every Sunday.
"""

import re
import sys
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

TODAY = date.today().isoformat()
WIKI_PAGES = Path("wiki/pages")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AmeyaWikiBot/1.0; personal wiki updater)"
}


def fetch(url, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  WARN: Could not fetch {url}: {e}")
        return None


def update_frontmatter_date(content):
    """Update the `updated:` field in YAML frontmatter."""
    return re.sub(r"(updated:\s*)\d{4}-\d{2}-\d{2}", rf"\g<1>{TODAY}", content)


def write_page(slug, content):
    path = WIKI_PAGES / f"{slug}.md"
    if path.exists():
        old = path.read_text()
        if old == content:
            print(f"  {slug}: no change")
            return
    path.write_text(content)
    print(f"  {slug}: updated")


# ── Blog ────────────────────────────────────────────────────────────────────

def update_blog():
    print("Fetching blog.ameya.page...")
    html = fetch("https://blog.ameya.page/")
    if not html:
        return

    soup = BeautifulSoup(html, "lxml")
    posts = []

    for article in soup.select("article, .post, .entry"):
        title_el = article.select_one("h2 a, h3 a, .entry-title a")
        date_el = article.select_one("time, .entry-date, .post-date")
        cat_el = article.select_one(".category, .cat-links a, .tags a")

        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        link = title_el.get("href", "")
        pub_date = date_el.get_text(strip=True) if date_el else ""
        cats = cat_el.get_text(strip=True) if cat_el else ""
        if title:
            posts.append((title, pub_date, cats, link))

    if not posts:
        print("  No posts found — structure may have changed.")
        return

    path = WIKI_PAGES / "blog-mind-machine-meaning.md"
    if not path.exists():
        return

    content = path.read_text()

    # Rebuild the posts table
    table_rows = "\n".join(
        f"| {t} | {d} | {c} |" for t, d, c, _ in posts[:10]
    )
    new_table = (
        "## Published Posts\n\n"
        "| Title | Date | Categories |\n"
        "|---|---|---|\n"
        + table_rows
    )

    # Replace existing table
    content = re.sub(
        r"## Published Posts\n\n.*?(?=\n## |\Z)",
        new_table + "\n\n",
        content,
        flags=re.DOTALL,
    )
    content = update_frontmatter_date(content)
    write_page("blog-mind-machine-meaning", content)


# ── GitHub ───────────────────────────────────────────────────────────────────

def update_github():
    print("Fetching github.com/ameyaagrawal99...")
    html = fetch("https://github.com/ameyaagrawal99")
    if not html:
        return

    soup = BeautifulSoup(html, "lxml")
    repos = []

    for item in soup.select("[itemprop='owns'] li, .pinned-item-list-item"):
        name_el = item.select_one("a[href*='/ameyaagrawal99/'] span.repo, span[class*='repo'], a span")
        desc_el = item.select_one("p.pinned-item-desc, [class*='description']")
        lang_el = item.select_one("span[itemprop='programmingLanguage'], [class*='language']")

        name = name_el.get_text(strip=True) if name_el else ""
        desc = desc_el.get_text(strip=True) if desc_el else ""
        lang = lang_el.get_text(strip=True) if lang_el else ""

        if name:
            repos.append((name, desc, lang))

    if not repos:
        # fallback: search for repo links
        seen = set()
        for a in soup.select("a[href^='/ameyaagrawal99/']"):
            href = a["href"].strip("/")
            parts = href.split("/")
            if len(parts) == 2 and parts[1] not in ("followers", "following", "stars"):
                repo_name = parts[1]
                if repo_name not in seen:
                    seen.add(repo_name)
                    repos.append((repo_name, "", ""))

    if not repos:
        print("  No repos found.")
        return

    path = WIKI_PAGES / "github-projects.md"
    if not path.exists():
        return

    content = path.read_text()
    content = update_frontmatter_date(content)

    # Update repo count in header
    content = re.sub(r"\*\*Repos:\*\* \d+", f"**Repos:** {len(repos)}", content)
    write_page("github-projects", content)


# ── Medium ───────────────────────────────────────────────────────────────────

def update_medium():
    print("Fetching ameyaagrawal.medium.com...")
    html = fetch("https://ameyaagrawal.medium.com/")
    if not html:
        return

    soup = BeautifulSoup(html, "lxml")
    articles = []

    for item in soup.select("article, [data-testid='post-preview']"):
        title_el = item.select_one("h2, h3, [data-testid='post-preview-title']")
        if title_el:
            articles.append(title_el.get_text(strip=True))

    if not articles:
        print("  No articles found — Medium may be JS-rendered.")
        return

    path = WIKI_PAGES / "medium-writing.md"
    if not path.exists():
        return

    content = path.read_text()
    content = update_frontmatter_date(content)
    write_page("medium-writing", content)


# ── Overview log ─────────────────────────────────────────────────────────────

def update_log():
    """Append a weekly update entry to the log."""
    log_path = Path("wiki/log.md")
    if not log_path.exists():
        return

    content = log_path.read_text()
    entry = f"\n## [{TODAY}] update | Weekly automated refresh\n"

    if TODAY not in content:
        log_path.write_text(content + entry)
        print(f"  log: appended entry for {TODAY}")
    else:
        print("  log: today already logged")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"=== Wiki update run: {TODAY} ===\n")
    update_blog()
    update_github()
    update_medium()
    update_log()
    print("\nDone.")


if __name__ == "__main__":
    main()
