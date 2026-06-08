from __future__ import annotations

import shutil
from pathlib import Path

from ..config import Settings


def bootstrap_armarium_root(settings: Settings, seed_dir: Path) -> list[str]:
    """Create the external ArmariumLabs folder layout and copy missing defaults."""
    actions: list[str] = []
    for path in [settings.works_dir, settings.scriptorium_dir, settings.templates_dir, settings.personas_dir]:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            actions.append(f"created {path}")

    seed_templates = seed_dir / "bauplaene"
    if seed_templates.exists():
        for source in sorted(path for path in seed_templates.iterdir() if path.is_dir()):
            target = settings.templates_dir / source.name
            if not target.exists():
                shutil.copytree(source, target)
                actions.append(f"copied {target}")

    seed_personas = seed_dir / "personen"
    if seed_personas.exists():
        for source in sorted(path for path in seed_personas.rglob("*") if path.is_file()):
            relative = source.relative_to(seed_personas)
            target = settings.personas_dir / relative
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                actions.append(f"copied {target}")

    return actions
