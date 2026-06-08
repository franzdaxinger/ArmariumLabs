from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth import REMEMBER_COOKIE_MAX_AGE, REMEMBER_COOKIE_NAME, authenticate, create_remember_token
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
        remember_me = form.get("remember_me") == "yes"
        if authenticate(username, password, settings):
            request.session["user"] = username
            response = RedirectResponse("/", status_code=303)
            if remember_me:
                response.set_cookie(
                    REMEMBER_COOKIE_NAME,
                    create_remember_token(username, settings),
                    max_age=REMEMBER_COOKIE_MAX_AGE,
                    httponly=True,
                    samesite="lax",
                )
            else:
                response.delete_cookie(REMEMBER_COOKIE_NAME)
            return response
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Login fehlgeschlagen.", "default_login": settings.admin_username == "admin" and settings.admin_password == "1"},
            status_code=401,
        )

    @app.post("/logout")
    async def logout(request: Request):
        request.session.clear()
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie(REMEMBER_COOKIE_NAME)
        return response

    return app
