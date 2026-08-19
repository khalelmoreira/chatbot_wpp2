# Task: ISS Rate (Alíquota) Resolution — Rio de Janeiro

## Goal

Given a user's free-text service description, resolve:
1. The `codigoTributacaoNacional` (6-digit LC 116/2003 national service code)
2. The current ISS rate for that code in Rio de Janeiro (`codigoMunicipio` = 3304557)

Scope: **RJ only** for MVP. Don't build multi-município support now, but don't hardcode RJ into places that should stay configurable just to save time.

This feeds the pre-emission validation checkpoint. A resolution failure should block emission, not surface later.

## ⚠️ Verify before building

Everything below about endpoint names, payload shape, and RJ's migration status came from web searches in a prior conversation — not verified primary sources. Brazilian tax law/APIs change often, and the tax reform transition is actively in progress in 2026. Before coding against any specific endpoint:

- Search current official docs (gov.br/nfse, Notaas docs) — don't assume what's below still holds.
- Check whether Notaas already exposes a municipal-parameters/rate lookup directly — that avoids a second integration (mTLS with Sefin Nacional). Confirm via docs or support before assuming it doesn't exist.
- Confirm RJ has actually completed migration to the Emissor Nacional by the time you implement this (expected 2026-01-01, but check for delays/exceptions).
- If anything you find conflicts with this doc, trust what you find.

## What to build

1. **Rate sync (not on the hot path).** Periodic job (e.g. daily) that fetches current RJ rates from the confirmed source and upserts a local table: national tax code, rate, validity start/end, updated timestamp. Respect validity — never let an expired rate override a current one, never treat "no current row" as zero. The emission flow reads only from this local table, never calls the external source synchronously per message.

2. **Service classification (AI, observer only).** Takes the user's free-text description, returns a candidate code from the ~200-item national list, or an explicit "unclassified" result when confidence is low. No guessing the closest code.

3. **Resolution.** Given a classified code, look up the current rate locally. No current row = visible failure, not a silent pass-through with missing/zero rate.

4. **Wire into the pre-emission checkpoint** alongside the other município-dependent fields already planned there.

## Out of scope

- Municípios other than RJ
- RJ's municipal tax-benefit / ISS-retention tables (leave a TODO, don't implement)
- IBS/CBS reform-transition calculations

## Acceptance criteria

- Rate sync can be run manually and populates the table with RJ data
- A clear service description (e.g. "digital marketing consulting") resolves to a code and rate
- An ambiguous/out-of-scope description returns explicit "unclassified," not a guessed code
- A valid code with no current rate row fails visibly
- Tests cover: classification against real example descriptions, rate lookup with an expired validity row, and ideally one integration test against the source's homologação environment
