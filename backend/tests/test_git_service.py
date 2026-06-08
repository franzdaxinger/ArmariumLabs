from pathlib import Path

from backend.app.services import git_service, project_service


def test_git_status_unknown(tmp_path):
    path = tmp_path / "not-a-repo"
    path.mkdir()
    assert git_service.status(path) == "unknown"


def test_git_status_clean_and_dirty(settings):
    work = project_service.create_work(settings, "Todo App", "todo-app", "Simple todo app")
    repo = Path(work.repo_path)
    assert git_service.status(repo) == "clean"
    (repo / "dirty.txt").write_text("changed", encoding="utf-8")
    assert git_service.status(repo) == "dirty"
