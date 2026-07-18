---
title: How this wiki works
created: 2026-07-16
updated: 2026-07-16
type: concept
tags: [meta]
---

# How this wiki works

This is a starter page. Read it, then **delete it** (and remove its line from [[index]]) once your own pages exist.

## The idea

This repository is an **LLM wiki**: a knowledge base your AI agent maintains for you. Unlike a chat that forgets, the wiki *compiles* what you learn once and keeps it linked and current, so future questions read from compiled knowledge instead of researching from scratch.

**Division of labour:** you curate sources and decide what matters; the agent summarizes, cross-references, files, and keeps things consistent. See the conventions in [[SCHEMA]].

## Two layers

1. **Raw** (`raw/`) — immutable source material. The agent reads it but never rewrites it.
2. **Compiled** (`entities/ concepts/ comparisons/ queries/`) — linked pages the agent writes and maintains.

`SCHEMA.md`, `index.md`, and `log.md` are the backbone: the rules, the catalog, and the append-only history.

## How you use it

Talk to your agent (Claude Code). The commands:

| Command | What it does |
|---|---|
| `/wiki-ingest <url\|file>` | Save a source into `raw/` and file the distilled knowledge into pages |
| `/wiki-research <question>` | Research the open web, dump raw sources, then compile cited findings |
| `/wiki-capture` | Persist a finished piece of research as a durable, curated finding |
| `/wiki-audit` | Scan for contradictions, stale pages, orphans, weak claims |
| `/wiki-learn <topic>` | Turn the wiki into a Markdown lesson that teaches you the topic |
| `/wiki-doctor` | Check your setup and install the recommended skills |
| `/wiki-update` | Pull engine updates from the template without touching your notes |

You can also just say *"add this to my wiki"* — the `llm-wiki` skill activates on its own.

## First steps

1. Open `SCHEMA.md` and fill in the **Domain** and **Tag Taxonomy** for your subject.
2. Ingest your first source: `/wiki-ingest <url>`.
3. Optional: `/wiki-doctor` checks the setup. The skills already ship in `.claude/skills/` — there's nothing to install.
4. Read `PRINCIPLES.md` once — the seven rules that keep the wiki trustworthy. _(It's a repo doc, not a wiki page, so it isn't linked with `[[wikilinks]]`.)_

## Long-running projects: keep state in the wiki, not in chat

If this wiki backs an ongoing project — one that spans many sessions, agents, or machines — put the
project's live state in a **page** (a `queries/` entry works well): what's decided, where the work
stands, what's next, and pointers to the source-of-truth files. It survives session compaction, a
folder rename, and a handoff between agents (Claude, Codex, Hermes all read the same page). Session
memory does none of that — it's keyed to one folder path and one agent. The wiki is the durable
place; use it.

## The rules that matter most

- Every claim traces to a source. A fact without a source is a hypothesis.
- One page, one idea. Link generously with `[[wikilinks]]`.
- Contradictions are recorded, not overwritten.
- The wiki declares its scope and abstains outside it — it goes to the source rather than guess.

Full set: [[SCHEMA]] and the repository's `PRINCIPLES.md`.
