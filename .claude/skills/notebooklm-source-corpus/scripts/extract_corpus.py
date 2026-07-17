#!/usr/bin/env python3
"""Build a resumable original-language Markdown corpus through NotebookLM.

NotebookLM is used only for local-source ingestion, speech transcription, and
fulltext extraction. The script never invokes chat, translation, or summaries.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_EXTENSIONS = {
    ".pdf", ".md", ".txt", ".csv", ".docx", ".epub",
    ".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus",
    ".mp4", ".jpg", ".jpeg", ".png", ".gif", ".webp",
}
MEDIA_EXTENSIONS = {".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus", ".mp4"}
DEFAULT_EXCLUDED_DIRS = {
    ".git", "node_modules", "_SOURCE_TEXT_MD", "_TRANSLATIONS_RU", "_CLEAN_TEXT_MD"
}
OUTPUT_MARKER = "## Исходный текст\n\n"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def natural_key(value: str) -> list[Any]:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def find_notebooklm() -> str:
    found = shutil.which("notebooklm")
    if found:
        return found
    fallback = Path.home() / ".local/bin/notebooklm"
    if fallback.exists():
        return str(fallback)
    raise RuntimeError(
        "notebooklm CLI not found. Install notebooklm-py and authenticate with `notebooklm login`."
    )


def run_cli(binary: str, args: list[str], timeout: int = 300, attempts: int = 1) -> dict[str, Any]:
    last_error = ""
    for attempt in range(1, attempts + 1):
        try:
            proc = subprocess.run(
                [binary, *args], capture_output=True, text=True, timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired as exc:
            last_error = f"timeout after {timeout}s: {exc}"
        else:
            if proc.returncode == 0:
                try:
                    return json.loads(proc.stdout)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(
                        f"Invalid JSON from notebooklm {' '.join(args[:3])}: {exc}; "
                        f"stdout={proc.stdout[:1000]!r}; stderr={proc.stderr[:1000]!r}"
                    ) from exc
            last_error = (proc.stderr or proc.stdout or f"exit {proc.returncode}").strip()
        if attempt < attempts:
            time.sleep(min(120, 15 * (2 ** (attempt - 1))))
    raise RuntimeError(last_error[:4000])


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def log(message: str, log_path: Path) -> None:
    line = f"[{datetime.now().astimezone().isoformat(timespec='seconds')}] {message}"
    print(line, flush=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def parse_extensions(raw: str | None) -> set[str]:
    if not raw:
        return set(DEFAULT_EXTENSIONS)
    extensions = set()
    for value in raw.split(","):
        value = value.strip().casefold()
        if not value:
            continue
        extensions.add(value if value.startswith(".") else "." + value)
    if not extensions:
        raise ValueError("--extensions did not contain any extensions")
    return extensions


def resolve_output(root: Path, raw: str) -> Path:
    candidate = Path(raw).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def discover(
    root: Path,
    output_root: Path,
    extensions: set[str],
    excluded_dirs: set[str],
) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in extensions:
            continue
        resolved = path.resolve()
        if is_within(resolved, output_root):
            continue
        relative_parts = path.relative_to(root).parts[:-1]
        if any(part in excluded_dirs for part in relative_parts):
            continue
        files.append(path)
    return sorted(files, key=lambda path: natural_key(str(path.relative_to(root))))


def output_path_for(root: Path, output_root: Path, source: Path) -> Path:
    relative = source.relative_to(root)
    stem = re.sub(r"\s*-\s*VIDEO$", "", relative.stem, flags=re.IGNORECASE)
    match = re.match(r"^(\d+)\.(.*)$", stem)
    if match:
        stem = f"{int(match.group(1)):02d}.{match.group(2)}"
    return output_root / relative.parent / f"{stem} — SOURCE.md"


def state_output_value(root: Path, output_path: Path) -> str:
    try:
        return str(output_path.relative_to(root))
    except ValueError:
        return str(output_path)


def output_from_state(root: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    return path if path.is_absolute() else root / path


def load_state(path: Path, root: Path, notebook_title: str) -> dict[str, Any]:
    if path.exists():
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(state, dict) and isinstance(state.get("items"), dict):
                return state
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "schema": 1,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "root": str(root),
        "notebook_title": notebook_title,
        "notebook_id": None,
        "items": {},
    }


def ensure_auth(binary: str, log_path: Path) -> None:
    auth = run_cli(binary, ["auth", "check", "--test", "--json"], timeout=90)
    if auth.get("status") == "ok" and auth.get("checks", {}).get("token_fetch") is True:
        return
    log("Auth test failed; trying server-side refresh", log_path)
    refresh = subprocess.run(
        [binary, "auth", "refresh", "--quiet"],
        capture_output=True, text=True, timeout=90, check=False,
    )
    if refresh.returncode != 0:
        raise RuntimeError("NotebookLM authentication needs interactive `notebooklm login`")
    auth = run_cli(binary, ["auth", "check", "--test", "--json"], timeout=90)
    if auth.get("status") != "ok" or auth.get("checks", {}).get("token_fetch") is not True:
        raise RuntimeError("NotebookLM authentication is not network-valid after refresh")


def ensure_notebook(
    binary: str,
    state: dict[str, Any],
    notebook_title: str,
    requested_id: str | None,
    log_path: Path,
) -> str:
    notebooks = run_cli(binary, ["list", "--json"], timeout=90).get("notebooks", [])
    if requested_id:
        matches = [item for item in notebooks if item.get("id") == requested_id]
        if not matches:
            raise RuntimeError(f"Notebook ID not found: {requested_id}")
        notebook_id = requested_id
        state["notebook_title"] = str(matches[0].get("title") or notebook_title)
        state["notebook_id"] = notebook_id
        return notebook_id

    stored_id = state.get("notebook_id")
    if stored_id and any(item.get("id") == stored_id for item in notebooks):
        return str(stored_id)

    exact = [item for item in notebooks if item.get("title") == notebook_title]
    if exact:
        notebook_id = str(exact[0]["id"])
        log(f"Reusing notebook {notebook_title}: {notebook_id}", log_path)
    else:
        created = run_cli(binary, ["create", notebook_title, "--json"], timeout=90)
        notebook_id = str(created.get("notebook", created)["id"])
        log(f"Created notebook {notebook_title}: {notebook_id}", log_path)
    state["notebook_title"] = notebook_title
    state["notebook_id"] = notebook_id
    return notebook_id


def source_title(root: Path, source: Path) -> str:
    return str(source.relative_to(root)).replace(os.sep, " / ")


def ensure_source(
    binary: str,
    root: Path,
    source: Path,
    notebook_id: str,
    known_sources: list[dict[str, Any]],
    log_path: Path,
) -> tuple[str, bool]:
    wanted = source_title(root, source)
    matches = [item for item in known_sources if item.get("title") == wanted]
    if not matches:
        basename_matches = [item for item in known_sources if item.get("title") == source.name]
        matches = basename_matches if len(basename_matches) == 1 else []
    if matches:
        return str(matches[0]["id"]), False

    log(f"Uploading {source.relative_to(root)} ({source.stat().st_size} bytes)", log_path)
    added = run_cli(
        binary,
        [
            "source", "add", str(source), "--title", wanted,
            "--notebook", notebook_id, "--request-timeout", "900", "--json",
        ],
        timeout=960,
        attempts=2,
    )
    payload = added.get("source", added)
    source_id = payload.get("id")
    if not source_id:
        raise RuntimeError(f"Source upload returned no ID: {added}")
    known_sources.append(payload)
    return str(source_id), True


def wait_source(binary: str, source_id: str, notebook_id: str, log_path: Path) -> None:
    for attempt in range(1, 4):
        try:
            payload = run_cli(
                binary,
                [
                    "source", "wait", source_id, "-n", notebook_id,
                    "--timeout", "900", "--json",
                ],
                timeout=930,
            )
            if payload.get("status") == "ready":
                return
            raise RuntimeError(f"Unexpected source status: {payload}")
        except RuntimeError as exc:
            if attempt == 3:
                raise
            log(f"Source wait attempt {attempt} failed: {exc}; retrying", log_path)
            time.sleep(30 * attempt)


def get_fulltext(binary: str, source_id: str, notebook_id: str) -> str:
    payload = run_cli(
        binary,
        ["source", "fulltext", source_id, "--notebook", notebook_id, "--json"],
        timeout=300,
        attempts=2,
    )
    content = str(payload.get("content", "")).strip()
    if not content:
        raise RuntimeError("NotebookLM returned empty fulltext")
    return content


def source_kind(source: Path) -> str:
    extension = source.suffix.casefold()
    if extension in MEDIA_EXTENSIONS:
        return "Транскрипция речи из аудио/видео"
    if extension in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return "Извлечённый текст/описание изображения"
    return "Извлечённый исходный текст"


def write_output(
    output_path: Path,
    root: Path,
    source: Path,
    notebook_id: str,
    source_id: str,
    content: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    relative = source.relative_to(root)
    document = f"""# {source.stem}

- **Исходный материал:** `{relative}`
- **Тип:** {source_kind(source)}
- **Язык:** язык оригинала
- **NotebookLM:** https://notebooklm.google.com/notebook/{notebook_id}
- **Источник NotebookLM:** `{source_id}`
- **Обработка:** полный индексированный текст без перевода и без пересказа

## Исходный текст

{content.strip()}
"""
    output_path.write_text(document, encoding="utf-8")


def valid_output(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 200:
        return False
    try:
        return OUTPUT_MARKER in path.read_text(encoding="utf-8")
    except OSError:
        return False


def write_readme(output_root: Path, state: dict[str, Any]) -> None:
    items = state.get("items", {})
    rows = []
    for relative in sorted(items, key=natural_key):
        item = items[relative]
        error = str(item.get("error", "")).replace("\n", " ")[:180]
        rows.append(
            f"| `{relative}` | {item.get('status', 'pending')} | "
            f"`{item.get('output', '')}` | {item.get('chars', '')} | {error} |"
        )
    complete = sum(1 for item in items.values() if item.get("status") == "complete")
    failed = sum(1 for item in items.values() if item.get("status") == "failed")
    notebook_id = state.get("notebook_id") or ""
    notebook_link = f"https://notebooklm.google.com/notebook/{notebook_id}" if notebook_id else "not selected"
    readme = f"""# Source corpus — original-language Markdown

- NotebookLM: {notebook_link}
- Ready: **{complete}/{len(items)}**
- Failed: **{failed}**
- Updated: `{state.get('updated_at')}`
- Translation and summarization: **not performed**

| Source | Status | Markdown | Characters | Error |
|---|---:|---|---:|---|
{os.linesep.join(rows)}
"""
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "README.md").write_text(readme, encoding="utf-8")


def verify_corpus(root: Path, output_root: Path, state_path: Path, discovered: list[Path]) -> int:
    issues: list[str] = []
    warnings: list[str] = []
    if not state_path.exists():
        print(json.dumps({"status": "error", "issues": [f"Missing state: {state_path}"]}, indent=2))
        return 1
    state = json.loads(state_path.read_text(encoding="utf-8"))
    items = state.get("items", {})
    discovered_rel = {str(path.relative_to(root)) for path in discovered}
    state_rel = set(items)
    for relative in sorted(discovered_rel - state_rel, key=natural_key):
        issues.append(f"Source missing from state: {relative}")
    for relative in sorted(state_rel - discovered_rel, key=natural_key):
        warnings.append(f"State item not currently discovered: {relative}")

    outputs = 0
    total_chars = 0
    for relative, item in items.items():
        if item.get("status") != "complete":
            issues.append(f"Not complete: {relative}: {item.get('status')}")
        raw_output = item.get("output")
        if not raw_output:
            issues.append(f"Missing output path in state: {relative}")
            continue
        output = output_from_state(root, str(raw_output))
        if not output.exists():
            issues.append(f"Missing output file: {relative}: {output}")
            continue
        outputs += 1
        text = output.read_text(encoding="utf-8")
        if OUTPUT_MARKER not in text:
            issues.append(f"Missing text marker: {relative}")
            continue
        body = text.split(OUTPUT_MARKER, 1)[1].strip()
        if not body:
            issues.append(f"Empty body: {relative}")
            continue
        total_chars += len(body)
        if item.get("chars") != len(body):
            issues.append(
                f"Character mismatch: {relative}: state={item.get('chars')} actual={len(body)}"
            )
        if "\ufffd" in body:
            issues.append(f"Unicode replacement character: {relative}")
        if re.search(r"\[truncated\]", body, flags=re.IGNORECASE):
            issues.append(f"Literal truncation marker: {relative}")
        asset_urls = len(re.findall(r"https://lh3\.googleusercontent\.com/notebooklm/\S+", body))
        if asset_urls:
            warnings.append(f"NotebookLM asset URLs: {relative}: {asset_urls}")
        if len(body) < 500:
            warnings.append(f"Very short body: {relative}: {len(body)} chars")

    summary = {
        "status": "ok" if not issues else "issues",
        "root": str(root),
        "output_root": str(output_root),
        "sources_discovered": len(discovered),
        "state_items": len(items),
        "complete": sum(item.get("status") == "complete" for item in items.values()),
        "failed": sum(item.get("status") == "failed" for item in items.values()),
        "outputs_found": outputs,
        "total_source_chars": total_chars,
        "issues": issues,
        "warnings": warnings,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


def process_item(
    binary: str,
    root: Path,
    output_root: Path,
    source: Path,
    notebook_id: str,
    known_sources: list[dict[str, Any]],
    state: dict[str, Any],
    state_path: Path,
    log_path: Path,
    force: bool,
) -> None:
    relative = str(source.relative_to(root))
    output_path = output_path_for(root, output_root, source)
    item = state["items"].setdefault(relative, {})
    current_size = source.stat().st_size
    current_mtime = source.stat().st_mtime_ns
    unchanged = item.get("source_size") == current_size and item.get("source_mtime_ns") == current_mtime
    item.update({
        "source_path": relative,
        "source_size": current_size,
        "source_mtime_ns": current_mtime,
        "output": state_output_value(root, output_path),
    })
    if not force and unchanged and item.get("status") == "complete" and valid_output(output_path):
        log(f"Skipping completed {relative}", log_path)
        return

    item.update({"status": "running", "started_at": utc_now()})
    item.pop("error", None)
    state["updated_at"] = utc_now()
    atomic_json(state_path, state)
    write_readme(output_root, state)

    source_id, uploaded = ensure_source(
        binary, root, source, notebook_id, known_sources, log_path
    )
    item.update({"source_id": source_id, "uploaded": uploaded})
    atomic_json(state_path, state)
    wait_source(binary, source_id, notebook_id, log_path)
    content = get_fulltext(binary, source_id, notebook_id)
    write_output(output_path, root, source, notebook_id, source_id, content)
    item.update({"status": "complete", "completed_at": utc_now(), "chars": len(content)})
    state["updated_at"] = utc_now()
    atomic_json(state_path, state)
    write_readme(output_root, state)
    log(f"Completed {relative}: {len(content)} source chars", log_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract a resumable original-language Markdown corpus through NotebookLM."
    )
    parser.add_argument("root", type=Path, help="Local source folder")
    parser.add_argument("--output-dir", default="_SOURCE_TEXT_MD")
    parser.add_argument("--notebook-title")
    parser.add_argument("--notebook-id")
    parser.add_argument("--extensions", help="Comma-separated extension allowlist")
    parser.add_argument("--exclude-dir", action="append", default=[])
    parser.add_argument("--match", help="Process only relative paths containing this text")
    parser.add_argument("--max-items", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"Source folder does not exist: {root}")
    output_root = resolve_output(root, args.output_dir)
    extensions = parse_extensions(args.extensions)
    excluded_dirs = set(DEFAULT_EXCLUDED_DIRS) | set(args.exclude_dir) | {output_root.name}
    all_files = discover(root, output_root, extensions, excluded_dirs)
    state_path = output_root / ".extract-state.json"
    log_path = output_root / "extract.log"

    if args.verify_only:
        return verify_corpus(root, output_root, state_path, all_files)

    selected = all_files
    if args.match:
        needle = args.match.casefold()
        selected = [p for p in selected if needle in str(p.relative_to(root)).casefold()]
    if args.max_items > 0:
        selected = selected[: args.max_items]
    if not selected:
        raise SystemExit("No matching source files")

    notebook_title = args.notebook_title or f"Source corpus — {root.name}"
    output_root.mkdir(parents=True, exist_ok=True)
    state = load_state(state_path, root, notebook_title)
    state["root"] = str(root)

    for source in all_files:
        relative = str(source.relative_to(root))
        state["items"].setdefault(relative, {
            "status": "pending",
            "source_path": relative,
            "source_size": source.stat().st_size,
            "source_mtime_ns": source.stat().st_mtime_ns,
            "output": state_output_value(root, output_path_for(root, output_root, source)),
        })
    state["updated_at"] = utc_now()
    atomic_json(state_path, state)
    write_readme(output_root, state)

    binary = find_notebooklm()
    ensure_auth(binary, log_path)
    notebook_id = ensure_notebook(
        binary, state, notebook_title, args.notebook_id, log_path
    )
    state["updated_at"] = utc_now()
    atomic_json(state_path, state)
    write_readme(output_root, state)
    known_sources = run_cli(
        binary, ["source", "list", "--notebook", notebook_id, "--json"], timeout=120
    ).get("sources", [])

    log(f"Starting extraction: {len(selected)} selected; {len(all_files)} discovered; notebook={notebook_id}", log_path)
    failures = 0
    for index, source in enumerate(selected, start=1):
        relative = str(source.relative_to(root))
        log(f"[{index}/{len(selected)}] {relative}", log_path)
        try:
            if index > 1 and index % 5 == 0:
                ensure_auth(binary, log_path)
            process_item(
                binary, root, output_root, source, notebook_id, known_sources,
                state, state_path, log_path, args.force,
            )
        except Exception as exc:
            failures += 1
            item = state["items"].setdefault(relative, {})
            item.update({"status": "failed", "failed_at": utc_now(), "error": str(exc)[:4000]})
            state["updated_at"] = utc_now()
            atomic_json(state_path, state)
            write_readme(output_root, state)
            log(f"FAILED {relative}: {exc}", log_path)

    complete = sum(item.get("status") == "complete" for item in state["items"].values())
    pending = sum(item.get("status") == "pending" for item in state["items"].values())
    log(f"Extraction finished: complete={complete}, failed_this_run={failures}, pending={pending}", log_path)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
