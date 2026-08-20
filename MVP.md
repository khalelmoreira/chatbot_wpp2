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

**Secrets/agent isolation (decided before touching the VPS):** production credentials (root password, SSH private key, prod `.env`) must never enter the devcontainer this AI agent runs in — an agent with file-read + internet access is an exfiltration path (e.g. via prompt injection) that a `settings.json` deny-list doesn't reliably close. All credential-bearing steps below run from the author's own laptop terminal, outside Claude Code. On the VPS itself, isolation is enforced at the OS level (separate Unix users + file permissions), not by agent-side config, so it holds even if an AI agent is later run on the VPS for coding.

- [✓] Generate SSH key pair on own laptop (not devcontainer); first login to VPS as root using the one-time Hostinger password
- [✓] Create personal sudo admin user (`khalel`), install SSH pubkey, confirm key-based login works
- [✓] Create `nfse-app` service user (nologin shell) — owns app code checkout, prod `.env` (chmod 600), runs gunicorn + worker systemd services
- [✓] Create `nfse-agent` user (nologin/restricted shell, no sudo, no group overlap with `nfse-app`) reserved for running an AI coding agent on the VPS later, with no read access to `nfse-app`'s secrets or env files
- [✓] Basic firewall (UFW): allow SSH, HTTP, HTTPS only
- [✓] Disable root SSH login and password auth in `sshd_config` (via `00-hardening.conf` drop-in, wins over cloud-init's conflicting defaults), key-based auth only, verified via fresh session before closing root access
- [ ] Domain + real HTTPS (Let's Encrypt/Certbot), replacing ngrok
- [✓] Deploy Flask with gunicorn under `systemd` (as `nfse-app`), not an open terminal session
- [✓] `EmissaoWorker` as its own systemd service with automatic restart (`PollingWorker` kept in code, unused — webhook covers that role now)
- [✓] Automated SQLite backups (daily systemd timer, `.backup` snapshot + 14-day rotation)
- [✓] Claude Code running on the VPS as `nfse-agent`: real shell + home dir (`usermod`), own git checkout at `~/chatbot_wpp2` (separate from `nfse-app`'s deployment checkout, no `.env`), Node via user-space `nvm` (no `sudo` ever needed), Claude Code via `npm install -g`, own independent login — verified it cannot read `/opt/nfse-app/.env`
- [✓] Restrict `nfse-agent`'s outbound network egress: `iptables`/UFW rule (`/etc/ufw/before.rules`, `owner --uid-owner`) allows only 443/80/53, drops everything else for that UID — verified `khalel` unaffected, `nfse-agent` reaches HTTPS/DNS, blocked port (22) silently times out

---

## Week 5 — User-facing errors + edge cases (emission flow)

- [✓] Clear messages for: AI didn't understand, Notaas rejected the payload, city is down, AI provider timeout — `src/services/errors/error_notifier.py` is a new central error boundary in `wpp_handler._process`: any exception that escapes flow dispatch (AI fallback exhausted, Notaas errors, anything else) now gets mapped to a PT-BR user message and saved/sent instead of crashing silently in the debounce thread or 500ing the webhook. Notaas emission errors are now typed (`NotaasEmissaoPermanenteError` for 4xx payload rejections incl. unsupported city, `NotaasEmissaoTransitoriaError` for network/5xx) so the worker can tell "will never work, stop retrying" apart from "try again later"
- [✓] Verify that `CONFIRMING` actually surfaces extraction errors before emission — confirmed by design: `ValidationService.valido_e_completo` (collecting) already blocks the COLLECTING→CONFIRMING transition unless the draft is complete, valid, and has a resolved ISS rate; `ConfirmingService` only acts on an already-validated draft
- [✓] Deliberate tests (automated, standing in for the manual pass — see note below):
- [✓] Intentionally invalid CPF/CNPJ — `test_validador_tomador.py` (tomador flow only validates CNPJ; no CPF field is collected for tomadores yet, so CPF isn't in scope here)
- [✓] Two simultaneous messages (SQLite concurrency) — `test_user_lock_service.py` covers the lock; added `PRAGMA busy_timeout` so genuinely concurrent writers (e.g. webhook + `EmissaoWorker`) wait instead of erroring
- [✓] Duplicate WhatsApp webhook — `test_wpp_handler_edge_cases.py`; new `wpp_mensagens_processadas` table + `ja_processado()`, same idempotency pattern already used for Notaas deliveries
- [✓] City not supported by Notaas — covered by the permanent/transient split above (`test_emission_service_errors.py`); exact Notaas error code for this case still needs confirming against the real API
- [✓] Restart the server with a conversation in `QUEUED`/`PROCESSING` — found and fixed a real bug: `resetar_jobs_travados()` only ran *after* a `QUEUED` job was found, so an all-`PROCESSING` restart with no `QUEUED` jobs left could never self-heal. Now runs every worker tick regardless (`test_nf_worker_manager.py`). Also fixed: correcting and reconfirming a `nfs` row stuck in `ERROR` didn't reset `status`/`tentativas`, so it silently never got picked up again (`test_tomador_manager.py`)

**Note:** the "Deliberate manual tests" above were implemented as automated tests instead of run by hand against live WhatsApp/Notaas, since that requires interactive access this session doesn't have. Worth an actual manual pass against the Notaas sandbox before Week 7's dress rehearsal, especially to confirm the real error codes Notaas returns for an unsupported city vs. other 4xx payload issues.

---

## Week 6 — Observability + LGPD/liability

- [ ] Structured logging for remote debugging, without full CPF/CNPJ/amounts in logs
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