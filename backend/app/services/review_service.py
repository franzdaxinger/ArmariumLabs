from __future__ import annotations

from pathlib import Path

from ..config import REVIEW_DECISIONS, Settings
from ..database import connect, init_db, row_to_review
from ..models import Review
from . import filesystem_service, project_service
from .filesystem_service import ValidationError


def validate_decision(decision: str) -> str:
    if decision not in REVIEW_DECISIONS:
        raise ValidationError("Ungültige Review-Entscheidung: " + decision)
    return decision


def add_review(settings: Settings, work_id: str, decision: str, comment: str, created_by: str = "admin") -> Review:
    init_db(settings.db_path)
    work = project_service.require_work(settings, work_id)
    validate_decision(decision)
    created_at = project_service.now_iso()
    review = Review(
        id=None,
        work_id=work_id,
        stage=work.phase,
        decision=decision,
        comment=comment.strip(),
        created_at=created_at,
        created_by=created_by,
    )
    with connect(settings.db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO reviews (work_id, stage, decision, comment, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (review.work_id, review.stage, review.decision, review.comment, review.created_at, review.created_by),
        )
        conn.execute("UPDATE works SET updated_at = ? WHERE work_id = ?", (created_at, work_id))
        review.id = cursor.lastrowid

    entry = (
        f"\n## {created_at} - {decision}\n\n"
        f"- Phase: {work.phase}\n"
        f"- Person: {created_by}\n\n"
        f"{review.comment}\n"
    )
    filesystem_service.append_text(Path(work.repo_path) / "docs" / "05_acceptance_log.md", entry)
    return review


def list_reviews(settings: Settings, work_id: str) -> list[Review]:
    init_db(settings.db_path)
    with connect(settings.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM reviews WHERE work_id = ? ORDER BY created_at DESC, id DESC",
            (work_id,),
        ).fetchall()
    return [row_to_review(row) for row in rows]


def last_review(settings: Settings, work_id: str) -> Review | None:
    reviews = list_reviews(settings, work_id)
    return reviews[0] if reviews else None
