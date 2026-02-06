---
description: Run and validate quality gates for Python, frontend, or full-stack projects
---

<quality-gates>

## Quality Gates

Run quality gates appropriate to the project type. All gates must pass before a task is marked complete.

### Python Backend

```bash
ruff check . --fix
python -m mypy .
pytest --tb=short -q
```

Config reference: `~/.claude/patterns/quality-gates/python.yaml`

### Frontend (React/TypeScript)

```bash
npm run build
npm run lint
npm test -- --watchAll=false
```

Config reference: `~/.claude/patterns/quality-gates/frontend.yaml`

### Full-Stack

```bash
# Backend
ruff check . --fix && python -m mypy . && pytest --tb=short -q

# Frontend
cd frontend && npm run build && npm run lint && npm test -- --watchAll=false
```

Config reference: `~/.claude/patterns/quality-gates/fullstack.yaml`

### Evidence Artifacts (REQUIRED)

After running gates, produce these files in `.claude/evidence/`:

```json
// quality_gates_run.json
{
  "timestamp": "2026-01-31T14:00:00Z",
  "status": "PASS",
  "gates": {
    "lint": {"status": "pass", "tool": "ruff"},
    "typecheck": {"status": "pass", "tool": "mypy"},
    "tests": {"status": "pass", "tool": "pytest", "passed": 42, "failed": 0}
  }
}
```

```json
// test_report.json - pytest output
// test_failures.json - empty array if all pass, failure details if not
```

### Manifest Update

After gates pass, update `manifest.yaml`:
- `evidence.quality_gates_run` path
- `evidence.test_report` path
- `evidence.test_failures` path

</quality-gates>
