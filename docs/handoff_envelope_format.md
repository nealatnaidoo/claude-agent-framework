# Handoff Envelope Format

**Version**: 2.0
**Date**: 2026-02-06
**Purpose**: Standardized format for agent-to-agent handoffs

---

## Overview

Handoff envelopes are structured documents that transfer work between agents. Each agent in the workflow produces a handoff envelope that the next agent consumes.

## Workflow Sequence

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Project      │─▶│ Persona      │─▶│ Solution     │─▶│ Business     │
│ Initializer  │  │ Evaluator    │  │ Designer     │  │ Analyst      │
└──────────────┘  └──────────────┘  └──────┬───────┘  └──────┬───────┘
       │                │              consults│              │
       ▼                ▼                     ▼              ▼
  .claude/        000_user_          ┌──────────────┐  002_spec_v1.md
  structure       journeys_v1.md     │ DevOps Gov   │  003_tasklist_v1.md
                                     │ (approval)   │  004_rules_v1.yaml
                                     └──────────────┘  005_quality_gates_v1.md
                                                              │
                                     ┌────────────────────────┤
                                     ▼                        ▼
                              ┌──────────────┐   ┌──────────────────┐
                              │ Backend      │   │ Frontend         │
                              │ Coding Agent │   │ Coding Agent     │
                              └──────┬───────┘   └────────┬─────────┘
                                     └────────┬───────────┘
                                              ▼
                                     ┌──────────────┐  ┌──────────────┐
                                     │ QA Reviewer  │─▶│ Code Review  │
                                     │ (per-task)   │  │ (per-feature)│
                                     └──────────────┘  └──────┬───────┘
                                                              │
                                              feedback ◄──────┘
                                              envelope
                                                 │
                                                 ▼
                                        Solution Designer
                                        (next sprint)
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

### 8. Feedback Envelope (QA/Code Review → Solution Designer) [v2.0]

After completing review cycles, QA Reviewer and Code Review Agent create feedback envelopes for Solution Designer to incorporate into next sprint planning.

**When Created**:
- End of sprint/phase
- After reviewing a complete feature
- When `needs_work` findings indicate design issues

**File**: `.claude/remediation/feedback_envelope_YYYY-MM-DD.md` (from QA)
or `.claude/remediation/code_review_feedback_YYYY-MM-DD.md` (from Code Review)

**Format**:

```markdown
# QA Feedback Envelope — {YYYY-MM-DD}

## Summary for Solution Designer

### Review Metrics
| Metric | Backend | Frontend | Total |
|--------|---------|----------|-------|
| Tasks Reviewed | N | N | N |
| Bugs Found | N | N | N |
| Improvements | N | N | N |
| Pass Rate | X% | X% | X% |

### Domain Health
| Domain | Status | Key Issues |
|--------|--------|------------|
| Backend | HEALTHY/NEEDS_ATTENTION | {summary} |
| Frontend | HEALTHY/NEEDS_ATTENTION | {summary} |

### Evolution Log Summary
{Relevant entries from .claude/evolution/evolution.md}

### Patterns Observed
- {Recurring issue pattern 1}
- {Recurring issue pattern 2}

### Recommendations for Next Sprint
1. {Architectural recommendation}
2. {Process improvement}
3. {Technical debt item}

### Unresolved Items Requiring Design Input
| ID | Domain | Issue | Design Question |
|----|--------|-------|-----------------|
| BUG-XXX | backend | {issue} | {question for SD} |
| IMPROVE-XXX | frontend | {issue} | {question for SD} |
```

**Manifest Update**:

```yaml
feedback_envelopes:
  - date: "YYYY-MM-DD"
    source: "qa_reviewer"  # or "code_review_agent"
    file: ".claude/remediation/feedback_envelope_YYYY-MM-DD.md"
    status: "pending_review"  # Solution Designer to review
    domains_affected: ["backend", "frontend"]
```

**Consumption**: Solution Designer reads feedback envelopes before next sprint planning, updates solution envelope with learnings, marks status as `"incorporated"`.

---

### 9. Agent Teams Coordination (Team Lead → Teammates) [v2.0]

Agent Teams enable parallel development within a single session. The team lead distributes tasks from BA artifacts to teammates.

**Prerequisite**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

**Task Distribution**: Team lead reads manifest `outstanding.tasks` and distributes by `domain` tag:

```yaml
# Tasks distributed by domain
backend_tasks:   # → backend-worker teammate
  - id: "T001"
    domain: "backend"
  - id: "T002"
    domain: "backend"

frontend_tasks:  # → frontend-worker teammate
  - id: "T003"
    domain: "frontend"
  - id: "T004"
    domain: "frontend"

integration_tasks:  # → team lead (after both complete)
  - id: "T005"
    domain: "fullstack"
    blocked_by: ["T002", "T004"]
```

**Coordination Rules**:
- All teammates work on the same branch (no merge needed)
- Exclusive permissions still apply (backend teammate writes Python only, frontend writes TypeScript only)
- Team lead updates manifest on completion
- Evidence artifacts created per-teammate, consolidated by team lead

**Completion**: Team lead marks all tasks complete in manifest, triggers QA review.

See: `~/.claude/docs/agent_teams.md` for full setup and configuration.

---

### 10. Worktree Handoff (Legacy, Deprecated) [v1.2]

Git worktree-based parallelism is deprecated in favor of Agent Teams (Type 9). Worktrees are still supported for cross-session parallel work on separate branches.

Full worktree protocol: `~/.claude/docs/agent_operating_model.md` (Section 5.1)
Helper script: `~/.claude/scripts/worktree_manager.sh`

Manifest schema v1.3 still supports `feature_backlog` and `active_worktrees` fields for backward compatibility.

---

## Envelope Validation Rules

1. **DevOps Approval Required**: Solution envelopes MUST have `devops_approval` section before BA can proceed (mechanically enforced via hook)
2. **BA Artifacts Required**: Coding agents CANNOT start without spec and tasklist (mechanically enforced via hook)
3. **Evidence Required**: QA reviewer SHOULD have evidence artifacts before starting review (mechanically enforced via hook)
4. **Version Incrementing**: New versions increment the N in `*_vN.md`
5. **Never Overwrite**: Old versions are preserved for audit trail
6. **Manifest Sync**: Manifest MUST reflect current artifact versions
7. **Phase Transitions**: Only valid phase transitions allowed (see agent operating model)
8. **ID Uniqueness**: All IDs (T001, BUG-001, EV-001) are project-global and never reused
9. **Feedback Loop**: QA/Code Review feedback envelopes consumed by Solution Designer before next sprint
