#!/usr/bin/env python3
"""Deterministic wiki linter — canon invariants, no LLM.

The wiki lives at the repository root. Content pages are the *.md files under
entities/ concepts/ comparisons/ queries/ (plus raw/ sources and the root meta
files SCHEMA.md / index.md / log.md). Repo docs (README, PRINCIPLES, AGENTS, …)
are NOT wiki pages and are not linted.

Checks:
  E1  broken [[wikilinks]] (target missing as path or filename)
  E2  broken relative ](*.md) links
  E3  missing required frontmatter fields (created, updated, type)
  W1  staleness: `updated` older than --max-age-days (default 180)
  W2  orphans: a content page with no inbound [[wikilink]]
  W3  page longer than 200 lines — split candidate

Exit 1 on any E*; W* are warnings (--strict promotes them to errors).
Usage: python3 scripts/lint_wiki.py [--strict] [--max-age-days N]
"""
import argparse
import datetime
import pathlib
import re
import sys

try:
    import yaml
except ImportError:  # graceful fallback — CI installs pyyaml
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT_DIRS = ["entities", "concepts", "comparisons", "queries", "raw"]
ROOT_META = {"index.md", "log.md", "SCHEMA.md"}
REQUIRED = ["created", "updated", "type"]

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
MDLINK = re.compile(r"\]\((?!https?://|mailto:|#)([^)#\s]+\.md)")
FENCED = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")


def strip_code(text: str) -> str:
    """Links inside fenced or `inline` code are examples, not real links."""
    return INLINE_CODE.sub("", FENCED.sub("", text))


def frontmatter(text: str):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    if yaml:
        try:
            data = yaml.safe_load(block)
            return data if isinstance(data, dict) else None
        except yaml.YAMLError:
            return None
    data = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data


def collect_pages():
    pages = [ROOT / n for n in ROOT_META if (ROOT / n).exists()]
    for d in CONTENT_DIRS:
        pages += list((ROOT / d).rglob("*.md"))
    return pages


def is_exempt(p: pathlib.Path) -> bool:
    """raw sources and root meta are link targets but skip frontmatter/orphan/size."""
    return p.name in ROOT_META or "raw" in p.relative_to(ROOT).parts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="promote warnings to errors")
    ap.add_argument("--max-age-days", type=int, default=180)
    args = ap.parse_args()

    pages = collect_pages()
    by_stem: dict[str, list] = {}
    for p in pages:
        by_stem.setdefault(p.stem.lower(), []).append(p)
        rel = p.relative_to(ROOT).with_suffix("").as_posix().lower()
        by_stem.setdefault(rel, []).append(p)

    errors: list[str] = []
    warnings: list[str] = []
    inbound = {p: 0 for p in pages}
    today = datetime.date.today()

    for p in pages:
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(ROOT)
        linkable = strip_code(text)

        for m in WIKILINK.finditer(linkable):
            target = m.group(1).strip().lower()
            hits = by_stem.get(target) or by_stem.get(target.split("/")[-1])
            if hits:
                for h in hits:
                    if h != p:
                        inbound[h] = inbound.get(h, 0) + 1
            else:
                errors.append(f"E1 {rel}: broken wikilink [[{m.group(1).strip()}]]")

        for m in MDLINK.finditer(linkable):
            target = (p.parent / m.group(1)).resolve()
            if not target.exists():
                errors.append(f"E2 {rel}: broken link ]({m.group(1)})")

        if is_exempt(p):
            continue

        fm = frontmatter(text)
        if fm is None:
            errors.append(f"E3 {rel}: no frontmatter")
            continue
        missing = [k for k in REQUIRED if k not in fm]
        if missing:
            errors.append(f"E3 {rel}: missing field(s) {', '.join(missing)}")

        upd = fm.get("updated")
        if upd:
            try:
                d = datetime.date.fromisoformat(str(upd)[:10])
                age = (today - d).days
                if age > args.max_age_days:
                    warnings.append(f"W1 {rel}: updated {age} days ago (> {args.max_age_days})")
            except ValueError:
                warnings.append(f"W1 {rel}: unreadable `updated` date: {upd!r}")

        if len(text.splitlines()) > 200:
            warnings.append(f"W3 {rel}: {len(text.splitlines())} lines — split candidate")

    for p, count in inbound.items():
        if is_exempt(p):
            continue
        if count == 0:
            warnings.append(f"W2 {p.relative_to(ROOT)}: orphan (0 inbound wikilinks)")

    for e in errors:
        print(e)
    for w in warnings:
        print(w)
    print(f"\nPages: {len(pages)}; errors: {len(errors)}; warnings: {len(warnings)}")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
