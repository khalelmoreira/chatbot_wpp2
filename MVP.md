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

- [ ] Clear messages for: AI didn't understand, Notaas rejected the payload, city is down, AI provider timeout
- [ ] Verify that `CONFIRMING` actually surfaces extraction errors before emission
- [ ] Deliberate manual tests:
- [ ] Intentionally invalid CPF/CNPJ
- [ ] Two simultaneous messages (SQLite concurrency)
- [ ] Duplicate WhatsApp webhook
- [ ] City not supported by Notaas
- [ ] Restart the server with a conversation in `QUEUED`/`PROCESSING`

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