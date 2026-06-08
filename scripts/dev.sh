#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r backend/requirements.txt

python scripts/bootstrap.py

python - <<'PY'
from backend.app.config import get_settings
from backend.app.database import init_db

init_db(get_settings().db_path)
PY

uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
