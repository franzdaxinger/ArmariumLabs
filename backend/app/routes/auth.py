from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth import authenticate
from ..config import Settings


def router(settings: Settings, templates: Jinja2Templates) -> APIRouter:
    app = APIRouter()

    @app.get("/login", response_class=HTMLResponse)
    async def login_form(request: Request):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "default_login": settings.admin_username == "admin" and settings.admin_password == "1"},
        )

    @app.post("/login")
    async def login(request: Request):
        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))
        if authenticate(username, password, settings):
            request.session["user"] = username
            return RedirectResponse("/", status_code=303)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Login fehlgeschlagen.", "default_login": settings.admin_username == "admin" and settings.admin_password == "1"},
            status_code=401,
        )

    @app.post("/logout")
    async def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/login", status_code=303)

    return app
