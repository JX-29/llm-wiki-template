#!/usr/bin/env python3
"""Convert SingleFile-saved HTML pages to a clean Markdown corpus via defuddle.

Mirrors the notebooklm-source-corpus artifact contract, but as a SEPARATE tree
(_HTML_TEXT_MD) so it never pollutes the NotebookLM state/verifier in _SOURCE_TEXT_MD.

No translation, no summarization — original-language fulltext only.

Usage: python3 scripts/html_to_md.py <folder> [<folder> ...]
Requires: defuddle CLI (npm install -g defuddle).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR_NAME = "_HTML_TEXT_MD"
EXTS = {".htm", ".html"}
TIMEOUT = 180

# --- locate defuddle -------------------------------------------------------
npm_bin = subprocess.run(["npm", "prefix", "-g"], capture_output=True, text=True).stdout.strip()
search_path = os.pathsep.join(filter(None, [os.path.join(npm_bin, "bin"), os.environ.get("PATH", "")]))
DEFUDDLE = shutil.which("defuddle", path=search_path)
if not DEFUDDLE:
    sys.exit("defuddle not found (npm install -g defuddle)")

DEFUDDLE_VERSION = subprocess.run([DEFUDDLE, "--version"], capture_output=True, text=True).stdout.strip()

# --- SingleFile provenance -------------------------------------------------
URL_RE = re.compile(r"^\s*url:\s*(\S+)", re.MULTILINE)
SAVED_RE = re.compile(r"^\s*saved date:\s*(.+?)\s*$", re.MULTILINE)

# SingleFile inlines every asset as a base64 data: URI. Those are binary image
# payloads, not text — in one page they were 99.5% of the output. The .htm file
# on disk remains the immutable source; this derived corpus keeps prose only.
DATA_URI_RE = re.compile(r"data:[^)\s\"']{100,}")


def singlefile_meta(path: Path) -> dict:
    """Pull the original URL + save date out of the SingleFile banner comment."""
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:4000]
    except Exception:
        return {}
    meta = {}
    if m := URL_RE.search(head):
        meta["source_url"] = m.group(1)
    if m := SAVED_RE.search(head):
        meta["saved_date"] = m.group(1)
    return meta


def extract(path: Path) -> tuple[str, int, str]:
    """Run defuddle and drop inlined assets. Returns (markdown, assets_omitted, error)."""
    try:
        r = subprocess.run([DEFUDDLE, "parse", str(path), "--md"],
                           capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return "", 0, "timeout"
    md = (r.stdout or "").strip()
    if not md:
        return "", 0, (r.stderr or "").strip().splitlines()[0] if r.stderr else "empty output"
    md, n_assets = DATA_URI_RE.subn("asset-omitted", md)
    return md.strip(), n_assets, ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SingleFile HTML → Markdown corpus (defuddle), one _HTML_TEXT_MD per root.")
    parser.add_argument("roots", nargs="+", type=Path, help="Folders with saved .htm/.html pages")
    args = parser.parse_args()

    grand = []
    for root in args.roots:
        root = root.expanduser().resolve()
        if not root.is_dir():
            print(f"!! missing root: {root}")
            continue

        out_root = root / OUT_DIR_NAME
        files = sorted(
            p for p in root.rglob("*")
            if p.suffix.lower() in EXTS
            and OUT_DIR_NAME not in p.parts
            and not p.name.startswith("._")
        )

        print(f"\n{'=' * 70}\nROOT: {root.name}\nDiscovered: {len(files)} HTML files\n{'=' * 70}")
        items = []
        for i, f in enumerate(files, 1):
            rel = f.relative_to(root)
            meta = singlefile_meta(f)
            md, assets, err = extract(f)
            size = f.stat().st_size

            if md:
                out_path = out_root / rel.parent / f"{rel.stem} — SOURCE.md"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                header = [
                    f"# {rel.stem}",
                    "",
                    f"- Источник: `{rel}`",
                    "- Тип: сохранённая веб-страница (SingleFile) → Markdown",
                    f"- Извлечено: defuddle {DEFUDDLE_VERSION}",
                    "- Язык: оригинал; перевод и резюмирование не выполнялись",
                ]
                if meta.get("source_url"):
                    header.append(f"- Исходный URL: {meta['source_url']}")
                if meta.get("saved_date"):
                    header.append(f"- Дата сохранения: {meta['saved_date']}")
                if assets:
                    header.append(f"- Вырезано инлайновых base64-ассетов: {assets} "
                                  "(картинки; текст не затронут — оригинал в `.htm`)")
                header += ["", "## Исходный текст", "", md, ""]
                out_path.write_text("\n".join(header), encoding="utf-8")
                status, chars, rel_out = "complete", len(md), str(out_path.relative_to(root))
            else:
                status, chars, rel_out = "no_content", 0, ""

            items.append({
                "source": str(rel),
                "status": status,
                "chars": chars,
                "bytes": size,
                "assets_omitted": assets,
                "output": rel_out,
                "source_url": meta.get("source_url", ""),
                "error": err,
            })
            flag = "ok  " if status == "complete" else "SKIP"
            extra = f"  (-{assets} assets)" if assets else ""
            print(f"[{i:>2}/{len(files)}] {flag} {chars:>6} ch  {rel}{extra}")

        done = [i for i in items if i["status"] == "complete"]
        skipped = [i for i in items if i["status"] != "complete"]

        # README index
        out_root.mkdir(parents=True, exist_ok=True)
        total_assets = sum(i["assets_omitted"] for i in items)
        lines = [
            "# HTML source corpus — original-language Markdown",
            "",
            f"- Extractor: **defuddle {DEFUDDLE_VERSION}** (local; no NotebookLM involved)",
            f"- Discovered: **{len(items)}** · Extracted: **{len(done)}** · No content: **{len(skipped)}**",
            f"- Prose characters: **{sum(i['chars'] for i in items):,}**",
            f"- Inlined base64 assets stripped: **{total_assets}**",
            f"- Updated: `{datetime.now(timezone.utc).isoformat(timespec='seconds')}`",
            "- Translation and summarization: **not performed**",
            "",
            "Pages reporting *no content* are navigation-only shells — their substance is the "
            "accompanying media, handled separately by the NotebookLM corpus in `_SOURCE_TEXT_MD/`.",
            "",
            "SingleFile inlines every image as a base64 `data:` URI. Those payloads are stripped "
            "here (replaced by `asset-omitted`) so this stays a *text* corpus. "
            "The untouched `.htm` on disk remains the immutable source.",
            "",
            "| Source | Status | Chars | Assets cut | Markdown | Original URL |",
            "|---|---:|---:|---:|---|---|",
        ]
        for it in sorted(items, key=lambda x: -x["chars"]):
            out_cell = f"`{it['output']}`" if it["output"] else "—"
            url_cell = it["source_url"] or "—"
            lines.append(f"| `{it['source']}` | {it['status']} | {it['chars']} | "
                         f"{it['assets_omitted'] or '—'} | {out_cell} | {url_cell} |")
        (out_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

        state = {
            "root": str(root),
            "output_root": str(out_root),
            "extractor": f"defuddle {DEFUDDLE_VERSION}",
            "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "discovered": len(items),
            "complete": len(done),
            "no_content": len(skipped),
            "total_chars": sum(i["chars"] for i in items),
            "assets_omitted": total_assets,
            "items": items,
        }
        (out_root / ".html-extract-state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"\n-- {root.name}: {len(done)} extracted, {len(skipped)} no-content, "
              f"{sum(i['chars'] for i in items)} chars -> {out_root}")
        grand.append(state)

    print(f"\n{'#' * 70}\nSUMMARY")
    for s in grand:
        print(f"  {Path(s['root']).name}: {s['complete']}/{s['discovered']} extracted, "
              f"{s['total_chars']} chars")

    # External links found in thin pages = files not included in the download
    print("\nGoogle Drive links found inside extracted pages:")
    found = 0
    for s in grand:
        root = Path(s["root"])
        for it in s["items"]:
            if not it["output"]:
                continue
            body = (root / it["output"]).read_text(encoding="utf-8")
            for m in re.findall(r"https://drive\.google\.com/\S+", body):
                print(f"  - {it['source']}\n      {m.rstrip(')')}")
                found += 1
    print(f"  ({found} link(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
