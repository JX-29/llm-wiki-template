---
name: llm-wiki
description: "Karpathy's LLM Wiki: build and maintain an interlinked markdown knowledge base. Use when the user asks to create a wiki/knowledge base, ingest a source (URL, PDF, pasted text) into their wiki, query it, or lint/audit it — including Russian phrasing (вики, база знаний, «добавь в вики»). The wiki structure is shared with Hermes Agent's llm-wiki skill: both agents maintain the same folder."
---

# Karpathy's LLM Wiki

Build and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on Andrej Karpathy's LLM Wiki pattern. Ported from the Hermes Agent `llm-wiki` skill
(v2.1.0, MIT). **The wiki data structure and conventions are identical to the Hermes version** —
Hermes and Claude Code can maintain the same wiki folder interchangeably. Do not diverge from
the conventions without updating both skills.

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki
compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**Division of labor:** The human curates sources and directs analysis. The agent
summarizes, cross-references, files, and maintains consistency.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base
- Asks to ingest, add, or process a source into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- References their wiki, knowledge base, or "notes" in a research context

## Wiki Location

**Location:** `WIKI_PATH` environment variable; if unset, defaults to `~/wiki`.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
```

**Path coordination with Hermes:** Hermes resolves `WIKI_PATH` from `~/.hermes/.env`;
Claude Code's Bash sees only the shell environment. If the user customizes the path, it must
be set in BOTH places (`~/.hermes/.env` and the shell profile) — otherwise the two agents
will silently maintain two different wikis. The safe default is to keep `~/wiki`.

The wiki is just a directory of markdown files — open it in Obsidian, VS Code, or
any editor. No database, no special tooling required.

**Multi-vault routing:** if `~/.agents/wikis.yaml` exists, it is the registry of the
user's wikis (name → path → domain). Route knowledge to the vault whose domain matches
the material; honor per-vault `capture: manual-only` flags. When this skill is vendored
inside a wiki repo (as in this template), that repo's root is the wiki root.

## Architecture: Three Layers

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams referenced by sources
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
└── queries/            # Layer 2: Filed query results worth keeping
```

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent.
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

### Layout dialects & resolution

The three layers are **logical**; physical folder names vary per wiki. The tree above is
the template-flat dialect. Known dialects:

| Logical layer | template-flat (default) | hermes-numbered (Hermes vaults) |
|---|---|---|
| Sources (immutable) | `raw/` | `02 Sources/` (plus `01 Inbox/`) |
| Compiled pages | `entities/ concepts/ comparisons/ queries/` | `03 Concepts/ 04 Entities/ 05 Comparisons/ 06 Queries/ 08 Workflows/` |
| Index | `index.md` | `00 Meta/Index.md` |
| Log | `log.md` | `00 Meta/Log.md` |

**Resolve the layout during orientation, before any read or write**, in priority order:

1. **Declared** — a `layout:` block in SCHEMA.md frontmatter (authoritative; this is how
   custom dialects are supported):

   ```yaml
   layout:
     sources:  ["02 Sources", "01 Inbox"]   # unchecked but linkable
     compiled: ["03 Concepts", "04 Entities", "05 Comparisons", "06 Queries", "08 Workflows"]
     index: "00 Meta/Index.md"
     log:   "00 Meta/Log.md"
   ```

2. **Detected** — `00 Meta/Index.md` exists → hermes-numbered; `index.md` at the wiki
   root → template-flat.
3. **Default** — template-flat (what this skill creates for new wikis).

Everywhere this skill says `raw/`, `index.md`, `log.md`, or names a compiled directory,
substitute the resolved paths. Never mix dialects inside one wiki; if resolution is
ambiguous, ask the user instead of guessing. `scripts/lint_wiki.py` resolves layouts the
same way — `--root` points it at any vault.

## Resuming an Existing Wiki (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

① **Read `$WIKI/SCHEMA.md`** — understand the domain, conventions, and tag taxonomy,
   and **resolve the layout** (see Layout dialects & resolution above).
② **Read `$WIKI/index.md`** — learn what pages exist and their summaries.
③ **Scan recent `$WIKI/log.md`** — read the last 20-30 entries (`tail -n 30 "$WIKI/log.md"`).

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick Grep for the topic at hand
before creating anything new.

## Initializing a New Wiki

When the user asks to create or start a wiki:

1. Determine the wiki path (from `$WIKI_PATH`, or ask the user; default `~/wiki`)
2. Create the directory structure above
3. Ask the user what domain the wiki covers — be specific
4. Write `SCHEMA.md` customized to the domain — read [TEMPLATES.md](TEMPLATES.md)
   for the SCHEMA.md, index.md, and log.md templates (byte-compatible with Hermes)
5. Write initial `index.md` with sectioned header
6. Write initial `log.md` with creation entry
7. Confirm the wiki is ready and suggest first sources to ingest

## Core Operations

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture the raw source:**
   - URL → WebFetch to get clean markdown (or the defuddle skill for cluttered pages),
     save to `raw/articles/`
   - PDF → download via Bash (`curl`), extract text with Read, save the extracted
     markdown to `raw/papers/` (keep the original PDF in `raw/assets/` if worth keeping)
   - Pasted text → save to the appropriate `raw/` subdirectory
   - Name the file descriptively: `raw/articles/karpathy-llm-wiki-2026.md`
   - **Add raw frontmatter** (`source_url`, `ingested`, `sha256` of the body — everything
     after the closing `---`; compute with `shasum -a 256` or python3 hashlib).
     On re-ingest of the same URL: recompute the sha256, compare to the stored value —
     skip if identical, flag drift and update if different.

② **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/headless contexts — proceed directly.)

③ **Check what already exists** — search `index.md` and Grep the wiki for mentioned
   entities/concepts. This is the difference between a growing wiki and a pile of duplicates.

④ **Write or update wiki pages:**
   - **New entities/concepts:** Create pages only if they meet the Page Thresholds
     in SCHEMA.md (2+ source mentions, or central to one source)
   - **Existing pages:** Add new information, update facts, bump `updated` date.
     When new info contradicts existing content, follow SCHEMA.md's Update Policy.
   - **Cross-reference:** Every new or updated page must link to at least 2 other
     pages via `[[wikilinks]]`. Check that existing pages link back.
   - **Tags:** Only use tags from the taxonomy in SCHEMA.md
   - **Provenance:** On pages synthesizing 3+ sources, append `^[raw/articles/source.md]`
     markers to paragraphs whose claims trace to a specific source.
   - **Confidence:** For opinion-heavy, fast-moving, or single-source claims, set
     `confidence: medium` or `low` in frontmatter. Don't mark `high` unless the
     claim is well-supported across multiple sources.

⑤ **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically
   - Update the "Total pages" count and "Last updated" date in the index header
   - Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
   - List every file created or updated in the log entry

⑥ **Report what changed** — list every file created or updated to the user.

A single source can trigger updates across 5-15 wiki pages. This is normal
and desired — it's the compounding effect.

### 2. Query

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also Grep across all `.md` files for key terms —
   the index alone may miss relevant content.
③ **Read the relevant pages.**
④ **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
⑤ **File valuable answers back** — if the answer is a substantial comparison,
   deep dive, or novel synthesis, create a page in `queries/` or `comparisons/`.
   Don't file trivial lookups — only answers that would be painful to re-derive.
⑥ **Update log.md** with the query and whether it was filed.

### 3. Lint

When the user asks to lint, health-check, or audit the wiki, run programmatic scans
(Bash + python3) across all wiki pages:

① **Orphan pages:** pages with no inbound `[[wikilinks]]` from other pages.
② **Broken wikilinks:** `[[links]]` pointing to pages that don't exist.
③ **Index completeness:** every wiki page should appear in `index.md`. Compare
   the filesystem against index entries.
④ **Frontmatter validation:** every wiki page must have all required fields
   (title, created, updated, type, tags, sources). Tags must be in the taxonomy.
⑤ **Stale content:** pages whose `updated` date is >90 days older than the most
   recent source mentioning the same entities.
⑥ **Contradictions:** pages sharing tags/entities but stating different facts.
   Surface all pages with `contested: true` or `contradictions:` frontmatter.
⑦ **Quality signals:** list pages with `confidence: low` and single-source pages
   with no confidence field — candidates for corroboration or demotion.
⑧ **Source drift:** for each `raw/` file with `sha256:` frontmatter, recompute the
   hash and flag mismatches (raw edited — shouldn't happen — or source URL changed).
⑨ **Page size:** flag pages over 200 lines — candidates for splitting.
⑩ **Tag audit:** list all tags in use, flag any not in the SCHEMA.md taxonomy.
⑪ **Log rotation:** if log.md exceeds 500 entries, rotate it (`log-YYYY.md`).
⑫ **Report findings** with specific file paths and suggested actions, grouped by
   severity (broken links > orphans > source drift > contested > stale > style).
⑬ **Append to log.md:** `## [YYYY-MM-DD] lint | N issues found`

## Working with the Wiki

### Searching

- Pages by content: Grep `pattern="transformer"`, `path=$WIKI`, `glob="*.md"`
- Pages by filename: Glob `pattern="**/*.md"`, `path=$WIKI`
- Pages by tag: Grep `pattern="tags:.*alignment"`, `path=$WIKI`, `glob="*.md"`
- Recent activity: `tail -n 20 "$WIKI/log.md"`

### Bulk Ingest

When ingesting multiple sources at once, batch the updates:
1. Read all sources first
2. Identify all entities and concepts across all sources
3. Check existing pages for all of them (one search pass, not N)
4. Create/update pages in one pass (avoids redundant updates)
5. Update index.md once at the end
6. Write a single log entry covering the batch

### Archiving

When content is fully superseded or the domain scope changes:
1. Create `_archive/` if it doesn't exist
2. Move the page to `_archive/` with its original path (e.g., `_archive/entities/old-page.md`)
3. Remove from `index.md`
4. Update pages that linked to it — replace wikilink with plain text + "(archived)"
5. Log the archive action

### Obsidian Integration

The wiki directory works as an Obsidian vault out of the box: `[[wikilinks]]` render as
clickable links, Graph View visualizes the network, YAML frontmatter powers Dataview.
Set Obsidian's attachment folder to `raw/assets/`. If using an Obsidian skill alongside
this one, point `OBSIDIAN_VAULT_PATH` at the same directory as the wiki.
(For headless/server sync setups, see the upstream Hermes skill's `obsidian-headless` section.)

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log before any operation in a new
  session. Skipping this causes duplicates and missed cross-references.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are
  the navigational backbone.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page
  must link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to
  SCHEMA.md first, then use them.
- **Keep pages scannable** — readable in 30 seconds. Split pages over 200 lines.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm scope.
- **Rotate the log** — when log.md exceeds 500 entries, rename to `log-YYYY.md`, start fresh.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with
  dates and sources, mark in frontmatter, flag for user review.

---

*Ported from Hermes Agent `skills/research/llm-wiki` v2.1.0 (MIT). Wiki structure must stay
compatible: a wiki maintained by Hermes is valid for this skill and vice versa. Extended
2026-07-19 with layout resolution — additive: a Hermes-numbered vault is served as-is,
with no changes required on the Hermes side.*
