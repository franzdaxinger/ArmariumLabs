from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import DECISION_LABELS, PHASE_LABELS, Settings
from ..services import git_service, project_service, review_service
from .common import require_login


def router(settings: Settings, templates: Jinja2Templates) -> APIRouter:
    app = APIRouter()

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        user = require_login(request)
        if isinstance(user, RedirectResponse):
            return user
        works = []
        for work in project_service.list_works(settings):
            last = review_service.last_review(settings, work.work_id)
            works.append(
                {
                    "work": work,
                    "phase_label": PHASE_LABELS.get(work.phase, work.phase),
                    "git_status": git_service.status(Path(work.repo_path)),
                    "last_review": DECISION_LABELS.get(last.decision, last.decision) if last else "Noch keine Abnahme",
                    "next_action": project_service.next_action_for_phase(work.phase, last.decision if last else None),
                }
            )
        return templates.TemplateResponse("dashboard.html", {"request": request, "works": works, "user": user})

    return app
