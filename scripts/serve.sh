#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/setup_runtime.sh
. .venv/bin/activate

exec uvicorn backend.app.main:app --host "${ARMARIUM_HOST:-127.0.0.1}" --port "${ARMARIUM_PORT:-8000}"
