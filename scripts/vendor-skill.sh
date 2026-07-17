#!/usr/bin/env bash
# Re-vendor the skills bundled with this template from their upstream checkouts.
#
# MAINTAINER tool — not for end users. It keeps .claude/skills/ in sync with the upstream
# single-sources so the vendored copies don't silently drift, and it NORMALIZES machine-specific
# paths (a stranger who used this template has no ~/.agents/skills).
#
# Usage:
#   bash scripts/vendor-skill.sh                 # re-vendor everything
#   bash scripts/vendor-skill.sh llm-wiki        # re-vendor one skill
#   SKILLS_SRC=~/.agents/skills HERMES_SRC=~/src/hermes-agent bash scripts/vendor-skill.sh
#
# Run with bash (the shebang handles it) — zsh does not word-split the skill lists.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${SKILLS_SRC:-$HOME/.agents/skills}"
HERMES_SRC="${HERMES_SRC:-$HOME/Downloads/hermes-agent-main}"
DST="$ROOT/.claude/skills"
ONLY="${1:-}"

# Vendored from the single-source skills directory
FROM_AGENTS="llm-wiki notebooklm-source-corpus research grilling domain-modeling writing-shape writing-beats writing-fragments"
# Vendored from a Hermes Agent checkout (paths within that repo)
FROM_HERMES="skills/media/youtube-content"

vendor_dir() {
  local src="$1" name="$2"
  if [ ! -f "$src/SKILL.md" ]; then
    echo "  SKIP $name — no SKILL.md at $src" >&2
    return 0
  fi
  rm -rf "${DST:?}/$name"
  mkdir -p "$DST/$name"
  cp -R "$src/." "$DST/$name/"
  find "$DST/$name" -name ".DS_Store" -delete 2>/dev/null
  echo "  vendored $name"
}

sed_inplace() {
  # macOS sed needs an empty -i arg; GNU sed does not.
  if sed --version >/dev/null 2>&1; then sed -i "$@"; else sed -i '' "$@"; fi
}

echo "Vendoring skills into $DST"
for name in $FROM_AGENTS; do
  [ -n "$ONLY" ] && [ "$ONLY" != "$name" ] && continue
  vendor_dir "$SRC/$name" "$name"
done
for path in $FROM_HERMES; do
  name="$(basename "$path")"
  [ -n "$ONLY" ] && [ "$ONLY" != "$name" ] && continue
  vendor_dir "$HERMES_SRC/$path" "$name"
done

# Normalize machine-specific paths — the end user has no ~/.agents/skills.
echo "Normalizing machine-specific paths..."
grep -rIl -e '\.agents/skills/' "$DST" 2>/dev/null | while read -r f; do
  sed_inplace -E 's#(~/|\$HOME/)?\.agents/skills/#.claude/skills/#g' "$f"
  echo "  normalized $(basename "$(dirname "$f")")/$(basename "$f")"
done

echo
echo "Leak check (machine-specific paths must not survive):"
if grep -rIn -e '/Users/' -e '\.agents/' "$DST" 2>/dev/null; then
  echo "  ^^ FIX THESE before committing"
  exit 1
else
  echo "  clean"
fi
echo "Review 'git diff .claude/skills' before committing."
