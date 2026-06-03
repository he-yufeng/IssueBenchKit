"""Data models for IssueBenchKit."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TaskManifest:
    name: str
    repo: str
    test_command: str
    issue_url: str = ""
    base: str = ""
    expected_signal: str = "test command exits with code 0"
    notes: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskManifest:
        allowed = cls.__dataclass_fields__.keys()
        clean = {key: value for key, value in data.items() if key in allowed}
        return cls(**clean)


@dataclass
class RunResult:
    task: str
    repo: str
    command: str
    exit_code: int
    passed: bool
    duration_seconds: float
    stdout_tail: str = ""
    stderr_tail: str = ""
    started_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunResult:
        allowed = cls.__dataclass_fields__.keys()
        clean = {key: value for key, value in data.items() if key in allowed}
        return cls(**clean)


def task_name_from_path(path: str | Path) -> str:
    return Path(path).resolve().name
