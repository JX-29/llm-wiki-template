# llm-wiki-template

**A knowledge base your AI agent maintains for you.** Click **Use this template**, get your own
private wiki, and start filling it — the agent handles the structure, the linking, and the
consistency. Domain-agnostic: ML research, medicine, a product, a hobby — whatever you're learning.

🇷🇺 [Русская версия — README.ru.md](README.ru.md)

---

## Why

A chat forgets. Ordinary RAG re-reads everything from scratch on every question. An **LLM wiki**
compiles what you learn **once** into linked Markdown pages and keeps them current — so future
questions read from compiled knowledge, with the contradictions already flagged and the sources
already attached. You curate what matters; the agent summarizes, cross-references, and files.

It's just Markdown files in a git repo. Open them in Obsidian, VS Code, or any editor. No database.

## Quick start

1. Click **Use this template** → **Create a new repository** → choose **Private**.
2. Clone it and open the folder in [Claude Code](https://claude.com/claude-code).
3. Say hello — the agent onboards you in the chat. (Or run **`/wiki-doctor`** to check the setup.)
4. Open **`SCHEMA.md`** and fill in your **Domain** and **Tag Taxonomy**.
5. Ingest your first source: **`/wiki-ingest <url>`**. Then read `concepts/how-this-wiki-works.md` and delete it.

## What's inside

```
raw/           # immutable sources (articles, papers, transcripts, assets) — the agent never rewrites these
entities/      # compiled pages: people, orgs, products, models
concepts/      # compiled pages: topics and ideas
comparisons/   # side-by-side analyses
queries/       # filed answers worth keeping
SCHEMA.md      # conventions, frontmatter, tag taxonomy  ← edit this first
index.md       # the catalog of every page
log.md         # append-only history
PRINCIPLES.md  # the seven rules that keep the wiki trustworthy
.claude/       # the agent harness: vendored skills + /wiki-* commands
scripts/       # lint_wiki.py (also runs in CI) + vendor-skill.sh
```

## Commands

| Command | What it does |
|---|---|
| `/wiki-ingest <url\|file>` | Save a source into `raw/` and file the distilled knowledge |
| `/wiki-research <question>` | Research the open web, dump raw sources, compile cited findings |
| `/wiki-capture` | Persist finished research as a durable, curated finding |
| `/wiki-audit` | Scan for contradictions, stale pages, orphans, weak claims |
| `/wiki-learn <topic>` | Turn the wiki into a Markdown lesson (in-chat, no HTML) |
| `/wiki-doctor` | Check setup and install the recommended skills |
| `/wiki-update` | Pull engine updates from this template without touching your notes |

You can also just say *"add this to my wiki"* — the `llm-wiki` skill activates on its own.

## Skills — included, nothing to install

The agent skills ship **inside the repo** (`.claude/skills/`), so a fresh copy works immediately:

`llm-wiki` (the core) · `youtube-content` (YouTube → transcript) · `notebooklm-source-corpus`
(local media → Markdown corpus) · `research` (primary-source investigation) · `grilling`
(stress-test a plan) · `domain-modeling` (build your glossary) · `writing-shape` / `writing-beats` /
`writing-fragments` (prose).

All MIT — see [THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md). Only `notebooklm-source-corpus`
needs anything external (the NotebookLM CLI). Optional extras:
[RECOMMENDED-SKILLS.md](RECOMMENDED-SKILLS.md).

## Principles

Seven domain-agnostic rules — primary sources, explicit provenance, freshness, one-idea pages,
recorded contradictions, human curation, and scope/abstention. See **[PRINCIPLES.md](PRINCIPLES.md)**.

## Search

`rg` (ripgrep) over the repo is the default — instant and always fresh. For large wikis, an optional
local semantic layer (qmd) is described in [docs/search-qmd.md](docs/search-qmd.md). Not a dependency.

## Staying current

This is a template, so its history is detached — updates don't merge automatically. `/wiki-update`
pulls engine changes (skills, commands, linter, principles) from upstream **without touching your notes**.

## Obsidian

The repo is already a valid Obsidian vault — open the folder, and `[[wikilinks]]` + graph view just
work. A minimal `.obsidian/app.json` points attachments at `raw/assets/`; the rest of `.obsidian/` is
gitignored so your per-machine state stays out of the repo.

## License

MIT — see [LICENSE](LICENSE). This template vendors two MIT skills from
[Hermes Agent](https://github.com/NousResearch/hermes-agent); see
[THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md).
