from __future__ import annotations

from fastapi import Request
from fastapi.responses import RedirectResponse


def current_user(request: Request) -> str | None:
    return request.session.get("user")


def require_login(request: Request) -> str | RedirectResponse:
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return user
