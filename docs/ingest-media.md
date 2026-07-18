# Ingesting a folder of media (video / audio / PDF / saved HTML)

When a source isn't a single URL but a **folder** — a course, a video series, a pile of PDFs, a
set of saved web pages — this is the repeatable recipe for turning it into `raw/`. Battle-tested on
multi-gigabyte course folders; the traps below each cost real time before they were understood.

## Step 0 — unpack and check integrity (before any upload)

**Unzip large archives with Python, not the system tools.** A course archive over 4 GB is
**Zip64**, and macOS system unzippers mishandle it:

- `ditto` can't read Zip64 (`Couldn't read pkzip signature`) and — worse — **returns exit 0** while
  extracting one file out of a hundred. Silent partial success.
- Info-ZIP `unzip` mangles non-ASCII / emoji in folder names (`Illegal byte sequence`) and stops
  mid-archive.

Use `python3 -m zipfile -e archive.zip dest/` (or `zipfile.ZipFile.extractall`) — it handles Zip64
and UTF-8 names. **Always compare the extracted file count against `unzip -l`**, never trust the
exit code.

**Then check media integrity.** Truncated downloads (MEGA and others leave block-aligned stubs that
look valid by size but lack the `moov` atom) make NotebookLM wait 900 s per file and return an
error. Catch them first:

```bash
python3 scripts/check_mp4_integrity.py "<folder>"
```

Rename any broken file to `*.broken` so the extractor skips it, and re-download from the source —
integrity problems at the origin don't heal on re-download of the archive.

## Step 1 — media → text corpus (audio-first)

The vendored `notebooklm-source-corpus` skill turns video/audio/PDF into a mirrored Markdown corpus.
Key behaviour it now has by default:

- **Audio-first upload:** video's picture is dropped before upload. NotebookLM transcribes *speech*
  and does not read what's on screen (measured +0.2% text across 13 screencast lessons), so the
  video track is dead weight — files go **5–23× smaller**, uploads finish far faster.
- It clears NotebookLM's errored sources before reuse, renames uploads to their relative path
  (so a resume recognises them), and resumes rather than restarts.

```bash
notebooklm auth check --test --json    # status ok + token_fetch true
python3 ~/.agents/skills/notebooklm-source-corpus/scripts/extract_corpus.py \
  "<folder>" --extensions ".mp4,.pdf,.md" --notebook-title "Source corpus — <name>"
```

Run long folders as a tracked background process; resume with the same command. Verify with
`--verify-only`. Output: `<folder>/_SOURCE_TEXT_MD/**/… — SOURCE.md`.

Needs `ffmpeg` (preferred, lossless remux) or macOS `avconvert` for the audio strip; without either
it uploads whole. Presence is probed by **running** the tool, not `which` — a Homebrew ffmpeg can
resolve on PATH yet die on a missing dylib.

## Step 2 — saved HTML pages → Markdown (optional)

If the folder has SingleFile-saved `.htm` pages:

```bash
python3 scripts/html_to_md.py "<folder>"    # needs: npm install -g defuddle
```

Output goes to a **separate** `_HTML_TEXT_MD/` tree (never mixed with the NotebookLM state). Pages
reporting *no content* are navigation shells — their substance is the accompanying media from Step 1.
External links (e.g. Google Drive) surfaced in the output are files **not** in your download —
fetch them separately if you need them.

## Step 3 — corpus → `raw/`

Copy each `— SOURCE.md` into `raw/transcripts/` (media) or `raw/articles/` (documents) with a
descriptive slug and the raw-frontmatter block from `SCHEMA.md` (`ingested`, `source_url`/origin,
`sha256` of the body). `raw/` is immutable after this — corrections live in compiled pages.

## Step 4 — compile pages

Follow the `llm-wiki` skill's Bulk Ingest: orient (`SCHEMA.md` → `index.md` → recent `log.md`),
read sources in batches, write **knowledge-first** pages (not lesson mirrors), cross-link, add to
`index.md`, one bulk `log.md` entry, then `python3 scripts/lint_wiki.py` until clean.

For a large corpus, fan this out: one distiller subagent per section returns a structured digest,
then writer subagents each take a page-set spec, then a single lint pass. Keep provenance and the
trust rules from `PRINCIPLES.md` — course/source claims are `confidence: medium` until verified.
