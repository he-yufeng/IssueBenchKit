"""Task validation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from issuebenchkit.models import RunResult, TaskManifest
from issuebenchkit.runner import run_task
from issuebenchkit.task import load_manifest, manifest_path


@dataclass
class ValidationCheck:
    name: str
    passed: bool
    detail: str


@dataclass
class ValidationReport:
    manifest: TaskManifest
    checks: list[ValidationCheck] = field(default_factory=list)
    before: RunResult | None = None
    after: RunResult | None = None

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def validate_task(
    task_dir: str | Path,
    *,
    before_repo: str | Path | None = None,
    after_repo: str | Path | None = None,
    timeout: int = 600,
) -> ValidationReport:
    task_dir = Path(task_dir)
    manifest = load_manifest(task_dir)
    report = ValidationReport(manifest=manifest)
    _add_manifest_checks(report, task_dir, manifest)

    if before_repo is not None:
        before = run_task(task_dir, repo=before_repo, timeout=timeout)
        report.before = before
        report.checks.append(
            ValidationCheck(
                "before-fails",
                not before.passed,
                f"before exit code {before.exit_code}",
            )
        )

    if after_repo is not None:
        after = run_task(task_dir, repo=after_repo, timeout=timeout)
        report.after = after
        report.checks.append(
            ValidationCheck("after-passes", after.passed, f"after exit code {after.exit_code}")
        )

    return report


def _add_manifest_checks(
    report: ValidationReport,
    task_dir: Path,
    manifest: TaskManifest,
) -> None:
    path = manifest_path(task_dir)
    report.checks.append(ValidationCheck("manifest-exists", path.is_file(), str(path)))
    report.checks.append(
        ValidationCheck(
            "test-command",
            bool(manifest.test_command.strip()),
            manifest.test_command or "missing",
        )
    )
    repo_path = Path(manifest.repo)
    report.checks.append(
        ValidationCheck("manifest-repo-exists", repo_path.is_dir(), str(repo_path))
    )


def validation_markdown(report: ValidationReport) -> str:
    lines = [
        f"# IssueBenchKit validation: {report.manifest.name}",
        "",
        f"- Task: `{report.manifest.name}`",
        f"- Command: `{report.manifest.test_command}`",
        f"- Verdict: {'PASS' if report.passed else 'FAIL'}",
        "",
        "## Checks",
        "",
        "| Check | Result | Detail |",
        "|---|:---:|---|",
    ]
    for check in report.checks:
        result = "PASS" if check.passed else "FAIL"
        lines.append(f"| `{check.name}` | {result} | `{check.detail}` |")

    if report.before or report.after:
        lines.extend(["", "## Runs", ""])
    if report.before:
        lines.extend(_run_section("Before", report.before))
    if report.after:
        lines.extend(_run_section("After", report.after))
    return "\n".join(lines).rstrip() + "\n"


def _run_section(title: str, result: RunResult) -> list[str]:
    return [
        f"### {title}",
        "",
        f"- Repo: `{result.repo}`",
        f"- Exit code: `{result.exit_code}`",
        f"- Passed: `{result.passed}`",
        f"- Duration: `{result.duration_seconds:.3f}s`",
        "",
    ]
