#!/usr/bin/env bash
# Re-vendor the llm-wiki skill from a source checkout into this template.
#
# MAINTAINER tool — not for end users. Keeps .claude/skills/llm-wiki/ in sync with
# the upstream single-source so the vendored copy doesn't silently drift. The change
# is deterministic: `git diff .claude/skills/llm-wiki` shows exactly what moved.
#
# Usage:
#   SKILL_SRC=~/.agents/skills/llm-wiki bash scripts/vendor-skill.sh
#   # defaults SKILL_SRC to ~/.agents/skills/llm-wiki
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${SKILL_SRC:-$HOME/.agents/skills/llm-wiki}"
DST="$ROOT/.claude/skills/llm-wiki"

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "No SKILL.md at $SRC — set SKILL_SRC to your llm-wiki skill directory." >&2
  exit 1
fi

rm -rf "$DST"
mkdir -p "$DST"
cp -R "$SRC/." "$DST/"
find "$DST" -name ".DS_Store" -delete 2>/dev/null || true

echo "Vendored llm-wiki: $SRC -> $DST"
echo "Review 'git diff .claude/skills/llm-wiki' before committing."
