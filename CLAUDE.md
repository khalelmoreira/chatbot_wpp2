<!-- Verified against github.com/khalelmoreira/chatbot_wpp2 on 2026-08-04.-->

# NFS-e WhatsApp Automation

Conversational system that lets users emit Brazilian electronic service invoices (NFS-e) over WhatsApp. A message comes in, an AI layer extracts/classifies the content, deterministic Python code decides what happens next, and the result is pushed to the Notaas fiscal API.

Integrations: **Notaas** (NFS-e platform), **Meta WhatsApp Business API**, **ViaCEP** (address lookup by CEP).

This is the author's first software project as a developer. When proposing something, briefly say *why* it's the right call — especially when it introduces a new pattern instead of reusing an existing one.

## Domain glossary

- **Prestador** — the service provider; the account holder who emits invoices. Onboards through `UserStatus`.
- **Tomador** — the service taker; the invoice recipient, collected per NFS-e.
- **Conversation** (`conversations` table / `ConvStatus`) — one NFS-e emission attempt, holding `draft_json` until confirmed.
- **NFS-e** (`Nfs` / `NfseStatus`) — the invoice itself, once queued for issuance with Notaas.

## Non-negotiable principles

- **AI extracts and classifies only.** It never decides or writes. Every state transition and side effect is deterministic Python (`AIOperations` in `src/services/ai/`).
- **`NULL` = absence**, never conflated with empty string / zero / false. Validators and merge logic (`MergeableMixin`) treat "not provided" and "provided as empty" as distinct.
- **Explicit over implicit.** Don't infer missing state; fail early and loudly (`InvalidTransactionError`) rather than guessing.
- **No optimistic state.** Guarded transitions (`DB.update_guarded`, `WHERE status = 'X' ... RETURNING`) only flip status after the precondition is confirmed in the same query — never set preemptively in application code.

## Layer discipline

`routes/` (HTTP only, Flask blueprints) → `handlers/` (parse request, delegate) → `flows/` (dispatch by status — `user_flows/` for `UserStatus`, `active_flows/` for `ConvStatus`) → `services/` (business rules, one subpackage per concern) → `managers/` (own DB access for one entity, return domain dataclasses) → `database/` (generic SQL helpers).

Before adding code to a layer, ask: *does this function need to know what an HTTP request or a SQL table is?* If yes, it's in the wrong layer.

## Three state machines — don't conflate them

- **`UserStatus`** (prestador onboarding, `src/types/user.py`): `COLLECTING → ADDRESS → CONFIRMING → PROJECT → CERTIFICATE → ACTIVE`, or `ERROR` / `CANCELLED`. Dispatched by `src/flows/user_flows/`.
- **`ConvStatus`** (one NFS-e conversation, `src/types/conversation.py`): `COLLECTING → CONFIRMING → QUEUED → DONE`, or `ERROR` / `CANCELLED`. `conversations.draft_json` holds the draft; nothing reaches the `nfs` table until confirmed. Dispatched by `src/flows/active_flows/`.
- **`NfseStatus`** (the invoice once queued, `src/types/nfs.py`): `QUEUED → PROCESSING → ISSUED`, or `ERROR` / `CANCELLED`. Owned by the background workers (`src/workers/`), not the conversational flows.

## Conventions

- `StrEnum` for every status and AI-facing key; values are UPPERCASE and match the member name (`QUEUED = "QUEUED"`). Enums live next to the dataclasses they describe (e.g. `UserStatus` in `user.py`) — there's no separate `enums.py`.
- `Protocol` (not `ABC`) for structural typing — `Mergeable`, `FromDictable`, `IsDataclass` in `src/types/protocols.py`, `@runtime_checkable` where used with `isinstance()`. `ABC` still shows up for external interfaces like `AIClient` — a real boundary, not an inconsistency to fix.
- `protocols.py` imports nothing from domain modules — keep it that way if you add a protocol there.
- Deeper, directory-scoped conventions live in nested `CLAUDE.md` files (`src/types/`, `src/database/`, `src/services/ai/`) — Claude Code loads those automatically when it reads files there, so they aren't repeated here.

## Working style

- Explain tradeoffs before recommending — this project doubles as how the author is learning software engineering.
- If a shortcut is proposed for MVP scope, say so explicitly rather than presenting it as the ideal solution.
- Organize code by domain principle (entity vs. cross-cutting concern), not by coincidence of current usage.

## Production deployment (VPS)

The app runs on a Hostinger VPS as `nfse-app` (systemd services `nfse-app` and `nfse-emissao-worker`, gunicorn in front of Flask). `PollingWorker` exists in code but is intentionally not run — the webhook covers that role.

A second, unrelated Unix user, `nfse-agent`, runs a separate Claude Code instance directly on the VPS for coding tasks there. Own git checkout (`~/chatbot_wpp2`, no `.env`), own independent Claude Code login, not shared with `nfse-app` or any devcontainer identity. No sudo, no group overlap with `nfse-app`, no write access to `/opt/nfse-app`. Scoped **read-only** access to `/opt/nfse-app`'s code via POSIX ACLs on specific paths; `.env`, `certs/`, `backups/`, and live `data/whatsapp.db` stay unreadable, enforced at the OS level. Don't merge the two users, grant write access, or share credentials — the boundary is *write* and *secrets*, not *read*. See [`NFSE_AGENT.md`](NFSE_AGENT.md) for ACL scope and VPS-session quirks; `MVP.md` Week 4 for setup history.

## Commands

- Run: `python app.py` — loads `.env`, starts Flask on port 5000, and starts the `EmissaoWorker`/`PollingWorker` background workers.
- Test: `pytest` — `pytest.ini` sets `testpaths = src/tests`, split into `unit/` (flat) and `integration/` (subfoldered by layer: `routes/`, `services/`, `flow/`).
- Lint/format: nothing configured in `pyproject.toml` yet — add a command here once you pick a tool.