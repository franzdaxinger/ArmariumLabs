from __future__ import annotations

import os
import subprocess
import sys


def run_cli(settings, *args):
    env = os.environ.copy()
    env["ARMARIUM_ROOT"] = str(settings.armarium_root)
    env["ARMARIUM_DB"] = str(settings.db_path)
    return subprocess.run(
        [sys.executable, "scripts/armarium_cli.py", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )


def test_cli_list_and_status(settings):
    created = run_cli(settings, "create-work", "--name", "Todo App", "--work-id", "todo-app", "--idea", "Simple todo app")
    assert created.returncode == 0, created.stderr

    listed = run_cli(settings, "list")
    assert listed.returncode == 0
    assert "todo-app" in listed.stdout

    status = run_cli(settings, "status", "todo-app")
    assert status.returncode == 0
    assert "Git: clean" in status.stdout
