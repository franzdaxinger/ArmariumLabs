from __future__ import annotations

import json

from ..config import Settings
from ..database import connect, init_db
from ..models import Review


def _style_summary(review_count: int, average_length: float, decision_counts: dict[str, int]) -> str:
    if review_count == 0:
        return "Noch kein Review-Stil gespeichert."
    dominant_decision = max(decision_counts, key=decision_counts.get)
    length_label = "knapp" if average_length < 80 else "ausführlich" if average_length > 220 else "mittel"
    return f"{length_label}, meist {dominant_decision}, basiert auf {review_count} Reviews"


def update_review_style(settings: Settings, review: Review) -> None:
    init_db(settings.db_path)
    comment_length = len(review.comment)
    with connect(settings.db_path) as conn:
        row = conn.execute(
            "SELECT * FROM review_style_profiles WHERE created_by = ?",
            (review.created_by,),
        ).fetchone()
        if row:
            review_count = int(row["review_count"]) + 1
            old_average = float(row["average_comment_length"])
            average_length = ((old_average * (review_count - 1)) + comment_length) / review_count
            decision_counts = json.loads(row["decision_counts_json"])
            decision_counts[review.decision] = decision_counts.get(review.decision, 0) + 1
        else:
            review_count = 1
            average_length = float(comment_length)
            decision_counts = {review.decision: 1}

        conn.execute(
            """
            INSERT INTO review_style_profiles (
                created_by, review_count, average_comment_length, decision_counts_json, style_summary, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(created_by) DO UPDATE SET
                review_count = excluded.review_count,
                average_comment_length = excluded.average_comment_length,
                decision_counts_json = excluded.decision_counts_json,
                style_summary = excluded.style_summary,
                updated_at = excluded.updated_at
            """,
            (
                review.created_by,
                review_count,
                average_length,
                json.dumps(decision_counts, sort_keys=True),
                _style_summary(review_count, average_length, decision_counts),
                review.created_at,
            ),
        )


def get_review_style(settings: Settings, created_by: str) -> dict | None:
    init_db(settings.db_path)
    with connect(settings.db_path) as conn:
        row = conn.execute(
            "SELECT * FROM review_style_profiles WHERE created_by = ?",
            (created_by,),
        ).fetchone()
    if not row:
        return None
    return {
        "created_by": row["created_by"],
        "review_count": row["review_count"],
        "average_comment_length": row["average_comment_length"],
        "decision_counts": json.loads(row["decision_counts_json"]),
        "style_summary": row["style_summary"],
        "updated_at": row["updated_at"],
    }
