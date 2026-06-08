from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.config import Settings
from backend.app.database import init_db


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    root = tmp_path / "ArmariumLabs"
    repo = tmp_path / "core"
    templates = root / "bauplaene" / "einfaches-werk"
    docs = templates / "docs"
    docs.mkdir(parents=True)
    (templates / "README.md").write_text("# {{WORK_NAME}}\n{{PROJECT_IDEA}}\n", encoding="utf-8")
    (templates / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    (templates / "armarium.werk.yaml").write_text(
        "work_id: '{{WORK_ID}}'\nname: '{{WORK_NAME}}'\nphase: idea_draft\nscriptorium_path: '{{SCRIPTORIUM_PATH}}'\n",
        encoding="utf-8",
    )
    for name in [
        "00_idee.md",
        "01_stakeholders.md",
        "02_functional_requirements.yaml",
        "03_technical_requirements.yaml",
        "04_testcases.yaml",
        "05_acceptance_log.md",
        "06_project_status.yaml",
    ]:
        (docs / name).write_text("", encoding="utf-8")
    personas = root / "personen" / "global"
    personas.mkdir(parents=True)
    (personas / "schatzmeister.yaml").write_text(
        "id: schatzmeister\nname: Schatzmeister\ntitel: Kostenblick\nregeln:\n  - Einfach halten.\n",
        encoding="utf-8",
    )
    value = Settings(
        repo_root=repo,
        armarium_root=root,
        works_dir=root / "werke",
        scriptorium_dir=root / "skriptorium",
        templates_dir=root / "bauplaene",
        personas_dir=root / "personen",
        db_path=repo / "armarium.sqlite3",
        admin_username="admin",
        admin_password="1",
        session_secret="test-secret",
    )
    init_db(value.db_path)
    return value
