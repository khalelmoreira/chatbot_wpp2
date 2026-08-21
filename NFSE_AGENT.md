<!-- Verified against the actual VPS (srv1896363) on 2026-08-21. Read this at the start of any nfse-agent session working against /opt/nfse-app — it's the practical companion to CLAUDE.md's "Production deployment (VPS)" section, which covers the *why*. -->

# nfse-agent on the VPS — practical notes

This file is about running Claude Code as the `nfse-agent` Unix user directly
on the production VPS, operating against `/opt/nfse-app` (the deployed app —
not this git checkout, which is a separate dev-only clone at
`~/chatbot_wpp2`). If you're working in a devcontainer or on your own laptop
instead, none of this applies.

## What nfse-agent can and can't touch on the VPS

- **No sudo, no group overlap with `nfse-app`.** Every access `nfse-agent`
  has to `/opt/nfse-app` is via POSIX ACLs (`setfacl`) on specific paths, not
  Unix group membership — that keeps the grant narrow and legible instead of
  "in the group, sees everything."
- **Read+traverse (`rX`) granted on:** `src/`, `tools/`, and a fixed
  allowlist of top-level files (`app.py`, `config.py`,
  `run_emissao_worker.py`, `backup_db.sh`, `requirements*.txt`,
  `pyproject.toml`, `pytest.ini`, `README.md`, `CLAUDE.md`, `MVP.md`,
  `task-aliquota-iss-rj.md`, `.env.example`). Default ACLs on `src/` and
  `tools/` mean files added there later inherit read access automatically —
  new top-level files do **not** and need an explicit `setfacl` grant.
- **Never grant read access to:** `.env` (prod secrets), `certs/` (the A1
  certificate), `backups/` (SQLite backup snapshots), `data/` (the live
  `whatsapp.db` — real customer conversation data, kept at `700`/`600`
  owner-only), `.git` (history may predate the data-hygiene fixes below),
  `.claude/settings.local.json`.
- **No write access, ever.** Deploys, `git pull`, restarts, and file edits on
  `/opt/nfse-app` happen as `nfse-app` or via `khalel`'s sudo — never from an
  `nfse-agent` session. If a task seems to need writing to `/opt/nfse-app`
  directly, that's a sign to hand the change back to the user instead of
  finding a way around it.
- ACL state isn't self-documenting from inside an `nfse-agent` session — if
  `Permission denied` shows up reading something under `src/` that should be
  readable, the grant may need re-running. `nfse-agent` has no sudo, so only
  the user can run `setfacl`.

## VPS shell quirks (each of these cost real time to figure out)

- The `acl` package isn't installed by default — `setfacl`/`getfacl` need
  `sudo apt-get install -y acl` first.
- `sudo` needs a real TTY. Commands relayed through this session's
  `!`-prefixed shell passthrough have no TTY attached, so `sudo` fails with
  *"a terminal is required to read the password."* Any command needing sudo
  has to be run by the user from their own actual SSH/terminal session, not
  executed by the agent.
- Long single-line commands with many space-separated arguments, or
  multi-line heredocs, can get silently reflowed or truncated when pasted
  into an interactive shell over SSH — symptoms include a heredoc that never
  terminates (looks like a hung shell) or a filename from the middle of a
  command line getting executed as its own bare command. Prefer one command
  per line, or have the user build a script with `nano` instead of pasting a
  `cat <<EOF` block.
- `nfse-agent`'s own scratchpad directory
  (`/tmp/claude-*/…/scratchpad/`) is `700`, owned by `nfse-agent` — other
  users, including `khalel`, cannot `cat`/`cp` a file from it even via
  `sudo -u nfse-agent` in some configurations. When the user needs to run
  something themselves, paste the script contents inline rather than
  handing them a path into that directory.

## Git push access

- This checkout's `origin` remote uses HTTPS with a fine-grained GitHub PAT
  (scoped to `chatbot_wpp2` only, Contents: Read/write), stored in
  `~/.git-credentials` (`chmod 600`, readable only by `nfse-agent`).
- Workflow: `nfse-agent` commits to and pushes the `nfse-agent` branch only.
  Merging into `main` is the user's call, done by them (PR or direct merge)
  — never push directly to `main` from this session.

## Data-hygiene incidents worth remembering

- `whatsapp.db` used to live at `src/database/whatsapp.db` — inside the code
  tree, and (as a result) tracked in git with real production-shaped data
  going back to the first commit. Moved to a sibling `data/` directory (see
  `src/database/CLAUDE.md`) and untracked going forward; the pre-existing
  git history still has it, and hasn't been scrubbed.
- During that migration, `mkdir -p` to create `data/` on the VPS left it
  world-readable (`other::r-x`, with the db file `other::r--`) under the
  shell's default umask — anyone on the box, not just `nfse-agent`, could
  have read it until this was caught and fixed. If `data/` or its contents
  ever need recreating, explicitly `chmod 700` the directory and `chmod 600`
  the db file rather than trusting the umask.
