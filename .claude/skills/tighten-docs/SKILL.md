---
name: tighten-docs
description: Trim a Markdown doc (or all task-*.md / *.md docs) down to decisions and facts — cut the explanation that accreted from chat sessions.
---

# /tighten-docs — make docs concise and objective

Docs in this repo grow because chat sessions dump rationale into them. This skill
rewrites a doc to keep what a future reader needs and drop the rest. **Meaning is
preserved; only length changes.** No new facts, no new decisions.

## Scope

- `/tighten-docs <path>` — one file.
- `/tighten-docs` with no arg — list the repo's tracked `*.md` (root + `docs/` +
  `task-*.md`), ask which to do. Never batch-rewrite without the user picking.
- Skip `CLAUDE.md` files unless named explicitly — they're instructions, not notes.

## What to cut

- Narration of how a conclusion was reached ("we first tried X, then realized Y").
  Keep the conclusion (Y); drop the journey.
- Repeated context — state a fact once, in the most relevant section.
- Motivational filler, hedging, and restated background the reader already has
  from `CLAUDE.md` or the domain glossary.
- Code blocks that duplicate what's in the repo; replace with a `path:line`
  pointer.
- Resolved open questions — move the answer inline, delete the Q.

## What to keep — do not touch

- Decisions and their one-sentence *why* (this project keeps the why on purpose).
- Non-obvious facts not derivable from code: vendor quirks, tax rules, IDs, URLs.
- Anything under a "Status" / "Open questions" / "TODO" heading that's still open.
- Numbers, dates (keep them absolute), file paths, endpoint shapes.
- The doc's existing heading structure, unless merging two sections removes a
  genuine redundancy.

## Procedure

1. Read the whole doc. Also skim any file/section it leans on so you can tell
   "derivable from code" from "only recorded here".
2. Draft the rewrite. Target roughly half the length, but correctness and the
   keep-list win over any ratio.
3. Show the user a diff (or before/after) **plus** a short bullet list of every
   fact or nuance you dropped, so they can veto. Wait for approval before writing.
4. On approval, write the file. Don't commit unless asked.

## Guardrails

- If you're unsure whether something is "explanation" or "load-bearing fact",
  keep it and flag it in the drop-list as a question.
- Never remove the last record of a decision. If a section is the only place a
  choice is documented, tighten the prose but keep the substance.
- One doc at a time. Report length before/after when done.
