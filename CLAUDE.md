@AGENTS.md

## First-run onboarding — do this before anything else

If this wiki is still fresh — `SCHEMA.md` still contains "Replace this line" in **Domain**, or the
only content page is `concepts/how-this-wiki-works.md` — then the user just created it from the
template and **does not know how it works yet**.

On your first reply, **teach them in the chat**. Do **not** answer with a link to a document, and do
not send them off to read a file. Speak their language.

Lead with a short, concrete orientation:

1. **What this is** — one line: *"This repository is your knowledge base — I maintain it for you in Markdown: sources in `raw/`, compiled pages linked together, every claim traceable."*
2. **How to talk to me** — say **both** ways explicitly:
   - **Plain language** (the normal way): *"add this to my wiki"*, *"what do we know about X?"*, *"research Y and save it with sources"*.
   - **Slash commands** — typed with a leading `/` in the chat; they're shortcuts for the standard workflows. **Show the table below inline** — don't link to it.
3. **The first step** — ask what the wiki is about, then offer to fill in **Domain** and **Tag Taxonomy** in `SCHEMA.md`; or take a first source immediately with `/wiki-ingest <url>`.

Spell the commands out — this is what to show:

| Command | What it does |
|---|---|
| `/wiki-ingest <url\|file>` | Save a source into `raw/` and file the distilled knowledge |
| `/wiki-research <question>` | Research the web, save raw sources, compile cited findings |
| `/wiki-capture` | Persist finished research as a curated finding |
| `/wiki-audit` | Find contradictions, stale pages, orphans, weak claims |
| `/wiki-learn <topic>` | Turn the wiki into a Markdown lesson |
| `/wiki-doctor` | Check the setup |
| `/wiki-update` | Pull engine updates from the template |

Keep it to a screen, not an essay. Then stop and let them steer. `concepts/how-this-wiki-works.md`
is a written reference for later — it is **not** a substitute for onboarding them yourself.

## Skills — already in this repo

They are **vendored into `.claude/skills/`**: a fresh copy of this template already has them, with
nothing to install. Reach for them by name; don't tell the user to go install skills.

| Skill | Use |
|---|---|
| `llm-wiki` | The core: ingest, query, lint, maintain the wiki |
| `youtube-content` | YouTube transcript → a source in `raw/` |
| `notebooklm-source-corpus` | A local video/audio/PDF folder → Markdown corpus (needs the NotebookLM CLI) |
| `research` | Investigate a question against primary sources |
| `grilling` | Stress-test a plan or a wiki's structure before committing to it |
| `domain-modeling` | Build the wiki's ubiquitous language / glossary |
| `writing-shape`, `writing-beats`, `writing-fragments` | Write and edit the wiki's prose |

Only `notebooklm-source-corpus` has an external dependency (the NotebookLM CLI). Everything else
works out of the box.

## Claude Code specifics

- **Permissions.** This is a Markdown-only knowledge base — wiki operations execute no code, so the
  constant approval prompts add friction without protecting much. For a **dedicated wiki repo** it's
  reasonable to run `claude --dangerously-skip-permissions` so pages can be written without
  interruption. This is **scoped to this wiki repo** — don't carry it into code repositories.
- **Markdown-first.** Everything happens in Markdown and in chat. `/wiki-learn` lessons are Markdown
  files in `lessons/`, never generated HTML.
