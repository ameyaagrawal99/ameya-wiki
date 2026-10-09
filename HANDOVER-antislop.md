# Handover: antislop skills install

## What
Six Claude Code skills from https://github.com/miqdadbadjuber/anti-slop (MIT), release **3.2.20**, commit `388cbe3b6c37d5175b9f460015bb092ef9e34894` (2026-10-05). They filter generic AI output in UI, copy, accessibility, mobile layout, and code comments.

## Where
Repo `ameyaagrawal99/ameya-wiki`, branch `ccr-4ff3f933-j5d9h4`.

| Path | Purpose |
|---|---|
| `.claude/skills/antislop/SKILL.md` | Core filter: rules R-01..R-38, Delivery Gate, usage modes |
| `.claude/skills/antislop/VERSION` | Upstream release number |
| `.claude/skills/antislop/LICENSE` | Upstream MIT license |
| `.claude/skills/antislop-ui/SKILL.md` | Color, layout, components, motion |
| `.claude/skills/antislop-copywriting/SKILL.md` | Prose, headlines, CTAs, AI-writing tells |
| `.claude/skills/antislop-human/SKILL.md` | Contrast, keyboard, focus, states |
| `.claude/skills/antislop-human/contrast-check.py` | WCAG contrast CLI: `python3 .claude/skills/antislop-human/contrast-check.py "#FFF" "#777"` |
| `.claude/skills/antislop-human/contrast-mcp.py` | Optional stdio MCP server for the same check (not registered) |
| `.claude/skills/antislop-layoutmobile/SKILL.md` | Responsive reflow, tap targets |
| `.claude/skills/antislop-code/SKILL.md` | Comment hygiene only, never touches code |
| `CLAUDE.md` | antislop pointer block; its presence stops the core's first-run install wizard |

## How it loads
Claude Code auto-discovers project skills in `.claude/skills/` at session start. Any session opened on this repo (local, cloud, Codex via the CLAUDE.md pointer) picks them up. Skills load at session start, so the session that installed them does not see them in its skill list.

## Status
- Done: files copied verbatim from upstream, reviewed (no network calls, no injected instructions; Python scripts are pure stdlib math). `contrast-check.py --selftest` passed (8/8 reference pairs).
- Done: pointer block in `CLAUDE.md`.
- Not done (deliberate): the plugin's `antislop-contrast` MCP server is not registered in `.mcp.json`. The CLI script covers the same need. Register it only if wanted.
- Not done: no global mode preference saved. Each session will ask "DURING or AFTER?" on first activation. To skip that, create `~/.config/antislop/settings.json` with `{"mode":"during"}` on the machine in use.

## Decisions / learnings
- Installed as raw project skills instead of `claude plugin install antislop@anti-slop` because cloud containers are ephemeral; committed files persist, a plugin install does not.
- Core skill text refers to `antislop.md`; in this layout that file is `.claude/skills/antislop/SKILL.md`. The pointer block maps the paths.
- Upstream also ships `rules/antislop.md` / `.mdc` for Cursor-style agents; not copied (duplicate of core SKILL.md).

## Update procedure
```bash
git clone --depth 1 https://github.com/miqdadbadjuber/anti-slop /tmp/anti-slop
cp -r /tmp/anti-slop/skills/* .claude/skills/
cat .claude/skills/antislop/VERSION   # confirm new release, then update this file
python3 .claude/skills/antislop-human/contrast-check.py --selftest
```
Read the diff before committing: SKILL.md files are instructions the agent obeys.

## Remove
`rm -rf .claude/skills/antislop*` and delete the `antislop:start..end` block from `CLAUDE.md`.
