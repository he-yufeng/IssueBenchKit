from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from issuebenchkit.cli import main
from issuebenchkit.demo import create_demo_workspace
from issuebenchkit.validate import validate_task, validation_markdown


def test_validate_demo_before_fails_after_passes(tmp_path: Path) -> None:
    paths = create_demo_workspace(tmp_path / "demo")

    report = validate_task(
        paths["task"],
        before_repo=paths["buggy_repo"],
        after_repo=paths["fixed_repo"],
    )

    assert report.passed
    assert report.before is not None and not report.before.passed
    assert report.after is not None and report.after.passed
    assert "before-fails" in validation_markdown(report)


def test_validate_cli_writes_report(tmp_path: Path) -> None:
    paths = create_demo_workspace(tmp_path / "demo")
    out = tmp_path / "validation.md"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "validate",
            str(paths["task"]),
            "--before-repo",
            str(paths["buggy_repo"]),
            "--after-repo",
            str(paths["fixed_repo"]),
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "IssueBenchKit validation" in out.read_text(encoding="utf-8")
