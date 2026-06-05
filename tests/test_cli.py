from click.testing import CliRunner

from issuebenchkit.cli import main
from issuebenchkit.runner import run_task


def test_cli_init_and_inspect(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    task = tmp_path / "task"

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "init",
            str(task),
            "--repo",
            str(repo),
            "--test",
            "python -m pytest",
            "--issue",
            "https://github.com/o/r/issues/1",
        ],
    )
    assert result.exit_code == 0

    result = runner.invoke(main, ["inspect", str(task)])
    assert result.exit_code == 0
    assert "https://github.com/o/r/issues/1" in result.output


def test_cli_demo_creates_runnable_before_after(tmp_path):
    runner = CliRunner()
    demo_root = tmp_path / "demo"

    result = runner.invoke(main, ["demo", str(demo_root)])
    assert result.exit_code == 0

    task = demo_root / "task"
    buggy = demo_root / "buggy_repo"
    fixed = demo_root / "fixed_repo"

    before = run_task(task, repo=buggy, timeout=30)
    after = run_task(task, repo=fixed, timeout=30)

    assert before.passed is False
    assert after.passed is True


def test_cli_context_exports_task_pack(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    task = tmp_path / "task"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "init",
            str(task),
            "--repo",
            str(repo),
            "--test",
            "python check.py",
            "--expected",
            "check.py passes",
            "--note",
            "Traceback points to src/app.py",
        ],
    )
    assert result.exit_code == 0

    out = tmp_path / "context.md"
    result = runner.invoke(main, ["context", str(task), "--out", str(out)])

    assert result.exit_code == 0
    text = out.read_text(encoding="utf-8")
    assert "# IssueBench task context: task" in text
    assert "python check.py" in text
    assert "src/app.py" in text
