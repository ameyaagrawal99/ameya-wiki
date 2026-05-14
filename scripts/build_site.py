"""
Static site builder for Ameya Agrawal's personal wiki.
Converts markdown pages → pre-built HTML. Run by GitHub Actions after update_wiki.py.
"""

import json
import re
from datetime import date
from pathlib import Path

import markdown

TODAY = date.today().isoformat()
SITE_ROOT = Path(".")
PAGES_OUT = SITE_ROOT / "pages"
WIKI_PAGES = SITE_ROOT / "wiki" / "pages"
WIKI_ROOT = SITE_ROOT / "wiki"
BASE = "/ameya-wiki"           # GitHub Pages base path
REPO = "ameyaagrawal99/ameya-wiki"
BRANCH = "main"

# Sections stripped from public output (internal wiki notes only)
PRIVATE_SECTIONS = ["Open Questions", "Sources Not Yet Ingested"]

CATEGORY_ORDER = ["Overview", "Identity", "Writing", "Work", "Ideas", "Social"]

PAGES = [
    {"slug": "overview",                      "title": "Overview",                        "cat": "Overview", "src": WIKI_ROOT  / "overview.md",                        "out": SITE_ROOT / "index.html"},
    {"slug": "identity-ameya-agrawal",        "title": "Profile & Bio",                   "cat": "Identity", "src": WIKI_PAGES / "identity-ameya-agrawal.md",          "out": PAGES_OUT / "identity-ameya-agrawal.html"},
    {"slug": "achievements-awards",           "title": "Achievements & Awards",           "cat": "Identity", "src": WIKI_PAGES / "achievements-awards.md",             "out": PAGES_OUT / "achievements-awards.html"},
    {"slug": "blog-mind-machine-meaning",     "title": "Blog — Mind, Machine & Meaning",  "cat": "Writing",  "src": WIKI_PAGES / "blog-mind-machine-meaning.md",       "out": PAGES_OUT / "blog-mind-machine-meaning.html"},
    {"slug": "a-leap-within",                 "title": "A Leap Within (Book)",            "cat": "Writing",  "src": WIKI_PAGES / "a-leap-within.md",                   "out": PAGES_OUT / "a-leap-within.html"},
    {"slug": "medium-writing",                "title": "Medium Articles",                 "cat": "Writing",  "src": WIKI_PAGES / "medium-writing.md",                  "out": PAGES_OUT / "medium-writing.html"},
    {"slug": "media-coverage-interviews",     "title": "Media & Interviews",              "cat": "Writing",  "src": WIKI_PAGES / "media-coverage-interviews.md",       "out": PAGES_OUT / "media-coverage-interviews.html"},
    {"slug": "professional-experience",       "title": "Professional Experience",         "cat": "Work",     "src": WIKI_PAGES / "professional-experience.md",         "out": PAGES_OUT / "professional-experience.html"},
    {"slug": "mgss-mahatma-gandhi-seva-sangh","title": "MGSS",                            "cat": "Work",     "src": WIKI_PAGES / "mgss-mahatma-gandhi-seva-sangh.md", "out": PAGES_OUT / "mgss-mahatma-gandhi-seva-sangh.html"},
    {"slug": "skillslate-foundation",         "title": "SkillSlate Foundation",           "cat": "Work",     "src": WIKI_PAGES / "skillslate-foundation.md",           "out": PAGES_OUT / "skillslate-foundation.html"},
    {"slug": "github-projects",               "title": "GitHub Projects",                 "cat": "Work",     "src": WIKI_PAGES / "github-projects.md",                 "out": PAGES_OUT / "github-projects.html"},
    {"slug": "certifications-skills",         "title": "Certifications & Skills",         "cat": "Work",     "src": WIKI_PAGES / "certifications-skills.md",           "out": PAGES_OUT / "certifications-skills.html"},
    {"slug": "ideas-recurring-themes",        "title": "Recurring Themes",                "cat": "Ideas",    "src": WIKI_PAGES / "ideas-recurring-themes.md",          "out": PAGES_OUT / "ideas-recurring-themes.html"},
    {"slug": "social-presence",               "title": "All Platforms",                   "cat": "Social",   "src": WIKI_PAGES / "social-presence.md",                 "out": PAGES_OUT / "social-presence.html"},
    {"slug": "linkedin-profile",              "title": "LinkedIn",                        "cat": "Social",   "src": WIKI_PAGES / "linkedin-profile.md",                "out": PAGES_OUT / "linkedin-profile.html"},
]
page_map = {p["slug"]: p for p in PAGES}


def page_url(slug):
    if slug == "overview":
        return f"{BASE}/"
    return f"{BASE}/pages/{slug}.html"


def src_path(page):
    """Return the GitHub-relative source path for the edit link."""
    p = Path(page["src"])
    parts = list(p.parts)
    try:
        idx = parts.index("wiki")
        return "/".join(parts[idx:])
    except ValueError:
        return str(p)


# ── Markdown pre-processing ──────────────────────────────────────────────────

def strip_frontmatter(md):
    return re.sub(r"^---[\s\S]*?---\n?", "", md).strip()


def hide_private_sections(md):
    for s in PRIVATE_SECTIONS:
        md = re.sub(rf"## {re.escape(s)}\n[\s\S]*?(?=\n## |\Z)", "", md)
    return md.strip()


def convert_wikilinks(md):
    def replace(m):
        slug = m.group(1).strip()
        page = page_map.get(slug)
        return f"[{page['title']}]({page_url(slug)})" if page else f"*{slug}*"
    return re.sub(r"\[\[([^\]]+)\]\]", replace, md)


# ── HTML post-processing ─────────────────────────────────────────────────────

def linkify_footnote_urls(html):
    """Make bare URLs inside the footnotes div clickable."""
    url_re = re.compile(r"(?<![\"'=])(https?://[^\s<>\"']+?)(?=[<\s,\.)]|$)")

    def make_link(m):
        url = m.group(1)
        label = re.sub(r"^https?://", "", url)
        if len(label) > 55:
            label = label[:55] + "…"
        return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'

    def process_section(m):
        return url_re.sub(make_link, m.group(0))

    return re.sub(
        r'<div class="footnote">[\s\S]*?</div>',
        process_section,
        html,
    )


def fix_external_links(html):
    """Open all http(s) links in a new tab."""
    return re.sub(
        r'<a href="(https?://[^"]+)"',
        r'<a href="\1" target="_blank" rel="noopener"',
        html,
    )


# ── Sidebar ──────────────────────────────────────────────────────────────────

def build_sidebar(current_slug):
    cats = {}
    for p in PAGES:
        cats.setdefault(p["cat"], []).append(p)

    lines = ['<nav id="sidebar">']
    lines.append(
        f'<div id="cv-wrap">'
        f'<a class="cv-btn" href="{BASE}/assets/cv/ameya-agrawal-cv.pdf" '
        f'target="_blank" rel="noopener">⬇ Download CV</a>'
        f'</div>'
    )

    for cat in CATEGORY_ORDER:
        pages = cats.get(cat, [])
        if not pages:
            continue
        lines.append(f'<div class="nav-section"><div class="nav-label">{cat}</div><ul>')
        for p in pages:
            active = ' class="active"' if p["slug"] == current_slug else ""
            lines.append(f'<li><a href="{page_url(p["slug"])}"{active}>{p["title"]}</a></li>')
        lines.append("</ul></div>")

    lines.append(
        f'<div id="sidebar-footer">'
        f'<div>Last updated: {TODAY}</div>'
        f'<div><a href="https://github.com/{REPO}" target="_blank" rel="noopener">View on GitHub ↗</a></div>'
        f'</div>'
    )
    lines.append("</nav>")
    return "\n".join(lines)


# ── Full page template ───────────────────────────────────────────────────────

def page_template(page, article_html):
    slug = page["slug"]
    title = page["title"]
    cat = page["cat"]
    edit_url = f"https://github.com/{REPO}/edit/{BRANCH}/{src_path(page)}"
    sidebar = build_sidebar(slug)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Ameya Agrawal Wiki</title>
  <meta name="description" content="Personal wiki of Ameya Agrawal — {title}">
  <link rel="stylesheet" href="{BASE}/assets/css/style.css">
</head>
<body>

<div id="header">
  <div id="header-inner">
    <div id="logo">
      <a href="{BASE}/">
        <span id="logo-icon">⬡</span>
        <span id="logo-title">Ameya Agrawal</span>
        <span id="logo-sub">Personal Wiki</span>
      </a>
    </div>
    <div id="search-wrap">
      <input type="text" id="search" placeholder="Search wiki…" autocomplete="off" aria-label="Search">
      <div id="search-results" role="listbox"></div>
    </div>
  </div>
</div>

<div id="layout">
  {sidebar}
  <main id="content">
    <div id="page-header">
      <div id="breadcrumb"><a href="{BASE}/">Wiki</a> › {cat} › {title}</div>
      <div id="page-actions">
        <a href="{edit_url}" target="_blank" rel="noopener" title="Edit this page on GitHub">Edit ✎</a>
      </div>
    </div>
    <article id="article">
      {article_html}
    </article>
    <div id="page-footer">Last updated: {TODAY}</div>
  </main>
</div>

<script>
  const BASE = "{BASE}";
</script>
<script src="{BASE}/assets/js/search.js"></script>
</body>
</html>"""


# ── Conversion ───────────────────────────────────────────────────────────────

def md_to_html(text):
    proc = markdown.Markdown(
        extensions=["footnotes", "tables", "fenced_code", "nl2br"],
        extension_configs={
            "footnotes": {"BACKLINK_TEXT": "&#8617;"}
        },
    )
    return proc.convert(text)


def build_page(page):
    src = Path(page["src"])
    if not src.exists():
        print(f"  SKIP  {page['slug']}: {src} not found")
        return None

    raw = src.read_text(encoding="utf-8")
    md = strip_frontmatter(raw)
    md = hide_private_sections(md)
    md = convert_wikilinks(md)

    article_html = md_to_html(md)
    article_html = linkify_footnote_urls(article_html)
    article_html = fix_external_links(article_html)

    full_html = page_template(page, article_html)

    out = Path(page["out"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(full_html, encoding="utf-8")
    print(f"  ✓  {page['slug']:40s} → {out}")

    # Return plain text for search index
    plain = re.sub(r"<[^>]+>", " ", article_html)
    plain = re.sub(r"\s+", " ", plain).strip()
    return {"slug": page["slug"], "title": page["title"], "cat": page["cat"],
            "url": page_url(page["slug"]), "text": plain[:2000]}


# ── Internal notes page (not in nav) ────────────────────────────────────────

def build_internal_notes():
    """Build a hidden page with internal wiki notes stripped from public pages."""
    src = Path(WIKI_ROOT / "overview.md")
    if not src.exists():
        return
    raw = src.read_text(encoding="utf-8")
    md = strip_frontmatter(raw)

    # Extract only the private sections
    notes = []
    for s in PRIVATE_SECTIONS:
        m = re.search(rf"## {re.escape(s)}\n([\s\S]*?)(?=\n## |\Z)", md)
        if m:
            notes.append(f"## {s}\n{m.group(1)}")

    if not notes:
        return

    content_md = "# Internal Wiki Notes\n\n*Not indexed. Direct URL only.*\n\n" + "\n\n".join(notes)
    content_html = md_to_html(content_md)
    content_html = linkify_footnote_urls(content_html)

    # Simple template without sidebar
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Internal Notes — Ameya Wiki</title>
  <meta name="robots" content="noindex, nofollow">
  <link rel="stylesheet" href="{BASE}/assets/css/style.css">
</head>
<body>
  <div id="header"><div id="header-inner">
    <div id="logo"><a href="{BASE}/"><span id="logo-icon">⬡</span>
    <span id="logo-title">Ameya Agrawal</span><span id="logo-sub">Internal Notes</span></a></div>
  </div></div>
  <div style="max-width:800px;margin:80px auto;padding:0 24px">
    <article id="article">{content_html}</article>
    <p style="margin-top:32px;font-size:13px;color:#666">
      <a href="{BASE}/">← Back to wiki</a> ·
      <a href="https://github.com/{REPO}" target="_blank" rel="noopener">GitHub</a>
    </p>
  </div>
  <link rel="stylesheet" href="{BASE}/assets/css/style.css">
</body>
</html>"""
    out = SITE_ROOT / "internal" / "notes.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  ✓  internal/notes.html (private)")


# ── Search index ─────────────────────────────────────────────────────────────

def build_search_index(entries):
    idx = [e for e in entries if e]
    out = SITE_ROOT / "search-index.json"
    out.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓  search-index.json ({len(idx)} entries)")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n=== Building site: {TODAY} ===\n")
    PAGES_OUT.mkdir(exist_ok=True)

    entries = []
    for page in PAGES:
        entry = build_page(page)
        entries.append(entry)

    build_internal_notes()
    build_search_index(entries)

    print(f"\nDone — {len(PAGES)} pages built.\n")


if __name__ == "__main__":
    main()
