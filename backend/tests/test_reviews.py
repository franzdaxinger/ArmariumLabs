from pathlib import Path

from backend.app.services import project_service, review_service, style_service


def test_review_is_saved_to_db_and_acceptance_log(settings):
    work = project_service.create_work(settings, "Todo App", "todo-app", "Simple todo app")
    review = review_service.add_review(settings, "todo-app", "approve", "Freigegeben", "admin")

    reviews = review_service.list_reviews(settings, "todo-app")
    assert reviews[0].id == review.id
    assert reviews[0].decision == "approve"
    log = (Path(work.repo_path) / "docs" / "05_acceptance_log.md").read_text(encoding="utf-8")
    assert "Freigegeben" in log
    assert "approve" in log


def test_review_updates_user_style_profile(settings):
    project_service.create_work(settings, "Todo App", "todo-app", "Simple todo app")

    review_service.add_review(settings, "todo-app", "comment", "Kurz geprüft.", "admin")
    review_service.add_review(settings, "todo-app", "approve", "Ausführlicher Kommentar mit klarem Entscheid.", "admin")

    profile = style_service.get_review_style(settings, "admin")
    assert profile is not None
    assert profile["review_count"] == 2
    assert profile["decision_counts"] == {"approve": 1, "comment": 1}
    assert "basiert auf 2 Reviews" in profile["style_summary"]
