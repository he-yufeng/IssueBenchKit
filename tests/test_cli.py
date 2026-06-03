from click.testing import CliRunner

from issuebenchkit.cli import main


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
