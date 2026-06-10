import sqlite3
from typing import Dict, List

_DB_PATH = None


def init_db(path: str):
    """Initialize the SQLite database and create tables."""
    global _DB_PATH
    _DB_PATH = path
    conn = sqlite3.connect(_DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS activities (
            name TEXT PRIMARY KEY,
            description TEXT,
            schedule TEXT,
            max_participants INTEGER
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_name TEXT,
            email TEXT,
            UNIQUE(activity_name, email)
        )
        """
    )
    conn.commit()
    conn.close()


def _get_conn():
    if not _DB_PATH:
        raise RuntimeError("Database not initialized. Call init_db(path) first.")
    return sqlite3.connect(_DB_PATH)


def import_activities(activities: Dict[str, Dict]):
    """Import initial activities dict into the database.
    Existing rows are ignored.
    """
    conn = _get_conn()
    c = conn.cursor()
    for name, meta in activities.items():
        maxp = meta.get("max_participants")
        description = meta.get("description")
        schedule = meta.get("schedule")
        try:
            c.execute(
                "INSERT OR IGNORE INTO activities (name, description, schedule, max_participants) VALUES (?, ?, ?, ?)",
                (name, description, schedule, maxp),
            )
        except Exception:
            continue
        participants = meta.get("participants", []) or []
        for email in participants:
            try:
                c.execute(
                    "INSERT OR IGNORE INTO participants (activity_name, email) VALUES (?, ?)",
                    (name, email),
                )
            except Exception:
                continue
    conn.commit()
    conn.close()


def get_activities() -> Dict[str, Dict]:
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT name, description, schedule, max_participants FROM activities")
    rows = c.fetchall()
    result = {}
    for name, description, schedule, max_participants in rows:
        c.execute(
            "SELECT email FROM participants WHERE activity_name = ?",
            (name,),
        )
        participants = [r[0] for r in c.fetchall()]
        result[name] = {
            "description": description,
            "schedule": schedule,
            "max_participants": max_participants,
            "participants": participants,
        }
    conn.close()
    return result


def add_participant(activity_name: str, email: str):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT max_participants FROM activities WHERE name = ?",
        (activity_name,),
    )
    row = c.fetchone()
    if not row:
        conn.close()
        raise LookupError("Activity not found")
    maxp = row[0]
    c.execute(
        "SELECT COUNT(*) FROM participants WHERE activity_name = ?",
        (activity_name,),
    )
    count = c.fetchone()[0]
    if maxp is not None and count >= maxp:
        conn.close()
        raise ValueError("Activity is full")
    # Check existing
    c.execute(
        "SELECT 1 FROM participants WHERE activity_name = ? AND email = ?",
        (activity_name, email),
    )
    if c.fetchone():
        conn.close()
        raise ValueError("Student is already signed up")
    c.execute(
        "INSERT INTO participants (activity_name, email) VALUES (?, ?)",
        (activity_name, email),
    )
    conn.commit()
    conn.close()


def remove_participant(activity_name: str, email: str):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM activities WHERE name = ?",
        (activity_name,),
    )
    if not c.fetchone():
        conn.close()
        raise LookupError("Activity not found")
    c.execute(
        "SELECT 1 FROM participants WHERE activity_name = ? AND email = ?",
        (activity_name, email),
    )
    if not c.fetchone():
        conn.close()
        raise ValueError("Student is not signed up for this activity")
    c.execute(
        "DELETE FROM participants WHERE activity_name = ? AND email = ?",
        (activity_name, email),
    )
    conn.commit()
    conn.close()
