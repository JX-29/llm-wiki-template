---
description: Research a question on the open web, save raw sources, and compile cited findings
argument-hint: <research question>
---

Research this question and compile the findings into the wiki:

$ARGUMENTS

Steps:

1. **Fan out over primary sources** using WebSearch / WebFetch (and the browser if available). Prefer official docs, papers, specs, and first-party APIs over secondary write-ups.
2. **Save each source you rely on** as a full raw dump under `raw/articles/` or `raw/papers/`, with frontmatter (`source_url`, `ingested`, `sha256`). This is the "save the raw source" step — don't keep only your summary.
3. **Follow every claim back** to the party that owns it, and cite each claim.
4. **Distil** the findings into compiled pages via the `/wiki-capture` importance gate and the `llm-wiki` skill: concept / comparison / query pages with ≥2 `[[wikilinks]]` and provenance markers.
5. **Update** `index.md` and `log.md`.

Respect freshness (Principle 3): date volatile claims and note what should be re-verified later. If the question is outside this wiki's domain (`SCHEMA.md`), say so before filing anything.
