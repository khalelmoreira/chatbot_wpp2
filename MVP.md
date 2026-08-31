# MVP Launch Schedule — NFS-e Automation

---

## Weeks 1–2 — Prestador Flow (Org API)

### Week 1 — Rework of existing code + integration
- [✓] Review the onboarding state machine, applying the same separation of concerns already used in the emission flow (extraction, validation, and persistence as distinct services)
- [✓] Fix known state-logic bugs
- [✓] Implement/review authentication and the prestador-creation call against the Notaas Org API
- [✓] Map and handle Org API-specific errors

### Week 2 — Merge, improve prompts, and end-to-end validation
- [✓] Fix the merge step (re-typed data vs. existing partial registration) — historically the point most prone to subtle bugs
- [✓] Rewrite all prompts for the cloud model — review what was a local-model limitation vs. what can now become a richer prompt
- [✓] Test extraction quality against varied real cases (gpt-5-mini; Anthropic fallback still needs a real key to test live)
- [✓] Implement fallback between AI providers — define what counts as a "failure" that triggers the fallback
- [✓] Decide whether the local model stays on as the final fallback — no, removed (`GemmaClient` deleted)
- [✓] End-to-end test: register a real prestador from scratch through to a working `Prestador`
- [✓] Edge-case tests: partially registered prestador, divergent data across attempts, invalid tax regime

---

## Week 3 — Credential security

**Security (blockers):**
- [✓] Fernet encryption of the `notaas_api_key`
- [✓] End-to-end audit of the `.pfx`/single-use HTTPS token flow — confirm the certificate is never written to disk or logged
- [✓] Secrets in `.env`, `.gitignore` confirmed
- [✓] Signature/origin validation for Notaas webhooks

**CNPJ:**
- [✓] Replace the standalone math validation with a real lookup (Receita Federal) — decide sync vs. async in the flow

---

## Week 4 — VPS and deployment

- [✓] Provision a VPS (Hostinger)

**Secrets/agent isolation (decided before touching the VPS):** production credentials (root password, SSH private key, prod `.env`) never enter the devcontainer. Credential-bearing steps below run from the author's own laptop terminal, outside Claude Code. On the VPS, isolation is enforced at the OS level (separate Unix users + file permissions), not agent-side config.

- [✓] Generate SSH key pair on own laptop (not devcontainer); first login to VPS as root using the one-time Hostinger password
- [✓] Create personal sudo admin user (`khalel`), install SSH pubkey, confirm key-based login works
- [✓] Create `nfse-app` service user (nologin shell) — owns app code checkout, prod `.env` (chmod 600), runs gunicorn + worker systemd services
- [✓] Create `nfse-agent` user (nologin/restricted shell, no sudo, no group overlap with `nfse-app`) reserved for running an AI coding agent on the VPS later, with no read access to `nfse-app`'s secrets or env files
- [✓] Basic firewall (UFW): allow SSH, HTTP, HTTPS only
- [✓] Disable root SSH login and password auth in `sshd_config` (via `00-hardening.conf` drop-in, wins over cloud-init's conflicting defaults), key-based auth only, verified via fresh session before closing root access
- [✓] Domain + real HTTPS (Let's Encrypt/Certbot), replacing ngrok
- [✓] Deploy Flask with gunicorn under `systemd` (as `nfse-app`), not an open terminal session
- [✓] `EmissaoWorker` as its own systemd service with automatic restart (`PollingWorker` kept in code, unused — webhook covers that role now)
- [✓] Automated SQLite backups (daily systemd timer, `.backup` snapshot + 14-day rotation)
- [✓] Claude Code running on the VPS as `nfse-agent`: real shell + home dir (`usermod`), own git checkout at `~/chatbot_wpp2` (separate from `nfse-app`'s deployment checkout, no `.env`), Node via user-space `nvm` (no `sudo` ever needed), Claude Code via `npm install -g`, own independent login — verified it cannot read `/opt/nfse-app/.env`
- [✓] Restrict `nfse-agent`'s outbound network egress: `iptables`/UFW rule (`/etc/ufw/before.rules`, `owner --uid-owner`) allows only 443/80/53, drops everything else for that UID — verified `khalel` unaffected, `nfse-agent` reaches HTTPS/DNS, blocked port (22) silently times out
- [✓] (2026-08-21) Granted `nfse-agent` scoped **read-only** POSIX ACLs on `/opt/nfse-app`'s code (`src/`, `tools/`, an allowlist of top-level files); `.env`, `certs/`, `backups/`, `data/` (live `whatsapp.db`) stay unreadable, no write access. See `NFSE_AGENT.md` for setup commands and gotchas.
- [✓] (2026-08-25) Added `~khalel/handoff/` (write-only ACL for `nfse-agent`) so debugging commands are handed to khalel as a reviewable script instead of pasted in chat — see `NFSE_AGENT.md`.

---

## Week 5 — User-facing errors + edge cases (emission flow)

- [✓] Clear messages for: AI didn't understand, Notaas rejected the payload, city is down, AI provider timeout — `src/services/errors/error_notifier.py`, central error boundary in `wpp_handler._process`. Notaas emission errors typed: `NotaasEmissaoPermanenteError` (4xx, incl. unsupported city, stop retrying), `NotaasEmissaoTransitoriaError` (network/5xx, retry)
- [✓] `CONFIRMING` surfaces extraction errors before emission — `ValidationService.valido_e_completo` blocks COLLECTING→CONFIRMING unless the draft is complete/valid/has a resolved ISS rate; `ConfirmingService` only acts on an already-validated draft
- [✓] Deliberate tests (automated, standing in for manual pass — see note below):
- [✓] Intentionally invalid CPF/CNPJ — `test_validador_tomador.py` (tomador flow validates CNPJ only, no CPF field collected)
- [✓] Two simultaneous messages — `test_user_lock_service.py`; added `PRAGMA busy_timeout` so concurrent writers wait instead of erroring
- [✓] Duplicate WhatsApp webhook — `test_wpp_handler_edge_cases.py`; `wpp_mensagens_processadas` table + `ja_processado()`
- [✓] City not supported by Notaas — `test_emission_service_errors.py`; exact Notaas error code still needs confirming against the real API
- [✓] Restart the server with a conversation in `QUEUED`/`PROCESSING` — fixed: `resetar_jobs_travados()` now runs every worker tick, not only after finding a `QUEUED` job (`test_nf_worker_manager.py`). Also fixed: reconfirming an `ERROR`-stuck `nfs` row now resets `status`/`tentativas` (`test_tomador_manager.py`)

**Note:** tests above stand in for a manual pass against live WhatsApp/Notaas — do that before Week 7, especially to confirm real Notaas error codes for unsupported city vs. other 4xx.

---

## Week 6 — Observability + LGPD/liability

- [✓] Structured logging for remote debugging, without full CPF/CNPJ/amounts in logs

**Note (resolved):** pruned the `logger.debug()` calls that dumped whole objects (extracted/merged draft data, ViaCEP/CNPJ lookups) — replaced with either nothing (redundant with the AI extraction log already at the source) or a structural summary (booleans, ids, field names), never raw PII. Flow-entry banners and field-name-list traces (`ValidationResult.invalid`/`.missing`) were already low-noise and left as-is. `run_emissao_worker.py` was missing `setup_logging()` entirely — its logs bypassed redaction and JSON formatting; fixed.

Also added a second log destination: a rotating file under `logs/` (via `config.LOGS_DIR`), capped at INFO regardless of the app's configured level — this is the copy `nfse-agent` gets read access to (POSIX ACL, done manually on the VPS), separate from `journalctl` which `nfse-agent` can't read. The INFO cap means a DEBUG troubleshooting session only widens the journald stream, never the file `nfse-agent` sees.
- [✓] **ISS rates — real resolution:** dropped the ADN integration (mTLS + NBS + Anexo VIII) — RJ runs the SNNFSE Federal engine, so Notaas takes the 6-digit cTribNac directly and resolves incidence município + cTribMun itself; the only thing we owe the payload is the rate. Rates come from a hand-maintained, partner-confirmed table (`src/models/iss_rates_rj.py`, sourced from the RJ municipal table on contabilidade.com, 331/335 national codes), loaded into `iss_rates` by `python -m src.workers.iss_rate_load` (`--clear` to undo). `_iss_ok()` now writes the resolved `(cTribNac, aliquota)` into the draft; `TomadorManager` reads both (no more `ALIQUOTA_ISS` constant); `codigo_servico` reaches the `nfs` row and the Notaas `servico.codigo`. **Deploy step:** run `iss_rate_load` once on the VPS after the code lands.
- [ ] Review sender calls + check WhatsApp caller service state
- [ ] Simple alert if `EmissaoWorker` dies or a job gets stuck in `PROCESSING`
- [ ] LGPD legal basis documented (contract performance) and minimum retention policy
- [ ] Written alignment with partners on liability for emission errors
- [ ] Confirm shared understanding that this is an internal tool with no SLA

---

## Week 7 — Final hardening

- [ ] Security review as if it were an external audit (re-read everything from week 3)
- [ ] Basic rate limiting on the webhook
- [ ] Real registration of the first prestadores (partners) using the working flow
- [ ] Full dress rehearsal: complete onboarding → emission → confirmation cycle, no shortcuts

---

## Weeks 8–9 — Buffer + supervised soft launch

- [ ] Run 1–2 weeks with real usage by the partners, monitoring every emission and every registration
- [ ] Adjust prompts based on real errors
- [ ] Only declare it "launched" without manual supervision after this period