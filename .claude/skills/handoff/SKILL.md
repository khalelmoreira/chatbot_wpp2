---
name: handoff
description: Format a privileged command as a reviewed script in ~khalel/handoff/ for the user to run.
---

# /handoff — hand a privileged command to khalel

Claude (`nfse-agent`) has write-only ACL access to `~khalel/handoff/` and nothing
else of khalel's. Use this for anything needing sudo, a service restart, or a
write under `/opt/nfse-app`.

## Rules

- Write **one** script to `~khalel/handoff/<verb>-<YYYY-MM-DD>.sh`, starting with
  `set -euo pipefail`, safe to run top to bottom. Do not dictate commands in chat
  for the user to paste.
- In the same message, explain what the script does and why. Never write one
  silently.
- Absolute paths only. The `/opt/nfse-app` venv is `venv/bin/python` after
  `cd /opt/nfse-app` — never `.venv`.
- Match identity to whoever should own the result:
  - writes under `/opt/nfse-app` (`git pull`, `pip install`, file edits) →
    `sudo -u nfse-app bash <<'EOF' … EOF`
  - true root only (`systemctl`, `setfacl`, `apt-get`) → plain `sudo`
  - **never** wrap the whole script in `sudo bash` — root-owned files break the
    next deploy.
- End with a one-line verification command.
- Tell the user: review with `less ~/handoff/<name>.sh`, then run it.

## After the user runs it

- If it created files under `/opt/nfse-app`, confirm ownership is
  `nfse-app:nfse-app`; if not, follow up with a `chown -R nfse-app:nfse-app`
  script.
