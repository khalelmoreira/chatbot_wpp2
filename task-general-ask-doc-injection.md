# Task: `PREST_GENERAL_ASK_RESP` has no documentation to answer from

## RESOLVED — option 1 taken (see `task-improve-initial-prompts.md`)

`PREST_GENERAL_ASK_RESP` was renamed `PREST_HELP_RESP` and folded into the new
HELP assistant state. `PREST_FAQ` (static constant) is now baked into the prompt,
so the `DOCUMENTAÇÃO` section is never empty. The `GENERAL_ASK` classifier branch
is gone — HELP is reached only by the reserved word `ajuda`/`help`.

Original write-up kept below for context.

## Symptom

When a prestador (still onboarding) asks a general question about the system —
`IntentUserType.GENERAL_ASK` — the reply is always some variant of *"não tenho
essa informação, procure o suporte"*, regardless of the question. The feature
looks wired up but can never give a real answer.

## Root cause

`PREST_GENERAL_ASK_RESP` (`src/models/prompts/prestador_prompts.py`) is a
RAG-style prompt: it ends with a `DOCUMENTAÇÃO:` section and instructs the model
*"Answer strictly from DOCUMENTAÇÃO below"* / *"If the answer isn't there, say
you don't have that information"*.

Nothing ever fills that section:

- `src/services/sign_up/intent_user_service.py:58`
  `self.ai.prest.respond(PrestRespKey.GENERAL_ASK, self.ctx.text)` — no `params`.
- `AIOperations._render` (`src/services/ai/ai_service.py:164`) returns the prompt
  unchanged when `params` is empty, so the placeholder is never substituted.
- The model receives a literal empty `DOCUMENTAÇÃO:` block → "not in the docs" →
  the fallback answer, every time.

There is **no documentation source anywhere in the repo** — no FAQ file, no docs
table, no constant. The prompt was written for an injection step that was never
built.

## Fix options (ranked)

### 1. Static FAQ constant — recommended for MVP

Add a `PREST_FAQ` string constant (a dozen Q&A lines covering: what data
registration needs, how issuance works, how to check status, what the bot can't
do) next to the prompt, and pass it:

```python
self.ai.prest.respond(PrestRespKey.GENERAL_ASK, self.ctx.text, [PREST_FAQ])
```

*Why:* the question space here is small and stable (onboarding + basic issuance).
A hand-written FAQ is the whole feature — no retrieval, no new infra. This is an
MVP shortcut, not the end state, but it's the right size for the actual need.

*Cost:* the FAQ text has to be kept in sync with product behaviour by hand.

### 2. Real doc store + retrieval

A `docs` table or markdown corpus, chunked and retrieved by the question, then
injected. Correct long-term if the help surface grows to cover fiscal rules,
per-município specifics, certificate troubleshooting, etc.

*Why not now:* retrieval infra + content authoring for a feature that today has
~5 real questions. Revisit when the FAQ constant starts feeling cramped.

### 3. Drop the feature

Route `GENERAL_ASK` to a fixed "posso te ajudar com cadastro e emissão de notas"
message and delete the prompt. Honest about current capability, but throws away a
classifier branch that already works.

## Scope notes

- The `{ARG}` placeholder in the prompt is fine as-is (renders to `{}` for
  `AIPrompt.render`). The bug is the missing call-site argument, not the prompt
  syntax.
- Whatever fills `DOCUMENTAÇÃO` must be a single positional arg — the prompt has
  exactly one `{ARG}`.
- If option 1: add a test in `src/tests/` asserting the prompt is rendered with
  non-empty documentation before it reaches the client (the current gap is
  exactly the kind a unit test would have caught).
