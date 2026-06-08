from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PHASES = [
    "ideation",
    "requirements_definition",
    "test_plan_definition",
    "build_phase",
    "review",
    "acceptance",
]

PHASE_LABELS = {
    "ideation": "Ideenfindung",
    "requirements_definition": "Aufstellen Anforderungen",
    "test_plan_definition": "Aufstellen Testplan",
    "build_phase": "Bauphase",
    "review": "Prüfung",
    "acceptance": "Abnahme",
}

PHASE_ALIASES = {
    "testcases_review": "test_plan_definition",
}

REVIEW_DECISIONS = ["approve", "request_changes", "reject", "defer", "comment"]

DECISION_LABELS = {
    "approve": "Freigegeben",
    "request_changes": "Änderungen angefordert",
    "reject": "Abgelehnt",
    "defer": "Zurückgestellt",
    "comment": "Kommentar",
}


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    armarium_root: Path
    works_dir: Path
    scriptorium_dir: Path
    templates_dir: Path
    personas_dir: Path
    db_path: Path
    admin_username: str
    admin_password: str
    session_secret: str


def get_settings() -> Settings:
    repo_root = Path(__file__).resolve().parents[2]
    armarium_root = Path(os.environ.get("ARMARIUM_ROOT", "~/ArmariumLabs")).expanduser()
    return Settings(
        repo_root=repo_root,
        armarium_root=armarium_root,
        works_dir=armarium_root / "werke",
        scriptorium_dir=armarium_root / "skriptorium",
        templates_dir=armarium_root / "bauplaene",
        personas_dir=armarium_root / "personen",
        db_path=Path(os.environ.get("ARMARIUM_DB", repo_root / "armarium.sqlite3")).expanduser(),
        admin_username=os.environ.get("ARMARIUM_ADMIN_USERNAME", "admin"),
        admin_password=os.environ.get("ARMARIUM_ADMIN_PASSWORD", "1"),
        session_secret=os.environ.get("ARMARIUM_SESSION_SECRET", "change-this-local-secret"),
    )
