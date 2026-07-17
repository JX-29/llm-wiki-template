# Third-party licenses

This template **vendors** the skills below — copies ship inside `.claude/skills/` so a fresh copy of
the template works with nothing to install. Each is redistributed under its own license, reproduced
here. All are MIT.

| Vendored skill | Upstream | Copyright |
|---|---|---|
| `llm-wiki`, `youtube-content` | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | © 2025 Nous Research |
| `research`, `grilling`, `domain-modeling`, `writing-shape`, `writing-beats`, `writing-fragments` | [mattpocock/skills](https://github.com/mattpocock/skills) | © 2026 Matt Pocock |
| `notebooklm-source-corpus` | Anton Tretakov | © 2026 Anton Tretakov |

The `llm-wiki` wiki structure is byte-compatible with Hermes Agent `llm-wiki` v2.1.0 — keep it
compatible if you modify it.

## MIT License — Nous Research

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

## MIT License — Matt Pocock

```
MIT License

Copyright (c) 2026 Matt Pocock

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

- Vendored copies are refreshed with `scripts/vendor-skill.sh`, which also normalizes
  machine-specific paths so the skills work in any copy of this template.
- The `/wiki-capture` and `/wiki-learn` commands are original to this template. They adapt the
  *patterns* of the author's `research-capture` skill and of the classic "teach" workflow
  (Markdown-native, no HTML) — not their code.
- Skills listed as **Optional** in `RECOMMENDED-SKILLS.md` are **not** vendored: you install those
  from their own sources, under their own licenses.
