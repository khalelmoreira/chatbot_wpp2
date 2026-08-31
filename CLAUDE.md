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
- **LC 116 code** (`codigoTributacaoNacional`) — the 6-digit national service code from Lei Complementar 116/2003; what the AI classification step resolves to today.
- **NBS code** (Nomenclatura Brasileira de Serviços) — a *separate*, 9-digit taxonomy introduced for the IBS/CBS tax reform. ADN's ISS-rate endpoint requires the 9-digit NBS code, **not** the LC 116 code, and the two are not 1:1 (Receita Federal's Anexo VIII crosswalk fans one LC 116 item out to several NBS codes). Full detail in `task-aliquota-iss-rj.md`.

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
- Explain domain/tax and systems concepts in layers: one plain-language paragraph with a concrete example first, then the mechanism, then the code or commands — don't open with a table.
- When something fails, give a ranked list of hypotheses each with its cheapest check *before* changing code — don't commit to the first plausible one. For an external API returning 404 / empty results, verifying the endpoint path and payload shape against current vendor docs is hypothesis #1, ahead of any network / firewall / TLS theory (a hallucinated endpoint in `adn_client.py` was the real ADN-sync cause, found only after chasing UFW and cert theories).

## Production deployment (VPS)

The app runs on a Hostinger VPS as `nfse-app` (systemd services `nfse-app` and `nfse-emissao-worker`, gunicorn in front of Flask). `PollingWorker` exists in code but is intentionally not run — the webhook covers that role.

A second, unrelated Unix user, `nfse-agent`, runs a separate Claude Code instance directly on the VPS for coding tasks there. Own git checkout (`~/chatbot_wpp2`, no `.env`), own independent Claude Code login, not shared with `nfse-app` or any devcontainer identity. No sudo, no group overlap with `nfse-app`, no write access to `/opt/nfse-app`. Scoped **read-only** access to `/opt/nfse-app`'s code via POSIX ACLs on specific paths; `.env`, `certs/`, `backups/`, and live `data/whatsapp.db` stay unreadable, enforced at the OS level. Don't merge the two users, grant write access, or share credentials — the boundary is *write* and *secrets*, not *read*. See [`NFSE_AGENT.md`](NFSE_AGENT.md) for ACL scope and VPS-session quirks; `MVP.md` Week 4 for setup history.

### Working on the VPS as `nfse-agent` — always-loaded essentials

`NFSE_AGENT.md` is the full reference but is **not** auto-loaded — read it before any deploy or handoff step. The facts that bite most often:

- The deployed virtualenv is `/opt/nfse-app/venv/`, **never `.venv/`**. Any `python -m …` / `pip …` for `/opt/nfse-app` must `cd /opt/nfse-app` first and use `venv/bin/python`.
- `nfse-agent` has no sudo and no write access to `/opt/nfse-app`. Privileged or write steps are handed to khalel as a reviewed script in `~khalel/handoff/` (see the `/handoff` skill), never pasted in chat.
- Steps writing under `/opt/nfse-app` (`git pull`, `pip install`) run as `sudo -u nfse-app`; only true root steps (`systemctl restart`, `setfacl`, `apt-get`) use plain `sudo`. Never wrap a whole handoff script in `sudo bash` — it leaves files root-owned and breaks the next deploy.
- `gh` is installed user-local at `~/.local/bin/gh` (not on the non-login-shell PATH — call it by full path). It has no auth of its own; pass the PAT from git's store: `export GH_TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p')`. Used by `/deploy` to open the PR — Claude opens it, the user reviews and merges.

### Before touching production

- Never run a command that hits the live production API, emits a real invoice, or mutates production data — from any environment. Explain what would happen and hand over step-by-step instructions for the user to run.
- Before claiming a branch is ahead/behind, run `git fetch --all --prune` — local refs go stale here.
- A deploy only picks up new code after the PR is merged to `main` **and** `/opt/nfse-app` has pulled it. Verify the merge before deploying. The `/deploy` skill encodes this sequence.

## Commands

- Run: `python app.py` — loads `.env`, starts Flask on port 5000, and starts the `EmissaoWorker`/`PollingWorker` background workers.
- Test: `pytest` — `pytest.ini` sets `testpaths = src/tests`, split into `unit/` (flat) and `integration/` (subfoldered by layer: `routes/`, `services/`, `flow/`).
- Lint: `ruff check .` — config in `pyproject.toml` (`E`, `F`, `I`; line-length 120). Format: `ruff format`.
- Types: `pyright` — basic mode, configured in `pyproject.toml` (`include = src`, `app.py`, `config.py`).