---
name: deploy
description: Ship the nfse-agent branch to the nfse-app VPS — preflight, PR, merge check, handoff script, verify.
---

# /deploy — release chatbot_wpp2 to the VPS

Claude runs as `nfse-agent`: no sudo, no write access to `/opt/nfse-app`. This
skill produces a reviewed handoff script; it never deploys directly. Read
`NFSE_AGENT.md` first.

## 1. Preflight (Claude runs these)

- `git fetch --all --prune`
- `git status --short` — if the working tree is dirty, stop and commit first.
- `git rev-list --left-right --count origin/main...nfse-agent` — show the real
  ahead/behind, not a stale local guess.
- `git diff --stat origin/main...nfse-agent` — summarise what ships.
- `ruff check $(git diff --name-only origin/main...nfse-agent -- '*.py')` and
  `python3 -m pytest -q` — lint only what this branch changed (the repo carries
  pre-existing E501 debt in `src/models/`). Don't proceed past failures without
  the user's explicit OK.

## 2. Commit & push

- Commit outstanding work with a conventional-commit message (`feat:` / `fix:` /
  `docs:` …).
- `git push origin nfse-agent`. **Never** push to `main`.

## 3. Open the PR (Claude does this) — merge is the user's

Use `gh` (installed user-local at `~/.local/bin/gh`). It has no stored auth of
its own — feed it the PAT from git's credential store via `GH_TOKEN`, so the
`~/.git-credentials` file is never read directly:

```bash
export GH_TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p')
~/.local/bin/gh pr create --repo khalelmoreira/chatbot_wpp2 \
  --base main --head nfse-agent \
  --title "<conventional-commit title>" \
  --body "<what ships + lint/test status>"
```

- If `gh` errors with `403` / "not accessible by personal access token", the
  fine-grained PAT is missing **Pull requests: Read and write** — tell the user
  to add that scope at github.com/settings/tokens and retry. Contents:
  Read/write alone cannot open a PR.
- Post the PR URL `gh` prints to the user.
- **STOP.** Do not merge. Wait for the user to review and merge into `main`
  themselves, then confirm before continuing. Merging to `main` is always the
  user's call.

## 4. Handoff script (Claude writes, user runs)

Write `~khalel/handoff/deploy-<YYYY-MM-DD>.sh` and explain it in the same
message. Template — verify the branch/pull mechanism of `/opt/nfse-app` against
the server the first time you use this:

```bash
#!/usr/bin/env bash
set -euo pipefail

# pull as the app user so files stay nfse-app:nfse-app
sudo -u nfse-app bash <<'EOF'
cd /opt/nfse-app
git fetch origin
git checkout main
git pull --ff-only origin main
venv/bin/pip install -q -r requirements.txt
EOF

# restarts need real root
sudo systemctl restart nfse-app nfse-emissao-worker
sudo systemctl --no-pager status nfse-app nfse-emissao-worker | head -20
```

Never wrap the whole script in `sudo bash` — root-owned files under
`/opt/nfse-app` break the next deploy.

## 5. Verify

- User tails logs: `sudo journalctl -u nfse-app -u nfse-emissao-worker -n 50 -f`
  (or the nfse-agent-readable file log if one is configured).
- Probe the HTTPS endpoint if there is a health route.
- Rollback = the same handoff shape with `git checkout <previous-sha>` + restart.
