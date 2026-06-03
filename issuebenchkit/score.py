"""Before/after scoring helpers."""

from __future__ import annotations

import json
from pathlib import Path

from issuebenchkit.models import RunResult


def load_result(path: str | Path) -> RunResult:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return RunResult.from_dict(data)


def save_result(path: str | Path, result: RunResult) -> Path:
    out = Path(path)
    out.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return out


def score_results(before: RunResult | None, after: RunResult) -> dict[str, object]:
    if before is None:
        verdict = "pass" if after.passed else "fail"
        improved = after.passed
    elif before.passed and after.passed:
        verdict = "still-passing"
        improved = True
    elif not before.passed and after.passed:
        verdict = "fixed"
        improved = True
    elif before.passed and not after.passed:
        verdict = "regressed"
        improved = False
    else:
        verdict = "still-failing"
        improved = False

    return {
        "task": after.task,
        "verdict": verdict,
        "passed": after.passed,
        "improved": improved,
        "before_exit_code": before.exit_code if before else None,
        "after_exit_code": after.exit_code,
        "after_duration_seconds": round(after.duration_seconds, 3),
    }
