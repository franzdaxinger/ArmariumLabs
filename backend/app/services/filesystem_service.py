from __future__ import annotations

import re
import shutil
from pathlib import Path


WORK_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ValidationError(ValueError):
    pass


def slugify_work_id(name: str) -> str:
    value = name.strip().lower()
    value = (
        value.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def validate_work_id(work_id: str) -> str:
    if not WORK_ID_PATTERN.fullmatch(work_id or ""):
        raise ValidationError("Work ID darf nur Kleinbuchstaben, Zahlen und Bindestriche enthalten.")
    return work_id


def ensure_not_exists(path: Path, label: str) -> None:
    if path.exists():
        raise ValidationError(f"{label} existiert bereits: {path}")


def copy_template(template_path: Path, target_path: Path) -> None:
    if not template_path.exists() or not template_path.is_dir():
        raise ValidationError(f"Bauplan existiert nicht: {template_path.name}")
    ensure_not_exists(target_path, "Werk")
    shutil.copytree(template_path, target_path)


def create_scriptorium_structure(path: Path) -> None:
    ensure_not_exists(path, "Skriptorium")
    for name in ["data", "databases", "uploads", "generated", "test-results", "builds", "logs"]:
        (path / name).mkdir(parents=True, exist_ok=True)


def replace_placeholders(root: Path, replacements: dict[str, str]) -> None:
    placeholders = {f"{{{{{key}}}}}": value for key, value in replacements.items()}
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        original = content
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, value)
        if content != original:
            path.write_text(content, encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(content)
