# Skills

**Everything you need ships inside this repo.** The skills below are vendored into
`.claude/skills/`, so a fresh copy from the template works immediately — there is nothing to
install. `/wiki-doctor` verifies them; `/wiki-update` refreshes them from the template upstream.

## Included (vendored, ready to use)

| Skill | What it does | Upstream (MIT) |
|---|---|---|
| `llm-wiki` | The core: ingest, query, lint, maintain the wiki | Hermes Agent |
| `youtube-content` | YouTube transcript → a source in `raw/` | Hermes Agent |
| `notebooklm-source-corpus` | A local video/audio/PDF folder → Markdown corpus | Anton Tretakov |
| `research` | Investigate a question against primary sources | Matt Pocock |
| `grilling` | Stress-test a plan or design before committing to it | Matt Pocock |
| `domain-modeling` | Build the wiki's ubiquitous language / glossary | Matt Pocock |
| `writing-shape` · `writing-beats` · `writing-fragments` | Write and edit the wiki's prose | Matt Pocock |

Plus the `/wiki-*` commands in `.claude/commands/`. Attribution: `THIRD-PARTY-LICENSES.md`.

### The one external dependency

`notebooklm-source-corpus` drives **NotebookLM** for transcription/extraction, so it needs the
NotebookLM CLI and a Google account. Everything else works out of the box. If you don't do local
media, ignore it — `youtube-content` covers YouTube with a single pip dependency
(`youtube-transcript-api`).

## Optional extras (install only if your sources call for it)

Not vendored — install from their own sources, under their own licenses.

| Skill | Use case | Note |
|---|---|---|
| `arxiv` (Hermes) | Search & pull arXiv papers | for academic wikis |
| `scrapling` (Hermes) | Spider a whole site, stealth fetch, Cloudflare bypass | heavy deps (headless browser) |
| `gitnexus-explorer` (Hermes) | Index a whole repository into a knowledge graph | for capturing codebases |
| `searxng-search` / `duckduckgo-search` (Hermes) | Keyless web search | fallback if you have no WebSearch tool |
| `nlm-skill` | Lower-level NotebookLM CLI guide | companion to `notebooklm-source-corpus` |
| `obsidian-vault` | Deeper Obsidian integration | the wiki already opens as an Obsidian vault without it |

Hermes skills live in the [Hermes Agent](https://github.com/NousResearch/hermes-agent) repo
(`skills/`, `optional-skills/`), MIT-licensed. The full Matt Pocock set — including the software
engineering flow (`to-spec`, `to-tickets`, `implement`, `tdd`, `code-review`) that this wiki template
deliberately leaves out — is at [mattpocock/skills](https://github.com/mattpocock/skills).
