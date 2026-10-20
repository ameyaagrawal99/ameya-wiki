# ameya-wiki

Personal wiki for Ameya Agrawal: professional identity, writing, projects, ideas, and public presence across platforms. Published as a static site (GitHub Pages) from Markdown source.

## Structure
- `wiki/pages/*.md` — source content, flat, no subdirectories. Schema and conventions: `SCHEMA.md`.
- `wiki/overview.md` — current synthesis across all sources; regenerated on every operation that adds/changes pages.
- `pages/*.html`, `index.html` — generated site output. Don't hand-edit; regenerate via `scripts/build_site.py`.
- `scripts/update_wiki.py` — fetches public sources (blog, LinkedIn, etc.) and updates `wiki/pages/*.md`. Runs weekly via GitHub Actions.
- `scripts/build_site.py` — converts `wiki/pages/*.md` → prebuilt HTML in `pages/`. Page list/order is a hardcoded `PAGES` array — add new pages there too, not just in `wiki/pages/`.
- `search-index.json`, `sitemap.xml` — derived from the same page list; regenerate alongside the HTML.
- `update-wiki.sh` — syncs the private Google-Drive-backed wiki source into this repo's `wiki/` and pushes. Not meant to run outside that environment.

## Working in this repo
- Follow `SCHEMA.md` exactly: frontmatter (`title`, `tags`, `sources`, `updated`), `[[slug]]` cross-references, footnote citations for every non-common-knowledge claim (quote or `[synthesis]`), append-only `log.md`.
- `raw/` (where present) is immutable — never edit or delete source material there.
- After editing `wiki/pages/*.md`, update `wiki/overview.md` and `wiki/index.md` if the change affects synthesis or the page list, then regenerate the site output before committing.
- New wiki page → add its entry to `PAGES` in `scripts/build_site.py` (slug, title, category, src, out) or it won't be built.

## Style
Write wiki content as prose, not bullet-heavy fact sheets — this mirrors how the rest of the wiki reads. Reserve lists for genuinely enumerable things (platforms, tags, dated log entries).
