"""Хранение прогресса пользователя (SQLite)."""
from __future__ import annotations

import os
import sqlite3
import time
from typing import Iterable

from .config import DATA_DIR, DB_PATH

_conn: sqlite3.Connection | None = None


def _db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.execute("""CREATE TABLE IF NOT EXISTS progress (
            user_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            done INTEGER DEFAULT 1,
            attempts INTEGER DEFAULT 1,
            updated_at REAL,
            PRIMARY KEY (user_id, task_id)
        )""")
        _conn.execute("""CREATE TABLE IF NOT EXISTS unlocks (
            user_id TEXT PRIMARY KEY,
            until REAL
        )""")
        _conn.commit()
    return _conn


def get_progress(user_id: str) -> dict[str, dict]:
    cur = _db().execute(
        "SELECT task_id, done, attempts, updated_at FROM progress WHERE user_id = ?",
        (user_id,))
    return {
        row[0]: {"done": bool(row[1]), "attempts": row[2], "updated_at": row[3]}
        for row in cur.fetchall()
    }


def mark(user_id: str, task_id: str, done: bool = True) -> None:
    db = _db()
    row = db.execute(
        "SELECT attempts FROM progress WHERE user_id=? AND task_id=?",
        (user_id, task_id)).fetchone()
    attempts = (row[0] if row else 0) + 1
    db.execute(
        """INSERT INTO progress (user_id, task_id, done, attempts, updated_at)
           VALUES (?,?,?,?,?)
           ON CONFLICT(user_id, task_id) DO UPDATE SET
             done=excluded.done, attempts=excluded.attempts, updated_at=excluded.updated_at""",
        (user_id, task_id, 1 if done else 0, attempts, time.time()))
    db.commit()


def reset(user_id: str) -> None:
    db = _db()
    db.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
    db.commit()


def summary(user_id: str, task_ids: Iterable[str]) -> dict:
    prog = get_progress(user_id)
    total = len(list(task_ids))
    done = sum(1 for t in prog if prog[t]["done"])
    return {"total": total, "done": done, "percent": round(done * 100 / total, 1) if total else 0.0}


# ---------------- разблокировка копирования ----------------
def set_unlock(user_id: str, until: float) -> None:
    db = _db()
    db.execute(
        "INSERT INTO unlocks (user_id, until) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET until = excluded.until",
        (user_id, until))
    db.commit()


def clear_unlock(user_id: str) -> None:
    db = _db()
    db.execute("DELETE FROM unlocks WHERE user_id = ?", (user_id,))
    db.commit()


def is_unlocked(user_id: str) -> bool:
    db = _db()
    row = db.execute("SELECT until FROM unlocks WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        return False
    if row[0] and row[0] > time.time():
        return True
    clear_unlock(user_id)
    return False
