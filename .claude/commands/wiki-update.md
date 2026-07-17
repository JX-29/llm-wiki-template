---
description: Pull engine updates (skills, commands, linter) from the template upstream — without touching your notes
---

Update the wiki **engine** from the template upstream, leaving your **knowledge** (notes, `index.md`, `log.md`, and your `SCHEMA.md` domain edits) untouched.

Because this repo was created with "Use this template", its history is detached from the template — so there's no automatic merge. Do it explicitly:

1. **Add the upstream remote once** (if you haven't):
   ```bash
   git remote add upstream https://github.com/JX-29/llm-wiki-template.git
   ```
   (Replace with the repository you templated from.)
2. **Fetch it:** `git fetch upstream`.
3. **Update only engine files** — never the user's content:
   ```bash
   git checkout upstream/main -- \
     .claude/ scripts/ .github/ docs/ \
     AGENTS.md CLAUDE.md PRINCIPLES.md PRINCIPLES.ru.md \
     RECOMMENDED-SKILLS.md THIRD-PARTY-LICENSES.md README.md README.ru.md
   ```
   Do **not** check out `SCHEMA.md`, `index.md`, `log.md`, or anything under `raw/ entities/ concepts/ comparisons/ queries/ lessons/` — those hold the user's knowledge and domain edits.
4. **Review** `git diff --staged`, keep what's intentional, commit.
5. **Re-lint:** `python3 scripts/lint_wiki.py` to confirm the wiki still passes.

If `SCHEMA.md`'s conventions changed upstream, apply them by hand so you keep your Domain and Tag Taxonomy.
