---
description: Turn the wiki into a Markdown lesson that teaches you a topic (in-chat, no HTML)
argument-hint: <topic to learn>
---

Teach the user this topic, drawing on the wiki — as Markdown, in the chat and in `lessons/`. **No HTML.**

Topic: $ARGUMENTS

## How

1. **Ground it in the wiki.** Read the relevant compiled pages (`index.md` → pages). If coverage is thin, say so, and offer to `/wiki-research` the gaps first.
2. **Teach one tightly-scoped thing** per lesson, tied to what the user actually wants to learn. Explain conversationally in the chat.
3. **Save the lesson** as `lessons/NNNN-<dash-case-name>.md` (increment `NNNN`), with short frontmatter (`title`, `created`, `type: lesson`) and `[[wikilinks]]` back to the wiki pages it draws on.
4. Optionally add a few "check your understanding" questions in Markdown.
5. If more than one lesson exists, keep a `lessons/README.md` index.

Markdown-first: everything is chat + Markdown files, never generated HTML. This is the in-chat adaptation of the classic "teach" workflow — the learning logic lives in the conversation and the vault, where you and your colleagues can read it.
