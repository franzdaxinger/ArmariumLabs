from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from ..config import PHASE_ALIASES, PHASES, Settings
from ..database import connect, init_db, row_to_work
from ..models import Work
from . import filesystem_service, git_service, persona_service
from .filesystem_service import ValidationError


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def validate_phase(phase: str) -> str:
    phase = PHASE_ALIASES.get(phase, phase)
    if phase not in PHASES:
        raise ValidationError("Ungültige Pipeline-Stufe: " + phase)
    return phase


def list_templates(settings: Settings) -> list[str]:
    if not settings.templates_dir.exists():
        return []
    return sorted(path.name for path in settings.templates_dir.iterdir() if path.is_dir())


def list_works(settings: Settings) -> list[Work]:
    init_db(settings.db_path)
    with connect(settings.db_path) as conn:
        rows = conn.execute("SELECT * FROM works ORDER BY updated_at DESC, name ASC").fetchall()
    return [row_to_work(row) for row in rows]


def get_work(settings: Settings, work_id: str) -> Work | None:
    init_db(settings.db_path)
    with connect(settings.db_path) as conn:
        row = conn.execute("SELECT * FROM works WHERE work_id = ?", (work_id,)).fetchone()
    return row_to_work(row) if row else None


def require_work(settings: Settings, work_id: str) -> Work:
    work = get_work(settings, work_id)
    if not work:
        raise ValidationError("Werk nicht gefunden: " + work_id)
    return work


def read_work_file(work: Work, relative_path: str) -> str:
    path = Path(work.repo_path) / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def create_work(
    settings: Settings,
    name: str,
    work_id: str | None,
    idea: str,
    hard_requirements: str = "",
    template_id: str = "einfaches-werk",
    personas: list[str] | None = None,
) -> Work:
    init_db(settings.db_path)
    clean_name = name.strip()
    if not clean_name:
        raise ValidationError("Name ist erforderlich.")
    final_work_id = filesystem_service.validate_work_id(work_id.strip() if work_id else filesystem_service.slugify_work_id(clean_name))
    if get_work(settings, final_work_id):
        raise ValidationError("Werk existiert bereits in der Datenbank: " + final_work_id)

    selected_personas = personas or ["schatzmeister"]
    persona_service.validate_persona_ids(settings.personas_dir, selected_personas)

    template_path = settings.templates_dir / template_id
    repo_path = settings.works_dir / final_work_id
    scriptorium_path = settings.scriptorium_dir / final_work_id
    filesystem_service.ensure_not_exists(repo_path, "Werk")
    filesystem_service.ensure_not_exists(scriptorium_path, "Skriptorium")

    created_at = now_iso()
    filesystem_service.copy_template(template_path, repo_path)
    filesystem_service.create_scriptorium_structure(scriptorium_path)
    filesystem_service.replace_placeholders(
        repo_path,
        {
            "WORK_ID": final_work_id,
            "WORK_NAME": clean_name,
            "SCRIPTORIUM_PATH": str(scriptorium_path),
            "CREATED_AT": created_at,
            "PROJECT_IDEA": idea.strip(),
            "WERKIDEE": idea.strip(),
        },
    )

    filesystem_service.write_text(repo_path / "docs" / "00_idee.md", f"# Idee\n\n{idea.strip()}\n")
    filesystem_service.write_text(repo_path / "docs" / "01_hard_requirements.md", f"# Harte Requirements\n\n{hard_requirements.strip()}\n")
    filesystem_service.write_text(
        repo_path / "docs" / "02_selected_personas.yaml",
        yaml.safe_dump({"active_personas": selected_personas}, allow_unicode=True, sort_keys=False),
    )
    werk_yaml = {
        "work_id": final_work_id,
        "name": clean_name,
        "phase": "ideation",
        "scriptorium_path": str(scriptorium_path),
        "created_at": created_at,
        "active_personas": selected_personas,
    }
    filesystem_service.write_text(
        repo_path / "armarium.werk.yaml",
        yaml.safe_dump(werk_yaml, allow_unicode=True, sort_keys=False),
    )
    filesystem_service.write_text(
        repo_path / "docs" / "06_project_status.yaml",
        yaml.safe_dump({"phase": "ideation", "next_action": "Anforderungen klären und Abnahme dokumentieren."}, allow_unicode=True, sort_keys=False),
    )

    git_service.init_repo(repo_path)
    git_service.commit_all(repo_path, "Initial ArmariumLabs work")

    work = Work(
        id=None,
        work_id=final_work_id,
        name=clean_name,
        phase="ideation",
        idea=idea.strip(),
        hard_requirements=hard_requirements.strip(),
        template_id=template_id,
        personas=selected_personas,
        repo_path=str(repo_path),
        scriptorium_path=str(scriptorium_path),
        created_at=created_at,
        updated_at=created_at,
    )
    with connect(settings.db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO works (
                work_id, name, phase, idea, hard_requirements, template_id, personas_json,
                repo_path, scriptorium_path, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                work.work_id,
                work.name,
                work.phase,
                work.idea,
                work.hard_requirements,
                work.template_id,
                json.dumps(work.personas),
                work.repo_path,
                work.scriptorium_path,
                work.created_at,
                work.updated_at,
            ),
        )
        work.id = cursor.lastrowid
    return work


def set_phase(settings: Settings, work_id: str, phase: str) -> Work:
    phase = validate_phase(phase)
    work = require_work(settings, work_id)
    updated_at = now_iso()
    with connect(settings.db_path) as conn:
        conn.execute("UPDATE works SET phase = ?, updated_at = ? WHERE work_id = ?", (phase, updated_at, work_id))
    repo_path = Path(work.repo_path)
    filesystem_service.write_text(
        repo_path / "docs" / "06_project_status.yaml",
        yaml.safe_dump({"phase": phase, "next_action": next_action_for_phase(phase)}, allow_unicode=True, sort_keys=False),
    )
    return require_work(settings, work_id)


def next_action_for_phase(phase: str, last_decision: str | None = None) -> str:
    if last_decision == "request_changes":
        return "Änderungen einarbeiten und erneut zur Abnahme vorlegen."
    if last_decision == "approve":
        return "Nächste Pipeline-Stufe vorbereiten."
    return {
        "ideation": "Idee schärfen und Anforderungen sammeln.",
        "requirements_definition": "Anforderungen prüfen und Testfälle ableiten.",
        "test_plan_definition": "Testplan abnehmen und Bauphase vorbereiten.",
        "build_phase": "Umsetzung gegen freigegebene Anforderungen prüfen.",
        "review": "Lagebericht lesen und Entscheidung dokumentieren.",
        "acceptance": "Meisterstück final abnehmen oder offene Punkte notieren.",
    }.get(phase, "Status prüfen.")
