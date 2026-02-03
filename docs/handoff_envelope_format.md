# Handoff Envelope Format

**Version**: 1.1
**Date**: 2026-01-31
**Purpose**: Standardized format for agent-to-agent handoffs

---

## Overview

Handoff envelopes are structured documents that transfer work between agents. Each agent in the workflow produces a handoff envelope that the next agent consumes.

## Workflow Sequence

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Solution        │────▶│ Business        │────▶│ Coding          │
│ Designer        │     │ Analyst         │     │ Agent           │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
  001_solution_           002_spec_v1.md          Evidence +
  envelope_v1.md          003_tasklist_v1.md      Updated
  (with DevOps            004_rules_v1.yaml       Manifest
   approval)              005_quality_gates_v1.md
```

---

## Envelope Types

### 1. Solution Envelope (Solution Designer → BA)

**File**: `.claude/artifacts/001_solution_envelope_vN.md`

**Required Sections**:

```markdown
# {project_slug} — Solution Envelope

## Metadata
- **Project Slug**: {slug}
- **Version**: vN
- **Created**: {YYYY-MM-DD}
- **Status**: ready_for_ba | needs_revision

## DevOps Approval (MANDATORY)

```yaml
devops_approval:
  approved_by: "devops-governor"
  date: "{YYYY-MM-DD}"
  canonical_version: "{pattern_version}"
  non_negotiables_verified: true
  notes: "{optional notes}"
```

## Problem Statement
{2-5 lines describing the problem}

## Constraints & Inputs
- Stack: {tech stack}
- Hosting: {where deployed}
- Timeline: {if applicable}
- Budget: {if applicable}

## Personas & Roles
| Persona | Role | Permissions |
|---------|------|-------------|
| {name} | {role} | {what they can do} |

## In Scope
- {item 1}
- {item 2}

## Out of Scope
- {item 1}
- {item 2}

## Core User Flows
### F1: {Flow Name}
**Actor**: {persona}
**Trigger**: {what starts this flow}
**Steps**:
1. {step}
2. {step}
**Outcome**: {result}
**Edge Cases**:
- {case}: {handling}

## Key Domain Objects
| Object | Purpose | Invariants |
|--------|---------|------------|
| {name} | {purpose} | {rules that must never break} |

## Policy & Rules Candidates
- {rule_key}: {description}

## Architecture Proposal

### Components
| ID | Name | Responsibility | Boundary |
|----|------|----------------|----------|
| C1 | {name} | {what it does} | {what it owns} |

### Ports
| ID | Name | Protocol | Used By |
|----|------|----------|---------|
| P1 | {name} | {interface} | {components} |

### Adapters
| ID | Name | Implements | External Dependency |
|----|------|------------|---------------------|
| A1 | {name} | P1 | {library/service} |

## Security & Privacy

### Threats
| ID | Threat | Impact | Likelihood |
|----|--------|--------|------------|
| T1 | {threat} | {impact} | {high/med/low} |

### Controls
| ID | Control | Mitigates | Implementation |
|----|---------|-----------|----------------|
| CTRL1 | {control} | T1 | {how to implement} |

## Operational Reality
- **Deploy Model**: {how deployed}
- **Environment Separation**: {dev/staging/prod}
- **Observability**: {logging, metrics, tracing}
- **Rollback**: {procedure}

## Gotchas & Ambiguities
| Issue | Interpretation | Recommended Default |
|-------|---------------|---------------------|
| {issue} | {interpretation} | {what we'll assume} |

## Open Questions (Blocking Only)
- [ ] {question that must be answered before proceeding}

## BA Handoff Instructions
{Specific guidance for BA on how to translate this into spec/tasklist}
```

---

### 2. BA Handoff (BA → Coding Agent)

**Files**:
- `.claude/artifacts/002_spec_vN.md`
- `.claude/artifacts/003_tasklist_vN.md`
- `.claude/artifacts/004_rules_vN.yaml`
- `.claude/artifacts/005_quality_gates_vN.md`

**Manifest Update**:

```yaml
# In .claude/manifest.yaml
phase: "coding"
phase_started: "{ISO timestamp}"
artifact_versions:
  solution_envelope:
    version: 1
    file: ".claude/artifacts/001_solution_envelope_v1.md"
  spec:
    version: 1
    file: ".claude/artifacts/002_spec_v1.md"
  tasklist:
    version: 1
    file: ".claude/artifacts/003_tasklist_v1.md"
  rules:
    version: 1
    file: ".claude/artifacts/004_rules_v1.yaml"
  quality_gates:
    version: 1
    file: ".claude/artifacts/005_quality_gates_v1.md"
outstanding:
  tasks:
    - id: "T001"
      status: "pending"
      subject: "{task title}"
    - id: "T002"
      status: "pending"
      blocked_by: ["T001"]
      subject: "{task title}"
```

**Task Format in Tasklist**:

```markdown
## T001: {Task Title}

**Status**: pending | in_progress | completed
**Blocked By**: {task IDs or "none"}
**Estimated**: 30-120 min

### Description
{Detailed description of what needs to be done}

### Acceptance Criteria
- [ ] AC1: {Observable criterion}
- [ ] AC2: {Observable criterion}

### Test Assertions
- TA1: {Automated test that proves AC1}
- TA2: {Automated test that proves AC2}

### Files to Create/Modify
- `src/path/to/file.py`

### References
- Spec: Section X.Y
- Rules: {rule_key}
- Flow: F1

---
```

---

### 3. Coding Completion (Coding Agent → QA)

**Manifest Update**:

```yaml
phase: "qa_review"
phase_started: "{ISO timestamp}"
outstanding:
  tasks: []  # All completed
reviews:
  last_qa_review: null  # Pending
```

**Evidence Files**:
- `.claude/evidence/quality_gates_run.json`
- `.claude/evidence/test_report.json`
- `.claude/evidence/test_failures.json`

---

### 4. QA/Review Handoff (QA → Coding Agent for fixes)

**File**: `.claude/remediation/qa_YYYY-MM-DD.md`

**Format**:

```markdown
# QA Review — {YYYY-MM-DD}

## Summary
- **Files Reviewed**: {count}
- **Issues Found**: {count}
- **Critical**: {count}
- **Verdict**: PASS | PASS_WITH_NOTES | NEEDS_WORK

## Findings

### BUG-XXX: {Title}
- **Severity**: critical | high | medium | low
- **Category**: {tdd | hex | determinism | evidence | other}
- **Location**: `{file}:{line}`
- **Description**: {what's wrong}
- **Expected**: {what should happen}
- **Actual**: {what actually happens}
- **Evidence**: {how to reproduce}
- **Fix Guidance**: {suggested fix approach}

### IMPROVE-XXX: {Title}
- **Priority**: high | medium | low
- **Category**: {category}
- **Location**: `{file}:{line}`
- **Description**: {improvement opportunity}
- **Recommendation**: {what to do}
```

**Manifest Update**:

```yaml
phase: "coding"  # Return to coding
outstanding:
  remediation:
    - id: "BUG-001"
      source: "qa_review"
      severity: "high"
      status: "pending"
```

---

### 5. Drift Report (Coding Agent → BA)

**File**: `.claude/evolution/evolution.md` (append-only)

**Format**:

```markdown
## EV-XXXX: {Title}

- **Date**: {YYYY-MM-DD}
- **Type**: drift | change_request | risk | ambiguity
- **Trigger**: {what happened}
- **Impact**: {what breaks / why it matters}
- **Proposed Resolution**: {what BA must change}
- **Refs**:
  - Task: T00X
  - Spec: Section X.Y
  - Files: `{file1}`, `{file2}`
- **Status**: pending_ba | resolved

---
```

**Manifest Update**:

```yaml
phase: "ba"  # Return to BA
drift_detected:
  ev_id: "EV-XXXX"
  date: "{ISO timestamp}"
```

---

### 6. DevOps Consultation (Solution Designer → DevOps Governor)

**Request Format** (via Task tool):

```
"DevOps review for {project} architecture proposal"

Project: {project_slug}
Stack: {tech stack}
Deployment: {deployment architecture}
CI/CD: {platform choice}
Environments: {environment strategy}
```

**Response Format**:

```markdown
## DevOps Consultation Response

**Project**: {project_slug}
**Date**: {YYYY-MM-DD}
**Requested By**: solution-designer

### Non-Negotiables Check

| Requirement | Status | Notes |
|-------------|--------|-------|
| Lint | PASS/FAIL | {notes} |
| Type Check | PASS/FAIL | {notes} |
| Unit Tests | PASS/FAIL | {notes} |
| Security Tests | PASS/FAIL | {notes} |
| SAST | PASS/FAIL | {notes} |
| Secret Detection | PASS/FAIL | {notes} |
| Dependency Scanning | PASS/FAIL | {notes} |
| Environment Separation | PASS/FAIL | {notes} |
| Progressive Deployment | PASS/FAIL | {notes} |
| Health Checks | PASS/FAIL | {notes} |
| Rollback Documentation | PASS/FAIL | {notes} |
| Test Coverage | PASS/FAIL | {notes} |
| Pipeline Metrics | PASS/FAIL | {notes} |

### Decision
**Status**: APPROVED | NEEDS_CHANGES

### Required Changes (if NEEDS_CHANGES)
1. {change 1}
2. {change 2}

### DevOps Stamp (if APPROVED)
```yaml
devops_approval:
  approved_by: "devops-governor"
  date: "{YYYY-MM-DD}"
  canonical_version: "{version}"
  non_negotiables_verified: true
  notes: "{any notes}"
```
```

---

### 7. Deployment Request (Any Agent → DevOps Governor)

**Request Format**:

```yaml
deployment_request:
  project_slug: "{slug}"
  environment: "dev" | "staging" | "prod"
  commit_sha: "{sha}"
  quality_gates_evidence: ".claude/evidence/quality_gates_run.json"
  requesting_agent: "{agent_type}"
  reason: "{why deployment needed}"
```

**Response Format**:

```markdown
## Deployment Response

**Project**: {project_slug}
**Environment**: {environment}
**Status**: DEPLOYED | FAILED | REJECTED

### Verification
- [ ] Quality gates passed
- [ ] Non-negotiables met
- [ ] Correct environment
- [ ] Previous env verified (for prod)

### Result
{Deployment URL or failure reason}
```

---

### 8. BA to Worktree Handoff (BA → Coding Agent via Worktree) [v1.2]

When spawning a feature worktree:

**Main Manifest Update**:

```yaml
# Add to main .claude/manifest.yaml
feature_backlog:
  - slug: "user-auth"
    status: "in_progress"  # Changed from "ready"
    worktree: "user-auth"  # Links to active_worktrees entry

active_worktrees:
  - name: "user-auth"
    path: "../myproject-user-auth"
    branch: "feature/user-auth"
    phase: "coding"
    created: "{ISO timestamp}"
    tasks: ["T001", "T002", "T003"]
    last_sync: "{ISO timestamp}"
```

**Worktree Manifest** (created at `../myproject-user-auth/.claude/manifest.yaml`):

```yaml
schema_version: "1.2"
project_slug: "{project_slug}"
project_name: "{Project Name} - {Feature Name}"
created: "{ISO timestamp}"
phase: "coding"

worktree:
  is_worktree: true
  name: "user-auth"
  branch: "feature/user-auth"
  main_worktree_path: "../myproject"
  created: "{ISO timestamp}"
  feature_scope:
    - "T001"
    - "T002"
    - "T003"

artifact_versions:
  spec:
    version: 1
    file: ".claude/artifacts/002_spec_user_auth_v1.md"
  tasklist:
    version: 1
    file: ".claude/artifacts/003_tasklist_user_auth_v1.md"
  rules:
    version: 1
    file: ".claude/artifacts/004_rules_v1.yaml"
  quality_gates:
    version: 1
    file: ".claude/artifacts/005_quality_gates_v1.md"

outstanding:
  tasks:
    - id: "T001"
      status: "pending"
    - id: "T002"
      status: "pending"
      blocked_by: ["T001"]
    - id: "T003"
      status: "pending"
      blocked_by: ["T002"]
  remediation: []
```

---

### 9. Worktree Completion (Coding Agent → QA → BA for Merge) [v1.2]

When a worktree is complete and ready for merge:

**Worktree Manifest Update**:

```yaml
phase: "complete"
phase_started: "{ISO timestamp}"
outstanding:
  tasks: []  # All completed
reviews:
  last_qa_review:
    date: "{timestamp}"
    result: "pass"
    report_file: ".claude/remediation/qa_YYYY-MM-DD.md"
```

**Main Manifest Update**:

```yaml
active_worktrees:
  - name: "user-auth"
    phase: "complete"  # Changed from "qa"
    last_sync: "{ISO timestamp}"

feature_backlog:
  - slug: "user-auth"
    status: "complete"  # Changed from "in_progress"
```

**Merge Report** (BA creates after merging):

```markdown
# Merge Report — {feature_slug}

## Summary
- **Feature**: {feature_name}
- **Branch**: feature/{feature_slug}
- **Merged**: {ISO timestamp}
- **Tasks Completed**: T001, T002, T003

## QA Review
- **Date**: {date}
- **Result**: pass
- **Report**: .claude/remediation/qa_YYYY-MM-DD.md

## Post-Merge Actions
- [ ] Worktree removed (if auto_cleanup: true)
- [ ] Branch deleted
- [ ] Backlog updated
- [ ] Unblocked features can now spawn
```

---

## Envelope Validation Rules

1. **DevOps Approval Required**: Solution envelopes MUST have `devops_approval` section before BA can proceed
2. **Version Incrementing**: New versions increment the N in `*_vN.md`
3. **Never Overwrite**: Old versions are preserved for audit trail
4. **Manifest Sync**: Manifest MUST reflect current artifact versions
5. **Phase Transitions**: Only valid phase transitions allowed (see agent operating model)
6. **ID Uniqueness**: All IDs (T001, BUG-001, EV-001) are project-global and never reused
