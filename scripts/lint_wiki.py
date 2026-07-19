#!/usr/bin/env python3
"""Deterministic wiki linter — canon invariants, no LLM.

Lints the wiki at --root (default: this repository). The physical layout is
resolved per wiki, in priority order:

  1. `layout:` block in SCHEMA.md frontmatter (authoritative):
       ---
       layout:
         sources:  ["02 Sources", "01 Inbox"]   # unchecked but linkable dirs
         compiled: ["03 Concepts", "04 Entities"]
         index: "00 Meta/Index.md"
         log:   "00 Meta/Log.md"
       ---
  2. Detected dialect: `00 Meta/Index.md` exists → hermes-numbered
     (02 Sources/ + 03 Concepts/ 04 Entities/ 05 Comparisons/ 06 Queries/
      08 Workflows/, index and log under 00 Meta/; every non-hidden *.md in
      the tree is a valid wikilink target).
  3. Default: template-flat (raw/ + entities/ concepts/ comparisons/ queries/,
     index.md + log.md at the wiki root).

Only *compiled* pages are fully checked; sources and meta files are link
targets but skip frontmatter/orphan/size checks. Link validation (E1/E2)
runs only inside the governed set (sources + compiled + meta): archives,
projects and daily notes expand the valid-target universe and feed inbound
counts, but their own stale links do not fail the lint. Repo docs (README,
PRINCIPLES, AGENTS, …) are NOT wiki pages and are not linted in the flat
dialect. Markdown links may be URL-encoded (`%20`) or angle-bracketed
(`](<path with spaces.md>)`); asset embeds resolve page-relative,
root-relative, or by unique basename (Obsidian shortest-path).

Checks:
  E1  broken [[wikilinks]] (target missing as path or filename)
  E2  broken relative ](*.md) links
  E3  missing required frontmatter fields (created, updated, type)
  W0  layout looks misconfigured (no compiled dirs found — declare `layout:`)
  W1  staleness: `updated` older than --max-age-days (default 180)
  W2  orphans: a compiled page with no inbound [[wikilink]]
  W3  page longer than 200 lines — split candidate

Exit 1 on any E*; W* are warnings (--strict promotes them to errors).
Usage: python3 scripts/lint_wiki.py [--root PATH] [--strict] [--max-age-days N]
"""
import argparse
import dataclasses
import datetime
import pathlib
import re
import sys
import unicodedata
from urllib.parse import unquote

try:
    import yaml
except ImportError:  # graceful fallback — CI installs pyyaml
    yaml = None

DEFAULT_ROOT = pathlib.Path(__file__).resolve().parent.parent
FLAT_SOURCES = ["raw"]
FLAT_COMPILED = ["entities", "concepts", "comparisons", "queries"]
NUMBERED_SOURCES = ["01 Inbox", "02 Sources"]
NUMBERED_COMPILED = ["03 Concepts", "04 Entities", "05 Comparisons",
                     "06 Queries", "08 Workflows"]
REQUIRED = ["created", "updated", "type"]

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
# page titles legitimately contain dots ("GPT-5.6", "Next.js 16") — only these
# suffixes mark a wikilink as an asset embed rather than a page link
ASSET_EXT = re.compile(r"\.(png|jpe?g|gif|webp|svg|pdf|mp4|mov|mp3|wav|m4a|zip|csv|json|html?)$",
                       re.IGNORECASE)
MDLINK = re.compile(r"\]\((?!https?://|mailto:|#)([^)#\s]+\.md)")
MDLINK_ANGLE = re.compile(r"\]\(<(?!https?://|mailto:)([^>#]+\.md)>")
FENCED = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")


def strip_code(text: str) -> str:
    """Links inside fenced or `inline` code are examples, not real links."""
    return INLINE_CODE.sub("", FENCED.sub("", text))


def norm(s: str) -> str:
    """Filesystems and editors disagree on unicode normalization (NFC/NFD);
    wikilink matching must not."""
    return unicodedata.normalize("NFC", s).lower()


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


@dataclasses.dataclass
class Layout:
    mode: str
    sources: list
    compiled: list
    index: str
    log: str
    scan_all: bool = False  # numbered wikis link freely across the whole tree
    note: str = ""  # resolution caveat surfaced as a W0 warning

    @property
    def meta_files(self):
        return ["SCHEMA.md", self.index, self.log]

    @property
    def meta_dirs(self):
        dirs = {str(pathlib.PurePosixPath(f).parent) for f in (self.index, self.log)}
        return sorted(d for d in dirs if d != ".")


def resolve_layout(root: pathlib.Path) -> Layout:
    note = ""
    schema = root / "SCHEMA.md"
    if schema.exists():
        txt = schema.read_text(encoding="utf-8")
        fm = frontmatter(txt) or {}
        lay = fm.get("layout")
        if isinstance(lay, dict) and lay.get("index") and lay.get("log"):
            aslist = lambda v: [v] if isinstance(v, str) else list(v or [])
            # declared wikis link freely across their whole tree (projects,
            # archives, daily notes) — narrow the CHECKS, not the link universe
            return Layout("declared (SCHEMA.md)", aslist(lay.get("sources")),
                          aslist(lay.get("compiled")),
                          str(lay["index"]), str(lay["log"]), scan_all=True)
        # the naive no-yaml fallback cannot parse a nested layout block —
        # say so instead of silently linting the wrong dialect
        if yaml is None and txt.startswith("---"):
            end = txt.find("\n---", 3)
            if end != -1 and re.search(r"(?m)^layout:", txt[3:end]):
                note = ("SCHEMA.md declares `layout:` but PyYAML is unavailable — "
                        "install pyyaml; falling back to layout detection")
    if (root / "00 Meta" / "Index.md").exists():
        return Layout("hermes-numbered (detected)",
                      [d for d in NUMBERED_SOURCES if (root / d).is_dir()],
                      [d for d in NUMBERED_COMPILED if (root / d).is_dir()],
                      "00 Meta/Index.md", "00 Meta/Log.md", scan_all=True,
                      note=note)
    return Layout("template-flat (default)", FLAT_SOURCES, FLAT_COMPILED,
                  "index.md", "log.md", note=note)


def collect_pages(root: pathlib.Path, layout: Layout):
    if layout.scan_all:
        return [p for p in sorted(root.rglob("*.md"))
                if not any(part.startswith(".")
                           for part in p.relative_to(root).parts)]
    seen, pages = set(), []
    for name in layout.meta_files:
        p = root / name
        if p.exists() and p not in seen:
            seen.add(p)
            pages.append(p)
    for d in dict.fromkeys(layout.sources + layout.compiled + layout.meta_dirs):
        base = root / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if p not in seen:
                seen.add(p)
                pages.append(p)
    return pages


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None,
                    help="wiki root to lint (default: this repository)")
    ap.add_argument("--strict", action="store_true", help="promote warnings to errors")
    ap.add_argument("--max-age-days", type=int, default=180)
    args = ap.parse_args()

    root = (pathlib.Path(args.root).expanduser().resolve()
            if args.root else DEFAULT_ROOT)
    if not root.is_dir():
        print(f"error: root is not a directory: {root}")
        return 2
    layout = resolve_layout(root)
    pages = collect_pages(root, layout)
    compiled_dirs = [root / d for d in layout.compiled]
    governed_dirs = [root / d for d in
                     dict.fromkeys(list(layout.sources) + list(layout.compiled)
                                   + layout.meta_dirs)]
    meta_files_abs = {root / f for f in layout.meta_files}

    def is_checked(p: pathlib.Path) -> bool:
        return any(c in p.parents for c in compiled_dirs)

    def is_governed(p: pathlib.Path) -> bool:
        """E1/E2 fire only here; the rest of the tree is link targets only."""
        return p in meta_files_abs or any(d in p.parents for d in governed_dirs)

    asset_index = None

    def asset_by_name(name: str):
        """Obsidian shortest-path embeds ([[pic.png]]) resolve by basename."""
        nonlocal asset_index
        if asset_index is None:
            asset_index = {}
            for f in root.rglob("*"):
                if (f.is_file() and ASSET_EXT.search(f.name)
                        and not any(part.startswith(".")
                                    for part in f.relative_to(root).parts)):
                    asset_index.setdefault(norm(f.name), []).append(f)
        return asset_index.get(norm(name))

    by_stem: dict[str, list] = {}
    for p in pages:
        by_stem.setdefault(norm(p.stem), []).append(p)
        rel = p.relative_to(root).with_suffix("").as_posix()
        by_stem.setdefault(norm(rel), []).append(p)

    errors: list[str] = []
    warnings: list[str] = []
    inbound = {p: 0 for p in pages}
    today = datetime.date.today()

    if not any(d.is_dir() for d in compiled_dirs):
        warnings.append("W0 layout: no compiled dirs found for this dialect — "
                        "declare `layout:` in SCHEMA.md frontmatter")
    if layout.note:
        warnings.append(f"W0 layout: {layout.note}")

    for p in pages:
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(root)
        linkable = strip_code(text)

        for m in WIKILINK.finditer(linkable):
            raw_target = m.group(1).strip()
            if ASSET_EXT.search(raw_target):
                # asset embed ([[img.jpg]], [[doc.pdf]]) — not in the md index;
                # verify on disk: page-relative, root-relative, then basename
                if not ((p.parent / raw_target).exists()
                        or (root / raw_target).exists()
                        or asset_by_name(raw_target.rsplit("/", 1)[-1])):
                    if is_governed(p):
                        errors.append(f"E1 {rel}: broken asset wikilink [[{raw_target}]]")
                continue
            target = norm(raw_target)
            hits = by_stem.get(target) or by_stem.get(target.split("/")[-1])
            if hits:
                for h in hits:
                    if h != p:
                        inbound[h] = inbound.get(h, 0) + 1
            elif is_governed(p):
                errors.append(f"E1 {rel}: broken wikilink [[{raw_target}]]")

        for m in list(MDLINK.finditer(linkable)) + list(MDLINK_ANGLE.finditer(linkable)):
            target = (p.parent / unquote(m.group(1))).resolve()
            if not target.exists() and is_governed(p):
                errors.append(f"E2 {rel}: broken link ]({m.group(1)})")

        if not is_checked(p):
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
        if not is_checked(p):
            continue
        if count == 0:
            warnings.append(f"W2 {p.relative_to(root)}: orphan (0 inbound wikilinks)")

    for e in errors:
        print(e)
    for w in warnings:
        print(w)
    print(f"\nLayout: {layout.mode}; root: {root}")
    print(f"Pages: {len(pages)}; errors: {len(errors)}; warnings: {len(warnings)}")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
