# Post-MVP — Future Improvements

Backlog of work deliberately deferred past the MVP launch. **Not in priority order.**
Each item states the problem, why it matters, and the rough shape of a fix — not a committed plan.

When an item grows past a paragraph or two of real design, split it into its own
`task-*.md` and leave a one-line pointer here.

> **This file is a capture list, not yet a roadmap.** Revisit it once the MVP has shipped
> and run with real users for a few weeks. At that point:
> - group the items into phases (e.g. "before opening to paid users", "before scaling past
>   N users", "ongoing hygiene");
> - order them by a real priority call (impact × urgency × cost), not the order they were
>   written;
> - attach rough sizing and, where it makes sense, target dates or triggers ("do #13 when
>   we hit X concurrent conversations");
> - move anything done into `MVP.md`-style checked history or delete it.
> Until then, treat this as the raw input to that exercise.

---

## From the author

### 1. Emission-API provider agnosticism
The whole app is built directly on Notaas. Provider-specific assumptions (auth, payload
shape, error codes, webhook signature) leak out of `src/services/` into flows and managers.

**Why it matters:** vendor lock-in is a business risk (pricing, downtime, ToS changes) and
the LC 116 / NBS tax-reform transition may force a provider switch anyway.

**Shape of a fix:** define an `EmissionProvider` Protocol (issue, cancel, query-status,
verify-webhook) with a Notaas implementation behind it, mirroring how `AIClient` already
abstracts the AI vendor. Keep the domain dataclasses provider-neutral; do the mapping at
the adapter boundary only. First step is an audit of where `notaas` appears outside its
subpackage.

### 2. Stats / cost dashboard
No visibility into volume (NFS-e issued, conversations started vs. completed, failure
rates), AI spend, or infra cost.

**Why it matters:** can't reason about unit economics or spot a regression in extraction
quality / issuance success without eyeballing logs.

**Shape of a fix:** the data already lives in `conversations` / `nfs` / provider responses.
Start with a read-only internal page (counts, funnels, error breakdown) over the existing
DB before adding any metrics infrastructure. AI cost needs per-call token logging first
(see item 11).

### 3. AI-agent / tooling agnosticism
Development is tightly coupled to Claude Code. Project context (conventions, domain
glossary, deploy runbook) lives in CLAUDE.md files and tool-specific memory rather than a
neutral, portable form.

**Why it matters:** if the tool or vendor changes, the accumulated context shouldn't have
to be rebuilt. Also makes onboarding a human contributor easier (overlaps with item 7).

**Shape of a fix:** consolidate the durable project knowledge into plain docs that any
agent or person can consume; keep tool-specific files (skills, hooks) as a thin layer on
top. Decide what is genuinely portable vs. what is Claude-Code workflow.

### 4. Worker to refresh the `iss_rate` table
The ISS-rate data is static / seeded (`iss_rate_seed`, flat 5% for tests). Real rates vary
by municipality and service and change by law.

**Why it matters:** wrong ISS rate = wrong invoice = a fiscal problem for the prestador.
Currently blocked on confirming the RJ ISS-law change and the ADN NBS-code crosswalk
(`task-aliquota-iss-rj.md`).

**Shape of a fix:** a background worker (same pattern as `src/workers/`) that pulls rates
from the authoritative source (ADN ISS-rate endpoint, keyed by 9-digit NBS code) and
updates the table with an effective-date column, so historical invoices stay reproducible.
Unblock the crosswalk question first.

### 5. Certificate deletion — is `del` .pfx + password actually secure?
Prior note: simply deleting the `.pfx` file and its password is not the most secure
teardown, and the reason was never written down.

**Why it matters:** the certificate is the prestador's fiscal identity — a leaked private
key is serious.

**Likely reasons to dig into:** (a) a plain file delete only unlinks the inode; the bytes
stay on disk until overwritten, and on SSDs `shred` doesn't reliably help either;
(b) the password / PFX bytes may persist in swap, tmpfs, process memory, or logs even if
the file is gone; (c) whether the .pfx ever hits disk at all vs. staying in memory for the
single-use HTTPS token flow (Week 3 audited this — re-confirm). Produce a written threat
model and a documented teardown procedure.

### 6. Architecture / design cleanup
The codebase started from an amateur baseline; Claude Code then followed the established
patterns, so early bad practices propagated.

**Why it matters:** compounding maintenance cost; the project doubles as the author's
software-engineering apprenticeship, so the patterns should be ones worth learning.

**Shape of a fix:** targeted pass, not a rewrite. Candidates to look for: layer violations
(HTTP/SQL knowledge leaking across boundaries), inconsistent error handling, functions
grouped by coincidence of current usage rather than by domain concern, missing or weak
type coverage. Do it as a series of small reviewed PRs with a rationale each.

### 7. Documentation for other people
Docs are written for the author + Claude Code, assuming a lot of shared context.

**Why it matters:** needed before anyone else can contribute or audit; also forces
clarity that benefits the author.

**Shape of a fix:** a real README (what it does, how to run it, architecture at a glance),
a CONTRIBUTING guide, and an architecture doc with the three state machines drawn out.
The `tighten-docs` skill covers trimming chat-accreted explanation; this is the
complementary "write the missing parts" job.

---

## Additional candidates

### 8. CI pipeline
Run `ruff`, `pyright`, and `pytest` automatically on every PR. Right now nothing enforces
the checks in the CLAUDE.md "Commands" section before merge to `main`. Cheap to add
(GitHub Actions), high leverage given the deploy flow already goes through PRs.

### 9. Observability: structured logging + error alerting
No structured logs and no alerting. A failed issuance or a crashed worker is invisible
until someone looks. Add a correlation id per conversation/NFS-e threaded through logs,
and an error sink (e.g. Sentry) on the Flask app and both workers.

### 10. Webhook idempotency and message dedupe
Meta re-delivers webhooks. Confirm every inbound WhatsApp message is deduped by its
message id and that issuance is idempotent (no double invoice on retry). This is a
correctness issue, not a nice-to-have — worth promoting if not already handled.

### 11. Per-call AI token/cost logging
Log tokens and cost for every extraction/classification call, keyed by conversation.
Prerequisite for item 2's cost view and for spotting prompt regressions.

### 12. Extraction / classification eval harness
A regression suite of real messages → expected extracted fields and LC 116 / NBS codes,
run on prompt changes. Prompts are currently validated ad hoc against "varied real cases";
that doesn't catch a regression from a later edit.

### 13. Datastore: SQLite concurrency and migrations
SQLite + `whatsapp.db` is fine for MVP volume. Two questions to answer before it bites:
is there a schema-migration story (or is it hand-applied SQL?), and at what concurrency
does the single-writer lock become a problem — i.e. when does Postgres become necessary?

### 14. Secrets management beyond `.env`
`.env` on the VPS works but is fragile (readable by the app user, easy to leak in a
backup). Consider systemd credentials or a secret manager. Ties into item 5.

### 15. Backup / restore and disaster recovery
Backups exist (`backups/`) but the restore path isn't documented or tested. Write and
rehearse a "VPS is gone, rebuild from scratch" runbook.

### 16. LGPD / data retention
The app stores personal data of prestadores and tomadores plus certificates. Define a
retention policy, a deletion path on request, and what's actually needed vs. kept by
default.

### 17. Error-state recovery UX
When a conversation or onboarding hits `ERROR` / `CANCELLED`, how does the user get
unstuck? Make sure there's a clean path back rather than a dead end.

### 18. WhatsApp webhook rate limiting / abuse protection
The webhook is a public endpoint. Confirm there's a ceiling on per-sender message rate
and AI calls so a malicious or looping sender can't run up cost.

---

## From the author (second pass) — high importance

### 19. Payment methods + billing logic for real users
There is no billing. Before opening to paid users the app needs: a pricing model
(per-NFS-e, subscription, tiered?), a payment integration (Stripe / Mercado Pago / Pix),
the logic that ties an emission attempt to an entitlement (is this prestador allowed to
issue right now?), invoicing/receipts, failed-payment handling, and dunning.

**Why it matters:** it's the difference between a demo and a business; it also gates
almost every "scale" question below (you can't size capacity without knowing who's
paying for what).

**Shape of a fix:** likely its own `task-billing.md`. Keep the entitlement check
deterministic and in `services/` like every other rule; the payment provider goes behind
an adapter (same reasoning as item 1).

### 20. Close the GitHub repository
The repo is currently **public**. It contains business logic, the deploy runbook, and
infra details (VPS layout, ACL scheme). No secrets are committed, but the surface is
larger than it needs to be pre-launch.

**Why it matters:** low effort, removes a whole class of risk (someone forking the
approach, or spotting a weakness in the webhook/cert flow from the code).

**Shape of a fix:** flip to private. Check whether any tooling assumes public access
(the `gh`/PAT deploy flow already authenticates, so it should be fine). Decide later,
deliberately, if parts should be open-sourced.

### 21. Sales / landing web page
Will almost certainly need a public marketing page (what it does, pricing, sign-up).

**Why it matters:** acquisition channel; also where the WhatsApp onboarding link lives.

**Shape of a fix:** keep it a separate static site, not part of the Flask app — different
deploy cadence, different audience, no reason to couple them. The `design` skill can
mock it up.

### 22. App capacity metrics + scaling triggers
Define, with numbers, what this deployment can actually take and what to do when it
can't:
- concurrent conversations / messages-per-second the current VPS plan sustains;
- the SQLite write-lock ceiling — at what sustained write rate does it start timing out,
  and therefore when does Postgres become mandatory (ties into item 13);
- memory / CPU headroom on the current Hostinger plan and the next upgrade step;
- provider-side limits (Meta WhatsApp send rate, Notaas / emission-API quotas).

**Why it matters:** so scaling is a planned move against a known threshold, not a
fire-fight after the first outage.

**Shape of a fix:** a short load test against a staging copy to get real numbers, then
write the thresholds and the corresponding action ("at X, upgrade VPS"; "at Y, migrate
DB") into this doc.

### 23. Quality gates — definition
Decide what "good enough to merge" and "good enough to deploy" mean, concretely:
- **merge gate:** `ruff` clean, `pyright` clean, `pytest` green, min coverage on changed
  lines, no new layer violations (ties into items 6 and 8);
- **deploy gate:** all of the above plus the extraction/classification eval suite above a
  threshold (item 12), migrations applied, a smoke test of the WhatsApp round-trip on
  staging;
- **runtime health metrics to watch:** issuance success rate, conversation completion
  rate, extraction-retry rate, p95 response latency, AI cost per issued NFS-e, worker
  queue depth / age.

**Why it matters:** without an explicit bar, quality drifts and "is it safe to deploy?"
becomes a judgement call every time.

**Shape of a fix:** write the gates down as a checklist, then automate what can be
automated in CI (item 8) and the `/deploy` skill.
