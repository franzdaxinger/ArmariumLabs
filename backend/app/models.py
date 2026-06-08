from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Work:
    id: int | None
    work_id: str
    name: str
    phase: str
    idea: str
    hard_requirements: str
    template_id: str
    personas: list[str]
    repo_path: str
    scriptorium_path: str
    created_at: str
    updated_at: str


@dataclass
class Review:
    id: int | None
    work_id: str
    stage: str
    decision: str
    comment: str
    created_at: str
    created_by: str
