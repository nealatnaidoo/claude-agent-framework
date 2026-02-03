# Best Practice Pattern Templates Index

**Source**: devlessons.md (117 lessons)
**Version**: 1.0
**Date**: 2026-01-31
**Location**: `~/.claude/devops/patterns/`

---

## Overview

This directory contains reusable pattern templates derived from 117 hard-won lessons documented in `devlessons.md`. Each pattern includes:

- Specific lesson references
- Ready-to-use code/configuration
- Prevention checklists
- Evidence requirements

---

## Pattern Categories

### 1. Quality Gates (`quality-gates/`)

| Template | Purpose | Key Lessons |
|----------|---------|-------------|
| `python.yaml` | Python project quality gates | #4, #5, #36, #51, #87, #107 |
| `frontend.yaml` | Next.js/React quality gates | #18, #38-43, #53-57, #59, #81, #85 |
| `fullstack.yaml` | Combined backend + frontend gates | All of the above + #108, #109, #113 |

**Usage**:
```yaml
# Copy to your project and customize
cp ~/.claude/devops/patterns/quality-gates/python.yaml .claude/quality_gates.yaml
```

### 2. Testing Patterns (`testing/`)

| Template | Purpose | Key Lessons |
|----------|---------|-------------|
| `e2e-fixtures.ts.template` | Playwright E2E test fixtures | #44, #53-57, #60, #61 |
| `api-contract-tests.py.template` | API contract validation | #47, #48, #108, #109, #112, #113 |

**Key Patterns**:
- Authentication helpers (don't duplicate login code)
- Seed data constants (match actual schema)
- data-testid selectors (not CSS classes)
- Contract validation with Pydantic
- Filter parameter testing

### 3. Atomic Components (`atomic-component/`)

| Template | Purpose | Key Lessons |
|----------|---------|-------------|
| `contract.md.template` | Component contract documentation | #8, #12, #79 |
| `component.py.template` | Python component implementation | #8, #87, #107 |

**Required Files Per Component**:
```
src/components/{Name}/
├── component.py    # run() entry point
├── models.py       # Frozen dataclasses
├── ports.py        # Protocol interfaces
├── contract.md     # Specification (write FIRST)
└── __init__.py     # Public exports
```

### 4. CI/CD Patterns (`gitlab-ci/`, `github-actions/`)

| Template | Purpose | Key Lessons |
|----------|---------|-------------|
| `python-fastapi.yml` | GitLab CI for Python projects | #3, #5, #115 |

**Pipeline Stages**:
1. Quality gates (lint, types, tests, security)
2. Integration tests
3. Docker build
4. Deploy to dev (automatic)
5. Deploy to prod (manual)

### 5. Database Patterns (`db-harness/`)

| Template | Purpose | Decision Ref |
|----------|---------|--------------|
| `gitlab-ci-templates.yml` | Database gate CI templates (GitLab) | DEC-DEVOPS-014 |
| `baseline_masking_rules.yaml` | Portfolio-wide PII patterns | DEC-DEVOPS-010 |
| `README.md` | Integration guide | DEC-DEVOPS-014 |

**GitHub Actions Templates** (`db-harness/github-actions/`):
| Template | Gate | Purpose |
|----------|------|---------|
| `schema-drift.yml` | NN-DB-1 | Pre-migration schema drift detection |
| `fk-integrity.yml` | NN-DB-2 | Post-migration FK integrity validation |
| `pii-detection.yml` | NN-DB-3 | PII detection and masking coverage |
| `propagate.yml` | NN-DB-3 | Full database propagation with PII masking |

**Non-Negotiables (NN-DB-*)**:
| Gate | Description | Type |
|------|-------------|------|
| NN-DB-1 | Pre-migration schema drift check | Blocking |
| NN-DB-2 | Post-migration FK integrity | Blocking |
| NN-DB-3 | PII masking for propagation | Blocking |
| NN-DB-4 | Audit hash chain verification | Warning |

**Usage (GitLab)**:
```yaml
# In project's .gitlab-ci.yml
include:
  - local: '.gitlab/db-harness.yml'

schema-drift-check:
  extends: .db-harness-drift-check
  variables:
    SOURCE_CONN: "${DB_DEV_CONN}"
    TARGET_CONN: "${DB_STAGING_CONN}"
```

**Usage (GitHub Actions)**:
```yaml
# In .github/workflows/database-gates.yml
jobs:
  schema-drift:
    uses: ./.github/workflows/schema-drift.yml
    with:
      source_db: "sqlite:///dev.db"
      target_db: "sqlite:///staging.db"
      fail_on_breaking: true
```

---

## Top 30 Rules (Summary)

From `devlessons.md` lines 1263-1295:

| # | Rule | Lesson Ref |
|---|------|------------|
| 1 | Choose mature frameworks | #1 |
| 2 | Pin all dependencies | #2 |
| 3 | Use clean architecture (hexagonal) | #4 |
| 4 | Run quality gates constantly | #5 |
| 5 | Create BA artifacts first | #6 |
| 6 | Track drift explicitly | #7 |
| 7 | Different layers need different tests | #5 |
| 8 | Fly.io needs volumes before deploy | #3 |
| 9 | Document deployment quirks | #3 |
| 10 | One task at a time | #7 |
| 11 | Read playbook BEFORE coding | #8 |
| 12 | Contracts first, code second | #8, #79 |
| 13 | Audit early and often | #8 |
| 14 | TDD on contracts | #8 |
| 15 | Find ALL components before migration | #9 |
| 16 | External QA validates migrations | #9 |
| 17 | Manifest + Tasklist paths = Definition of Done | #11 |
| 18 | Deprecate with sunset dates | #10 |
| 19 | Use deprecation warnings | #10 |
| 20 | Complete ALL layers in migrations | #12 |
| 21 | Use DEPRECATED.md with migration maps | #10 |
| 22 | Add migration-specific quality gates | #12 |
| 23 | Inject TimePort for all time operations | #87, #107 |
| 24 | No global state in components | #87 |
| 25 | Re-export through __init__.py | #14 |
| 26 | Resolve type conflicts when re-exporting | #14 |
| 27 | Install @tiptap/html for rendering | #38 |
| 28 | Use Button over Toggle for toolbars | #38 |
| 29 | Content pages need force-dynamic | #85 |
| 30 | Create API transformation layers | #108 |

---

## Quick Reference by Technology

### Python
- Determinism: No `datetime.now()`, `uuid4()`, `random` in core (#87, #107)
- Deprecation: `datetime.utcnow()` → `datetime.now(timezone.utc)` (#27)
- Keywords as modules: Use importlib for `is/` folders (#15)
- Type hints: MyPy requires explicit None checks (#80)

### React/Next.js
- Radix Select: Can't use empty string as value (#18)
- TipTap: Install @tiptap/html for SSR (#38)
- shadcn/ui: Add components incrementally (#39)
- "use client": Affects ALL exports in file (#59)
- Static pages: Use `force-dynamic` for fresh data (#85)
- Derived state: useMemo, not setState in useEffect (#81)

### Testing
- E2E selectors: Prefer data-testid (#53)
- Auth helpers: Centralize login logic (#57)
- Seed data: Must match actual schema (#54)
- Port conflicts: Check before starting servers (#55)
- Filter tests: Prove filter actually works (#109)
- Contract tests: Validate ALL response fields (#108)

### Fly.io Deployment
- Create volume BEFORE first deploy (#3)
- Set PYTHONPATH in fly.toml AND Dockerfile (#3)
- Health check must return 200 (#3)
- Memory >= 512mb for Python (#3)
- Cold start: Set min_machines_running for latency (#3)

### MCP Development
- Response time: <200ms (spawn threads) (#22)
- Token efficiency: Return summaries, not raw output (#20)
- Fallback: Chain providers for resilience (#21)
- Paths: Use absolute paths in Claude Desktop config (#23)
- Atomic adapters: One per external service (#24)

---

## Usage Workflow

### Starting a New Project

1. **Consult lessons-advisor** with project context
2. **Copy quality gates template** to `.claude/artifacts/005_quality_gates_v1.md`
3. **Create manifest** with artifact references
4. **Apply applicable lessons** to `.claude/artifacts/006_lessons_applied_v1.md`

### Creating a New Component

1. **Copy contract.md.template** to component directory
2. **Fill in contract FIRST** (TDD approach)
3. **Copy component.py.template** as starting point
4. **Implement to match contract**
5. **Run quality gates**

### Setting Up CI/CD

1. **Copy appropriate CI template** (gitlab-ci or github-actions)
2. **Configure environment variables** (FLY_API_TOKEN, etc.)
3. **Create dev/prod Fly.io apps**
4. **Test pipeline with non-production branch first**

---

## Pattern Maintenance

When updating patterns:
1. Reference specific lesson numbers
2. Include prevention checklist
3. Document evidence requirements
4. Test with real project before committing

When adding new lessons:
1. Update devlessons.md
2. Extract reusable pattern to template
3. Add to this index
4. Update CLAUDE.md if significant
