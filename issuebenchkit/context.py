"""Build coding-agent context packs from IssueBench tasks."""

from __future__ import annotations

import re
from pathlib import Path

from issuebenchkit.models import RunResult, TaskManifest

_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(gho|ghp|github_pat)_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{16,}"),
    re.compile(r"(?i)(api[_-]?key['\"]?\s*[:=]\s*['\"]?)[^'\"\s,}]+"),
]


def export_context_pack(
    manifest: TaskManifest,
    output: str | Path,
    *,
    result: RunResult | None = None,
) -> Path:
    out = Path(output)
    out.write_text(render_context_pack(manifest, result=result), encoding="utf-8")
    return out


def render_context_pack(manifest: TaskManifest, *, result: RunResult | None = None) -> str:
    lines = [
        f"# IssueBench task context: {manifest.name}",
        "",
        "This pack is meant for a coding agent or reviewer before attempting the task.",
        "It captures the benchmark contract, the validation command, and the observed",
        "failure signal without requiring the agent to read the raw manifest first.",
        "",
        "## Task contract",
        "",
        f"- Repo: `{manifest.repo}`",
        f"- Issue: {_link_or_dash(manifest.issue_url)}",
        f"- Base: `{manifest.base or '-'}`",
        f"- Validation command: `{manifest.test_command}`",
        f"- Expected signal: {manifest.expected_signal}",
        f"- Tags: {', '.join(manifest.tags) or '-'}",
        "",
    ]
    if manifest.notes:
        lines.extend(["## Notes", "", _redact(manifest.notes).strip(), ""])
    if result:
        lines.extend(
            [
                "## Latest run result",
                "",
                f"- Candidate repo: `{result.repo}`",
                f"- Command: `{result.command}`",
                f"- Passed: `{result.passed}`",
                f"- Exit code: `{result.exit_code}`",
                f"- Duration: `{result.duration_seconds:.2f}s`",
                "",
            ]
        )
        if result.stdout_tail:
            lines.extend(["### stdout tail", "", "```text", _redact(result.stdout_tail), "```", ""])
        if result.stderr_tail:
            lines.extend(["### stderr tail", "", "```text", _redact(result.stderr_tail), "```", ""])

    lines.extend(
        [
            "## Suggested first pass",
            "",
            "1. Read the files named in the issue, notes, traceback, or diff.",
            "2. Reproduce the failure with the validation command before editing.",
            "3. Keep the patch scoped to the benchmark contract.",
            "4. Re-run the same command and compare before/after results.",
            "",
            "PatchContext hint:",
            "",
            "```bash",
            f"patchcontext scan --repo {manifest.repo} --issue <context-pack.md>",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _link_or_dash(value: str) -> str:
    return value if value else "-"


def _redact(text: str) -> str:
    redacted = text
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub(_replace_secret, redacted)
    return redacted


def _replace_secret(match: re.Match[str]) -> str:
    if match.lastindex:
        return f"{match.group(1)}<REDACTED>"
    return "<REDACTED>"
