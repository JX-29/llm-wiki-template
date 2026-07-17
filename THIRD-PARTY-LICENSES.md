# Third-party licenses

This template **vendors** the following skills (copies included in `.claude/skills/`). Each is
redistributed under its own license, reproduced below.

## llm-wiki, youtube-content — Hermes Agent

- Source: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
  (`skills/research/llm-wiki`, `skills/media/youtube-content`).
- The `llm-wiki` wiki structure is byte-compatible with Hermes Agent `llm-wiki` v2.1.0; keep it
  compatible if you modify it.

```
MIT License

Copyright (c) 2025 Nous Research

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Notes

- The `/wiki-capture` and `/wiki-learn` commands are original to this template; they adapt the
  *patterns* of the author's `research-capture` and the classic `teach` workflow (Markdown-native,
  no HTML), not their code.
- Skills listed in `RECOMMENDED-SKILLS.md` under "Recommended" and "Optional" are **not** vendored —
  you install them from their own sources, under their own licenses.
