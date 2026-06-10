Title: Persist activities to SQLite (fixes #12)

Summary
- Replace the current in-memory activity store with a persistent SQLite database so activity, signup, and attendance data survive restarts.

Why
- Data loss on restart prevents reliable admin features and real-world usage.

Changes proposed
- Backend (`src/app.py`):
  - Add a `models` layer using `sqlite3` (or SQLAlchemy if preferred).
  - Replace in-memory list with DB queries for activities, signups, and attendance.
  - Add simple data migration: if `data/activities.json` exists, import into DB on first run.
  - Add configuration option `DATABASE_URL` (default: `data/db.sqlite`).
- New files:
  - `data/` directory to store `db.sqlite` and optional `activities.json`.
- Frontend (`static/app.js`):
  - Update fetch calls to expect persisted endpoints (no shape change required).

Testing
- Start the app and create an activity via the UI; restart server; verify activity persists.
- Run quick script `scripts/dump_activities.py` to show DB rows (optional).

Rollback/Migration
- Keep previous in-memory path as fallback for one release only.

Checklist
- [ ] Implement DB models and migration
- [ ] Update endpoints in `src/app.py`
- [ ] Add tests or manual verification steps
- [ ] Update README with migration/run steps

Notes
- This is intentionally lightweight; use `sqlite3` to avoid adding heavy deps. If you prefer `SQLAlchemy`, I can update the draft to include `requirements.txt` changes.