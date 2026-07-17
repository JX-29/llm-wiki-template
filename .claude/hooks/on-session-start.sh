#!/usr/bin/env bash
# SessionStart hook — first-run onboarding.
#
# On a FRESH wiki (Domain still unset in SCHEMA.md), remind the agent to onboard the user
# in the chat instead of pointing at a document. Goes silent as soon as the wiki has a real
# domain, so it never nags an established wiki.
#
# Always exits 0 — a hook must never block a session.
set +e

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# Not a fresh wiki? Say nothing.
grep -q "Replace this line" "$ROOT/SCHEMA.md" 2>/dev/null || exit 0

cat <<'EOF'
[llm-wiki · first run] This wiki is still a fresh template — the Domain in SCHEMA.md is not set,
so the user has just created it from the template and does not yet know how it works.

On your first reply: onboard them IN THE CHAT. Do not answer with a link to a document.
Cover briefly: (1) what this repo is — their knowledge base, maintained in Markdown;
(2) that they can talk in plain language OR use /wiki-* slash commands — show the command table
inline; (3) the first step — set Domain + Tag Taxonomy in SCHEMA.md, or ingest a first source.

The skills are already vendored in .claude/skills/ — nothing to install; don't send them shopping.
Full protocol: CLAUDE.md -> "First-run onboarding".
EOF

exit 0
