# MVP Launch Schedule — NFS-e Automation

**Total deadline:** 74 days

---

## Weeks 1–2 — Prestador Flow (Org API)

### Week 1 — Rework of existing code + integration
- [ ] Review and fix the onboarding state machine, applying the same separation of concerns already used in the emission flow (extraction, validation, and persistence as distinct services)
- [ ] Fix known state-logic bugs before touching the integration — treat as separate tasks
- [ ] Implement/review authentication and the prestador-creation call against the Notaas Org API
- [ ] Map and handle Org API-specific errors (expect quirks, as already happened with the city hall's 400 error in the emission flow)

### Week 2 — Merge, prompt, and end-to-end validation
- [ ] Fix the merge step (re-typed data vs. existing partial registration) — historically the point most prone to subtle bugs
- [ ] Adapt/simplify the extraction prompt for prestador data
- [ ] End-to-end test: register a real prestador from scratch through to a working `Prestador`
- [ ] Edge-case tests: partially registered prestador, divergent data across attempts, invalid tax regime

---

## Week 3 — Meta unblock + credential security

**Priority #1, start on the first day of the week:**
- [ ] Open an appeal for the Meta/WhatsApp Business block. If there's no response within ~5 days, start creating a new account in parallel as plan B

**Security (blockers):**
- [ ] Fernet encryption of the `notaas_api_key`
- [ ] End-to-end audit of the `.pfx`/single-use HTTPS token flow — confirm the certificate is never written to disk or logged
- [ ] Secrets in `.env`, `.gitignore` confirmed
- [ ] Signature/origin validation for Notaas webhooks

**CNPJ:**
- [ ] Replace the standalone math validation with a real lookup (Receita Federal) — decide sync vs. async in the flow

---

## Week 4 — VPS and deployment

- [ ] Provision a VPS (Fedora)
- [ ] SSH with key-based auth, basic firewall, non-root user for the application
- [ ] Domain + real HTTPS (Let's Encrypt/Certbot), replacing ngrok
- [ ] Deploy Flask with `systemd`, not an open terminal session
- [ ] `PollingWorker`/`EmissaoWorker` as separate systemd services with automatic restart
- [ ] Automated SQLite backups

---

## Week 5 — Prompts for the cloud model + fallback

- [ ] Rewrite extraction/classification prompts (tomador) for the cloud model — review what was a local-model limitation vs. what can now become a richer prompt
- [ ] Test extraction quality against varied real cases
- [ ] Implement fallback between AI providers — define what counts as a "failure" that triggers the fallback
- [ ] Decide whether the local model stays on as the final fallback

---

## Week 6 — User-facing errors + edge cases (emission flow)

- [ ] Clear messages for: AI didn't understand, Notaas rejected the payload, city is down, AI provider timeout
- [ ] Verify that `CONFIRMING` actually surfaces extraction errors before emission
- [ ] Deliberate manual tests:
  - [ ] Intentionally invalid CPF/CNPJ
  - [ ] Two simultaneous messages (SQLite concurrency)
  - [ ] Duplicate WhatsApp webhook
  - [ ] City not supported by Notaas
  - [ ] Restart the server with a conversation in `QUEUED`/`PROCESSING`

---

## Week 7 — Observability + LGPD/liability

- [ ] Structured logging for remote debugging, without full CPF/CNPJ/amounts in logs
- [ ] Simple alert if `EmissaoWorker` dies or a job gets stuck in `PROCESSING`
- [ ] LGPD legal basis documented (contract performance) and minimum retention policy
- [ ] Written alignment with partners on liability for emission errors
- [ ] Confirm shared understanding that this is an internal tool with no SLA

---

## Week 8 — Final hardening

- [ ] Security review as if it were an external audit (re-read everything from week 3)
- [ ] Basic rate limiting on the webhook
- [ ] Real registration of the first prestadores (partners) using the working flow
- [ ] Full dress rehearsal: complete onboarding → emission → confirmation cycle, no shortcuts

---

## Weeks 9–10 — Buffer + supervised soft launch

- [ ] Run 1–2 weeks with real usage by the partners, monitoring every emission and every registration
- [ ] Adjust prompts based on real errors
- [ ] Only declare it "launched" without manual supervision after this period

---

## Known risks

- **Prestador flow (weeks 1–2):** the schedule's biggest source of uncertainty, since it depends on largely untested Org API behavior. A delay here cascades into every later stage.
- **VPS (week 4):** first time setting up a production environment personally; risk of underestimating the time even with Linux familiarity.
- **Meta/WhatsApp (week 3):** the only external blocker, outside development's direct control.
