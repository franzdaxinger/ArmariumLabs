from __future__ import annotations

from fastapi import Request
from fastapi.responses import RedirectResponse

from ..auth import REMEMBER_COOKIE_NAME, verify_remember_token


def current_user(request: Request) -> str | None:
    session_user = request.session.get("user")
    if session_user:
        return session_user
    settings = getattr(request.app.state, "settings", None)
    token = request.cookies.get(REMEMBER_COOKIE_NAME)
    if not settings or not token:
        return None
    remembered_user = verify_remember_token(token, settings)
    if remembered_user:
        request.session["user"] = remembered_user
    return remembered_user


def require_login(request: Request) -> str | RedirectResponse:
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return user
