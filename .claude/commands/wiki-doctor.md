---
description: Check your wiki setup and install the recommended skills
---

Run a setup check for this wiki, then help the user install the recommended skills.

## Environment

- `python3 --version` (the linter needs Python 3). Check whether pyyaml imports (`python3 -c "import yaml"`); if not, mention `pip install pyyaml` — the linter falls back without it, but pyyaml is more robust.
- `rg --version` (default search). Optionally, whether a `qmd` daemon is up (see `docs/search-qmd.md`).
- Vendored skills present: `.claude/skills/llm-wiki/` and `.claude/skills/youtube-content/`.
- Does `SCHEMA.md` still have the placeholder **Domain** / **Tag Taxonomy**? Nudge the user to fill them in — the wiki is much more useful once its scope is declared.

## Recommended skills (strongly recommend — install unless the user declines)

See `RECOMMENDED-SKILLS.md`. Check whether each is present; for any missing, explain what it adds and offer the install command:

- **Superpowers** — process discipline (brainstorming, TDD, systematic debugging). Plugin marketplace.
- **Matt Pocock skills** — the grill → spec → tickets → implement flow. `npx skills` / `setup-matt-pocock-skills`.
- **find-skills** — discover and install more skills as your wiki grows.

Superpowers and Matt Pocock **overlap** (both bring planning / TDD / grilling) — explain the roles so the user isn't confused about which to reach for, and note they can skip any they don't want. These are strong recommendations, **not hard requirements**: the wiki works with just the vendored core.

## Bypass-permissions tip

Explain — **scoped to this wiki repo only** — that bypass-permissions mode removes the constant approval prompts a wiki triggers (many file writes), and that it's low-risk here because wiki operations execute no code. Make clear this does **not** extend to code repositories, where approvals matter.
