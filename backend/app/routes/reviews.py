from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import Settings
from ..services import review_service
from ..services.filesystem_service import ValidationError
from .common import require_login


def router(settings: Settings, templates: Jinja2Templates) -> APIRouter:
    app = APIRouter()

    @app.post("/works/{work_id}/reviews")
    async def add_review(request: Request, work_id: str):
        user = require_login(request)
        if isinstance(user, RedirectResponse):
            return user
        form = await request.form()
        try:
            review_service.add_review(
                settings,
                work_id=work_id,
                decision=str(form.get("decision", "")),
                comment=str(form.get("comment", "")),
                created_by=str(user),
            )
        except ValidationError as exc:
            return templates.TemplateResponse("error.html", {"request": request, "message": str(exc)}, status_code=400)
        return RedirectResponse(f"/works/{work_id}", status_code=303)

    return app
