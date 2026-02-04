# Agent Architecture Guide

**Version**: 1.0.0
**Last Updated**: 2026-02-04
**Framework Version**: 2.6.0

## Table of Contents

1. [Overview](#1-overview)
2. [Agent Taxonomy](#2-agent-taxonomy)
3. [Agent Profiles](#3-agent-profiles)
4. [Workflow Lifecycle](#4-workflow-lifecycle)
5. [Handoff Envelopes](#5-handoff-envelopes)
6. [Agent Interactions](#6-agent-interactions)
7. [Manifest as Central Hub](#7-manifest-as-central-hub)
8. [Architecture Patterns](#8-architecture-patterns)
9. [Governance Rules](#9-governance-rules)
10. [Quick Reference](#10-quick-reference)

---

## 1. Overview

The Claude Agent Framework implements a **hierarchical multi-agent governance model** designed to ensure deterministic, task-scoped, and evidenced software development. The architecture enforces the **Prime Directive**:

> **Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.**

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Scope Separation** | Macro agents govern portfolios; micro agents work within projects |
| **Exclusive Permissions** | Only designated agents can perform certain operations |
| **Standardized Handoffs** | Agents communicate via versioned envelope formats |
| **Evidence Requirements** | Every task completion requires machine-readable artifacts |
| **Manifest-First** | All agents read the manifest before any operation |

### Agent Hierarchy Diagram

```d2
direction: down

title: Agent Hierarchy {
  near: top-center
  shape: text
  style.font-size: 24
}

# Scope containers
macro: Macro Level (Portfolio) {
  style.fill: "#e8f4f8"
  style.stroke: "#2196F3"

  devops: DevOps Governor {
    style.fill: "#bbdefb"
    style.stroke: "#1565c0"
    icon: https://icons.terrastruct.com/essentials%2F112-server.svg
  }

  devops.permission: "EXCLUSIVE:\nExecute Deployments" {
    shape: text
    style.font-size: 10
    style.font-color: "#c62828"
  }
}

micro: Micro Level (Project) {
  style.fill: "#fff3e0"
  style.stroke: "#FF9800"

  internal: Internal Agents {
    style.fill: "#ffe0b2"

    solution: Solution Designer
    ba: Business Analyst
    backend: Backend Coding Agent {
      style.fill: "#c8e6c9"
    }
    frontend: Frontend Coding Agent {
      style.fill: "#c8e6c9"
    }
    qa: QA Reviewer
    review: Code Review Agent
    lessons: Lessons Advisor

    backend.permission: "EXCLUSIVE:\nBackend Code" {
      shape: text
      style.font-size: 10
      style.font-color: "#c62828"
    }
    frontend.permission: "EXCLUSIVE:\nFrontend Code" {
      shape: text
      style.font-size: 10
      style.font-color: "#c62828"
    }
  }

  visiting: Visiting Agents {
    style.fill: "#f3e5f5"
    style.stroke-dash: 3

    security: Security Auditor
    perf: Performance Analyst
    a11y: Accessibility Auditor
    domain: Domain Expert
    compliance: Compliance Auditor

    note: "READ-ONLY\nCannot modify code" {
      shape: text
      style.font-size: 10
      style.font-color: "#7b1fa2"
    }
  }
}

# Relationships
macro.devops -> micro.internal.solution: "approves stack" {
  style.stroke: "#1565c0"
}
macro.devops -> micro.internal.backend: "deployment requests" {
  style.stroke: "#1565c0"
  style.stroke-dash: 3
}
macro.devops -> micro.internal.frontend: "deployment requests" {
  style.stroke: "#1565c0"
  style.stroke-dash: 3
}
```

---

## 2. Agent Taxonomy

### 2.1 Scope Classification

Agents operate at two distinct scopes:

| Scope | Entry Point | Characteristics |
|-------|-------------|-----------------|
| **MACRO** | `~/.claude/{domain}/manifest.yaml` | Cross-project governance, exclusive permissions |
| **MICRO** | `{project}/.claude/manifest.yaml` | Single project, internal or visiting |

### 2.2 Agent Types

```d2
direction: right

types: Agent Types {
  style.fill: "#fafafa"

  macro: MACRO AGENTS {
    style.fill: "#e3f2fd"
    desc: |md
      - Portfolio-wide scope
      - Enforce cross-project consistency
      - Exclusive deployment permissions
      - Entry: ~/.claude/{domain}/manifest.yaml
    |

    devops: devops-governor
  }

  micro: MICRO AGENTS {
    style.fill: "#fff8e1"

    internal: INTERNAL {
      style.fill: "#fff3e0"
      desc: |md
        - Participate in workflow
        - Can modify artifacts
        - Phase-specific tasks
        - Entry: {project}/.claude/manifest.yaml
      |

      agents: |md
        - solution-designer
        - business-analyst
        - backend-coding-agent
        - frontend-coding-agent
        - qa-reviewer
        - code-review-agent
        - lessons-advisor
      |
    }

    visiting: VISITING {
      style.fill: "#f3e5f5"
      style.stroke-dash: 3
      desc: |md
        - Read-only access
        - Cannot modify source code
        - Cannot change workflow phase
        - Entry: {project}/.claude/manifest.yaml
      |

      agents: |md
        - security-auditor
        - performance-analyst
        - accessibility-auditor
        - domain-expert
        - compliance-auditor
        - test-specialist
      |
    }
  }
}
```

### 2.3 Exclusive Permissions

Three capabilities are exclusively reserved:

| Permission | Assigned To | Prohibited For |
|------------|-------------|----------------|
| **Write Backend Code** | `backend-coding-agent` | All other agents |
| **Write Frontend Code** | `frontend-coding-agent` | All other agents |
| **Execute Deployments** | `devops-governor` | All other agents |

**Enforcement**: Violations are flagged as CRITICAL governance issues.

---

## 3. Agent Profiles

### 3.1 DevOps Governor (Macro)

```yaml
name: devops-governor
scope: macro
version: 1.1.0
exclusive_permission: execute_deployments
tools: [Read, Write, Edit, Glob, Grep, Bash]
model: sonnet
```

**Entry Point**: `~/.claude/devops/manifest.yaml`

**Responsibilities**:
- Ensure CI/CD consistency across all projects
- Review and approve tech stack proposals
- Enforce non-negotiables checklist
- Execute deployments (ONLY agent permitted)
- Manage database gates via db-harness tool
- Document all decisions (DEC-DEVOPS-XXX)

**Non-Negotiables Enforced**:

| Category | Requirements |
|----------|--------------|
| Quality Gates | lint, type check, unit tests, security tests |
| Security | SAST, secret detection, dependency scanning |
| Deployment | environment separation, progressive deployment, health checks |
| Database | NN-DB-1 through NN-DB-4 (if applicable) |

**Interaction Pattern**:
```d2
devops_flow: DevOps Governor Workflow {
  direction: down

  request: Consultation Request {
    style.fill: "#e3f2fd"
  }

  check: Non-Negotiables Check {
    style.fill: "#fff9c4"
  }

  decision: {
    shape: diamond
    style.fill: "#ffecb3"
  }

  approve: Approve + Stamp {
    style.fill: "#c8e6c9"
  }

  reject: Reject + Required Changes {
    style.fill: "#ffcdd2"
  }

  deploy: Execute Deployment {
    style.fill: "#b2dfdb"
  }

  request -> check -> decision
  decision -> approve: "compliant"
  decision -> reject: "non-compliant"
  approve -> deploy: "deployment request"
}
```

---

### 3.2 Solution Designer

```yaml
name: solution-designer
scope: micro
version: 2.3.0
tools: [Read, Write, Glob, Grep, WebSearch, WebFetch]
model: sonnet
depends_on: [persona-evaluator, devops-governor]
depended_by: [business-analyst]
```

**Responsibilities**:
- Turn user ideas into bounded solution outlines
- Create user flows from personas
- Identify gotchas, ambiguities, threats
- Propose hexagonal architecture
- **MUST CONSULT** DevOps Governor before finalizing

**Output**: `.claude/artifacts/001_solution_envelope_v1.md`

---

### 3.3 Business Analyst

```yaml
name: business-analyst
scope: micro
version: 4.2.0
tools: [Read, Write, Glob, Grep, Bash]
model: sonnet
depends_on: [solution-designer, devops-governor]
depended_by: [backend-coding-agent, frontend-coding-agent]
```

**Responsibilities**:
- Create implementation-grade spec from envelope
- Break down into atomic tasks (30-120 min each)
- Define acceptance criteria and test assertions
- Extract domain rules into YAML
- Define quality gates
- Load ALL tasks into `manifest.outstanding.tasks`
- **MUST VERIFY** DevOps approval exists in envelope

**Outputs**:
- `.claude/artifacts/002_spec_vN.md`
- `.claude/artifacts/003_tasklist_vN.md`
- `.claude/artifacts/004_rules_vN.yaml`
- `.claude/artifacts/005_quality_gates_vN.md`

---

### 3.4 Backend Coding Agent

```yaml
name: backend-coding-agent
scope: micro
version: 1.0.0
exclusive_permission: write_backend_code
tools: [Read, Write, Edit, Glob, Grep, Bash]
model: sonnet
depends_on: [business-analyst]
depended_by: [qa-reviewer, code-review-agent]
```

**Responsibilities**:
- Implement Python backend code (hexagonal architecture)
- Follow ports/adapters pattern strictly
- Write tests BEFORE implementation (TDD)
- Maintain determinism (no datetime.now/uuid4 in core)
- Create evidence artifacts after each task
- Report drift to BA if scope changes

**Cannot**:
- Write frontend code
- Accept direct user coding requests
- Deploy (must request from DevOps)

**Architecture Rules**:
```d2
hex_rules: Hexagonal Import Rules {
  direction: right

  domain: Domain {
    style.fill: "#fff9c4"
    model: "model.py\n(stdlib ONLY)"
    service: "service.py"

    model -> service: {style.stroke-dash: 3}
  }

  ports: Ports {
    style.fill: "#e8f5e9"
    inbound: "inbound.py\n(ABC interfaces)"
    outbound: "outbound.py\n(ABC interfaces)"
  }

  adapters: Adapters {
    style.fill: "#e3f2fd"
    in_api: "api_handler.py"
    out_repo: "postgres_repo.py"
  }

  # Allowed imports (green)
  adapters.in_api -> ports.inbound: {style.stroke: "#4caf50"}
  adapters.in_api -> domain.service: {style.stroke: "#4caf50"}
  adapters.out_repo -> ports.outbound: {style.stroke: "#4caf50"}
  adapters.out_repo -> domain.model: {style.stroke: "#4caf50"}
  domain.service -> ports.inbound: {style.stroke: "#4caf50"}
  domain.service -> ports.outbound: {style.stroke: "#4caf50"}

  # FORBIDDEN (red X)
  forbidden: "FORBIDDEN:\ndomain -> adapters" {
    shape: text
    style.font-color: "#c62828"
    style.font-size: 14
  }
}
```

---

### 3.5 Frontend Coding Agent

```yaml
name: frontend-coding-agent
scope: micro
version: 1.0.0
exclusive_permission: write_frontend_code
tools: [Read, Write, Edit, Glob, Grep, Bash]
model: sonnet
depends_on: [business-analyst]
depended_by: [qa-reviewer, code-review-agent]
```

**Responsibilities**:
- Implement React/TypeScript frontend (Feature-Sliced Design)
- Maintain FSD layer hierarchy strictly
- Types defined in `model/types.ts` BEFORE implementation
- Tests BEFORE implementation
- Include `data-testid` for E2E tests

**Cannot**:
- Write backend code
- Accept direct user coding requests
- Deploy (must request from DevOps)

---

### 3.6 QA Reviewer

```yaml
name: qa-reviewer
scope: micro
version: 2.3.0
tools: [Read, Grep, Glob, Bash]
model: sonnet
depends_on: [backend-coding-agent, frontend-coding-agent]
depended_by: [code-review-agent]
```

**Responsibilities**:
- Quick governance checks (5-10 min)
- Verify TDD adherence, quality gates pass
- Validate Prime Directive compliance
- Validate user journey coverage + E2E tests
- Create BUG/IMPROVE items (sequential IDs)
- Create feedback envelope for sprint planning

**Output**: `.claude/remediation/qa_YYYY-MM-DD.md`

---

### 3.7 Code Review Agent

```yaml
name: code-review-agent
scope: micro
version: 2.3.0
tools: [Read, Grep, Glob, Bash]
model: sonnet
depends_on: [qa-reviewer, backend-coding-agent, frontend-coding-agent]
depended_by: [lessons-advisor]
```

**Responsibilities**:
- Deep code review (60 min)
- Verify tasks actually complete (not just marked done)
- Map user stories → code → tests
- Compare spec → implementation
- Produce detailed bug docs with fix guidance

**Output**: `.claude/remediation/code_review_YYYY-MM-DD.md`

---

### 3.8 Lessons Advisor

```yaml
name: lessons-advisor
scope: micro (with portfolio knowledge)
version: 1.0.0
tools: [Read, Glob, Grep]
model: haiku
```

**Responsibilities**:
- Consult devlessons.md (100+ lessons)
- Provide guidance on framework selection, deployment, architecture
- Create lessons_applied artifacts for new projects
- Capture new lessons after recurring issues (3+)

**Knowledge Base**: `~/.claude/knowledge/devlessons.md`

---

### 3.9 Visiting Agents

Visiting agents are **read-only reviewers** that analyze and report but cannot modify:

```yaml
# Template: ~/.claude/agents/visiting-agent-template.md
permissions:
  - READ all files
  - EXECUTE tests, scanners, profilers
cannot:
  - Modify source code
  - Mark tasks complete
  - Change workflow phase
```

| Type | Focus Area |
|------|------------|
| `security-auditor` | OWASP Top 10, secrets, auth |
| `performance-analyst` | Response time, N+1 queries, memory |
| `accessibility-auditor` | WCAG compliance, screen readers |
| `domain-expert` | Business logic correctness |
| `compliance-auditor` | Regulatory requirements |

---

## 4. Workflow Lifecycle

### 4.1 Phase Sequence

```d2
lifecycle: Project Workflow Lifecycle {
  direction: right

  style.fill: "#fafafa"

  # Phases
  design: Solution Design {
    style.fill: "#e3f2fd"
    icon: https://icons.terrastruct.com/essentials%2F018-lightbulb.svg
  }

  ba: Business Analysis {
    style.fill: "#fff3e0"
    icon: https://icons.terrastruct.com/essentials%2F016-list.svg
  }

  coding: Coding {
    style.fill: "#e8f5e9"
    icon: https://icons.terrastruct.com/tech%2F004-laptop.svg

    backend: Backend {
      style.fill: "#c8e6c9"
    }
    frontend: Frontend {
      style.fill: "#c8e6c9"
    }
  }

  qa: QA Review {
    style.fill: "#fff9c4"
    icon: https://icons.terrastruct.com/essentials%2F108-search.svg
  }

  review: Code Review {
    style.fill: "#f3e5f5"
    icon: https://icons.terrastruct.com/essentials%2F115-settings.svg
  }

  complete: Complete {
    style.fill: "#c8e6c9"
    icon: https://icons.terrastruct.com/essentials%2F041-check.svg
  }

  # Flow
  design -> ba: "envelope" {
    style.stroke: "#1976d2"
    style.stroke-width: 2
  }
  ba -> coding: "spec + tasks" {
    style.stroke: "#f57c00"
    style.stroke-width: 2
  }
  coding -> qa: "evidence" {
    style.stroke: "#388e3c"
    style.stroke-width: 2
  }
  qa -> review: "pass" {
    style.stroke: "#fbc02d"
    style.stroke-width: 2
  }
  qa -> coding: "needs work" {
    style.stroke: "#d32f2f"
    style.stroke-dash: 3
  }
  review -> complete: "verified" {
    style.stroke: "#7b1fa2"
    style.stroke-width: 2
  }
  review -> coding: "findings" {
    style.stroke: "#d32f2f"
    style.stroke-dash: 3
  }

  # DevOps consultation
  devops: DevOps Governor {
    style.fill: "#bbdefb"
    style.stroke: "#1565c0"
    style.stroke-width: 2
  }

  design -> devops: "consult" {
    style.stroke: "#1565c0"
    style.stroke-dash: 3
  }
  devops -> design: "approve" {
    style.stroke: "#1565c0"
    style.stroke-dash: 3
  }

  coding -> devops: "deploy request" {
    style.stroke: "#1565c0"
    style.stroke-dash: 3
  }
}
```

### 4.2 Phase Details

| Phase | Agent | Input | Output | Evidence |
|-------|-------|-------|--------|----------|
| `solution_design` | Solution Designer | User request | Envelope (with DevOps approval) | - |
| `ba` | Business Analyst | Approved envelope | Spec, tasklist, rules, gates | - |
| `coding` | Coding Agents | Tasks from manifest | Source code, tests | quality_gates_run.json |
| `qa` | QA Reviewer | Evidence artifacts | QA report, remediation | qa_YYYY-MM-DD.md |
| `code_review` | Code Review Agent | All above | Review report, feedback | code_review_YYYY-MM-DD.md |
| `complete` | - | - | - | All evidence verified |

### 4.3 Parallel Worktree Development

For larger projects, multiple features can be developed in parallel using git worktrees:

```d2
worktrees: Worktree Parallelization {
  direction: down

  main: Main Worktree (Planning Hub) {
    style.fill: "#e3f2fd"
    style.stroke: "#1565c0"
    style.stroke-width: 2

    ba: BA + Solution Designer {
      style.fill: "#bbdefb"
    }

    backlog: Feature Backlog {
      style.fill: "#e8f5e9"
      f1: "Feature A: ready"
      f2: "Feature B: ready"
      f3: "Feature C: in_progress"
    }

    manifest: manifest.yaml {
      style.fill: "#fff9c4"
      shape: document
    }
  }

  worktrees: Feature Worktrees (Parallel) {
    style.fill: "#fff3e0"

    wt_a: Worktree A: user-auth {
      style.fill: "#ffe0b2"
      backend_a: Backend Tasks
      frontend_a: Frontend Tasks
      qa_a: QA Review
    }

    wt_b: Worktree B: billing {
      style.fill: "#ffe0b2"
      backend_b: Backend Tasks
      frontend_b: Frontend Tasks
      qa_b: QA Review
    }
  }

  main.backlog.f1 -> worktrees.wt_a: "spawn" {
    style.stroke: "#388e3c"
  }
  main.backlog.f3 -> worktrees.wt_b: "spawn" {
    style.stroke: "#388e3c"
  }

  worktrees.wt_a -> main: "merge on complete" {
    style.stroke: "#7b1fa2"
    style.stroke-dash: 3
  }
  worktrees.wt_b -> main: "merge on complete" {
    style.stroke: "#7b1fa2"
    style.stroke-dash: 3
  }

  governance: |md
    **Governance:**
    - max_parallel: 3
    - BUG/IMPROVE IDs are project-global
    - Each worktree has independent manifest
  | {
    style.fill: "#ffecb3"
  }
}
```

---

## 5. Handoff Envelopes

### 5.1 Envelope Types

```d2
envelopes: Handoff Envelope Types {
  direction: down

  # Solution Envelope
  solution: Solution Envelope {
    style.fill: "#e3f2fd"
    from: "Solution Designer"
    to: "Business Analyst"
    file: "001_solution_envelope_v1.md"

    contents: |md
      - Problem statement
      - Personas and journeys
      - Key flows
      - Architecture proposal
      - **DevOps approval stamp**
      - Open questions
    |
  }

  # BA Handoff
  ba_handoff: BA Handoff {
    style.fill: "#fff3e0"
    from: "Business Analyst"
    to: "Coding Agents"

    files: |md
      - 002_spec_vN.md
      - 003_tasklist_vN.md
      - 004_rules_vN.yaml
      - 005_quality_gates_vN.md
    |
  }

  # Coding Completion
  coding_complete: Coding Completion {
    style.fill: "#e8f5e9"
    from: "Coding Agent"
    to: "QA Reviewer"

    evidence: |md
      - quality_gates_run.json
      - test_report.json
      - test_failures.json
    |
  }

  # QA Handoff
  qa_handoff: QA/Review Handoff {
    style.fill: "#fff9c4"
    from: "QA/Code Review"
    to: "Coding Agent"

    file: "qa_YYYY-MM-DD.md"
    contents: |md
      - BUG-XXX entries
      - IMPROVE-XXX entries
      - Priority classification
    |
  }

  # Drift Report
  drift: Drift Report {
    style.fill: "#ffcdd2"
    from: "Coding Agent"
    to: "Business Analyst"

    file: "evolution.md (append)"
    contents: |md
      - EV-XXXX entries
      - Type: drift/change/risk
      - Impact assessment
    |
  }

  # Deployment Request
  deploy: Deployment Request {
    style.fill: "#b2dfdb"
    from: "Any Agent"
    to: "DevOps Governor"

    contents: |md
      - project_slug
      - environment
      - commit_sha
      - quality_gates_evidence
    |
  }

  # Feedback Envelope
  feedback: Feedback Envelope {
    style.fill: "#f3e5f5"
    from: "QA/Code Review"
    to: "Solution Designer"

    file: "feedback_envelope_YYYY-MM-DD.md"
    contents: |md
      - Sprint learnings
      - Architecture recommendations
      - Technical debt items
    |
  }
}
```

### 5.2 Solution Envelope Format

```markdown
# Solution Envelope: {Project Name}

## Version
- **Envelope Version**: 1
- **Created**: YYYY-MM-DD
- **Author**: solution-designer

## Problem Statement
{1-2 paragraphs describing the problem}

## Personas
| Persona | Goals | Pain Points |
|---------|-------|-------------|
| {name}  | {list}| {list}      |

## User Journeys
{Link to 000_user_journeys_v1.md or inline journeys}

## Key Flows
1. {Flow 1 description}
2. {Flow 2 description}

## Architecture
- **Backend**: Python + FastAPI (hexagonal)
- **Frontend**: Next.js + TypeScript (FSD)
- **Database**: PostgreSQL
- **Deployment**: Fly.io

## DevOps Approval
```yaml
devops_approval:
  approved_by: "devops-governor"
  date: "YYYY-MM-DD"
  decision_id: "DEC-DEVOPS-XXX"
  non_negotiables_verified: true
  conditions:
    blocking: []
    non_blocking: []
```

## Threats & Controls
| Threat | Mitigation |
|--------|------------|
| {threat} | {control} |

## Open Questions
- [ ] {Question 1}
- [ ] {Question 2}

## Next Agent
business-analyst
```

### 5.3 BA Handoff Structure

```d2
ba_artifacts: BA Handoff Artifacts {
  direction: right

  spec: 002_spec_vN.md {
    style.fill: "#fff3e0"
    shape: document

    contents: |md
      - Requirements
      - User stories
      - Acceptance criteria
      - API contracts
    |
  }

  tasklist: 003_tasklist_vN.md {
    style.fill: "#fff3e0"
    shape: document

    contents: |md
      - T001: {title}
        - domain: backend/frontend
        - blocked_by: []
        - AC: [list]
    |
  }

  rules: 004_rules_vN.yaml {
    style.fill: "#fff3e0"
    shape: document

    contents: |md
      - Domain rules
      - Validation policies
      - Business constraints
    |
  }

  gates: 005_quality_gates_vN.md {
    style.fill: "#fff3e0"
    shape: document

    contents: |md
      - Lint requirements
      - Type check rules
      - Test coverage
      - Evidence artifacts
    |
  }

  manifest: manifest.yaml {
    style.fill: "#e8f5e9"
    shape: cylinder

    contents: |md
      outstanding.tasks:
        - id: T001
          status: pending
          blocked_by: []
    |
  }

  spec -> manifest: "loaded"
  tasklist -> manifest: "tasks"
  rules -> manifest: "ref"
  gates -> manifest: "ref"
}
```

---

## 6. Agent Interactions

### 6.1 Complete Workflow Diagram

```d2
complete_flow: Complete Agent Workflow {
  direction: down

  # Actors
  user: User {
    shape: person
    style.fill: "#e0e0e0"
  }

  # Phase 1: Solution Design
  phase1: "1. SOLUTION DESIGN" {
    style.fill: "#e3f2fd"

    sd: Solution Designer
    devops: DevOps Governor

    sd -> devops: "consult on stack"
    devops -> sd: "approve + stamp"
  }

  # Phase 2: BA
  phase2: "2. BUSINESS ANALYSIS" {
    style.fill: "#fff3e0"

    ba: Business Analyst
    lessons: Lessons Advisor

    ba -> lessons: "consult lessons"
    lessons -> ba: "applicable lessons"
  }

  # Phase 3: Coding
  phase3: "3. CODING" {
    style.fill: "#e8f5e9"

    backend: Backend Agent
    frontend: Frontend Agent

    note: "Parallel execution\nvia worktrees" {
      shape: text
      style.font-size: 10
    }
  }

  # Phase 4: QA
  phase4: "4. QA REVIEW" {
    style.fill: "#fff9c4"

    qa: QA Reviewer
  }

  # Phase 5: Code Review
  phase5: "5. CODE REVIEW" {
    style.fill: "#f3e5f5"

    review: Code Review Agent
  }

  # Phase 6: Deployment
  phase6: "6. DEPLOYMENT" {
    style.fill: "#b2dfdb"

    deploy: DevOps Governor
  }

  # Flow
  user -> phase1.sd: "request"
  phase1 -> phase2: "001_solution_envelope"
  phase2 -> phase3: "spec + tasks"
  phase3 -> phase4: "evidence"
  phase4 -> phase5: "pass"
  phase5 -> phase6: "verified"

  # Feedback loops
  phase4 -> phase3: "needs work" {
    style.stroke: "#d32f2f"
    style.stroke-dash: 3
  }
  phase5 -> phase3: "findings" {
    style.stroke: "#d32f2f"
    style.stroke-dash: 3
  }
  phase3 -> phase2: "drift" {
    style.stroke: "#ff9800"
    style.stroke-dash: 3
  }

  # Visiting agents
  visiting: Visiting Agents {
    style.fill: "#f5f5f5"
    style.stroke-dash: 3

    sec: Security
    perf: Performance
    a11y: Accessibility
  }

  visiting -> phase3: "analyze" {
    style.stroke-dash: 3
  }
  visiting -> phase4: "report" {
    style.stroke-dash: 3
  }
}
```

### 6.2 Consultation Patterns

```d2
consultations: Agent Consultation Patterns {
  direction: right

  # DevOps consultations
  devops_consult: DevOps Consultation {
    style.fill: "#e3f2fd"

    trigger: |md
      **When to consult:**
      - Proposing tech stack
      - Defining deployment architecture
      - Selecting CI/CD platform
      - Defining environment strategy
    |

    flow: {
      sd: Solution Designer
      devops: DevOps Governor
      ba: Business Analyst

      sd -> devops: "1. propose"
      devops -> sd: "2. approve/reject"
      sd -> ba: "3. envelope\n(with stamp)"
    }
  }

  # Lessons consultation
  lessons_consult: Lessons Consultation {
    style.fill: "#fff3e0"

    trigger: |md
      **When to consult:**
      - Starting new project
      - Choosing framework
      - Making architecture decisions
      - After 3+ recurring issues
    |

    flow: {
      ba: Business Analyst
      lessons: Lessons Advisor

      ba -> lessons: "1. context + stack"
      lessons -> ba: "2. applicable lessons"
    }
  }

  # Deployment request
  deploy_request: Deployment Request {
    style.fill: "#b2dfdb"

    trigger: |md
      **When to request:**
      - Quality gates pass
      - All tests green
      - Evidence artifacts exist
    |

    flow: {
      coding: Coding Agent
      devops: DevOps Governor

      coding -> devops: |md
        project_slug
        environment
        commit_sha
        evidence_path
      |
      devops -> coding: "deployed / rejected"
    }
  }
}
```

### 6.3 Drift Handling Flow

```d2
drift_flow: Drift Detection & Handling {
  direction: down

  start: Coding Agent Working {
    style.fill: "#e8f5e9"
  }

  detect: Drift Detected {
    shape: diamond
    style.fill: "#fff9c4"
  }

  # Tiers
  tier1: Tier 1: Minor {
    style.fill: "#c8e6c9"
    desc: |md
      - Small utilities
      - Missing __init__.py
      - Typo fixes
    |
    action: "Document + Continue"
  }

  tier2: Tier 2: Moderate {
    style.fill: "#fff9c4"
    desc: |md
      - Files outside scope
      - Adjacent bugs
    |
    action: "Halt + EV Entry\nWait for BA"
  }

  tier3: Tier 3: Significant {
    style.fill: "#ffcdd2"
    desc: |md
      - New feature
      - Architecture change
      - Security risk
    |
    action: "HALT IMMEDIATELY\nEscalate to BA/SD"
  }

  ev_log: evolution.md {
    shape: document
    style.fill: "#fff3e0"
  }

  ba: Business Analyst {
    style.fill: "#fff3e0"
  }

  start -> detect
  detect -> tier1: "small"
  detect -> tier2: "moderate"
  detect -> tier3: "significant"

  tier1 -> ev_log: "append"
  tier2 -> ev_log: "append"
  tier2 -> ba: "notify"
  tier3 -> ev_log: "append"
  tier3 -> ba: "escalate"
}
```

---

## 7. Manifest as Central Hub

### 7.1 Manifest Structure

The `.claude/manifest.yaml` file is the **single source of truth** for every project:

```d2
manifest_structure: Manifest Structure {
  direction: down

  manifest: manifest.yaml {
    style.fill: "#e8f5e9"
    style.stroke: "#388e3c"
    style.stroke-width: 2
    shape: cylinder
  }

  sections: {
    style.fill: "#fafafa"

    meta: Metadata {
      style.fill: "#e3f2fd"
      content: |md
        - schema_version
        - project_slug
        - phase
        - last_updated
      |
    }

    artifacts: Artifact Versions {
      style.fill: "#fff3e0"
      content: |md
        - solution_envelope: v1
        - spec: v1
        - tasklist: v1
        - rules: v1
        - quality_gates: v1
      |
    }

    outstanding: Outstanding Work {
      style.fill: "#ffcdd2"
      content: |md
        - tasks: [T001, T002...]
        - remediation: [BUG-001...]
      |
    }

    reviews: Review History {
      style.fill: "#f3e5f5"
      content: |md
        - last_qa_review
        - last_code_review
      |
    }

    worktrees: Worktree State {
      style.fill: "#b2dfdb"
      content: |md
        - feature_backlog
        - active_worktrees
        - worktree_governance
      |
    }
  }

  manifest -> sections.meta
  manifest -> sections.artifacts
  manifest -> sections.outstanding
  manifest -> sections.reviews
  manifest -> sections.worktrees
}
```

### 7.2 Entry Protocol

**ALL agents** must follow this protocol:

```d2
entry_protocol: Agent Entry Protocol {
  direction: down

  start: Agent Starts/Restarts {
    shape: oval
    style.fill: "#e0e0e0"
  }

  read_manifest: "1. Read manifest.yaml FIRST" {
    style.fill: "#e3f2fd"
    style.stroke: "#1565c0"
    style.stroke-width: 2
  }

  extract: "2. Extract Context" {
    style.fill: "#fff3e0"

    items: |md
      - agent_routing: Am I internal/visiting?
      - artifact_versions: Current file paths
      - outstanding.remediation: Critical bugs
      - outstanding.tasks: Pending work
      - compliance_requirements: Rules
    |
  }

  prioritize: "3. Prioritize Work" {
    style.fill: "#fff9c4"

    order: |md
      1. Critical remediation
      2. High remediation
      3. In-progress tasks
      4. Medium remediation
      5. Pending tasks
      6. Low remediation
    |
  }

  proceed: "4. Proceed with Work" {
    style.fill: "#e8f5e9"
  }

  start -> read_manifest -> extract -> prioritize -> proceed

  warning: |md
    **NEVER hardcode artifact paths**
    **ALWAYS read from manifest**
  | {
    style.fill: "#ffcdd2"
    style.font-color: "#c62828"
  }
}
```

### 7.3 Manifest Synchronization

```d2
sync: Manifest Synchronization {
  direction: right

  events: Trigger Events {
    style.fill: "#e3f2fd"

    list: |md
      - Phase change
      - Task completion
      - Artifact version bump
      - Review completion
      - Drift detection
      - Worktree spawn/merge
    |
  }

  update: Update Manifest {
    style.fill: "#fff3e0"

    action: |md
      1. Read current state
      2. Apply changes
      3. Update last_updated
      4. Write atomically
    |
  }

  verify: Verify Sync {
    style.fill: "#e8f5e9"

    checks: |md
      - Artifact files exist
      - Phase matches reality
      - No stale tasks
    |
  }

  events -> update -> verify
}
```

---

## 8. Architecture Patterns

### 8.1 Backend: Hexagonal Architecture

```d2
hexagonal: Hexagonal Architecture {
  direction: right

  # External World
  external: External World {
    style.fill: "#e0e0e0"
    style.stroke-dash: 3

    http: HTTP Clients
    db: Database
    queue: Message Queue
    third: Third-party APIs
  }

  # Adapters Layer
  adapters: Adapters Layer {
    style.fill: "#e3f2fd"

    inbound: Inbound (Driving) {
      style.fill: "#bbdefb"
      api: "FastAPI handlers"
      cli: "CLI commands"
      events: "Event handlers"
    }

    outbound: Outbound (Driven) {
      style.fill: "#bbdefb"
      postgres: "PostgreSQL repo"
      redis: "Redis cache"
      http_client: "HTTP client"
    }
  }

  # Ports Layer
  ports: Ports Layer {
    style.fill: "#fff9c4"
    style.stroke: "#fbc02d"
    style.stroke-width: 2

    inbound_ports: Inbound Ports {
      style.fill: "#fff59d"
      service_if: "Service interfaces\n(ABC)"
    }

    outbound_ports: Outbound Ports {
      style.fill: "#fff59d"
      repo_if: "Repository interfaces\n(ABC)"
      cache_if: "Cache interfaces\n(ABC)"
    }
  }

  # Domain Layer
  domain: Domain Layer {
    style.fill: "#e8f5e9"
    style.stroke: "#388e3c"
    style.stroke-width: 2

    model: Model {
      style.fill: "#c8e6c9"
      entities: "Entities\n(frozen dataclass)"
      values: "Value Objects\n(immutable)"
    }

    service: Service {
      style.fill: "#c8e6c9"
      logic: "Business logic\n(pure functions)"
    }

    rules: Rules {
      style.fill: "#c8e6c9"
      policy: "Domain policies\n(YAML-driven)"
    }
  }

  # Connections
  external.http -> adapters.inbound.api
  external.db -> adapters.outbound.postgres

  adapters.inbound -> ports.inbound_ports
  adapters.outbound -> ports.outbound_ports

  ports.inbound_ports -> domain.service
  domain.service -> ports.outbound_ports

  # Sacred rule
  forbidden: |md
    **SACRED RULE:**
    Domain NEVER imports Adapters

    Core depends on ports only.
    Adapters depend on core.
  | {
    style.fill: "#ffcdd2"
    style.font-color: "#c62828"
  }
}
```

### 8.2 Frontend: Feature-Sliced Design

```d2
fsd: Feature-Sliced Design {
  direction: down

  # Layers (top to bottom)
  app: "Layer 7: app" {
    style.fill: "#e3f2fd"
    desc: "Application shell, providers, routing"
  }

  pages: "Layer 6: pages" {
    style.fill: "#bbdefb"
    desc: "Route pages (composition only)"
  }

  widgets: "Layer 5: widgets" {
    style.fill: "#90caf9"
    desc: "Composite UI blocks"
  }

  features: "Layer 4: features" {
    style.fill: "#64b5f6"
    desc: "User interactions"
  }

  entities: "Layer 3: entities" {
    style.fill: "#42a5f5"
    desc: "Business objects"
  }

  shared: "Layer 2: shared" {
    style.fill: "#2196f3"
    style.font-color: "white"
    desc: "UI kit, utilities"
  }

  # Import direction
  app -> pages: "imports" {style.stroke: "#4caf50"}
  pages -> widgets: "imports" {style.stroke: "#4caf50"}
  widgets -> features: "imports" {style.stroke: "#4caf50"}
  features -> entities: "imports" {style.stroke: "#4caf50"}
  entities -> shared: "imports" {style.stroke: "#4caf50"}

  # Forbidden
  forbidden: |md
    **FORBIDDEN:**
    - Upward imports
    - Same-layer cross-slice
    - Internal module imports

    **USE index.ts for public API**
  | {
    style.fill: "#ffcdd2"
    style.font-color: "#c62828"
  }

  # Slice structure
  slice: Slice Structure {
    style.fill: "#fff3e0"

    structure: |md
      features/auth/
      ├── ui/
      │   ├── LoginForm.tsx
      │   └── LoginForm.test.tsx
      ├── model/
      │   ├── types.ts  ← CONTRACT
      │   ├── store.ts
      │   └── hooks.ts
      ├── api/
      │   ├── queries.ts
      │   └── mutations.ts
      └── index.ts  ← PUBLIC API
    |
  }
}
```

---

## 9. Governance Rules

### 9.1 Prime Directive

> **Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.**

| Attribute | Meaning |
|-----------|---------|
| **Task-scoped** | Only changes for the current task |
| **Atomic** | Complete unit of work, no partial states |
| **Deterministic** | No datetime.now(), uuid4(), random in core |
| **Hexagonal** | Domain never imports adapters |
| **Evidenced** | Machine-readable artifacts prove completion |

### 9.2 ID Sequencing Protocol

```d2
id_protocol: ID Sequencing Protocol {
  direction: right

  search: "1. Search Existing" {
    style.fill: "#e3f2fd"

    cmd: |md
      ```bash
      grep -r "BUG-[0-9]" .claude/
      grep -r "IMPROVE-[0-9]" .claude/
      ```
    |
  }

  find_highest: "2. Find Highest" {
    style.fill: "#fff3e0"

    example: |md
      Found: BUG-001, BUG-002, BUG-015
      Highest: BUG-015
    |
  }

  increment: "3. Increment" {
    style.fill: "#e8f5e9"

    result: |md
      Next ID: BUG-016
    |
  }

  search -> find_highest -> increment

  rules: |md
    **Rules:**
    - IDs are project-global
    - IDs are never reused
    - IDs are sequential
    - Search BEFORE creating
  | {
    style.fill: "#ffecb3"
  }
}
```

### 9.3 Verification Checkpoints

**After ANY file edit**, run verification:

```bash
# Python projects
ruff check . && mypy . && pytest

# Frontend projects
npm run build && npm run lint
```

**Checkpoint Triggers**:

| Trigger | Action |
|---------|--------|
| Every 15 substantive turns | Re-anchor: read rules, gates, prompt |
| Before starting each new task | Re-anchor + verify no blockedBy |
| After error recovery (>3 turns) | Re-anchor + self-audit |
| After any tangent | Re-anchor before resuming |

### 9.4 Evidence Requirements

A task is **NOT COMPLETE** unless:

```d2
evidence: Task Completion Evidence {
  direction: right

  required: Required Artifacts {
    style.fill: "#e8f5e9"

    files: |md
      ✓ .claude/evidence/quality_gates_run.json
      ✓ .claude/evidence/test_report.json
      ✓ .claude/evidence/test_failures.json
    |
  }

  validation: Validation Checks {
    style.fill: "#fff9c4"

    checks: |md
      ✓ All task-relevant tests pass
      ✓ New code has corresponding tests
      ✓ manifest.yaml updated
      ✓ No lint/type errors
    |
  }

  required -> validation -> complete: Complete {
    style.fill: "#c8e6c9"
  }
}
```

---

## 10. Quick Reference

### 10.1 Agent Invocation

| Agent | Subagent Type | When to Invoke |
|-------|---------------|----------------|
| Solution Designer | `solution-designer` | Starting new project |
| Business Analyst | `business-analyst` | Create/update specs |
| Backend Coding | `backend-coding-agent` | Python backend tasks |
| Frontend Coding | `frontend-coding-agent` | React/TS frontend tasks |
| QA Reviewer | `qa-reviewer` | After code changes (quick) |
| Code Review | `code-review-agent` | Deep verification (60 min) |
| Lessons Advisor | `lessons-advisor` | Before decisions |
| DevOps Governor | `devops-governor` | Stack approval, deployments |

### 10.2 File Locations

```
~/.claude/
├── agents/                    # Agent prompt files
├── devops/
│   ├── manifest.yaml          # DevOps portfolio state
│   ├── project_registry.yaml  # All projects
│   └── patterns/              # CI/CD templates
├── docs/                      # Framework documentation
├── prompts/                   # System prompts & playbooks
├── schemas/                   # Validation schemas
└── knowledge/
    └── devlessons.md          # 100+ lessons

{project}/.claude/
├── manifest.yaml              # Project state (read FIRST)
├── artifacts/                 # Versioned BA artifacts
├── evolution/                 # Append-only logs
├── remediation/               # QA/review findings
└── evidence/                  # Quality gate outputs
```

### 10.3 Phase Transitions

| From | To | Trigger | Artifact Created |
|------|----|---------|------------------|
| - | `solution_design` | User request | - |
| `solution_design` | `ba` | Envelope + DevOps approval | 001_solution_envelope |
| `ba` | `coding` | Spec + tasklist complete | 002-005 artifacts |
| `coding` | `qa` | Evidence artifacts exist | evidence/*.json |
| `qa` | `code_review` | QA pass | qa_YYYY-MM-DD.md |
| `qa` | `coding` | QA needs_work | Remediation items |
| `code_review` | `complete` | Review verified | code_review_YYYY-MM-DD.md |
| `code_review` | `coding` | Findings | BUG/IMPROVE items |

### 10.4 Common Commands

```bash
# Validate agents
python ~/.claude/scripts/validate_agents.py

# Worktree management
~/.claude/scripts/worktree_manager.sh create <project> <feature>
~/.claude/scripts/worktree_manager.sh list
~/.claude/scripts/worktree_manager.sh sync <path>

# DevOps tools
db-harness drift SOURCE TARGET --fail-on-breaking
db-harness propagate PROD DEV --masking-rules rules.yaml

# Quality gates
ruff check . && mypy . && pytest
```

---

## Appendix: D2 Diagram Reference

All diagrams in this document use [D2](https://d2lang.com/) syntax. To render:

```bash
# Install D2
curl -fsSL https://d2lang.com/install.sh | sh -s --

# Render diagram
d2 input.d2 output.svg

# With theme
d2 --theme=200 input.d2 output.png
```

For interactive exploration, use the [D2 Playground](https://play.d2lang.com/).

---

**Document Version**: 1.0.0
**Framework Reference**: claude-agent-framework v2.6.0
**Last Updated**: 2026-02-04
