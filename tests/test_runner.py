import sys

from issuebenchkit.runner import run_task
from issuebenchkit.score import score_results
from issuebenchkit.task import init_manifest


def test_run_task_passes_and_scores(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    script = repo / "check.py"
    script.write_text("print('ok')\n", encoding="utf-8")
    task_dir = tmp_path / "task"
    init_manifest(task_dir, repo=repo, test_command=f'"{sys.executable}" check.py')

    result = run_task(task_dir)
    score = score_results(None, result)

    assert result.passed is True
    assert "ok" in result.stdout_tail
    assert score["verdict"] == "pass"


def test_score_detects_fix(tmp_path):
    before = run_task_result(False)
    after = run_task_result(True)

    score = score_results(before, after)

    assert score["verdict"] == "fixed"
    assert score["improved"] is True


def run_task_result(passed):
    from issuebenchkit.models import RunResult

    return RunResult(
        task="demo",
        repo="repo",
        command="test",
        exit_code=0 if passed else 1,
        passed=passed,
        duration_seconds=0.1,
    )
