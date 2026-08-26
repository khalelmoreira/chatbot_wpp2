<!-- Verified against the actual repo on 2026-08-21. Loads only when Claude Code reads files in src/database/. -->

# DB layer conventions (src/database/)

- Runtime SQLite file: `data/whatsapp.db` (repo root, sibling to `src/`), not in this directory. Untracked (`.gitignore`). `config.DB_PATH` is the source of truth and creates the parent dir if missing.
- `DB` (`db.py`) wraps sqlite3. Generic helpers: `select`, `select_one`, `insert`, `update`, `update_guarded`. Prefer these over hand-written SQL.
- `insert(table, data, returning=None)` returns `lastrowid` by default; pass `returning="col"` for a DB-generated value instead.
- `update(table, data, where)` is unconditional — no previous-state check, no returned row. Use for transitions that don't depend on current status.
- `update_guarded(table, data, where, returning="id")` is for conditional transitions; builds `RETURNING` for you — `where` should include the expected current status (e.g. `{"id": id, "status": "CERTIFICATE"}`). Returns `None` on guard failure — treat as a real failure, not a silent no-op.
- Raw `fetchone`, `fetchall`, `fetchone_exe`, `exe` exist for custom SQL (e.g. `JOIN`s). Mark with a `# SQL explícito:` comment naming why the generic helpers don't fit — not applied everywhere yet, but apply it to new hand-written queries.
- No `fetchone_modif` — `UPDATE ... RETURNING` via raw SQL uses `fetchone_exe`.
- `NULL` means absence, full stop. Never conflate with `0`, `''`, or `false`.
