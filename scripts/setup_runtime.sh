#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate

if ! python -c "import fastapi, uvicorn, jinja2, yaml" >/dev/null 2>&1; then
  pip install -r backend/requirements.txt
fi

python scripts/bootstrap.py

python - <<'PY'
from backend.app.config import get_settings
from backend.app.database import init_db

init_db(get_settings().db_path)
PY
