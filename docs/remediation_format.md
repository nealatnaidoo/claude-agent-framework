# Unified Remediation Format v1.0

## Overview

QA Reviewer and Code Review Agent both produce remediation items. This document defines the unified format for capturing, tracking, and resolving these items.

## Remediation Item Types

### BUG-XXX (Must Fix)

Issues that violate correctness, security, or Prime Directive.

**Severity Levels:**
- `critical` - Security vulnerability, data loss risk, production blocker
- `high` - Incorrect behavior, test failures, spec violation
- `medium` - Edge case not handled, inconsistent behavior
- `low` - Minor issue, unlikely to cause problems

### IMPROVE-XXX (Should Consider)

Quality improvements that don't affect correctness.

**Priority Levels:**
- `high` - Significantly impacts maintainability or performance
- `medium` - Noticeable improvement opportunity
- `low` - Nice to have, minor polish

## Remediation File Structure

### Individual Review Reports

Location: `.claude/remediation/{source}_YYYY-MM-DD.md`

```markdown
# {QA Review | Code Review | Project Review} - YYYY-MM-DD

## Summary

| Metric | Value |
|--------|-------|
| Result | PASS / PASS_WITH_NOTES / NEEDS_WORK / BLOCKED |
| Bugs Found | N |
| Improvements Suggested | N |
| Scope | {Task ID or "Full Project"} |

## Prime Directive Compliance

| Check | Status | Notes |
|-------|--------|-------|
| Task-Scoped | PASS/FAIL | ... |
| Atomic | PASS/FAIL | ... |
| Deterministic | PASS/FAIL | ... |
| Hexagonal | PASS/FAIL | ... |
| Evidenced | PASS/FAIL | ... |

## Bugs (Must Fix)

### BUG-001: {Title}

- **Severity**: critical | high | medium | low
- **Location**: `{file_path}:{line_number}`
- **Evidence**: {How this was discovered}
- **Impact**: {What happens if not fixed}
- **Recommended Fix**: {Specific guidance}

### BUG-002: {Title}
...

## Improvements (Should Consider)

### IMPROVE-001: {Title}

- **Priority**: high | medium | low
- **Location**: `{file_path}:{line_number}` or "Multiple files"
- **Current State**: {What exists now}
- **Suggested Change**: {What to do}
- **Rationale**: {Why this matters}

### IMPROVE-002: {Title}
...

## Required Actions

1. [ ] Fix BUG-001: {summary}
2. [ ] Fix BUG-002: {summary}
3. [ ] Consider IMPROVE-001: {summary}
```

### Consolidated Remediation Tasks

Location: `.claude/remediation/remediation_tasks.md`

This file aggregates all outstanding items from all reviews.

```markdown
# Remediation Tasks

Last updated: YYYY-MM-DD HH:MM:SS

## Critical / High Priority (Fix Before Continuing)

| ID | Type | Summary | Source | Status |
|----|------|---------|--------|--------|
| BUG-001 | critical | Missing null check in calculate_var() | code_review_2026-01-28 | pending |
| BUG-003 | high | SQL injection in search endpoint | qa_2026-01-29 | in_progress |

## Medium Priority (Fix This Sprint)

| ID | Type | Summary | Source | Status |
|----|------|---------|--------|--------|
| BUG-002 | medium | Incorrect timezone handling | code_review_2026-01-28 | pending |
| IMPROVE-001 | medium | Extract validation logic to port | code_review_2026-01-28 | pending |

## Low Priority (Backlog)

| ID | Type | Summary | Source | Status |
|----|------|---------|--------|--------|
| IMPROVE-002 | low | Add docstrings to public API | qa_2026-01-29 | pending |

## Resolved

| ID | Type | Summary | Resolved | Resolution |
|----|------|---------|----------|------------|
| BUG-004 | high | Race condition in cache | 2026-01-29 | Fixed in commit abc123 |

---

## Detail Sections

### BUG-001: Missing null check in calculate_var()

**Source**: code_review_2026-01-28.md
**Severity**: critical
**Location**: `src/core/risk_calculator.py:142`

**Evidence**:
```python
def calculate_var(self, positions: list[Position]) -> Decimal:
    return sum(p.value for p in positions)  # Crashes if positions is None
```

**Impact**: Production crash when portfolio has no positions.

**Recommended Fix**:
```python
def calculate_var(self, positions: list[Position] | None) -> Decimal:
    if not positions:
        return Decimal("0")
    return sum(p.value for p in positions)
```

**Status**: pending
**Assignee**: (unassigned)

---

### BUG-002: Incorrect timezone handling
...
```

## Manifest Integration

When remediation items are created, they must be added to the manifest:

```yaml
outstanding:
  remediation:
    - id: "BUG-001"
      source: "code_review"
      priority: "critical"
      status: "pending"
      summary: "Missing null check in calculate_var()"
      file: "src/core/risk_calculator.py"
      created: "2026-01-28T16:00:00Z"
    - id: "IMPROVE-001"
      source: "code_review"
      priority: "medium"
      status: "pending"
      summary: "Extract validation logic to port"
      file: "src/services/validator.py"
      created: "2026-01-28T16:00:00Z"
```

## ID Assignment Rules

### ID Sequence

IDs are globally unique within a project and never reused.

- BUG IDs: `BUG-001`, `BUG-002`, ... (sequential)
- IMPROVE IDs: `IMPROVE-001`, `IMPROVE-002`, ... (sequential)

### Finding Next ID

```bash
# Find highest BUG ID
grep -h "^### BUG-" .claude/remediation/*.md | \
  sed 's/### BUG-\([0-9]*\).*/\1/' | sort -n | tail -1

# Find highest IMPROVE ID
grep -h "^### IMPROVE-" .claude/remediation/*.md | \
  sed 's/### IMPROVE-\([0-9]*\).*/\1/' | sort -n | tail -1
```

## Workflow: From Finding to Resolution

### 1. Discovery (QA or Code Review)

Reviewer identifies issue and documents:
- Creates entry in review report (`.claude/remediation/{type}_YYYY-MM-DD.md`)
- Adds to consolidated tasks (`.claude/remediation/remediation_tasks.md`)
- Updates manifest (`outstanding.remediation`)
- **Deposits inbox file** in `.claude/remediation/inbox/{ID}_{source}_{YYYY-MM-DD}.md`

### 1b. Discovery (Coding Agent — Lightweight)

Coding agents discovering adjacent issues during implementation:
- **Append one-liner** to `.claude/remediation/findings.log`
- Format: `{ISO-timestamp} | {agent} | {task} | {severity} | {description}`
- **MUST NOT** create inbox files directly (QA promotes these)
- **MUST NOT** ad-hoc fix adjacent code (log it, move on)

### 2. Inbox Triage (BA Agent)

BA agent scans `remediation/inbox/` on startup:
- **Critical findings**: Block new feature work, create remediation tasks as P0 dependencies
- **High findings**: Address this sprint, no blocking
- **Medium/Low findings**: Next cycle, add to backlog
- Parse YAML frontmatter from each inbox file to determine severity
- Sort by severity (critical first), then by date

### 3. Archive Protocol (BA Agent)

After incorporating a finding into the tasklist:
- Read the inbox file
- Append archive annotation to frontmatter:
  - `resolved_as`: Task ID created (e.g., `T015`)
  - `picked_up`: ISO timestamp
  - `tasklist_version`: Tasklist file used (e.g., `003_tasklist_v3.md`)
  - `triage_decision`: Brief rationale
- Write annotated file to `remediation/archive/`
- Delete the original from `inbox/`
- Update manifest with `resolved_as` and `source_remediation` cross-links

**Traceability chain**: `BUG-NNN` → `inbox/` → `T-NNN` in tasklist → `archive/` with `resolved_as`

### 4. Prioritization

Based on severity/priority:
- `critical` bugs block all other work
- `high` bugs should be fixed before new tasks
- `medium` items batched at sprint boundaries
- `low` items go to backlog

### 5. Assignment

When work begins:
- Update `status: in_progress` in manifest
- Update consolidated tasks file

### 6. Resolution

When fixed:
- Update `status: resolved` in manifest
- Add `resolved: YYYY-MM-DDTHH:MM:SSZ` timestamp
- Move to "Resolved" section in consolidated tasks
- Link to commit/PR that fixed it

### 7. Verification

After fix:
- QA Reviewer or Code Review Agent verifies fix
- If not fixed correctly, status goes back to `pending`
- If fixed, remains `resolved`

### Inbox/Archive Relationship to Existing Artifacts

| Artifact | Purpose | Relationship to Inbox |
|----------|---------|----------------------|
| `manifest.outstanding.remediation` | Active tracking registry | Both updated in sync — inbox is queuing, manifest is tracking |
| `remediation_tasks.md` | Consolidated human-readable view | Updated alongside inbox deposit |
| `inbox/` | Arrival queue for findings | Writer: QA, Code Review, Visiting, External Agents. Reader: BA |
| `archive/` | Processed + traceable findings | Writer: BA (annotator). Reader: Audit trail |
| `findings.log` | Lightweight coding agent observations | Writer: Coding agents. Reader: QA (promotes to inbox) |
| `outbox/` | Task commissioning queue | Writer: Internal agents. Reader: External agents (Antigravity) |

## External Research Results (Outbox Protocol)

Results commissioned via the outbox protocol (see `docs/outbox_protocol.md`) arrive in `remediation/inbox/` with `source: "external_research"`.

### Inbox Envelope for External Research

```yaml
---
id: "OBX-001"
source: "external_research"
severity: "low"
created: "2026-02-11T16:00:00Z"
context: "Research VaR calculation library options"
commissioned_by: "back"
task_type: "research"
delivery_format: "yaml"
---
```

### BA Triage Rules for External Research

External research results are informational, not bugs. The BA triages them differently:

| Task Type | BA Action | Archive `resolved_as` |
|-----------|-----------|----------------------|
| `research` | Incorporate into context for relevant tasks | `context_incorporated` |
| `data_gathering` | Attach data to relevant task | Task ID (e.g., `T005`) |
| `analysis` | Feed into solution design decisions | `analysis_consumed` |
| `validation` | Update assumptions, flag if validation failed | `validation_complete` |

### Archive Annotation

```yaml
---
# ... original frontmatter preserved ...
resolved_as: "context_incorporated"
picked_up: "2026-02-12T09:00:00Z"
tasklist_version: "003_tasklist_v3.md"
triage_decision: "Research data incorporated into T005 context"
source_outbox_id: "OBX-001"
---
```

---

## Escalation Triggers

Remediation items can trigger escalation:

| Condition | Escalate To | Action |
|-----------|-------------|--------|
| 3+ similar bugs | Lessons Advisor | Capture pattern in devlessons.md |
| Spec ambiguity | BA Agent | Clarify spec before fixing |
| Architecture violation | Solution Designer | May need design change |
| Unfixable within task scope | BA Agent | Create new task |

## Cross-References

When a remediation item relates to other items:

```markdown
### BUG-005: Cache invalidation race condition

**Related**:
- Caused by: BUG-003 fix (incomplete)
- Blocks: T015, T016
- See also: IMPROVE-002 (suggested refactor would prevent this)
```

Update manifest `blocked_by` for affected tasks:

```yaml
outstanding:
  tasks:
    - id: "T015"
      status: "blocked"
      blocked_by: ["BUG-005"]
```
