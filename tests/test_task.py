import json

from issuebenchkit.context import render_context_pack
from issuebenchkit.task import init_manifest, load_manifest, manifest_path


def test_init_manifest_creates_task(tmp_path):
    task_dir = tmp_path / "task"
    manifest = init_manifest(
        task_dir,
        repo=tmp_path,
        issue_url="https://github.com/o/r/issues/1",
        base="abc123",
        test_command="python -m pytest",
        tags=["python", "bug"],
    )

    assert manifest.name == "task"
    assert manifest_path(task_dir).exists()
    loaded = load_manifest(task_dir)
    assert loaded.issue_url.endswith("/1")
    assert loaded.tags == ["python", "bug"]
    assert json.loads(manifest_path(task_dir).read_text(encoding="utf-8"))["version"] == 1


def test_context_pack_redacts_common_tokens(tmp_path):
    manifest = init_manifest(
        tmp_path / "task",
        repo=tmp_path,
        test_command="pytest",
        notes="Failure includes Authorization: Bearer abcdefghijklmnop",
    )

    text = render_context_pack(manifest)

    assert "abcdefghijklmnop" not in text
    assert "Bearer <REDACTED>" in text
