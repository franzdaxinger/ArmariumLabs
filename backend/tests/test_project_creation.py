from pathlib import Path

import yaml

from backend.app.services.filesystem_service import ValidationError
from backend.app.services import project_service


def test_create_work_from_template(settings):
    work = project_service.create_work(settings, "Todo App", "", "Simple todo app", "Must be local")

    repo = Path(work.repo_path)
    scriptorium = Path(work.scriptorium_path)
    assert repo.exists()
    assert (repo / ".git").exists()
    assert (repo / "docs" / "00_idee.md").read_text(encoding="utf-8").strip().endswith("Simple todo app")
    assert (repo / "docs" / "01_hard_requirements.md").read_text(encoding="utf-8").strip().endswith("Must be local")
    assert yaml.safe_load((repo / "docs" / "02_selected_personas.yaml").read_text(encoding="utf-8")) == {
        "active_personas": ["schatzmeister"]
    }
    for name in ["data", "databases", "uploads", "generated", "test-results", "builds", "logs"]:
        assert (scriptorium / name).is_dir()


def test_create_work_prevents_duplicates(settings):
    project_service.create_work(settings, "Todo App", "todo-app", "Simple todo app")
    try:
        project_service.create_work(settings, "Todo App", "todo-app", "Simple todo app")
    except ValidationError:
        pass
    else:
        raise AssertionError("duplicate work was allowed")


def test_set_phase(settings):
    project_service.create_work(settings, "Todo App", "todo-app", "Simple todo app")
    work = project_service.set_phase(settings, "todo-app", "review")
    assert work.phase == "review"


def test_set_phase_accepts_documented_cli_alias(settings):
    project_service.create_work(settings, "Todo App", "todo-app", "Simple todo app")
    work = project_service.set_phase(settings, "todo-app", "testcases_review")
    assert work.phase == "test_plan_definition"
