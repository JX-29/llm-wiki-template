---
description: Ingest a source (URL, file, or pasted text) into the wiki
argument-hint: <url | filepath | "pasted text">
---

Ingest the following source into this wiki (the repo root is the wiki root):

$ARGUMENTS

Use the `llm-wiki` skill's ingest flow:

1. Save the raw source under `raw/` (articles / papers / transcripts) with frontmatter: `source_url`, `ingested`, `sha256` (over the body only). If it's a YouTube URL, use the `youtube-content` skill to fetch the transcript first, then save that.
2. Orient: read `SCHEMA.md`, `index.md`, and grep the wiki for the entities/concepts mentioned — don't create duplicates.
3. Create or update compiled pages (`entities/ concepts/ comparisons/ queries/`) per `SCHEMA.md`, each with ≥2 `[[wikilinks]]` and provenance to the raw source.
4. Update `index.md` (add new pages, bump the count/date) and append an `ingest` entry to `log.md`.
5. Report every file you created or updated.
