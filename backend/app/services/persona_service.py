from __future__ import annotations

from pathlib import Path

import yaml

from .filesystem_service import ValidationError


def load_personas(personas_dir: Path) -> list[dict]:
    global_dir = personas_dir / "global"
    if not global_dir.exists():
        return []
    personas: list[dict] = []
    for path in sorted(global_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ValidationError(f"Personendatei ist nicht lesbar: {path.name}") from exc
        data["_path"] = str(path)
        personas.append(data)
    return personas


def get_persona_map(personas_dir: Path) -> dict[str, dict]:
    return {persona.get("id", ""): persona for persona in load_personas(personas_dir)}


def validate_persona_ids(personas_dir: Path, persona_ids: list[str]) -> None:
    known = get_persona_map(personas_dir)
    missing = [persona_id for persona_id in persona_ids if persona_id not in known]
    if missing:
        raise ValidationError("Unbekannte Personen: " + ", ".join(missing))
