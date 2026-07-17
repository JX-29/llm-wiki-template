# Principles

Seven rules that separate a *growing* wiki from a *pile of notes*. They are domain-agnostic —
they hold whether your wiki is about machine learning, medicine, or motorcycle maintenance.

### 1. Primary source, not the model's paraphrase

Capture the source itself into `raw/`, then link to it. Follow every claim back to the party
that owns it — official docs, the paper, the spec, the first-party API — not a second-hand write-up.
*In practice:* ingesting a blog post's claim about an API? Verify it against the API's own docs before it becomes a wiki fact.

### 2. Every claim carries provenance

A fact with no source is a hypothesis, not knowledge. Cite it (`sources:` frontmatter or a `^[raw/…]`
marker), or mark it `confidence: low` until it's corroborated.
*In practice:* if you can't point to where a statement came from, write it as an open question, not an assertion.

### 3. Freshness is explicit

Date what you write (`updated`). Volatile claims — prices, versions, "current best practice", and
**anything an AI generated or recommended** — get re-verified against the source, because they rot fastest.
*In practice:* a page that says "the latest model is X" needs a date and a periodic recheck; a page defining a stable concept does not.

### 4. One page, one idea

Keep pages readable in 30 seconds. Split at ~200 lines. Link generously with `[[wikilinks]]`, and
**grep before you create** — a duplicate page is worse than none.
*In practice:* before writing `concepts/backpropagation.md`, search the wiki; if it exists, extend it instead.

### 5. Contradictions are recorded, not overwritten

When two sources disagree, keep both positions with their dates and sources; mark the page
`contested: true`. Don't silently pick the newer one — the disagreement is itself knowledge.
*In practice:* two studies reach opposite conclusions → one page, both findings, and a note on why they differ.

### 6. The model compiles; the human curates

The agent summarizes, links, and maintains consistency. You decide what's important enough to keep.
Automation does bookkeeping; judgment stays with you.
*In practice:* the agent proposes a new page; you decide whether it clears the bar or is just a passing mention.

### 7. Declare scope, then abstain

The wiki states what it covers (`SCHEMA.md`). Outside that scope, or when a page is stale, it goes to
the primary source rather than over-answering from thin coverage. A wiki that knows its edges is trustworthy.
*In practice:* asked something the wiki doesn't cover, the agent says so and researches it fresh — it doesn't bluff from a loosely-related page.
