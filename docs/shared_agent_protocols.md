# Shared Agent Protocols

**Version**: 1.0.0
**Used by**: back, front
**Purpose**: Single source of truth for protocols shared across coding agents. Agents MUST read this file during pre-flight.

---

## Autonomous Work Loop

You process ALL assigned tasks without human intervention. After pre-flight, enter the autonomous loop and do not stop until all tasks are complete or a Tier 3 halt is triggered.

```
FOR EACH unblocked task (by dependency order):

  1. CLAIM: Mark task as "in_progress"

  2. READ: Load full task description + AC + TA

  3. SCAFFOLD: Create component/slice structure if missing

  4. TDD: Write tests BEFORE implementation

  5. IMPLEMENT: Inside atomic component/slice only

  6. INLINE QA (self-check):
     - Run linter (ruff/eslint)
     - Run type checker (mypy/tsc)
     - Run scoped tests (component/slice only)
     - Full suite: only at phase boundaries (final task)
     - Verify data-testid on interactive elements (frontend)

  7. AUTO-FIX (if inline QA fails):
     - Fix lint/type errors immediately
     - Fix failing tests (up to 2 attempts)
     - If fix fails after 2 attempts:
       → Log to .claude/evolution/evolution.md
       → Mark task with note, continue to next
     - Re-run inline QA after fix
     - Adjacent code issues: log to findings.log, do NOT auto-fix

  8. EVIDENCE: Write quality gate results
     → .claude/evidence/quality_gates_run.json
     → .claude/evidence/test_report.json

  9. COMPLETE: Mark task as "completed"

  10. NEXT: Find next unblocked task
      → If none remain: exit loop

  HALT CONDITIONS (exit loop immediately):
  - Tier 3 drift detected (new feature, architecture change)
  - Security vulnerability discovered
  - >3 consecutive tasks fail inline QA
```

---

## Drift Protocol (Tiered)

### Tier 1: Minor (Proceed + Document)
- Small utility functions for the task
- Fixing typos in spec
- Missing `__init__.py` or `index.ts`
- Adding missing `contract.md` to a component you're touching
- Migrating a component closer to canonical structure (if scope allows)

### findings.log Deposit Protocol

When you discover an issue in **adjacent code** (code outside your current task scope), you MUST log it rather than fix it:

**Format**: Append one line to `{project}/.claude/remediation/findings.log`

```
{ISO-timestamp} | {agent} | {task} | {severity} | {description}
```

**Example**:
```
2026-02-07T14:30:00Z | back | T005 | medium | Null check missing in portfolio_service.py:88
```

**Hard Constraint**: Coding agents MUST NOT create inbox files directly. Only QA Reviewer promotes findings.log entries to `remediation/inbox/` during its next review pass.

### Tier 2: Moderate (Assess + Document)
- Touching files outside task scope
- Bug discovered in adjacent code → **log to findings.log, do NOT fix**
- Creating new slice/component not in tasklist

### Tier 3: Significant (HALT)
- New feature not in task
- Architecture change required
- Security risk discovered
- Cross-layer violation (frontend) or domain-adapter coupling (backend)

---

## Architecture Convergence Policy

Some existing components use a simplified structure that predates the canonical target.

**When creating NEW components**: Follow the canonical structure defined in your agent instructions.

**When MODIFYING existing components**: If the change scope allows (Tier 1 drift), migrate toward canonical:
- Add missing `contract.md`
- Split oversized `component.py` into `domain/service.py` + logic (if >200 lines)
- Split `ports.py` into `inbound.py` + `outbound.py` (if >4 protocols)
- Add in-memory test adapter for outbound ports you're testing against
- Split flat test files into `unit/` + `integration/` (if >300 lines)

**NEVER force-migrate** a component you're not already touching for task reasons.

Reference: `.claude/evolution/architecture_debt.md` for the full gap register.

---

## Completion Protocol

After all tasks are processed (or loop exits), produce this report:

```markdown
# Coding Completion Report

## Summary
| Metric | Value |
|--------|-------|
| Tasks Completed | N / M |
| Tasks Skipped | N (with reasons) |
| Quality Gate Pass Rate | X% |
| Evolution Entries Created | N |

## Task Results
| Task | Status | Notes |
|------|--------|-------|
| T001 | completed | All gates pass |
| T002 | completed | Fixed lint on 2nd attempt |
| T003 | skipped | Tier 3 drift - needs BA |

## Evidence Artifacts
- .claude/evidence/quality_gates_run.json
- .claude/evidence/test_report.json

## Next Step
{phase: qa | phase: ba (if drift) | phase: complete (if all done)}
```

Update manifest: set `phase: qa` and ensure all evidence artifacts are written.

---

## Fast-Track Completion

If task meets ALL fast-track criteria:
- Less than 3 files modified
- Bug fix with existing test coverage
- No new user journeys or architecture changes
- Marked as `fast_track: true` in manifest

Then:
- Write evidence normally
- Note `fast_track: true` in task completion
- QA reviewer will run abbreviated review

---

## Startup Protocol

1. **Read manifest**: `{project}/.claude/manifest.yaml`
2. **Verify phase**: Must be `coding` or `fast_track` or `remediation`
3. **Load tasks**: From `outstanding.tasks` (filter by your domain)
4. **Verify BA artifacts**: Spec, tasklist exist at manifest versions
5. **Check remediation**: Handle `outstanding.remediation` (critical/high first)
6. **Read this file**: `~/.claude/docs/shared_agent_protocols.md`
7. **Read architecture debt**: `{project}/.claude/evolution/architecture_debt.md` (if exists)
8. **Run domain-specific pre-flight** (defined in your agent instructions)
