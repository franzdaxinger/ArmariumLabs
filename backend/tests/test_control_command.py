from __future__ import annotations

import subprocess
import os
from pathlib import Path


def test_control_command_help():
    result = subprocess.run(
        ["scripts/ArmariumLabs", "--help"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0
    assert "ArmariumLabs --status" in result.stdout


def test_control_command_status_prints_simple_state_with_fake_systemctl(tmp_path: Path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    systemctl = fake_bin / "systemctl"
    systemctl.write_text(
        "#!/usr/bin/env bash\n"
        "if [ \"$1\" = \"--user\" ] && [ \"$2\" = \"is-active\" ]; then exit 0; fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    systemctl.chmod(0o755)

    result = subprocess.run(
        ["scripts/ArmariumLabs", "--status"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "running"
