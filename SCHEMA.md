# Wiki Schema

## Identity
- **Path:** /Users/ictadmin/Library/CloudStorage/GoogleDrive-ameya.agrawal@mitwpu.edu.in/My Drive/Ameya Agrawal/Ameya WPU Claude Desktop
- **Domain:** Personal wiki capturing Ameya Agrawal's professional identity, writing, projects, ideas, and public presence across platforms.
- **Source types:** Blog posts, LinkedIn profile & posts, Twitter/X threads, GitHub repos, YouTube videos, Facebook profile, Google search mentions
- **Created:** 2026-05-14

## Page Frontmatter
Every wiki page must start with:
---
title: <page title>
tags: [tag1, tag2]
sources: [source-slug1]
updated: YYYY-MM-DD
---

## Cross-References
Use `[[slug]]` where slug = filename without `.md`.
Example: `[[blog-ameya-page]]` → `wiki/pages/blog-ameya-page.md`

## Citations

Cite every non-common-knowledge factual claim. Format: Markdown footnotes.

**Quote citation** (preferred):
```
The post discusses AI agents.[^1]

[^1]: [[blog-ameya-page]] — "AI agents are the next frontier..."
```

**Synthesis citation**:
```
Ameya focuses on AI and education.[^2]

[^2]: [[linkedin-profile]] [synthesis] — About section and experience entries together describe AI + education focus
```

Three rules for every footnote:
1. Cited target is one of: `[[source-slug]]`, `raw/<file>`, or `<URL>`
2. A locator is present: section, paragraph, post date, or URL anchor
3. Either a verbatim quote, or `[synthesis]` tag plus description

## Log Entry Format
## [YYYY-MM-DD] <operation> | <title>
Operations: init, ingest, query, update, lint, audit

## Index Categories
- Identity
- Writing & Content
- Projects & Work
- Ideas & Insights
- Social Presence

## Conventions
- raw/ is immutable — skills never modify it
- log.md is append-only — never rewritten, only appended
- index.md is updated on every operation that adds or changes pages
- All pages live flat in wiki/pages/ — no subdirectories
- overview.md reflects the current synthesis across all sources
