# Task: ISS Rate (Alíquota) Resolution — Rio de Janeiro

## Goal

Given a user's free-text service description, resolve:
1. The `codigoTributacaoNacional` (6-digit LC 116/2003 national service code)
2. The current ISS rate for that code in Rio de Janeiro (`codigoMunicipio` = 3304557)

Scope: **RJ only** for MVP. Don't build multi-município support now, but don't hardcode RJ into places that should stay configurable just to save time.

This feeds the pre-emission validation checkpoint. A resolution failure should block emission, not surface later.

## ⚠️ Update 2026-08-25 — verified against the live production API

Production sync was returning `0/335` — every code, every município, 404. Root-caused
by hand against the real ADN host (`adn.nfse.gov.br`), with `AdnClient`'s own mTLS
cert, from the VPS. Findings supersede the "verify before building" section below,
which turned out to have been built against a hallucinated endpoint shape:

- **The URL path `adn_client.py` calls doesn't exist.** It hits
  `/parametrizacao/parametros_municipais/{municipio}/{codigo}` — not a real route.
  Confirmed via the live swagger spec (`GET
  /parametrizacao/swagger/v1/swagger.json`, itself behind the same mTLS cert but
  reachable — the doc site `/parametrizacao/docs/index.html` is too, so the cert and
  base host were never the problem). The real route is:

  ```
  GET /{codigoMunicipio}/{codigoServico}/{competencia}/aliquota
  ```

  (server prefix `/parametrizacao`, so full path
  `/parametrizacao/{municipio}/{codigo}/{competencia}/aliquota`). `competencia` is a
  date. Confirmed working shape from a live 400 response body once the URL was
  fixed: `{"aliquotas":null,"mensagem":"..."}`.

- **RJ is fully migrated** — `GET /parametrizacao/{municipio}/convenio` for `3304557`
  returns `aderenteAmbienteNacional: 1, aderenteEmissorNacional: 1`. The 404s were
  never a migration/data-availability issue, so this doc's old advice to "confirm RJ
  has completed migration" is moot — it has, and that was never the blocker.

- **`codigoServico` in the real endpoint is a 9-digit NBS code (Nomenclatura
  Brasileira de Serviços), not the 6-digit LC 116 `codigoTributacaoNacional`** this
  app classifies to today. Confirmed via a live 400 body: *"O código do serviço deve
  ser composto por nove dígitos."* NBS is the classification introduced for the
  IBS/CBS tax-reform transition — i.e. the exact thing this doc's original "Out of
  scope" section punted on, except it turns out to be load-bearing for the rate
  lookup itself, not a separate future concern.

- **The LC116→NBS mapping is not 1:1.** Receita Federal publishes the official
  crosswalk as **Anexo VIII**
  (`gov.br/nfse/.../rtc/anexoviii-correlacaoitemnbsindopcclasstrib_ibscbs_v1-00-00.xlsx`,
  sheet `tabela geral`, 1,739 rows: `Item LC 116 | Descrição | NBS | Descrição NBS |
  PS Onerosa? (S/N) | Adq Exterior? (S/N) | INDOP | Local incidência IBS |
  cClassTrib | nome cClassTrib`). Example: LC116 item `15.08` (the app's `150801`,
  "Emissão, reemissão... contrato de crédito") fans out to **six** different NBS
  codes (`1.0901.33.00`...`1.0901.39.00`, `1.0905.50.00`), disambiguated by whether
  the operation is onerous and whether the acquirer is abroad — fields the current
  classification step doesn't collect at all.

**What this means for scope**: this is no longer a client bug fix. Getting a real
rate back requires (a) importing/maintaining the Anexo VIII crosswalk, (b) picking
NBS codes some way — either extending classification to capture onerosidade/adq.
exterior, or making an explicit, documented default assumption for the RJ/MVP case
(e.g. "always onerosa, never exterior" — verify this is actually a safe default for
the prestadores this app serves before assuming it), and (c) rewriting
`adn_client.py`'s URL/params to the real route shape above. None of this has been
implemented yet — the sections below describe the original (now partly obsolete)
plan; treat "What to build" step 2 and the "Out of scope" IBS/CBS line as superseded
by this section.

## ⚠️ Verify before building (original, partially superseded above)

Everything below about endpoint names, payload shape, and RJ's migration status came from web searches in a prior conversation — not verified primary sources. Brazilian tax law/APIs change often, and the tax reform transition is actively in progress in 2026. Before coding against any specific endpoint:

- Search current official docs (gov.br/nfse, Notaas docs) — don't assume what's below still holds.
- Check whether Notaas already exposes a municipal-parameters/rate lookup directly — that avoids a second integration (mTLS with Sefin Nacional). Confirm via docs or support before assuming it doesn't exist.
- ~~Confirm RJ has actually completed migration to the Emissor Nacional~~ — confirmed 2026-08-25, see above. No longer a concern.
- If anything you find conflicts with this doc, trust what you find.

## What to build

1. **Rate sync (not on the hot path).** Periodic job (e.g. daily) that fetches current RJ rates from the confirmed source and upserts a local table: national tax code, rate, validity start/end, updated timestamp. Respect validity — never let an expired rate override a current one, never treat "no current row" as zero. The emission flow reads only from this local table, never calls the external source synchronously per message. Now also needs: the LC116→NBS crosswalk (Anexo VIII) available locally, and the correct `/{municipio}/{codigo}/{competencia}/aliquota` URL shape (see update above) — the currently-deployed `adn_client.py` needs this rewrite before sync can succeed at all.

2. **Service classification (AI, observer only).** Takes the user's free-text description, returns a candidate code from the ~200-item national list, or an explicit "unclassified" result when confidence is low. No guessing the closest code. **Now underspecified**: LC116 code alone isn't enough to pick an NBS code (see update above) — needs a decision on whether to collect onerosidade/exterior-acquisition from the AI classification step too, or default them.

3. **Resolution.** Given a classified code, look up the current rate locally. No current row = visible failure, not a silent pass-through with missing/zero rate.

4. **Wire into the pre-emission checkpoint** alongside the other município-dependent fields already planned there.

## Out of scope

- Municípios other than RJ
- RJ's municipal tax-benefit / ISS-retention tables (leave a TODO, don't implement)
- ~~IBS/CBS reform-transition calculations~~ — turned out not to be optional; the NBS code *is* an IBS/CBS-reform artifact and it's required to call the rate endpoint at all. What's still legitimately out of scope: any actual IBS/CBS rate *calculation* (as opposed to just carrying the NBS code needed for the ISS lookup).

## Acceptance criteria

- Rate sync can be run manually and populates the table with RJ data
- A clear service description (e.g. "digital marketing consulting") resolves to a code and rate
- An ambiguous/out-of-scope description returns explicit "unclassified," not a guessed code
- A valid code with no current rate row fails visibly
- Tests cover: classification against real example descriptions, rate lookup with an expired validity row, and ideally one integration test against the source's homologação environment
