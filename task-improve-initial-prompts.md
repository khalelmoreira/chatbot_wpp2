# task: improve initial prompts

## Status

**Greeting + help assistant: done** (this branch). Remaining: certificate-stage
tone (section below), still not started.

## What shipped

### Greeting card on a no-intent message

`PREST_HAS_INTENT_CLASS` is now boolean (onboarding intent: yes / no). The "no"
branch (`IntentUserService._nenhum`) sends the AI greeting text
(`PREST_NO_INTENT_RESP`, unchanged voice) as one interactive message with two
static buttons:

- **🚀 Começar** (`BotaoId.INICIO_COMECAR`) → `update_state(COLLECTING)` →
  `collecting_flow`, which fires `PREST_NO_DATA_RESP` (already lists all 5 fields).
- **📖 Como funciona** (`BotaoId.INICIO_COMO_FUNCIONA`) → a static explanation
  string (`greeting_service.COMO_FUNCIONA_MSG`), then a lone "🚀 Começar" button.

Button clicks are intercepted in `idle_user_flow` before the classifier
(`GreetingService.handle_button`) — a `button_id` never reaches `classify()`.

### `ajuda` / `help` reserved word → HELP assistant state

- New `UserStatus.HELP` + nullable `prestador.help_return_to` column (idempotent
  ALTER in `tables_db.py`).
- `help_command.is_help_command` — whole-message match on `{ajuda, help}` only,
  deterministic, mirrors `exit_command`. Shared normalizer moved to
  `src/utils/text.py`.
- Entry guarded in `DispatchUser` (`_ETAPAS_AJUDAVEIS` = the 5 onboarding stages
  + idle): stores the current status in `help_return_to`, moves to HELP, sends an
  intro. NFS-e / ACTIVE side is out of scope for now.
- In HELP every message goes to `help_flow`: an existing exit word
  (`is_exit_command`) restores `help_return_to` and clears it; anything else is
  answered by the assistant (`PREST_HELP_RESP`, nursed with the static
  `PREST_FAQ`). No buttons — the prompt itself offers "continue asking / write
  *sair*".

### `PREST_GENERAL_ASK_RESP` → `PREST_HELP_RESP`

Renamed, `PrestRespKey.GENERAL_ASK` → `PrestRespKey.HELP`. The empty-`DOCUMENTAÇÃO`
bug (`task-general-ask-doc-injection.md`) is fixed: `PREST_FAQ` is a static
constant baked into the prompt. That task is now resolved (option 1).

## Certificate stage: tone mismatch — NOT STARTED

The certificate step's user messages are **hardcoded strings** in
`src/services/sign_up/certificate_service.py`, colder than the rest of the app:

- *"Envie seu certificado digital (.pfx) neste link abaixo: {url}"*
- *"O link expira em 15 minutos."* (a bare second message, no context)
- *"✅ Certificado recebido e cadastro concluído! Você já pode emitir notas fiscais por aqui."*

Fix direction: match the plain, warm voice used elsewhere (`ROLE_SIGNUP`,
`LAY_TERMS_PREST`) — one plain sentence explaining what a certificado digital is,
fold the expiry into the same message, reassure on "recebido". Stay
hardcoded-but-reworded (no per-user variation to extract into a prompt).

## Out of scope

- Mid-flow prompts (`INCOMPLETE`, `INVALID`, address).
- `ajuda` on the NFS-e `ConvStatus` side.
