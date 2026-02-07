---
description: Run quality gates with optional scoping, filtering, and parallelism
argument-hint: [--only lint types] [--scope component] [--domain backend|frontend|fullstack]
allowed-tools: Bash(*:*), Read, Write
---

Run quality gates for the current project. Parse arguments from `$ARGUMENTS` and build the command.

## Help

If `$ARGUMENTS` contains `--help` or `-h`, **do not run any gates**. Instead, display this reference and stop:

```
/gates - Quality Gates Runner

Usage: /gates [flags]

Flags:
  --only <gates...>    Run only these gates (e.g. --only lint types)
  --skip <gates...>    Skip these gates (e.g. --skip format)
  --scope <component>  Narrow pytest gates to a component name
  --domain <d>         backend (default) | frontend | fullstack
  --no-parallel        Run sequentially instead of in parallel groups
  --list               Show available gates and exit
  --out <path>         Custom output path for JSON report
  --help, -h           Show this help

Available gates (backend):
  Group 0: rules
  Group 1: lint, format (optional), types
  Group 2: tests, security, privacy, reliability

Available gates (frontend):
  Group 1: frontend_lint
  Group 2: frontend_build

Examples:
  /gates                              Backend gates, parallel (default)
  /gates --only lint types            Just lint + type checking
  /gates --scope content_submission   Scoped pytest runs
  /gates --domain frontend            Frontend lint + build
  /gates --domain fullstack           All gates
  /gates --list                       Show gates for current domain
```

## Defaults
- `--parallel` (enabled by default)
- `--domain backend` (backend gates only)

## Steps

1. Determine the project root (look for `scripts/quality_gates.py`)
2. Build command: `python scripts/quality_gates.py` with flags from `$ARGUMENTS`
3. Run the command and display results
4. Copy the JSON output to `.claude/evidence/quality_gates_run.json`

## Argument Mapping

| User Argument | Maps To |
|--------------|---------|
| `--only lint types` | `--only lint types` |
| `--scope content_submission` | `--scope content_submission` |
| `--domain frontend` | `--domain frontend` |
| `--domain fullstack` | `--domain fullstack` |
| `--no-parallel` | `--no-parallel` |
| `--out path` | `--out path` |

## Example Commands

```bash
# Backend gates (default)
python scripts/quality_gates.py --parallel

# Only lint and types
python scripts/quality_gates.py --only lint types

# Scoped to a component
python scripts/quality_gates.py --scope content_submission

# Frontend gates
python scripts/quality_gates.py --domain frontend

# Full stack
python scripts/quality_gates.py --domain fullstack

# List available gates
python scripts/quality_gates.py --list --domain fullstack
```

## Post-Run

After running, copy the output to evidence:
```bash
mkdir -p .claude/evidence
cp artifacts/quality_gates_run.json .claude/evidence/quality_gates_run.json
```

Display a summary table of results to the user.
