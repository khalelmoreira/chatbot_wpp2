# NFS-e WhatsApp Automation

Conversational system that lets Brazilian service providers emit electronic
service invoices (NFS-e) over WhatsApp. A message comes in, an AI layer
extracts/classifies the content, deterministic Python decides what happens
next, and the result is pushed to the Notaas fiscal API.

Integrations: **Notaas** (NFS-e platform), **Meta WhatsApp Business API**,
**ViaCEP** (address lookup by CEP).

See [`CLAUDE.md`](CLAUDE.md) for the domain glossary, state machines, and
layering conventions, and [`MVP.md`](MVP.md) for project status/roadmap.

## Setup

### Option A — devcontainer (recommended)

Open the repo in VS Code / Claude Code with the Dev Containers extension and
reopen in container. `.devcontainer/` builds the environment and installs
`requirements.txt` automatically.

### Option B — manual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # fill in real credentials, never commit this file
```

Required environment variables (see `.env.example`): WhatsApp Business API
credentials (`ACCESS_TOKEN`, `APP_SECRET`, `VERIFY_TOKEN`,
`API_META_VERSION`, `PHONE_NUMBER_ID_TEST_META`), `NOTAAS_API_KEY`, and an AI
provider key (`ANTHROPIC_API_KEY` and/or `OPENAI_API_KEY`).

## Running

```bash
python app.py
```

Starts Flask on port 5000 and the `EmissaoWorker` background worker.
`PollingWorker` exists in code but isn't run in production — the WhatsApp
webhook covers that role.

## Testing

```bash
pytest
```

## Linting / formatting

```bash
ruff check .
ruff format .
```

## Production

Deployed on a Hostinger VPS as systemd services `nfse-app` (gunicorn) and
`nfse-emissao-worker`. See `MVP.md` for deployment history and the
`nfse-agent` sandboxing setup, and [`NFSE_AGENT.md`](NFSE_AGENT.md) for the
practical rundown of what `nfse-agent` can access and known VPS quirks.
