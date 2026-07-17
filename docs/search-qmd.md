# Optional search: ripgrep + qmd

Search is **not a dependency** of this wiki — but as it grows you may want more than text search.

## Default: ripgrep (`rg`)

Fast, always fresh, zero setup. Search the whole wiki:

```bash
rg -i "your term" entities concepts comparisons queries raw
```

For exact identifiers, dates, and known terms, `rg` is unbeatable. Use it first.

## Optional: qmd (semantic search)

When you want to ask *"where/how is X"* without knowing the exact term — especially across a large
wiki or in another language — a local semantic layer helps. [qmd](https://github.com/tobi/qmd) (MIT)
does BM25 + local vector search + reranking over Markdown, with no cloud.

- Install from git (the npm build lags): `git clone https://github.com/tobi/qmd && cd qmd && bun install`.
- Add this wiki as a collection, then `qmd update && qmd embed && qmd cleanup`.
- Run **one** HTTP daemon per machine (`qmd mcp --http --daemon`) and point your agents at it — don't
  spin up a fresh CLI per query (model load is slow).
- Embedding models are ~2 GB from Hugging Face; if that's slow on your network, fetch them once and
  reuse.

This is a power-user convenience, not a requirement. If in doubt, `rg` is enough.
