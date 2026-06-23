<div align="center">

<img src="docs/banner.png" alt="IssueBenchKit — turn a real GitHub issue into a coding-agent benchmark task" width="100%">

[![PyPI](https://img.shields.io/pypi/v/issuebenchkit.svg)](https://pypi.org/project/issuebenchkit/)
[![Python](https://img.shields.io/pypi/pyversions/issuebenchkit.svg)](https://pypi.org/project/issuebenchkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[**Quick Start**](#quick-start) · [**How It Works**](#how-it-works) · [**Scoring**](#scoring) · [中文](README_CN.md)

</div>

<p align="center"><img src="docs/demo.png" alt="issuebench init and run" width="620"></p>

Turn a real GitHub issue, pull request, or local bug into a small coding-agent benchmark task.

SWE-bench is great when you want a public leaderboard. Most teams need something smaller: a
repeatable task built from the bugs they actually care about, with a clear test command and a
report that says whether a candidate patch really fixed it.

IssueBenchKit is that local builder. It does not try to invent tests for you. It packages the
issue context, base commit, reproduction command, and scoring result so you can evaluate coding
agents on your own repositories.

## Quick Start

```bash
pip install issuebenchkit
```

Create a benchmark task:

```bash
issuebench init tasks/qwen-copy \
  --repo ./qwen-code \
  --issue https://github.com/QwenLM/qwen-code/issues/4716 \
  --base 8b4f3b2 \
  --test "npm test -- copyCommand.test.ts"
```

Or generate runnable demos first:

```bash
issuebench demo demo-task
issuebench run demo-task/task --repo demo-task/buggy_repo --out before.json
issuebench run demo-task/task --repo demo-task/fixed_repo --out after.json
issuebench score demo-task/task --before before.json --after after.json
issuebench validate demo-task/task --before-repo demo-task/buggy_repo --after-repo demo-task/fixed_repo --out validation.md
```

The built-in demos cover more than a toy Python case:

```bash
issuebench demo demo-python --kind python
issuebench demo demo-js --kind javascript
issuebench demo demo-mcp --kind mcp-pr
issuebench demo demo-gallery --all
```

- `python`: a small pytest task around a division-by-zero behavior bug.
- `javascript`: a Node-based slugification bug that drops numeric version suffixes.
- `mcp-pr`: a distilled real contribution around rejecting duplicate MCP `initialize` calls.

Run the task against a candidate checkout:

```bash
issuebench run tasks/qwen-copy --repo ./candidate-qwen-code --out after.json
```

Compare before and after:

```bash
issuebench score tasks/qwen-copy --before before.json --after after.json
```

Export a report:

```bash
issuebench export tasks/qwen-copy --format html --out report.html
```

Create a coding-agent context pack:

```bash
issuebench context tasks/qwen-copy --result after.json --out qwen-copy-context.md
patchcontext scan --repo ./qwen-code --issue qwen-copy-context.md
```

## What It Stores

Each task directory contains one `issuebench.json` manifest:

- source repo path and optional GitHub issue URL
- base commit or version marker
- reproduction / validation command
- expected signal, notes, and tags

Run results are plain JSON files with exit code, duration, command, stdout tail, stderr tail, and
the pass/fail verdict. They are easy to archive, diff, or attach to a PR.

## Why Not Just Use SWE-bench?

Use SWE-bench for public comparison. Use IssueBenchKit when you need:

- a benchmark task for a private or small repo
- a tiny task that can run in CI
- a before/after report for one real bug
- a dataset of issues that reflects your own engineering workflow

## Current Scope

The first version is intentionally small:

- generic shell test commands
- built-in runnable demo workspaces for Python, JavaScript, and a distilled real MCP PR
- JSON manifest files
- before/after scoring
- task validation that proves before fails, after passes, and both runs used the same task command
- JSONL and single-file HTML export
- Markdown context packs for coding agents and PatchContext

It does not generate tests automatically, mutate repositories, or claim that one command can
evaluate every language ecosystem.

## Roadmap

The scope above is deliberate. The next steps keep that small core and grow the parts that make a task easier to author and trust:

- **A task linter** — `issuebenchkit lint <task>` that flags a manifest before it runs: missing before/after commands, a task command that isn't reproducible, or a workspace that doesn't build, so a bad task is caught at authoring time.
- **More demo workspaces** — runnable Go and Rust demos alongside the Python/JS/MCP ones, since the validation contract (before fails, after passes, same command) is language-agnostic and only the demo is missing.
- **Cost and timing in the report** — record wall-clock and, when an agent runs the task, token usage, so a before/after report shows the price of a fix and not only whether it passed.
- **Task packs** — group related tasks into a named set that runs and scores together, for tracking a small private suite over time.

The line it won't cross stays the same: no automatic test generation, no repo mutation, no "one command evaluates every ecosystem" claim.

## Related projects

- [AgentProbe](https://github.com/he-yufeng/AgentProbe) — a pytest plugin for regression-testing AI agents
- [LiteBench](https://github.com/he-yufeng/LiteBench) — a pip-installable benchmark runner for LLMs and agents
- [CodeJoust](https://github.com/he-yufeng/CodeJoust) — pit coding agents against the same bug and score the patches
- [agentcikit](https://github.com/he-yufeng/agentcikit) — CLI tools for AI-agent, MCP, and CI evidence and safety

## License

MIT
