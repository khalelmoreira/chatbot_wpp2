# Task: tomador `nome` is never checked against the CNPJ

## Symptom

During an NFS-e conversation the tomador is collected as `{nome, cnpj}`
(`src/types/tomador.py` — `Tomador`). Validation
(`src/services/validators/validador_tomador.py`) only checks:

- `validar_nome` → non-empty, `len(strip()) >= 2`
- `val_cnpj` → format + check digit (`validador_prestador.val_cnpj`)

The two are validated **independently**. Nothing confirms the name the user
typed is the company that owns that CNPJ. So a note can be issued to
`nome="Padaria do Zé"` / a valid CNPJ belonging to some unrelated company, and
it goes straight to CONFIRMING and then to Notaas. The name on the invoice is
whatever the user (or the AI extraction) produced.

The prestador onboarding flow already does a Receita check
(`CnpjService.verificar`, `collecting_user_flow.py:29`): CNPJ exists +
`descricao_situacao_cadastral == "ATIVA"`. The tomador flow
(`active_flows/collecting_flow.py`) has no equivalent step at all.

## What the lookup API can and cannot do

`src/utils/get_cnpj.py` → `https://brasilapi.com.br/api/cnpj/v1/{cnpj}`
(BrasilAPI, proxying the Minha Receita / Receita Federal dataset).

- The CNPJ is a **path parameter**. It is a lookup, not a search:
  **CNPJ → data** (the payload includes `razao_social`, `nome_fantasia`,
  `descricao_situacao_cadastral`, address, CNAE).
- There is **no reverse direction** — you cannot pass a company name and get
  candidate CNPJs, and there is no fuzzy-match parameter.

So the feature we can build is **verification**, not autocomplete: look up the
CNPJ the user gave, then compare the returned canonical name to the name the
user typed.

Concrete example: user sends *"nota pra Comercial Silva, CNPJ 12.345.678/0001-90"*.
We call BrasilAPI with `12345678000190`, get back
`razao_social = "COMERCIAL SILVA E FILHOS LTDA"`, `nome_fantasia = "SILVA
MATERIAIS"`. "Comercial Silva" matches neither exactly. We then either
(a) reject, (b) auto-correct `nome` to `razao_social`, or (c) show the Receita
name and ask the user to confirm.

## Caveats that shape the design

- **`razao_social` is the exact registered legal name.** Users type the trade
  name (`nome_fantasia`), an abbreviation, or "the client's name" (a person at
  the company). Strict string equality will produce many false mismatches.
  Normalise (casefold, strip accents, collapse whitespace, drop
  `LTDA/ME/EPP/S.A.` suffixes) and compare against **both** `razao_social` and
  `nome_fantasia`.
- **`get_cnpj_info` returns `None`** on timeout / non-200 / unknown CNPJ — the
  caller must handle that (prestador flow treats it as "couldn't confirm, send
  again").
- **Tomador can be a CPF, not a CNPJ** (`DocTomadorType`). BrasilAPI has no CPF
  endpoint and there is no free CPF→name service. For CPF tomadores this check
  simply does not run — same shape as `CnpjService.verificar` returning `True`
  when `cnpj is None`.
- The domain rule question for khalel: does Notaas require the tomador
  `razaoSocial` to match Receita, or does it look the name up itself from the
  CNPJ? If Notaas ignores our name field, option 2 below is both simplest and
  correct.

## Status: implemented (2026-08-31)

Built a lighter variant of option 1 — verify + **reject** on mismatch (no new
button / confirm sub-state):

- `src/utils/nome_empresa.py` — `normalizar()` + `nome_confere_com_receita()`.
  Normalise both sides (casefold, strip accents/punctuation, drop
  `LTDA/ME/EPP/...` tokens), accept exact or substring match in either direction
  against `razao_social` **or** `nome_fantasia`. **Fails open**: if Receita
  returned neither name, we can't contradict the user → accept.
- `ValidationService._cnpj_ok()` in `collecting_service.py` — mirrors `_iss_ok()`:
  runs after `_iss_ok()`, before the CONFIRMING transition. CPF tomador
  (`cnpj is None`) → pass. `get_cnpj_info` `None` → "não consegui confirmar",
  stay COLLECTING. Not `ATIVA` → blocked (option 3, folded in). Name mismatch →
  reply with the Receita legal name, stay COLLECTING.
- Messages are plain hardcoded strings (like `_iss_*`), no new prompt/AI config.
- Tests: `src/tests/unit/test_nome_empresa.py`; two scenarios in
  `test_tomador_emission_scenario.py` (match advances, mismatch blocks);
  autouse `fake_tomador_cnpj_lookup` fixture in the scenarios `conftest.py`.

Not done / deferred:
- The Notaas contract question (does it need `razaoSocial` to match, or derive
  the name itself?) was **not** verified — worth confirming, but rejecting on
  mismatch is safe regardless.
- No auto-correct of `nome` to `razao_social` (option 2) — user must resend.
- Substring matching is lenient by design; tighten only if false accepts show up.

## Fix options considered (original analysis)

### 1. Verify + ask user to confirm on mismatch — safest, recommended

Add a `TomadorCnpjService` (mirror of `CnpjService`) called from
`collecting_flow` *before* the transition to CONFIRMING, or fold the check into
`ValidationService.valido_e_completo` right after `_iss_ok()`:

- `cnpj is None` (CPF tomador) → pass.
- `get_cnpj_info` → `None` → message "não consegui confirmar o CNPJ … na
  Receita", stay in COLLECTING (return `False`).
- name matches `razao_social` or `nome_fantasia` (normalised) → pass.
- mismatch → reply with the Receita name and a Confirmar/Corrigir button;
  only advance once the user accepts. On accept, persist `razao_social` as
  `nome` so the invoice carries the legal name.

Cost: one new service (~40 lines), one new prompt/response branch, one new
button id. No schema change.

### 2. Verify + auto-replace `nome` with `razao_social` — simplest

Same lookup, but on success just overwrite `ctx.valid.tomador.nome` with
`razao_social` (or `nome_fantasia` when present) and continue — no user
interaction. Only fail the flow when `get_cnpj_info` is `None` or the CNPJ is
not `ATIVA`.

Cheapest to build and removes the "random razão social" bug entirely, but
silently changes what the user typed. Acceptable **only if** Receita's name is
unambiguously the right one to print — confirm the Notaas requirement first
(see caveat above). Mark as MVP shortcut if chosen.

### 3. Also gate on `descricao_situacao_cadastral == "ATIVA"`

Independent of 1/2: the prestador flow blocks non-active CNPJs; the tomador
flow arguably should too (can you legally invoice a company whose registration
is `BAIXADA`?). Low cost to add alongside either option. Confirm whether this
is a real fiscal constraint or just defensiveness before shipping.

## Cheapest checks before coding

1. **Notaas payload/behaviour** — check `task-*` / adn/notaas client code and
   current Notaas docs: is `razaoSocial` sent for the tomador, and is it
   validated against the CNPJ on their side? (Hypothesis #1 per CLAUDE.md — an
   API contract question, verify against vendor docs first.)
2. **BrasilAPI response shape** — one real `curl` against a known CNPJ to
   confirm `razao_social` / `nome_fantasia` field names and that
   `nome_fantasia` can be empty.
3. **Extraction reality** — look at `TOM_NF_SCHEMA` / the extract prompt: what
   does the AI actually put in `tomador.nome` today (legal name? whatever the
   user said?). Decides how lenient the match must be.

## Touch points

- `src/utils/get_cnpj.py` — reused as-is.
- `src/services/active/collecting/collecting_service.py` — `ValidationService`
  (add the check) or a new sibling service.
- `src/flows/active_flows/collecting_flow.py` — wire the new step.
- `src/services/validators/validador_tomador.py` — if the match becomes a
  validator rather than a flow step (note: cross-field, needs network — does
  not fit the pure `Callable[[Any], bool]` table there; a flow-level service is
  the better home).
- `src/models/prompts/nfse_prompts.py` — mismatch response prompt (option 1).
- `src/tests/integration/scenarios/` — `get_cnpj_info` is already faked in
  `conftest.py`; extend the fake for match / mismatch / `None`.
