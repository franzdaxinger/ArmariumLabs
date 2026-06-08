from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(repo_path: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def init_repo(repo_path: Path) -> None:
    if not (repo_path / ".git").exists():
        result = _run_git(repo_path, ["init"])
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "git init failed")
    _run_git(repo_path, ["config", "user.name", "ArmariumLabs"])
    _run_git(repo_path, ["config", "user.email", "armariumlabs.local@example.invalid"])


def commit_all(repo_path: Path, message: str) -> None:
    add_result = _run_git(repo_path, ["add", "."])
    if add_result.returncode != 0:
        raise RuntimeError(add_result.stderr.strip() or "git add failed")
    commit_result = _run_git(repo_path, ["commit", "-m", message])
    if commit_result.returncode != 0 and "nothing to commit" not in commit_result.stderr.lower():
        raise RuntimeError(commit_result.stderr.strip() or "git commit failed")


def status(repo_path: Path) -> str:
    if not (repo_path / ".git").exists():
        return "unknown"
    result = _run_git(repo_path, ["status", "--porcelain"])
    if result.returncode != 0:
        return "unknown"
    return "clean" if result.stdout.strip() == "" else "dirty"
