"""Run task validation commands."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from issuebenchkit.models import RunResult
from issuebenchkit.task import load_manifest

TAIL_CHARS = 12_000


def run_task(
    task_dir: str | Path,
    *,
    repo: str | Path | None = None,
    timeout: int = 600,
) -> RunResult:
    manifest = load_manifest(task_dir)
    repo_path = Path(repo or manifest.repo).resolve()
    if not repo_path.is_dir():
        raise FileNotFoundError(f"Candidate repo does not exist: {repo_path}")

    started = time.perf_counter()
    completed = subprocess.run(
        manifest.test_command,
        cwd=repo_path,
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    duration = time.perf_counter() - started

    return RunResult(
        task=manifest.name,
        repo=str(repo_path),
        command=manifest.test_command,
        exit_code=completed.returncode,
        passed=completed.returncode == 0,
        duration_seconds=duration,
        stdout_tail=_tail(completed.stdout),
        stderr_tail=_tail(completed.stderr),
    )


def _tail(text: str) -> str:
    if len(text) <= TAIL_CHARS:
        return text
    return text[-TAIL_CHARS:]
