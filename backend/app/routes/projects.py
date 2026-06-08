from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import DECISION_LABELS, PHASE_LABELS, PHASES, Settings
from ..services import git_service, persona_service, project_service, review_service, style_service
from ..services.filesystem_service import ValidationError
from .common import require_login


def router(settings: Settings, templates: Jinja2Templates) -> APIRouter:
    app = APIRouter()

    @app.get("/works/new", response_class=HTMLResponse)
    async def new_project(request: Request):
        user = require_login(request)
        if isinstance(user, RedirectResponse):
            return user
        return templates.TemplateResponse(
            "new_project.html",
            {
                "request": request,
                "templates": project_service.list_templates(settings),
                "personas": persona_service.load_personas(settings.personas_dir),
                "selected_personas": ["schatzmeister"],
                "default_template": "einfaches-werk",
            },
        )

    @app.post("/works")
    async def create_project(request: Request):
        user = require_login(request)
        if isinstance(user, RedirectResponse):
            return user
        form = await request.form()
        selected_personas = [str(value) for value in form.getlist("personas")]
        try:
            work = project_service.create_work(
                settings,
                name=str(form.get("name", "")),
                work_id=str(form.get("work_id", "")),
                idea=str(form.get("idea", "")),
                hard_requirements=str(form.get("hard_requirements", "")),
                template_id=str(form.get("template_id", "einfaches-werk")),
                personas=selected_personas or ["schatzmeister"],
            )
        except ValidationError as exc:
            return templates.TemplateResponse(
                "new_project.html",
                {
                    "request": request,
                    "error": str(exc),
                    "form": form,
                    "templates": project_service.list_templates(settings),
                    "personas": persona_service.load_personas(settings.personas_dir),
                    "selected_personas": selected_personas or ["schatzmeister"],
                    "default_template": str(form.get("template_id", "einfaches-werk")),
                },
                status_code=400,
            )
        return RedirectResponse(f"/works/{work.work_id}", status_code=303)

    @app.get("/works/{work_id}", response_class=HTMLResponse)
    async def project_detail(request: Request, work_id: str):
        user = require_login(request)
        if isinstance(user, RedirectResponse):
            return user
        try:
            work = project_service.require_work(settings, work_id)
        except ValidationError as exc:
            return templates.TemplateResponse("error.html", {"request": request, "message": str(exc)}, status_code=404)
        reviews = review_service.list_reviews(settings, work_id)
        persona_map = persona_service.get_persona_map(settings.personas_dir)
        active_personas = [persona_map[persona_id] for persona_id in work.personas if persona_id in persona_map]
        last = reviews[0] if reviews else None
        return templates.TemplateResponse(
            "project_detail.html",
            {
                "request": request,
                "work": work,
                "phase_label": PHASE_LABELS.get(work.phase, work.phase),
                "phase_labels": PHASE_LABELS,
                "phases": PHASES,
                "git_status": git_service.status(Path(work.repo_path)),
                "idea": project_service.read_work_file(work, "docs/00_idee.md"),
                "hard_requirements": project_service.read_work_file(work, "docs/01_hard_requirements.md"),
                "active_personas": active_personas,
                "reviews": reviews,
                "review_style": style_service.get_review_style(settings, str(user)),
                "decision_labels": DECISION_LABELS,
                "next_action": project_service.next_action_for_phase(work.phase, last.decision if last else None),
            },
        )

    @app.post("/works/{work_id}/phase")
    async def set_phase(request: Request, work_id: str):
        user = require_login(request)
        if isinstance(user, RedirectResponse):
            return user
        form = await request.form()
        try:
            project_service.set_phase(settings, work_id, str(form.get("phase", "")))
        except ValidationError as exc:
            return templates.TemplateResponse("error.html", {"request": request, "message": str(exc)}, status_code=400)
        return RedirectResponse(f"/works/{work_id}", status_code=303)

    return app
