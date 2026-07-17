# AGENTS.md — entry point for agents

You are working inside an **LLM wiki** — a durable, interlinked Markdown knowledge base.
**This repository is the wiki: the repo root is the wiki root.** This file is a router, not
an encyclopedia — read what the task needs, don't load everything.

## Routes

| Task | Where |
|---|---|
| Conventions, frontmatter, tag taxonomy | `SCHEMA.md` |
| Find existing pages | `index.md` |
| The rules that keep the wiki trustworthy | `PRINCIPLES.md` |
| Available commands | `.claude/commands/wiki-*.md` |
| Recommended skills to install | `RECOMMENDED-SKILLS.md` |
| Optional local search (rg + qmd) | `docs/search-qmd.md` |

## Rules (mandatory)

1. **This repo is the wiki.** The repo root is the wiki root. Content lives in `raw/` (immutable sources) and `entities/ concepts/ comparisons/ queries/` (compiled pages).
2. **Orient before acting.** Read `SCHEMA.md`, `index.md`, and the recent `log.md` before ingesting, querying, or editing. This prevents duplicates and missed cross-references.
3. **`raw/` is immutable.** Read it; never rewrite it. Corrections live in compiled pages, not in sources.
4. **Provenance is required.** Every compiled page carries frontmatter (`created`, `updated`, `type`). A claim with no source is a hypothesis, not a fact — mark it `confidence: low`.
5. **Contradictions are not overwritten.** Found a conflict? Record both versions with dates and sources; mark `contested: true` / `contradictions: […]`. Never silently pick the newer one.
6. **Cross-reference and log.** Every new or updated page links to ≥2 others via `[[wikilinks]]`, is added to `index.md`, and is recorded in `log.md`.
7. **Declare scope, then abstain.** If a question is outside the wiki's domain (`SCHEMA.md`) or a page is stale, go to the primary source — don't over-answer from thin coverage.
8. **No secrets.** No tokens, credentials, or private data in the repo.

## Search

- Default: `rg` (ripgrep) across the repo — instant, always fresh.
- Semantic ("where/how is X" without knowing the term): optional `qmd` daemon — see `docs/search-qmd.md`. Not a dependency; don't spin it up for a single lookup.

## Skills

- **`llm-wiki`** (`.claude/skills/llm-wiki/`) — the core skill: ingest, query, lint. Activates on "add to wiki", "ingest", or a `/wiki-*` command.
- **`youtube-content`** (`.claude/skills/youtube-content/`) — pull a YouTube transcript as a source for the wiki.
- **Recommended set** (Superpowers, Matt Pocock, find-skills, …) — run `/wiki-doctor`; it checks your setup and helps install them.
