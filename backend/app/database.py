from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Review, Work


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    with connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS works (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                phase TEXT NOT NULL,
                idea TEXT NOT NULL,
                hard_requirements TEXT NOT NULL,
                template_id TEXT NOT NULL,
                personas_json TEXT NOT NULL,
                repo_path TEXT NOT NULL,
                scriptorium_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                decision TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS review_style_profiles (
                created_by TEXT PRIMARY KEY,
                review_count INTEGER NOT NULL,
                average_comment_length REAL NOT NULL,
                decision_counts_json TEXT NOT NULL,
                style_summary TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def row_to_work(row: sqlite3.Row) -> Work:
    return Work(
        id=row["id"],
        work_id=row["work_id"],
        name=row["name"],
        phase=row["phase"],
        idea=row["idea"],
        hard_requirements=row["hard_requirements"],
        template_id=row["template_id"],
        personas=json.loads(row["personas_json"]),
        repo_path=row["repo_path"],
        scriptorium_path=row["scriptorium_path"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def row_to_review(row: sqlite3.Row) -> Review:
    return Review(
        id=row["id"],
        work_id=row["work_id"],
        stage=row["stage"],
        decision=row["decision"],
        comment=row["comment"],
        created_at=row["created_at"],
        created_by=row["created_by"],
    )
