---
description: Check that this wiki's setup is healthy
---

Check this wiki's setup and report what (if anything) needs attention. Be concrete: run the checks,
don't guess.

## 1. Skills — should already be present

The skills are **vendored into this repo**; there is nothing for the user to install. Verify each
directory exists and has a `SKILL.md`:

`.claude/skills/` → `llm-wiki`, `youtube-content`, `notebooklm-source-corpus`, `research`,
`grilling`, `domain-modeling`, `writing-shape`, `writing-beats`, `writing-fragments`

If any are missing, the fix is `/wiki-update` (re-pull the engine from the template), **not** a
manual install. Do not report skills the user happens to have installed globally as if they were
this repo's — only what's in `.claude/skills/` travels with the template.

## 2. Environment

- `python3 --version` — the linter needs Python 3.
- `python3 -c "import yaml"` — optional; without pyyaml the linter uses a regex fallback (still
  correct, just less robust). Fix: `pip install pyyaml`.
- `rg --version` — the default search. Optional: a `qmd` daemon (see `docs/search-qmd.md`).
- `python3 -c "import youtube_transcript_api"` — only needed for `youtube-content`.
  Fix: `pip install youtube-transcript-api`.
- The NotebookLM CLI — only needed for `notebooklm-source-corpus`. Skip if the user doesn't do
  local media.

## 3. The wiki itself

- Does `SCHEMA.md` still say "Replace this line" in **Domain**, or still carry the example Tag
  Taxonomy? **This is the highest-value fix.** Offer to fill both in — ask what the wiki is about
  and propose a taxonomy for it. Until the domain is declared, the abstention rule makes the agent
  decline most questions.
- Run `python3 scripts/lint_wiki.py` and report the result.

## 4. Permissions tip

Mention — **scoped to this wiki repo only** — that bypass-permissions mode removes the constant
approval prompts a wiki triggers (many file writes), and that it's low-risk here because wiki
operations execute no code. Make clear it does **not** extend to code repositories.

## Report

Short table: check → status → fix. Lead with anything actually broken; if the only gap is the unset
Domain, say so plainly and offer to fix it now.
