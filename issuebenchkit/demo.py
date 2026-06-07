"""Create runnable IssueBenchKit demo workspaces."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from issuebenchkit.task import init_manifest

DEMO_KINDS = ("python", "javascript", "mcp-pr")


def create_demo_workspace(root: str | Path, *, kind: str = "python") -> dict[str, Path]:
    if kind not in DEMO_KINDS:
        raise ValueError(f"unknown demo kind: {kind}")
    root = Path(root)
    task_dir = root / "task"
    buggy_repo = root / "buggy_repo"
    fixed_repo = root / "fixed_repo"

    if kind == "python":
        _create_python_demo(task_dir, buggy_repo, fixed_repo)
    elif kind == "javascript":
        _create_javascript_demo(task_dir, buggy_repo, fixed_repo)
    else:
        _create_mcp_pr_demo(task_dir, buggy_repo, fixed_repo)

    return {
        "root": root,
        "task": task_dir,
        "buggy_repo": buggy_repo,
        "fixed_repo": fixed_repo,
    }


def create_all_demo_workspaces(root: str | Path) -> dict[str, dict[str, Path]]:
    root = Path(root)
    return {kind: create_demo_workspace(root / kind, kind=kind) for kind in DEMO_KINDS}


def _create_python_demo(task_dir: Path, buggy_repo: Path, fixed_repo: Path) -> None:
    for repo, fixed in ((buggy_repo, False), (fixed_repo, True)):
        _write_python_demo_repo(repo, fixed=fixed)

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


def _create_javascript_demo(task_dir: Path, buggy_repo: Path, fixed_repo: Path) -> None:
    for repo, fixed in ((buggy_repo, False), (fixed_repo, True)):
        _write_javascript_demo_repo(repo, fixed=fixed)

    init_manifest(
        task_dir,
        repo=buggy_repo,
        issue_url="https://github.com/example/web-utils/issues/42",
        base="demo-js-buggy",
        test_command="node test_slugify.js",
        expected_signal="slugify keeps numeric suffixes after punctuation cleanup",
        notes=(
            "Tiny JS/TS-style demo task: the buggy checkout drops digits when cleaning "
            "punctuation, so release-note titles like 'v2.0 RC1' lose their version signal."
        ),
        tags=["demo", "javascript", "unit-test"],
    )


def _create_mcp_pr_demo(task_dir: Path, buggy_repo: Path, fixed_repo: Path) -> None:
    for repo, fixed in ((buggy_repo, False), (fixed_repo, True)):
        _write_mcp_pr_demo_repo(repo, fixed=fixed)

    init_manifest(
        task_dir,
        repo=buggy_repo,
        issue_url="https://github.com/modelcontextprotocol/go-sdk/pull/962",
        base="demo-mcp-duplicate-initialize",
        test_command="python test_session.py",
        expected_signal="duplicate initialize requests are rejected after the first handshake",
        notes=(
            "Distilled from a real user contribution: MCP sessions should reject duplicate "
            "initialize requests so protocol state cannot be reset silently."
        ),
        tags=["demo", "mcp", "protocol", "real-pr"],
    )


def _write_python_demo_repo(repo: Path, *, fixed: bool) -> None:
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


def _write_javascript_demo_repo(repo: Path, *, fixed: bool) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    pattern = r"/[^a-z0-9]+/g" if fixed else r"/[^a-z]+/g"
    (repo / "slugify.js").write_text(
        dedent(
            f"""
            function slugify(title) {{
              return title
                .toLowerCase()
                .replace({pattern}, "-")
                .replace(/^-|-$/g, "");
            }}

            module.exports = {{ slugify }};
            """
        ).lstrip(),
        encoding="utf-8",
    )
    (repo / "test_slugify.js").write_text(
        dedent(
            """
            const assert = require("node:assert/strict");
            const { slugify } = require("./slugify");

            assert.equal(slugify("Release v2.0 RC1"), "release-v2-0-rc1");
            assert.equal(slugify("Hello, MCP Tools!"), "hello-mcp-tools");
            """
        ).lstrip(),
        encoding="utf-8",
    )


def _write_mcp_pr_demo_repo(repo: Path, *, fixed: bool) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    duplicate_branch = (
        "return {'error': {'code': -32600, 'message': 'already initialized'}}"
        if fixed
        else "return {'result': {'protocolVersion': '2025-06-18'}}"
    )
    (repo / "session.py").write_text(
        dedent(
            f"""
            class MCPSession:
                def __init__(self):
                    self.initialized = False

                def handle_initialize(self):
                    if self.initialized:
                        {duplicate_branch}
                    self.initialized = True
                    return {{"result": {{"protocolVersion": "2025-06-18"}}}}
            """
        ).lstrip(),
        encoding="utf-8",
    )
    (repo / "test_session.py").write_text(
        dedent(
            """
            from session import MCPSession


            session = MCPSession()
            first = session.handle_initialize()
            second = session.handle_initialize()

            assert "result" in first
            assert second["error"]["code"] == -32600
            """
        ).lstrip(),
        encoding="utf-8",
    )
