# Wiki Schema

> The conventions that keep this wiki consistent and machine-navigable.
> **This whole repository is your wiki** — the repo root is the wiki root.
> Edit the **Domain** and **Tag Taxonomy** sections to fit your subject, then start ingesting.

## Domain

<!-- One or two sentences: what this wiki covers. Replace this line. -->
_e.g._ "AI/ML research", "personal health", "startup intelligence", "home renovation".

## Layers

- `raw/` — **immutable source material** (articles, papers, transcripts, assets). The agent reads but never rewrites these.
- `entities/ concepts/ comparisons/ queries/` — **compiled knowledge**: agent-owned, cross-referenced Markdown pages.
- `SCHEMA.md` (this file), `index.md` (catalog), `log.md` (append-only action log) — the navigational backbone.

## Conventions

- File names: lowercase, hyphens, no spaces (e.g. `transformer-architecture.md`).
- Every wiki page starts with YAML frontmatter (see below).
- Use `[[wikilinks]]` to link between pages — **minimum 2 outbound links per page**. Isolated pages are invisible.
- When updating a page, always bump `updated`.
- Every new page is added to `index.md` under its section (alphabetical).
- Every action is appended to `log.md`.
- **Provenance markers:** on pages that synthesize 3+ sources, append `^[raw/articles/source-file.md]` to paragraphs whose claims trace to a specific source. Optional when a single `sources:` entry already covers the page.

## Frontmatter

```yaml
---
title: Page Title
created: YYYY-MM-DD          # required
updated: YYYY-MM-DD          # required — bump on every edit
type: entity | concept | comparison | query | summary   # required
tags: [from taxonomy below]  # recommended
sources: [raw/articles/source-name.md]   # recommended
# Optional quality signals:
confidence: high | medium | low   # how well-supported the claims are
contested: true                   # unresolved contradictions on this page
contradictions: [other-page-slug] # pages this one conflicts with
---
```

`created`, `updated`, and `type` are enforced by the linter. `confidence` and `contested` are optional but recommended for opinion-heavy or fast-moving topics — the linter surfaces `contested: true` and `confidence: low` so weak claims don't silently harden into fact.

### `raw/` frontmatter

Raw sources get a small block so re-ingests can detect drift:

```yaml
---
source_url: https://example.com/article   # original URL, if any
ingested: YYYY-MM-DD
sha256: <hex digest of the body below the closing --->
---
```

The `sha256` (computed over the body only) lets a future re-ingest skip unchanged content and flag drift when it changed.

## Tag Taxonomy

<!-- Define 10–20 top-level tags for YOUR domain. Add a tag here BEFORE using it — this prevents tag sprawl. -->

_Example (AI/ML — replace with yours):_

- **Subjects:** model, architecture, benchmark, technique
- **People / Orgs:** person, company, lab, open-source
- **Meta:** comparison, timeline, controversy, prediction, open-question

Rule: every tag on a page must appear here. Need a new one? Add it here first, then use it.

## Page Thresholds

- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source.
- **Add to an existing page** when a source mentions something already covered.
- **DON'T create a page** for passing mentions or things outside the domain.
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links.
- **Archive a page** when fully superseded — move to `_archive/`, remove from `index.md`.

## Update Policy

When new information conflicts with existing content:

1. Check dates — newer sources generally supersede older ones.
2. If genuinely contradictory, keep **both** positions with dates and sources — never silently overwrite.
3. Mark it: `contested: true` and `contradictions: [page-name]`.
4. The linter and `/wiki-audit` surface it for review.

## Scope & abstention

Declare what this wiki covers (the Domain above). When a question falls outside that scope, or a page's `updated` date is stale, go to the primary source instead of over-answering from thin coverage. A wiki that knows its edges is trustworthy; one that guesses is not.
