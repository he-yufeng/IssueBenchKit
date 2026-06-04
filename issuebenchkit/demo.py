"""Create a tiny runnable IssueBenchKit demo workspace."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from issuebenchkit.task import init_manifest


def create_demo_workspace(root: str | Path) -> dict[str, Path]:
    root = Path(root)
    task_dir = root / "task"
    buggy_repo = root / "buggy_repo"
    fixed_repo = root / "fixed_repo"

    for repo, fixed in ((buggy_repo, False), (fixed_repo, True)):
        _write_demo_repo(repo, fixed=fixed)

    init_manifest(
        task_dir,
        repo=buggy_repo,
        issue_url="https://github.com/example/calculator/issues/1",
        base="demo-buggy",
        test_command="python -m pytest -q",
        expected_signal="pytest passes after divide_by_zero is fixed",
        notes=(
            "Tiny demo task: the buggy checkout returns 0 for division by zero. "
            "The fixed checkout raises ZeroDivisionError."
        ),
        tags=["demo", "python", "unit-test"],
    )

    return {
        "root": root,
        "task": task_dir,
        "buggy_repo": buggy_repo,
        "fixed_repo": fixed_repo,
    }


def _write_demo_repo(repo: Path, *, fixed: bool) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "calculator.py").write_text(
        dedent(
            f"""
            def divide(a: int, b: int) -> float:
                {"return a / b" if fixed else "return 0 if b == 0 else a / b"}
            """
        ).lstrip(),
        encoding="utf-8",
    )
    (repo / "test_calculator.py").write_text(
        dedent(
            """
            import pytest

            from calculator import divide


            def test_divide_regular_numbers():
                assert divide(6, 3) == 2


            def test_divide_by_zero_raises():
                with pytest.raises(ZeroDivisionError):
                    divide(1, 0)
            """
        ).lstrip(),
        encoding="utf-8",
    )
