---
description: Persist a finished piece of research as a durable, curated wiki finding
argument-hint: [what you researched]
---

You just finished researching something. Decide **whether** and **what** to persist, then file it.

Context: $ARGUMENTS

## Step 1 — Importance gate

Capture only when ALL of these hold:

- (a) there's a reusable conclusion, or a source worth returning to;
- (b) re-deriving it later would cost real effort;
- (c) it fits this wiki's domain (`SCHEMA.md`);
- (d) it's not already here (grep + `index.md` to dedup).

Borderline → at most a one-line breadcrumb. If the gate fails → do nothing. Never persist trivial lookups, dead ends, or secrets.

## Step 2 — Capture via llm-wiki

Invoke the `llm-wiki` skill against this wiki:

1. Save any raw source under `raw/` (or the wiki's resolved sources dir — see the llm-wiki skill's layout resolution) with frontmatter (`source_url`, `ingested`, `sha256`). Redact secrets first.
2. **Distil** — never dump raw text as a "finding" — into concept / entity / comparison / query pages per `SCHEMA.md`, with ≥2 `[[wikilinks]]` and provenance.
3. Update `index.md` and `log.md`.

The judgement (whether / what) is the point of this command; `llm-wiki` handles the how.
