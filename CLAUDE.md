@AGENTS.md

## Claude Code specifics

- **Commands.** User-facing entry points live in `.claude/commands/`: `/wiki-ingest`, `/wiki-research`, `/wiki-capture`, `/wiki-audit`, `/wiki-doctor`, `/wiki-learn`. You may also act directly via the `llm-wiki` skill when the user says "add this to my wiki".
- **First run.** If the recommended skills aren't installed, run `/wiki-doctor` — it checks the setup and walks the user through installing Superpowers, Matt Pocock, and find-skills.
- **Permissions.** This is a Markdown-only knowledge base — no code is executed by wiki operations, so the constant approval prompts add friction without protecting much. For a **dedicated wiki repo** it's reasonable to enable bypass-permissions mode (`claude --dangerously-skip-permissions`) so the agent can write many pages without interruption. This advice is **scoped to this wiki repo** — do not carry it into code repositories, where approvals matter.
- **Markdown-first.** Everything happens in Markdown and in-chat. Lessons from `/wiki-learn` are Markdown files in `lessons/`, not HTML.
