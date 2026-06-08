#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config import get_settings
from backend.app.services.bootstrap_service import bootstrap_armarium_root


def main() -> int:
    settings = get_settings()
    actions = bootstrap_armarium_root(settings, ROOT / "seed")
    if actions:
        for action in actions:
            print(action)
    else:
        print("ArmariumLabs root already initialized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
