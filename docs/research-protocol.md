# Research protocol — from question to captured knowledge

The rule this document exists for: **any substantial research ends inside the wiki, with
its sources — automatically, not on request.** A finding that lives only in a chat
transcript will be re-derived, badly, three weeks later.

This is the engine-level protocol; it applies to every wiki built on this template
(and to Hermes-numbered vaults served by the same skill). Personal engine choices
(which CLI, which subscriptions) belong in the operator's own notes, not here.

## 1. Triage — pick the engine for the task class

| Task class | Engine | Output |
|---|---|---|
| Deep multi-source question | deep-research harness / `/wiki-research` | cited findings + raw dumps in the wiki |
| Quick cited compile of a few pages | `/wiki-research` | compiled page + sources |
| Known product / docs corpus | source-first ingestion (see ladder below) | corpus with manifest + compiled pages |
| Repository / codebase investigation | repo-inspection agent (e.g. Codex, read-only) | evidence with file/line refs |
| Bulk or multimodal digestion (long video, PDF piles) | large-context model executor (e.g. Gemini API) | normalized summaries → capture |
| Feed / newsletter sweep | feed reader (e.g. Folo) | selected items → `/wiki-ingest` |

One question may chain engines; whatever the chain, it ends at step 3.

## 2. Discovery ladder — stop at the first sufficient rung

1. **Local first.** Search the wiki (`rg`, index, optional qmd — `docs/search-qmd.md`).
   The answer may already be captured; re-fetching what you own is the original sin.
2. **Source-native inventory.** `llms.txt`, sitemap, RSS/Atom, OpenAPI spec, repo
   tags/releases. Publishers often hand you the complete corpus — take it instead of
   crawling.
3. **Web search** — only for URLs the inventory didn't surface.
4. **Direct conditional HTTP** for the chosen originals: keep raw bytes + headers,
   record `sha256`; on refresh use `ETag`/`Last-Modified` instead of re-downloading.

Search snippets and AI-generated answers are **routing hints, not evidence** — a claim
becomes high-confidence only against the original it led to. Publication date,
retrieval date, and version are three different fields; never conflate them.

## 3. Capture contract — the mandatory finish

- **Raw source** → the wiki's sources layer, with frontmatter (`source_url`,
  `ingested`, `sha256`). Immutable once written.
- **Compiled page(s)** → per `SCHEMA.md`: ≥2 `[[wikilinks]]`, tags from the taxonomy,
  `confidence:` set honestly for single-source or fast-moving claims.
- **Contradictions** are recorded, dated, with both sources — never silently resolved
  in favor of the newer claim.
- **Index and log updated**; lint passes (`scripts/lint_wiki.py`).
- **No secrets in the wiki, ever** — keys and tokens live in a secret manager; the wiki
  records secret *names* and owners at most.
- Curate: trivial lookups and dead ends are not captured (log-only if worth a trace).

## 4. Multi-agent boundary

- **One writer per wiki.** Exactly one agent writes pages (plus the vault's resident
  agent where one exists, e.g. Hermes on a shared vault). Everyone else is read-only.
- **Delegates return evidence, not pages.** A reviewer, searcher, or bulk processor
  hands back findings with provenance; the writer decides what enters the wiki.
- **Delegation is a contract:** goal, scope, non-scope, output schema, timeout. A
  result without provenance is an opinion.

Related: `docs/search-qmd.md` (local retrieval), `docs/ingest-media.md` (media
corpora), `PRINCIPLES.md` (why the wiki stays trustworthy).
