"""Manifest loading and task initialization."""

from __future__ import annotations

import json
from pathlib import Path

from issuebenchkit.models import TaskManifest, task_name_from_path

MANIFEST_NAME = "issuebench.json"


def manifest_path(task_dir: str | Path) -> Path:
    return Path(task_dir) / MANIFEST_NAME


def init_manifest(
    task_dir: str | Path,
    *,
    repo: str | Path,
    test_command: str,
    issue_url: str = "",
    base: str = "",
    expected_signal: str = "test command exits with code 0",
    notes: str = "",
    tags: list[str] | None = None,
) -> TaskManifest:
    task_dir = Path(task_dir)
    task_dir.mkdir(parents=True, exist_ok=True)
    manifest = TaskManifest(
        name=task_name_from_path(task_dir),
        repo=str(Path(repo)),
        issue_url=issue_url,
        base=base,
        test_command=test_command,
        expected_signal=expected_signal,
        notes=notes,
        tags=tags or [],
    )
    save_manifest(task_dir, manifest)
    return manifest


def save_manifest(task_dir: str | Path, manifest: TaskManifest) -> Path:
    path = manifest_path(task_dir)
    path.write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_manifest(task_dir: str | Path) -> TaskManifest:
    path = manifest_path(task_dir)
    if not path.exists():
        raise FileNotFoundError(f"Task manifest not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return TaskManifest.from_dict(data)
