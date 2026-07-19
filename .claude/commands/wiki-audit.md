---
description: Audit the wiki for contradictions, stale pages, orphans, and weak claims
---

Audit this wiki along two layers.

## 1. Deterministic — run the linter

```bash
python3 scripts/lint_wiki.py            # add --root <path> to audit an external vault

```

It reports broken `[[wikilinks]]`, broken relative links, missing frontmatter, stale pages, orphans, and oversized pages. Fix every `E*` error.

## 2. Semantic — agent pass

Scan the compiled pages for:

- **Contradictions** — pages sharing tags/entities that state different facts. Mark `contested: true` + `contradictions: […]`, keep both versions with dates/sources. Never silently pick one.
- **Superseded claims** — a newer source overrides an older page. Update it, preserve the history.
- **Weak claims** — `confidence: low`, or single-source pages with no confidence field. Flag for corroboration.
- **Scope drift** — pages outside the domain declared in `SCHEMA.md`.

Report findings grouped by severity (broken links > contradictions > stale > weak). Append a `## [YYYY-MM-DD] lint | N issues` entry to `log.md`.
