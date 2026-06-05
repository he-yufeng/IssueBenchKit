<p align="right"><a href="README_CN.md">中文文档</a></p>

# IssueBenchKit

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

Or generate a tiny runnable demo first:

```bash
issuebench demo demo-task
issuebench run demo-task/task --repo demo-task/buggy_repo --out before.json
issuebench run demo-task/task --repo demo-task/fixed_repo --out after.json
issuebench score demo-task/task --before before.json --after after.json
```

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
- a built-in runnable demo workspace
- JSON manifest files
- before/after scoring
- JSONL and single-file HTML export
- Markdown context packs for coding agents and PatchContext

It does not generate tests automatically, mutate repositories, or claim that one command can
evaluate every language ecosystem.

## License

MIT
