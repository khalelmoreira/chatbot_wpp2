<!-- Verified against the actual VPS (srv1896363) on 2026-08-21. Companion to CLAUDE.md's "Production deployment (VPS)" section. -->

# nfse-agent on the VPS — practical notes

Covers running Claude Code as `nfse-agent` on the production VPS, against
`/opt/nfse-app` (the deployed app — not this checkout, `~/chatbot_wpp2`).
Doesn't apply in a devcontainer or on your own laptop.

## What nfse-agent can and can't touch on the VPS

- No sudo, no group overlap with `nfse-app`. Access to `/opt/nfse-app` is
  via POSIX ACLs (`setfacl`) on specific paths only.
- Read+traverse (`rX`) granted on: `src/`, `tools/`, and a fixed allowlist
  of top-level files (`app.py`, `config.py`, `run_emissao_worker.py`,
  `backup_db.sh`, `requirements*.txt`, `pyproject.toml`, `pytest.ini`,
  `README.md`, `CLAUDE.md`, `MVP.md`, `task-aliquota-iss-rj.md`,
  `.env.example`). Default ACLs on `src/` and `tools/` propagate to new
  files automatically; new top-level files need an explicit `setfacl` grant.
- Never readable: `.env`, `certs/`, `backups/`, `data/` (live
  `whatsapp.db`, `700`/`600` owner-only), `.git`, `.claude/settings.local.json`.
- No write access, ever. Deploys, `git pull`, restarts, file edits on
  `/opt/nfse-app` happen as `nfse-app` or via khalel's sudo, never from
  `nfse-agent`. A task needing write access there goes back to the user.
- `Permission denied` under `src/` on something that should be readable →
  ACL grant needs re-running by the user (`nfse-agent` has no sudo).

## VPS shell quirks

- `acl` package isn't installed by default: `sudo apt-get install -y acl`
  first for `setfacl`/`getfacl`.
- `sudo` needs a real TTY — fails over the `!`-prefixed shell passthrough
  ("a terminal is required to read the password"). Anything needing sudo
  runs from the user's own SSH/terminal session.
- Long single-line commands and multi-line heredocs can get reflowed or
  truncated when pasted over SSH — symptoms: a heredoc that never
  terminates, or a mid-command filename executed as its own bare command.
  Prefer one command per line, or use the `~/handoff/` mechanism below.
- `nfse-agent`'s scratchpad (`/tmp/claude-*/…/scratchpad/`) is `700`,
  owned by `nfse-agent` — khalel can't read it, even via `sudo -u`. Don't
  hand the user a path into it; use `~/handoff/` instead.

## Handing commands to the user for execution

`nfse-agent` has write-only POSIX ACL access to `~khalel/handoff/`
(khalel's directory, `chmod 750`, otherwise inaccessible to `nfse-agent`).

For any command only khalel can run (sudo, service restarts, anything
under `/opt/nfse-app`):

1. Write the command(s) as a script to `~khalel/handoff/<name>.sh` instead
   of dictating them in chat for khalel to paste.
2. Always explain the script in the same turn: what it does, why it's
   needed. Never write one silently.
3. khalel reviews (`less ~/handoff/<name>.sh`) and runs it — see below for
   which identity.

`nfse-agent` still can't execute anything itself or read khalel's other
files.

### Match the identity in the script to the identity that should own the result

Don't default a handoff script to `sudo bash ...` (runs as root) just
because it needs elevated access. Anything that writes inside
`/opt/nfse-app` — `git pull`, `pip install`, file edits — must run as the
`nfse-app` user (`sudo -u nfse-app bash -c '...'` or a `sudo -u nfse-app
bash <<'EOF' ... EOF` heredoc inside the script), not as root, or the
files it touches end up owned by `root:root` instead of `nfse-app:nfse-app`
— breaking the *next* deploy once it's run correctly as `nfse-app`, since
that user then lacks write access to its own tree. Only steps that
actually require root (`systemctl restart`, `setfacl`, `apt-get install`)
should use plain `sudo`. A script mixing both needs both: elevate each
step to the minimum identity it needs, don't wrap the whole thing in one
`sudo bash`.

Got this wrong twice in a row (2026-08-27) — two deploy scripts run via
`sudo bash` left `/opt/nfse-app`'s git-tracked files root-owned, caught
only when a subsequent script needed to `cd`/write as khalel/nfse-app and
hit `Permission denied`. Fixed with a one-time `chown -R nfse-app:nfse-app
/opt/nfse-app`, run via a handoff script.

## Git push access

- `origin` uses HTTPS with a fine-grained GitHub PAT (scoped to
  `chatbot_wpp2`, Contents: Read/write), in `~/.git-credentials`
  (`chmod 600`, `nfse-agent`-only).
- `nfse-agent` commits and pushes to the `nfse-agent` branch only. Merging
  into `main` is the user's call — never push directly to `main`.

## Data-hygiene incidents

- `whatsapp.db` used to live at `src/database/whatsapp.db`, tracked in git
  with real production data since the first commit. Moved to `data/` (see
  `src/database/CLAUDE.md`) and untracked; existing git history still has
  it, unscrubbed.
- During that migration, `mkdir -p` for `data/` left it world-readable
  (`other::r-x`, db file `other::r--`) under the shell's default umask
  until caught and fixed. If recreating `data/`, explicitly `chmod 700`
  the directory and `chmod 600` the db file.
