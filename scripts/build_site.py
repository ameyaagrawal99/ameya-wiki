"""
Static site builder for Ameya Agrawal's personal wiki.
Converts markdown pages → pre-built HTML. Run by GitHub Actions after update_wiki.py.
"""

import json
import re
from datetime import date
from pathlib import Path

import markdown
from markdown.extensions.toc import TocExtension

TODAY = date.today().isoformat()
SITE_ROOT = Path(".")
PAGES_OUT = SITE_ROOT / "pages"
WIKI_PAGES = SITE_ROOT / "wiki" / "pages"
WIKI_ROOT = SITE_ROOT / "wiki"
BASE = "/ameya-wiki"
REPO = "ameyaagrawal99/ameya-wiki"
BRANCH = "main"

# Sections stripped from public output
PRIVATE_SECTIONS = [
    "Open Questions",
    "Sources Not Yet Ingested",
    "Sources Not Yet Fetchable",
]

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
    return f"{BASE}/" if slug == "overview" else f"{BASE}/pages/{slug}.html"


def src_github_path(page):
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

_URL_RE = re.compile(r'(?<!["\'=>])(https?://[^\s<>"\')\]]+)')


def linkify_bare_urls(html):
    """
    Make bare https:// URLs clickable throughout the article.
    Skips URLs already inside <a href="...">.
    """
    # Split on existing <a ...>...</a> blocks to avoid double-linking
    parts = re.split(r'(<a\b[^>]*>.*?</a>)', html, flags=re.DOTALL)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:          # inside existing <a> — leave untouched
            out.append(part)
        else:
            def make_link(m):
                url = m.group(1).rstrip(".,;:)")
                label = re.sub(r"^https?://(?:www\.)?", "", url)
                if len(label) > 60:
                    label = label[:60] + "…"
                return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
            out.append(_URL_RE.sub(make_link, part))
    return "".join(out)


def fix_multiple_backlinks(html):
    """
    When a footnote is cited multiple times, markdown generates multiple ↩↩↩.
    Collapse them to a single clean backlink.
    """
    return re.sub(
        r'(&#8617;(\s*&#8617;)+)',
        '&#8617;',
        html,
    )


def open_external_links(html):
    """Add target=_blank to all http(s) links that don't already have it."""
    return re.sub(
        r'<a (href="https?://[^"]+")(?![^>]*target)',
        r'<a \1 target="_blank" rel="noopener"',
        html,
    )


# ── Table of Contents ────────────────────────────────────────────────────────

def inject_toc(html, toc_html):
    """Insert Wikipedia-style TOC after the first paragraph/lead text."""
    if not toc_html or "<li>" not in toc_html:
        return html  # no sections — skip

    toc_block = (
        '<div id="toc">'
        '<div id="toc-title">Contents</div>'
        + toc_html +
        '</div>'
    )
    # Insert after first </p>
    return html.replace("</p>", f"</p>\n{toc_block}", 1)


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
    edit_url = f"https://github.com/{REPO}/edit/{BRANCH}/{src_github_path(page)}"
    sidebar = build_sidebar(slug)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Ameya Agrawal Wiki</title>
  <meta name="description" content="Personal wiki of Ameya Agrawal — {title}">
  <meta property="og:title" content="{title} — Ameya Agrawal Wiki">
  <meta property="og:description" content="Personal wiki of Ameya Agrawal">
  <meta property="og:type" content="article">
  <link rel="stylesheet" href="{BASE}/assets/css/style.css">
  <link rel="canonical" href="https://ameyaagrawal99.github.io{page_url(slug)}">
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

<script>const BASE = "{BASE}";</script>
<script src="{BASE}/assets/js/search.js"></script>
</body>
</html>"""


# ── Markdown → HTML ──────────────────────────────────────────────────────────

def md_to_html(text):
    toc_ext = TocExtension(title="", toc_depth="2-3", permalink=False)
    proc = markdown.Markdown(
        extensions=["footnotes", "tables", "fenced_code", "nl2br", toc_ext],
        extension_configs={"footnotes": {"BACKLINK_TEXT": "&#8617;"}},
    )
    html = proc.convert(text)
    toc_html = getattr(proc, "toc", "")
    return html, toc_html


def build_page(page):
    src = Path(page["src"])
    if not src.exists():
        print(f"  SKIP  {page['slug']}: {src} not found")
        return None

    raw = src.read_text(encoding="utf-8")
    md = strip_frontmatter(raw)
    md = hide_private_sections(md)
    md = convert_wikilinks(md)

    article_html, toc_html = md_to_html(md)
    article_html = inject_toc(article_html, toc_html)
    article_html = linkify_bare_urls(article_html)
    article_html = fix_multiple_backlinks(article_html)
    article_html = open_external_links(article_html)

    full_html = page_template(page, article_html)

    out = Path(page["out"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(full_html, encoding="utf-8")
    print(f"  ✓  {page['slug']:42s} → {out}")

    plain = re.sub(r"<[^>]+>", " ", article_html)
    plain = re.sub(r"\s+", " ", plain).strip()
    return {"slug": page["slug"], "title": page["title"], "cat": page["cat"],
            "url": page_url(page["slug"]), "text": plain[:3000]}


# ── Internal notes (hidden page) ─────────────────────────────────────────────

def build_internal_notes():
    src = Path(WIKI_ROOT / "overview.md")
    if not src.exists():
        return
    raw = src.read_text(encoding="utf-8")
    md = strip_frontmatter(raw)

    notes = []
    for s in PRIVATE_SECTIONS:
        m = re.search(rf"## {re.escape(s)}\n([\s\S]*?)(?=\n## |\Z)", md)
        if m:
            notes.append(f"## {s}\n{m.group(1)}")

    if not notes:
        return

    content_md = "# Internal Wiki Notes\n\n*Not indexed. Direct URL only.*\n\n" + "\n\n".join(notes)
    content_html, _ = md_to_html(content_md)
    content_html = linkify_bare_urls(content_html)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><title>Internal Notes — Ameya Wiki</title>
  <meta name="robots" content="noindex, nofollow">
  <link rel="stylesheet" href="{BASE}/assets/css/style.css">
</head>
<body>
  <div id="header"><div id="header-inner">
    <div id="logo"><a href="{BASE}/"><span id="logo-icon">⬡</span>
    <span id="logo-title">Ameya Agrawal</span><span id="logo-sub">Internal Notes</span></a></div>
  </div></div>
  <div style="max-width:800px;margin:80px auto 60px;padding:0 24px">
    <article id="article">{content_html}</article>
    <p style="margin-top:32px;font-size:13px;color:#666">
      <a href="{BASE}/">← Back to wiki</a> ·
      <a href="https://github.com/{REPO}" target="_blank" rel="noopener">GitHub ↗</a>
    </p>
  </div>
</body>
</html>"""
    out = SITE_ROOT / "internal" / "notes.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  ✓  internal/notes.html (private, noindex)")


# ── Sitemap (for Google) ──────────────────────────────────────────────────────

def build_sitemap():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in PAGES:
        url = f"https://ameyaagrawal99.github.io{page_url(p['slug'])}"
        lines.append(f"  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>")
    lines.append("</urlset>")
    out = SITE_ROOT / "sitemap.xml"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓  sitemap.xml ({len(PAGES)} URLs)")


# ── robots.txt ───────────────────────────────────────────────────────────────

def build_robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /internal/\n"
        f"Sitemap: https://ameyaagrawal99.github.io{BASE}/sitemap.xml\n"
    )
    (SITE_ROOT / "robots.txt").write_text(content)
    print(f"  ✓  robots.txt")


# ── Search index ─────────────────────────────────────────────────────────────

def build_search_index(entries):
    idx = [e for e in entries if e]
    (SITE_ROOT / "search-index.json").write_text(
        json.dumps(idx, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  ✓  search-index.json ({len(idx)} entries)")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n=== Building site: {TODAY} ===\n")
    PAGES_OUT.mkdir(exist_ok=True)

    entries = [build_page(p) for p in PAGES]
    build_internal_notes()
    build_sitemap()
    build_robots()
    build_search_index(entries)

    print(f"\nDone — {len(PAGES)} pages built.\n")


if __name__ == "__main__":
    main()
