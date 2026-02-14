---
description: Run quality gates and optionally launch QA reviewer agent
argument-hint: [--quick] [--task T-MU-001] [--background]
allowed-tools: Bash(*:*), Read, Write, Task
---

Run quality gates and optionally launch the QA reviewer agent. Parse arguments from `$ARGUMENTS`.

## Help

If `$ARGUMENTS` contains `--help` or `-h`, **do not run any gates or agents**. Instead, display this reference and stop:

```
/qa - Quality Gates & Review Runner

Usage: /qa [flags]

Flags:
  --quick              Run gates only, skip QA reviewer
  --task <ID>          Scope gates to a task's component (e.g. T-MU-001)
  --background         Launch QA reviewer in background
  --domain <d>         backend (default) | frontend | fullstack
  --scope <component>  Narrow pytest gates to a component name
  --help, -h           Show this help

When to use what:
  /qa                         You finished a task, want full validation + review
  /qa --quick                 Quick sanity check, no reviewer needed
  /qa --quick --scope auth    Fast feedback on one component while coding
  /qa --background            Keep working while QA reviews in parallel
  /qa --task T-MU-001         Scoped validation tied to a specific task
  /qa --domain frontend       Validate frontend (lint + build)
  /qa --domain fullstack      Validate everything

Workflow tips:
  - During coding: /qa --quick --scope <component>  (fast, scoped)
  - After each task: /qa --background                (parallel QA)
  - Before phase transition: /qa                     (full gates + review)
  - Frontend changes: /qa --quick --domain frontend  (lint + build)
```

## Modes

| Flag | Behavior |
|------|----------|
| (no flags) | Run gates + launch QA reviewer |
| `--quick` | Run gates only, skip QA reviewer |
| `--task T-MU-001` | Scope gates to task component + pass context to QA |
| `--background` | Launch QA reviewer in background |

## Steps

### 1. Run Quality Gates

```bash
python scripts/quality_gates.py --parallel
```

If `--task` is provided, extract the component name from the task and add `--scope <component>`.

### 2. Write Evidence

```bash
mkdir -p .claude/evidence
cp artifacts/quality_gates_run.json .claude/evidence/quality_gates_run.json
```

### 3. Launch QA Reviewer (unless `--quick`)

Use the Task tool to launch the QA reviewer:

```
Task(
  subagent_type: "qa",
  prompt: "Review recent code changes. Evidence is at .claude/evidence/quality_gates_run.json. {task context if --task provided}",
  run_in_background: true if --background
)
```

### 4. Report Results

Display:
- Quality gates summary (pass/fail per gate)
- Evidence file location
- QA reviewer status (launched / skipped / running in background)

## Examples

```
/qa                      # Full: gates + QA reviewer
/qa --quick              # Just gates, no QA
/qa --task T-MU-001      # Scoped gates + QA with task context
/qa --background         # Gates + QA reviewer in background
/qa --quick --task T-MU-001  # Scoped gates only
```
