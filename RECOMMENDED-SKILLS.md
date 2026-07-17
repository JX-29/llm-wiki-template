# Recommended skills

This template ships a small **vendored core** (see `.claude/skills/`). Everything else is
installed **on demand** so the repo stays light and each third-party skill keeps its own license.
Run `/wiki-doctor` and it will walk you through the recommended tier.

## Vendored (already in this repo)

| Skill | What it does | License |
|---|---|---|
| `llm-wiki` | The core: ingest, query, lint, maintain the wiki | MIT (Hermes Agent) |
| `youtube-content` | Fetch a YouTube transcript as a source | MIT (Hermes Agent) |

Plus the `/wiki-*` commands in `.claude/commands/`.

## Recommended (strongly recommended — install these)

These bring the process discipline that makes an agent-maintained wiki reliable. `/wiki-doctor`
checks for them and offers install commands. They're recommendations, not hard requirements —
the wiki works with just the vendored core, but these make it noticeably better.

| Skill | What it adds | Install |
|---|---|---|
| **Superpowers** | Brainstorming, TDD, systematic debugging, planning discipline | Plugin marketplace (`obra/superpowers`) |
| **Matt Pocock skills** | The `grill → spec → tickets → implement` flow + writing/domain skills | `npx skills` or `setup-matt-pocock-skills` |
| **find-skills** | Discover and install more skills as your wiki grows | via the skills manager |

> Note: Superpowers and Matt Pocock **overlap** (both include planning / TDD / grilling). That's
> fine — pick the one you reach for, or install both and let `/wiki-doctor` explain the roles.

## Optional (install if your sources call for it)

| Skill | Use case | Note |
|---|---|---|
| `arxiv` (Hermes) | Search & pull arXiv papers | academic sources |
| `scrapling` (Hermes) | Spider a whole site, stealth fetch, Cloudflare bypass | heavy deps (headless browser) |
| `gitnexus-explorer` (Hermes) | Index a whole repository into a knowledge graph | for capturing codebases |
| `searxng-search` / `duckduckgo-search` (Hermes) | Keyless web search | fallback if you lack a WebSearch tool |
| `notebooklm-source-corpus` / `nlm-skill` | Turn local media/PDF folders into a Markdown corpus | needs NotebookLM (Google auth) |
| `obsidian-vault` / `note-taking/obsidian` | Deeper Obsidian integration | the wiki already opens as an Obsidian vault without it |

Hermes skills live in the [Hermes Agent](https://github.com/NousResearch/hermes-agent) repo
(`skills/` and `optional-skills/`), MIT-licensed.
