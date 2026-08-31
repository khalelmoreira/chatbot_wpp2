---
name: write-prompt
description: Scaffold and wire a new message prompt (extract / classify / respond) in src/models/prompts/ so it matches the house structure and conventions.
---

# /write-prompt — add a consistent message prompt

Message prompts live in `src/models/prompts/`, one file per concern. Each is an
`AIPrompt(description=..., system="""...""")`. There are **three kinds**, each
with a fixed structure. This skill scaffolds one from the right template and
wires it into the AI layer end to end.

Read the target `*_prompts.py` file, `src/models/prompts/_common.py`, and
`src/services/ai/ai_service.py` before writing anything — match the surrounding
style exactly.

Prompts are f-strings that compose shared fragments from `_common.py`
(`ROLE_SIGNUP` / `ROLE_NFSE` / `ROLE_ASSISTANT`, `NO_INVENTION`, `EXTRACT_RULES`,
`LAY_TERMS_PREST` / `LAY_TERMS_TOM`, `PREST_CORE_FIELDS`). Reuse a fragment —
never paste its text. `ARG` is the literal `"{}"` that `AIPrompt.render(*args)`
fills at call time; write `{ARG}` once per injected value, in call-site order.

## 1. Pick the kind

| Kind | Suffix | Path | Returns |
|---|---|---|---|
| Extract | `_EXTRACT` | `extract_json` + JSON schema | structured fields |
| Classify | `_CLASS` | `extract_json`, parser reads `["value"]` | one label / bool |
| Respond | `_RESP` | `extract_text` → sent to the user | Portuguese message text |

Ask the user which kind and which entity (`PREST_` onboarding, `TOM_` NFS-e,
`ISS_` service-code, status/history queries) if it isn't obvious.

## 2. Templates — do not deviate from the section order

### Extract (`X_Y_EXTRACT`)

```
ROLE: Extract <what> from the WhatsApp message below — <list the field groups>.
The response format is enforced separately — focus only on getting each field right.

FIELDS:
<field>: <type/shape rule>. <normalization>. <"→" example>. Absent → null.
... one paragraph per field ...

{EXTRACT_RULES}
```

- `{EXTRACT_RULES}` from `_common.py` is the closing RULES block — don't retype it.
- For a prestador extractor, open FIELDS with `{PREST_CORE_FIELDS}` then add the
  extractor-specific fields below it.
- Every field paragraph ends with the absent-case (`→ null`).
- Give at least one `input → output` example for any field that needs
  normalization (digits-only, lowercase, Brazilian number format, code mapping).
- The keep-it-to-the-schema line ("response format is enforced separately") is
  mandatory — the schema in `ai_service.py` does the structural enforcement.

### Classify (`X_Y_CLASS`)

```
TASK: Classify the user's intent into exactly one category:

CATEGORY_A — <definition>, even if indirect.
CATEGORY_B — <definition>.
NENHUM — greeting, thanks, or unrelated.

The line between <A> and <B> is the non-obvious part — use these boundary examples:
"<msg>" / "<msg>" → CATEGORY_A
"<msg>" / "<msg>" → CATEGORY_B
```

- Labels are UPPERCASE and must match the schema `enum` in `ai_service.py`
  exactly (`NENHUM`, not `NONE`).
- Don't restate the output shape ("respond with one word") — the schema +
  `["value"]` parser already enforce it.
- Always name the hard distinction and give ≥2 boundary examples per side.
- Boolean classifiers: `true —` / `false —` with the same boundary-example rule.

### Respond (`X_Y_RESP`)

```
ROLE: {ROLE_SIGNUP}   # or {ROLE_NFSE} / {ROLE_ASSISTANT}

TASK: Write ONE short message (1-2 sentences) <doing exactly one thing>.
Do NOT recap, confirm, or list data already provided.

RULES:
- Reply in Brazilian Portuguese, plain language — {LAY_TERMS_TOM}.
- {NO_INVENTION} Mention only what's in <PLACEHOLDER_LABEL>.

EXAMPLES:
campo="X" → "..."
campo=["X", "Y"] → "..."

<PLACEHOLDER_LABEL>: {ARG}
```

- State an explicit length budget: "ONE short message (1-2 sentences)" /
  "(2-3 sentences)". Match the count to sibling prompts.
- One job per prompt. If it both asks for missing data and lists invalid data,
  it's two prompts.
- The lay-term glossary and the anti-invention rule are non-negotiable in every
  `_RESP` — insert `{LAY_TERMS_PREST}` / `{LAY_TERMS_TOM}` and `{NO_INVENTION}`
  from `_common.py`, don't retype them.
- Injected values use `{ARG}` under an ALLCAPS Portuguese label at the very end
  (`DADOS_FALTANTES:`, `DOCUMENTAÇÃO:`). `AIPrompt.render(*args)` does
  `.format(*args)` positionally — order matters, and the prompt must contain no
  other literal `{`/`}`. Multiple values: one label + `{ARG}` each, in call-site
  order.

## 3. Conventions (all kinds)

- Instructions in English; user-facing output in Brazilian Portuguese. Keep that
  split — never write the instructions in Portuguese.
- Section labels are bare ALLCAPS (`ROLE:`, `FIELDS:`, `RULES:`, `EXAMPLES:`) —
  not Markdown `##`.
- `description=` is a one-line human summary of what the prompt does — not a
  restatement of ROLE/TASK.
- Examples use the `input → output` arrow form. Be consistent within a file.
- Name: `<ENTITY>_<PURPOSE>_<KIND>`, e.g. `PREST_INCOMPLETE_RESP`,
  `TOM_NF_EXTRACT`, `ISS_SERVICE_CODE_CLASS`.

## 4. Wire it up (full path — don't stop at the prompt text)

1. **Prompt** — add the `AIPrompt` to the right `src/models/prompts/*_prompts.py`.
2. **Export** — add the name to that file's imports and `__all__` in
   `src/models/prompts/__init__.py` (keep the existing grouping comments).
3. **Enum key** — add a member to the matching `StrEnum` in
   `src/types/ai_types.py` (`PrestRespKey` / `TomClassKey` / `PrestExtractKey` /
   …). Value matches the member name.
4. **Schema** (extract & classify only) — add a `*_SCHEMA` near the others in
   `src/services/ai/ai_service.py`. Classify/bool: use `_value_schema({...})`.
   Extract: object with every field `["<type>", "null"]` and all `required`.
5. **Config** — register in the entity's `AIOperations(...)` block in
   `AIService.__init__`:
   - extract → `ExtractionConfig(PROMPT, OutputType, schema=PROMPT_SCHEMA)`
   - classify → `ClassificationConfig(prompt=PROMPT, schema=…, parser=…, fallback=…)`
   - respond → `ResponseConfig(PROMPT)` (add a second arg only for a non-default
     fallback string)
6. **Call site** — the flow/service calls `self.ai.<entity>.<kind>(KEY, ctx.text,
   [param1, param2])`; the list fills the `{}` placeholders left to right.

## 5. Check before finishing

- `ruff check` the touched files; `pyright` if types changed.
- `python -m pytest src/tests -q -k "ai or prompt"` if the AI layer has tests
  covering the new key.
- Confirm the classifier `enum` in the schema matches the labels in the prompt
  text character-for-character.
- Show the user the new prompt + the diff of the four wiring points, and note
  which call site still needs to invoke it.
