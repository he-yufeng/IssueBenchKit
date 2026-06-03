"""Report export helpers."""

from __future__ import annotations

import html
import json
from pathlib import Path

from issuebenchkit.models import RunResult, TaskManifest


def export_jsonl(manifest: TaskManifest, result: RunResult | None, output: str | Path) -> Path:
    entry = {
        "task": manifest.to_dict(),
        "result": result.to_dict() if result else None,
    }
    out = Path(output)
    out.write_text(json.dumps(entry, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def export_html(
    manifest: TaskManifest,
    result: RunResult | None,
    output: str | Path,
    score: dict[str, object] | None = None,
) -> Path:
    result_rows = ""
    if result:
        result_rows = f"""
        <tr><th>Passed</th><td>{html.escape(str(result.passed))}</td></tr>
        <tr><th>Exit code</th><td>{result.exit_code}</td></tr>
        <tr><th>Duration</th><td>{result.duration_seconds:.2f}s</td></tr>
        <tr><th>Command</th><td><code>{html.escape(result.command)}</code></td></tr>
        """
    score_html = ""
    if score:
        score_html = f"<p><strong>Verdict:</strong> {html.escape(str(score['verdict']))}</p>"

    body = f"""<!doctype html>
<meta charset="utf-8">
<title>{html.escape(manifest.name)} - IssueBenchKit</title>
<style>
body {{
  font-family: system-ui, sans-serif;
  max-width: 960px;
  margin: 40px auto;
  line-height: 1.5;
}}
code, pre {{ background: #f6f8fa; border-radius: 6px; padding: 2px 4px; }}
pre {{ padding: 12px; overflow: auto; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #d0d7de; padding: 8px; text-align: left; vertical-align: top; }}
th {{ width: 180px; background: #f6f8fa; }}
</style>
<h1>{html.escape(manifest.name)}</h1>
<p>{html.escape(manifest.expected_signal)}</p>
{score_html}
<table>
  <tr><th>Issue</th><td>{_link_or_text(manifest.issue_url)}</td></tr>
  <tr><th>Base</th><td><code>{html.escape(manifest.base or "-")}</code></td></tr>
  <tr><th>Repo</th><td><code>{html.escape(manifest.repo)}</code></td></tr>
  <tr><th>Test command</th><td><code>{html.escape(manifest.test_command)}</code></td></tr>
  {result_rows}
</table>
<h2>Notes</h2>
<pre>{html.escape(manifest.notes or "")}</pre>
"""
    if result:
        body += f"<h2>stdout tail</h2><pre>{html.escape(result.stdout_tail)}</pre>"
        body += f"<h2>stderr tail</h2><pre>{html.escape(result.stderr_tail)}</pre>"
    out = Path(output)
    out.write_text(body, encoding="utf-8")
    return out


def _link_or_text(value: str) -> str:
    if value.startswith("https://") or value.startswith("http://"):
        safe = html.escape(value)
        return f'<a href="{safe}">{safe}</a>'
    return html.escape(value or "-")
