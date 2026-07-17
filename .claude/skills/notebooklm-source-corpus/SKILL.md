---
name: notebooklm-source-corpus
description: "Use when a user wants to turn a local folder of videos, audio, PDFs, Markdown, or documents into a resumable original-language Markdown corpus for Hermes, Claude Code, Codex, or other agents. Uses NotebookLM only for ingestion, transcription, and fulltext extraction; performs no translation or summarization, mirrors the source tree, writes manifest/state files, and verifies completeness."
version: 1.0.0
author: Anton Tretakov
license: MIT
metadata:
  hermes:
    tags: [notebooklm, transcription, corpus, markdown, mixed-media]
    related_skills: [nlm-skill]
---

# NotebookLM Source Corpus

## Overview

Build an **immutable source corpus** from a local mixed-media folder. NotebookLM is the ingestion engine: it transcribes speech from supported audio/video and extracts indexed text from documents. The skill exports that original-language fulltext to mirrored Markdown files for later analysis by Hermes, Claude Code, Codex, or another agent.

The extraction phase does **not** translate, summarize, interpret, or create notes. Keep those downstream transformations separate so agents can return to the source text.

## When to Use

Use this skill when the user asks to:

- transcribe one video or an entire local folder;
- extract PDFs, Markdown, text documents, audio, and video into Markdown;
- create an agent-ready corpus without timestamps;
- batch-ingest local mixed media through NotebookLM;
- resume an interrupted NotebookLM extraction;
- verify that every source has a non-empty exported text file.

Use a timestamped Whisper/SRT workflow instead when the deliverable is subtitles, speaker alignment, or forensic word-level timing. Use OCR/document tooling instead when exact page layout, tables, or image positions are the source of truth.

## Artifact Contract

For source folder `COURSE/`, the default output is:

```text
COURSE/
├── original sections and files
└── _SOURCE_TEXT_MD/
    ├── README.md
    ├── .extract-state.json
    ├── extract.log
    └── mirrored sections/
        └── 04. Lesson — SOURCE.md
```

Every `— SOURCE.md` contains:

1. relative path to the original file;
2. source kind and original-language declaration;
3. NotebookLM notebook and source IDs;
4. `## Исходный текст` followed by the full indexed text.

Treat `SOURCE.md` as raw evidence. If a later cleanup removes asset URLs, normalizes product names, or splits paragraphs, write a separate `CLEAN.md` or notes tree rather than overwriting the source corpus.

## Prerequisites

The bundled script expects the `notebooklm` CLI from `notebooklm-py`:

```bash
notebooklm --version
notebooklm auth check --test --json
```

The auth check is valid only when both conditions hold:

- `status == "ok"`;
- `checks.token_fetch == true`.

If authentication is missing or stale, run `notebooklm login` interactively and repeat the network-tested auth check. Never copy cookies, OAuth state, or browser-profile data into the corpus or logs.

The script locates `notebooklm` through `PATH`, then falls back to `~/.local/bin/notebooklm`.

## Workflow

### 1. Inventory the source folder

Count supported files and identify generated folders that must be excluded. The bundled defaults cover:

- documents: PDF, Markdown, TXT, CSV, DOCX, EPUB;
- audio: MP3, M4A, WAV, AAC, OGG, OPUS;
- video: MP4;
- images: JPG, JPEG, PNG, GIF, WEBP.

Completion criterion: the intended source count is known before upload and generated output folders are excluded.

### 2. Choose notebook scope

Prefer one notebook per coherent corpus. Reuse it by exact title or pass its full UUID with `--notebook-id`. Full UUIDs and explicit notebook arguments avoid shared-profile context races between agents.

A new default title is `Source corpus — <folder name>`.

Completion criterion: the manifest records one valid notebook ID for the corpus.

### 3. Run the resumable extractor

Resolve the skill directory, then run its script:

```bash
python3 .claude/skills/notebooklm-source-corpus/scripts/extract_corpus.py \
  "/absolute/path/to/folder"
```

For a long folder, run it through the host's tracked background-process facility rather than `nohup`, shell `&`, or an untracked daemon. In Hermes use `terminal(background=true, notify_on_complete=true)`.

The script performs this loop for every source:

1. reuse an existing NotebookLM source by relative-path title or unique basename;
2. otherwise upload the local file;
3. wait for `ready` with bounded retries;
4. call `source fulltext` rather than chat, translation, or summary;
5. write `SOURCE.md` and update state atomically;
6. record a failure and continue when one item fails.

Completion criterion: the process exits and the persisted state—not transient stdout—shows every item complete or explicitly failed.

### 4. Resume rather than restart

Rerun the same command after interruption. A source is skipped only when:

- state says `complete`;
- source size and modification time are unchanged;
- output exists and contains `## Исходный текст`.

Use `--force` only when re-extraction is intentional. Use `--match TEXT` or `--max-items N` for a tracer-bullet run.

### 5. Verify the persisted corpus

Run the offline verifier after extraction:

```bash
python3 .claude/skills/notebooklm-source-corpus/scripts/extract_corpus.py \
  "/absolute/path/to/folder" \
  --verify-only
```

The verifier checks:

- discovered source count against state;
- all statuses and output paths;
- required Markdown marker;
- non-empty body;
- actual body length against `chars` in state;
- Unicode replacement characters and literal truncation markers;
- known NotebookLM image-asset URL noise as warnings.

Completion criterion: verifier returns exit code `0`, `status: "ok"`, no issues, and the source/output/complete counts agree.

## One-Shot Recipes

### Full folder with a custom notebook title

```bash
python3 .claude/skills/notebooklm-source-corpus/scripts/extract_corpus.py \
  "/data/course" \
  --notebook-title "Course — source corpus"
```

### Reuse a known notebook

```bash
python3 .claude/skills/notebooklm-source-corpus/scripts/extract_corpus.py \
  "/data/course" \
  --notebook-id "00000000-0000-0000-0000-000000000000"
```

### Tracer bullet

```bash
python3 .claude/skills/notebooklm-source-corpus/scripts/extract_corpus.py \
  "/data/course" \
  --match "intro.mp4"
```

### Custom output folder and extensions

```bash
python3 .claude/skills/notebooklm-source-corpus/scripts/extract_corpus.py \
  "/data/archive" \
  --output-dir "_RAW_CORPUS" \
  --extensions ".mp4,.pdf,.md,.txt"
```

## Quality Interpretation

- `source fulltext` is NotebookLM's complete indexed source, not a chat answer. This avoids silent summarization caused by asking the model to “give the transcript.”
- Video text is a readable normalized transcript, not forensic verbatim audio. Punctuation, filler words, and product names can be wrong.
- Timestamps are intentionally absent. They add no value when downstream agents search and analyze the corpus semantically.
- PDFs can contain `lh3.googleusercontent.com/notebooklm` asset URLs and UUIDs. Flag these as cleanup candidates; do not classify them as truncation.
- Very short output is a warning, not automatically a failure. Compare it with source duration or page count before retrying.

## Common Pitfalls

1. **Using NotebookLM chat for extraction.** Chat may summarize or truncate. Export `source fulltext`.
2. **Translating during ingestion.** It duplicates the corpus and adds errors. Translate only passages needed by downstream notes.
3. **Trusting exit code alone.** Verify persisted state and every output after the child process exits.
4. **Re-uploading on resume.** Reuse source IDs from state or exact titles.
5. **Relying on `notebooklm use`.** Shared profiles race. Pass explicit notebook IDs.
6. **Treating media size as transcript completeness.** Compare text with duration; bitrate and resolution dominate file size.
7. **Overwriting raw text during cleanup.** Preserve `SOURCE.md`; write derived material separately.
8. **Leaking authentication.** Logs may contain IDs and public notebook URLs, never cookies or browser storage.

## Verification Checklist

- [ ] Network-tested NotebookLM auth succeeded
- [ ] Intended source count recorded
- [ ] Output tree mirrors source structure
- [ ] One `SOURCE.md` exists per discovered source
- [ ] Every state item is `complete` or reported as failed
- [ ] No empty bodies or body-length mismatches
- [ ] No literal truncation markers or Unicode replacement characters
- [ ] PDF asset noise reported as warning, not silently deleted
- [ ] Translation, summaries, timestamps, and notes are absent from the source corpus
- [ ] Final report names the output root, manifest, counts, failures, and warnings
