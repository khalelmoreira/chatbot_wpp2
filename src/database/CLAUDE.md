<!-- Verified against the actual repo on 2026-08-21. Loads only when Claude Code reads files in src/database/. -->

# DB layer conventions (src/database/)

- The runtime SQLite file itself lives at `data/whatsapp.db` (repo root, sibling to `src/`), not in this directory — moved out of `src/database/` so app data isn't mixed into the code tree, and untracked from git (`.gitignore`) since it holds real prestador/conversation data. `config.DB_PATH` is the source of truth for the path and creates the parent dir if it doesn't exist yet.
- `DB` (`db.py`) wraps sqlite3. Generic helpers: `select`, `select_one`, `insert`, `update`, `update_guarded`. Prefer these over hand-written SQL.
- `insert(table, data, returning=None)` returns `lastrowid` by default; pass `returning="col"` to get a DB-generated value back instead (e.g. a non-autoincrement key, or a default like a timestamp).
- `update(table, data, where)` is unconditional — no previous-state check, no returned row. Use it when the transition doesn't depend on the current status.
- `update_guarded(table, data, where, returning="id")` is for conditional transitions and already builds `RETURNING` for you — pass a `where` that includes the expected current status (e.g. `{"id": id, "status": "CERTIFICATE"}`). Returns `None` when the guard fails (no row matched), which the caller should treat as a real failure, not silently ignore.
- Raw `fetchone`, `fetchall`, `fetchone_exe`, `exe` exist for genuinely custom SQL (e.g. `JOIN`s the generic helpers can't express). Mark that kind of block with a `# SQL explícito:` comment explaining *why* the generic helpers don't fit — this convention exists in the codebase but isn't applied everywhere yet, so apply it wherever you add a hand-written query rather than treating its absence elsewhere as license to skip it.
- There's no `fetchone_modif` — the method for `UPDATE ... RETURNING` via raw SQL is `fetchone_exe`.
- `NULL` means absence, full stop. Never write a query or schema default that conflates `NULL` with `0`, `''`, or `false`.
