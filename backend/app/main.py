from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings
from .database import init_db
from .routes import auth, dashboard, projects, reviews


settings = get_settings()
templates = Jinja2Templates(directory=str(settings.repo_root / "backend" / "app" / "templates"))

app = FastAPI(title="ArmariumLabs")
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, same_site="lax")
app.mount("/static", StaticFiles(directory=str(settings.repo_root / "backend" / "app" / "static")), name="static")


@app.on_event("startup")
async def startup() -> None:
    init_db(settings.db_path)


app.include_router(auth.router(settings, templates))
app.include_router(dashboard.router(settings, templates))
app.include_router(projects.router(settings, templates))
app.include_router(reviews.router(settings, templates))
