"""Command-line interface for IssueBenchKit."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from issuebenchkit import __version__
from issuebenchkit.context import export_context_pack
from issuebenchkit.demo import create_demo_workspace
from issuebenchkit.export import export_html, export_jsonl
from issuebenchkit.runner import run_task
from issuebenchkit.score import load_result, save_result, score_results
from issuebenchkit.task import init_manifest, load_manifest, manifest_path

console = Console()


@click.group()
@click.version_option(__version__, prog_name="issuebench")
def main() -> None:
    """Build small benchmark tasks from real issues."""


@main.command("init")
@click.argument("task_dir", type=click.Path(file_okay=False))
@click.option("--repo", required=True, type=click.Path(file_okay=False), help="Source repo path.")
@click.option("--issue", "issue_url", default="", help="GitHub issue or PR URL.")
@click.option("--base", default="", help="Base commit, tag, or version marker.")
@click.option("--test", "test_command", required=True, help="Command used to validate the task.")
@click.option("--expected", default="test command exits with code 0", help="Expected signal.")
@click.option("--note", "notes", default="", help="Free-form task notes.")
@click.option("--tag", "tags", multiple=True, help="Task tag. Can be passed multiple times.")
def init_cmd(
    task_dir: str,
    repo: str,
    issue_url: str,
    base: str,
    test_command: str,
    expected: str,
    notes: str,
    tags: tuple[str, ...],
) -> None:
    """Create an issuebench.json task manifest."""
    manifest = init_manifest(
        task_dir,
        repo=repo,
        issue_url=issue_url,
        base=base,
        test_command=test_command,
        expected_signal=expected,
        notes=notes,
        tags=list(tags),
    )
    console.print(f"[green]Created task:[/green] {manifest_path(task_dir)}")
    console.print(f"[dim]{manifest.name}: {manifest.expected_signal}[/dim]")


@main.command("demo")
@click.argument("output_dir", type=click.Path(file_okay=False))
def demo_cmd(output_dir: str) -> None:
    """Create a tiny runnable demo task with buggy and fixed repos."""
    paths = create_demo_workspace(output_dir)
    console.print(f"[green]Created demo workspace:[/green] {paths['root']}")
    console.print(f"Task: {paths['task']}")
    console.print(f"Buggy repo: {paths['buggy_repo']}")
    console.print(f"Fixed repo: {paths['fixed_repo']}")
    console.print()
    console.print("[bold]Try it:[/bold]")
    console.print(
        f"  issuebench run {paths['task']} --repo {paths['buggy_repo']} --out before.json"
    )
    console.print(
        f"  issuebench run {paths['task']} --repo {paths['fixed_repo']} --out after.json"
    )
    console.print(f"  issuebench score {paths['task']} --before before.json --after after.json")


@main.command("inspect")
@click.argument("task_dir", type=click.Path(file_okay=False, exists=True))
def inspect_cmd(task_dir: str) -> None:
    """Show a task manifest."""
    manifest = load_manifest(task_dir)
    table = Table(title=f"IssueBenchKit Task: {manifest.name}")
    table.add_column("Field")
    table.add_column("Value")
    rows = [
        ("Repo", manifest.repo),
        ("Issue", manifest.issue_url or "-"),
        ("Base", manifest.base or "-"),
        ("Test", manifest.test_command),
        ("Expected", manifest.expected_signal),
        ("Tags", ", ".join(manifest.tags) or "-"),
    ]
    for key, value in rows:
        table.add_row(key, value)
    console.print(table)
    if manifest.notes:
        console.print("\n[bold]Notes[/bold]")
        console.print(manifest.notes)


@main.command("run")
@click.argument("task_dir", type=click.Path(file_okay=False, exists=True))
@click.option("--repo", type=click.Path(file_okay=False), help="Candidate repo path.")
@click.option(
    "--out",
    default="result.json",
    type=click.Path(dir_okay=False),
    help="Result JSON path.",
)
@click.option("--timeout", default=600, show_default=True, help="Command timeout in seconds.")
def run_cmd(task_dir: str, repo: str | None, out: str, timeout: int) -> None:
    """Run the task's validation command against a candidate repo."""
    result = run_task(task_dir, repo=repo, timeout=timeout)
    save_result(out, result)
    color = "green" if result.passed else "red"
    console.print(f"[{color}]Result:[/{color}] {'PASS' if result.passed else 'FAIL'}")
    console.print(f"[dim]Wrote {out}[/dim]")


@main.command("score")
@click.argument("task_dir", type=click.Path(file_okay=False, exists=True))
@click.option("--before", type=click.Path(dir_okay=False), help="Before-result JSON.")
@click.option("--after", required=True, type=click.Path(dir_okay=False), help="After-result JSON.")
def score_cmd(task_dir: str, before: str | None, after: str) -> None:
    """Compare before and after run results."""
    load_manifest(task_dir)  # fail early if the task dir is wrong
    before_result = load_result(before) if before else None
    after_result = load_result(after)
    score = score_results(before_result, after_result)

    color = "green" if score["improved"] else "red"
    console.print(f"[{color}]Verdict:[/{color}] {score['verdict']}")
    console.print(score)


@main.command("export")
@click.argument("task_dir", type=click.Path(file_okay=False, exists=True))
@click.option("--result", type=click.Path(dir_okay=False), help="Optional result JSON to include.")
@click.option("--format", "fmt", type=click.Choice(["jsonl", "html"]), default="html")
@click.option("--out", type=click.Path(dir_okay=False), help="Output path.")
def export_cmd(task_dir: str, result: str | None, fmt: str, out: str | None) -> None:
    """Export a task as JSONL or a single-file HTML report."""
    manifest = load_manifest(task_dir)
    run_result = load_result(result) if result else None
    output = out or f"{Path(task_dir).name}.{fmt}"
    if fmt == "jsonl":
        export_jsonl(manifest, run_result, output)
    else:
        score = score_results(None, run_result) if run_result else None
        export_html(manifest, run_result, output, score=score)
    console.print(f"[green]Wrote:[/green] {output}")


@main.command("context")
@click.argument("task_dir", type=click.Path(file_okay=False, exists=True))
@click.option("--result", type=click.Path(dir_okay=False), help="Optional run-result JSON.")
@click.option("--out", type=click.Path(dir_okay=False), help="Output Markdown path.")
def context_cmd(task_dir: str, result: str | None, out: str | None) -> None:
    """Export a Markdown task pack for coding agents."""
    manifest = load_manifest(task_dir)
    run_result = load_result(result) if result else None
    output = out or f"{Path(task_dir).name}-context.md"
    export_context_pack(manifest, output, result=run_result)
    console.print(f"[green]Wrote context pack:[/green] {output}")
