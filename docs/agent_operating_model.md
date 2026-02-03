# Agent Operating Model

**Version**: 1.1
**Date**: 2026-01-31
**Status**: Active
**Authors**: Developed through iterative refinement during Research Lab project

---

## Executive Summary

This document defines the operating model for all agents (internal and visiting) working within the Claude Code ecosystem. It establishes the manifest as the universal entry gate, defines clear boundaries between internal and visiting agents, and provides domain-specific priority scales for consistent issue classification.

---

## Table of Contents

1. [Historical Context: Before This Model](#1-historical-context-before-this-model)
2. [Pain Points Encountered](#2-pain-points-encountered)
3. [Design Decisions and Motivations](#3-design-decisions-and-motivations)
4. [The Unified Entry Model](#4-the-unified-entry-model)
5. [Agent Taxonomy: Macro, Micro, and Visiting](#5-agent-taxonomy-macro-micro-and-visiting)
   - 5.1 [Worktree-Based Parallelization](#51-worktree-based-parallelization)
6. [Manifest Structure for Agent Routing](#6-manifest-structure-for-agent-routing)
7. [Compliance Requirements](#7-compliance-requirements)
8. [Priority Scales by Domain](#8-priority-scales-by-domain)
9. [Coordination Layer](#9-coordination-layer)
10. [Visual Reference Diagrams](#10-visual-reference-diagrams)

---

## 1. Historical Context: Before This Model

### The Original State (Pre-2026-01-31)

Before this model was established, agents operated with:

**Inconsistent Entry Points**
- Some agents read spec files directly by hardcoded name (`{project}_spec.md`)
- Some agents read from manifest
- Some agents skipped manifest entirely on restart/resume
- No clear protocol for context recovery after session breaks

**Fragmented Document Locations**
- Artifacts scattered: root folder, `docs/`, `specs/`, `.claude/artifacts/`
- Evidence files in `artifacts/` vs `.claude/evidence/`
- No versioning convention for artifacts
- Legacy naming (`{project}_spec.md`) conflicting with new convention (`002_spec_v1.md`)

**No Visiting Agent Protocol**
- External reviewers (security, performance, accessibility) had no defined entry point
- No clear boundaries on what visiting agents could/couldn't do
- Findings went into ad-hoc locations, not integrated with remediation system
- ID sequencing was not enforced, leading to potential duplicates

**Inconsistent Priority Classification**
- Each agent/reviewer used their own priority scale
- "Critical" meant different things to different reviewers
- Governance violations (missing tests, hex violations) not consistently prioritized

### Evidence of Problems (Research Lab Project)

The Research Lab project (2026-01-30) exposed these issues:

1. **QA Review found 27 test failures** but the report referenced `artifacts/quality_gates_run.json` while the actual file was at `.claude/evidence/quality_gates_run.json`

2. **Code Review produced 15 BUG items** but many were false positives because the agent looked for files in legacy locations

3. **Remediation tasks file was stale** - manifest showed items resolved but `remediation_tasks.md` still showed them as pending

4. **Multiple system prompts referenced different paths** - BA prompt said `{project}_spec.md`, coding prompt said same, but artifact convention said `.claude/artifacts/002_spec_v1.md`

5. **No protocol for visiting agents** - when external security review was needed, there was no defined process

---

## 2. Pain Points Encountered

### Pain Point 1: Session Amnesia

**Problem**: After context clear or session restart, agents would lose track of:
- Current artifact versions
- Outstanding remediation items
- In-progress tasks
- Recent review results

**Impact**:
- Work repeated unnecessarily
- Critical bugs forgotten
- Inconsistent state across artifacts

**Example**: Coding agent resumed work on T003 but didn't know T001 had been marked as having test failures that needed fixing first.

---

### Pain Point 2: Document Location Confusion

**Problem**: System prompts hardcoded legacy filenames while the actual convention had evolved.

**Evidence**:
```
BA System Prompt (v4.0):    {project}_spec.md
Coding System Prompt (v4.0): {project}_spec.md
Artifact Convention:         .claude/artifacts/002_spec_v1.md
Actual Files:               .claude/artifacts/002_spec_audience_growth_v1.md
```

**Impact**:
- Agents couldn't find artifacts
- False positive findings ("file missing" when it existed elsewhere)
- Manual intervention required to point agents to correct files

---

### Pain Point 3: No External Review Integration

**Problem**: When security/performance/accessibility reviews were needed, there was no:
- Defined entry point for external reviewers
- Standard output format
- Integration with existing remediation system
- ID sequencing to prevent collisions

**Impact**:
- External findings in separate documents, not tracked
- No prioritization relative to internal findings
- Duplicate reports of same issues
- Manual effort to consolidate

---

### Pain Point 4: Compliance Inconsistency

**Problem**: Different agents had different understanding of compliance requirements.

**Evidence**:
- QA flagged "44 determinism violations" that were actually Pydantic default_factory (acceptable pattern)
- Code Review flagged "missing auth checks" that actually existed (looked in wrong file)
- No shared definition of what constitutes "critical" vs "high"

**Impact**:
- False positive findings wasted remediation time
- Real issues potentially missed due to noise
- Loss of confidence in review outputs

---

### Pain Point 5: ID Collision Risk

**Problem**: Multiple reviewers (QA, Code Review, potential external) creating BUG/IMPROVE IDs without coordination.

**Evidence**: QA playbook had no ID sequencing protocol. Only Code Review playbook mentioned searching for existing IDs.

**Impact**:
- Risk of duplicate IDs
- Tracking nightmares when referencing "BUG-003" that exists twice
- No audit trail of which review created which finding

---

## 3. Design Decisions and Motivations

### Decision 1: Manifest as Universal Entry Gate

**Choice**: ALL agents (internal + visiting) MUST read `.claude/manifest.yaml` FIRST on every session start, restart, resume, or context clear.

**Motivation**:
- Single source of truth eliminates "which file is current?" confusion
- Manifest contains paths to all other artifacts (no hardcoding)
- Outstanding items (tasks, remediation) are immediately visible
- Phase information prevents wrong-workflow actions

**Validation**: After implementing this in system prompts v4.1, agents correctly found artifacts in multi-variant projects (Research Lab has 5 variants with different spec files).

---

### Decision 2: Clear Internal vs Visiting Distinction

**Choice**: Agent prompts explicitly state whether the agent is INTERNAL or VISITING, with different permission sets.

**Motivation**:
- Internal agents are part of the workflow: they can modify source, complete tasks, change phases
- Visiting agents are observers/reporters: they analyze, verify, and report but don't modify
- Clear boundaries prevent scope creep and maintain audit trail

**Validation**: Prevents confusion like "should the security auditor fix the vulnerability they found?" (No - they report, internal coding agent fixes through normal TDD workflow)

---

### Decision 3: Visiting Agents CAN Execute (Tests, Gates, Scanners)

**Choice**: Visiting agents have full read + execute permissions, only write-to-source is restricted.

**Motivation**:
- Security auditor needs to RUN exploit to prove vulnerability
- Performance analyst needs to RUN profiler to measure actual times
- A11y auditor needs to RUN axe/lighthouse to get scores
- Test specialist needs to RUN test suite to identify gaps

**Validation**: Restricting execution would make visiting agents unable to verify their findings, reducing report quality to speculation rather than evidence.

---

### Decision 4: Domain-Specific Priority Scales

**Choice**: Define explicit priority criteria for each domain (governance, security, performance, accessibility, domain/business).

**Motivation**:
- "Critical" means different things: SQL injection vs 10s response time vs screen reader blocked
- Governance violations (missing tests, hex violations) need their own scale
- All agents reference same scales = consistent classification

**Validation**: Prevents arguments about "is this really critical?" by providing objective criteria.

---

### Decision 5: Governance Scale Applies to ALL

**Choice**: Compliance with Prime Directive, hexagonal architecture, TDD, and quality gates is non-negotiable for all agents.

**Motivation**:
- Visiting agents must understand the codebase's architectural constraints
- A security fix that violates hex architecture creates new problems
- Missing tests for a fix means the fix itself becomes a liability

**Validation**: Visiting agent finds SQL injection (security critical), but also notes the affected code has no tests (governance high). Both get reported.

---

### Decision 6: Coordination Layer for Unified Feedback

**Choice**: All findings (internal + visiting) flow through a coordination mechanism that:
- Deduplicates across sources
- Validates priority against scales
- Assigns sequential IDs
- Updates manifest consistently

**Motivation**:
- Prevents ID collisions
- Ensures consistent format regardless of source
- Creates single view of all outstanding issues
- Enables prioritized remediation

**Validation**: When security_review and qa_review both find the same SQL injection (one via scanner, one via code inspection), coordination layer recognizes duplicate and links them.

---

### Decision 7: Manifest Contains Routing Instructions

**Choice**: The manifest itself contains agent routing information, compliance requirements, and priority scales.

**Motivation**:
- Since manifest is universal entry gate, it should provide routing
- Visiting agents need to know project-specific compliance expectations
- Priority scales may vary by project (finance vs blog)
- No need to read multiple files to understand context

**Validation**: A visiting security auditor reads manifest, sees `compliance_requirements` section, understands this project requires hexagonal architecture, includes hex violations in their report.

---

## 4. The Unified Entry Model

### Entry Protocol (ALL Agents)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ALL AGENTS (Internal + Visiting)                                            ║
║                                                                               ║
║   On: START | RESTART | RESUME | CONTEXT CLEAR                                ║
║                                                                               ║
║                              │                                                ║
║                              ▼                                                ║
║                                                                               ║
║   ╔═══════════════════════════════════════════════════════════════════════╗  ║
║   ║                                                                        ║  ║
║   ║                    .claude/manifest.yaml                               ║  ║
║   ║                                                                        ║  ║
║   ║                    UNIVERSAL ENTRY GATE                                ║  ║
║   ║                                                                        ║  ║
║   ║   Read:                                                                ║  ║
║   ║   1. agent_routing → Am I internal or visiting?                        ║  ║
║   ║   2. artifact_versions → Where are the files?                          ║  ║
║   ║   3. outstanding.remediation → What's broken? (handle critical first)  ║  ║
║   ║   4. outstanding.tasks → What's in progress?                           ║  ║
║   ║   5. compliance_requirements → What rules apply?                       ║  ║
║   ║   6. priority_scales → How do I classify findings?                     ║  ║
║   ║                                                                        ║  ║
║   ╚═══════════════════════════════════════════════════════════════════════╝  ║
║                                                                               ║
║   NO EXCEPTIONS. NO SHORTCUTS.                                                ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Why This Matters

| Without Universal Entry | With Universal Entry |
|------------------------|---------------------|
| May miss path changes | Always correct file paths |
| Missing remediation items | Critical bugs addressed first |
| Stale artifact versions | Current versions always |
| Session amnesia on restart | Full context recovery |
| "Which file is the spec?" | Manifest tells you |

---

## 5. Agent Taxonomy: Macro, Micro, and Visiting

### Agent Scope Classification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENT TAXONOMY                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MACRO AGENTS (Portfolio Level)                    │    │
│  │                                                                      │    │
│  │  Scope: Across ALL projects                                          │    │
│  │  Entry: ~/.claude/{domain}/manifest.yaml                             │    │
│  │  Registry: Maintains portfolio-wide registry                         │    │
│  │  Example: devops-governor                                            │    │
│  │                                                                      │    │
│  │  Special Permissions:                                                │    │
│  │  - Cross-project consistency enforcement                             │    │
│  │  - Canonical pattern management                                      │    │
│  │  - Migration orchestration                                           │    │
│  │  - Exclusive capabilities (e.g., deployment)                         │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              │ consults/approves                             │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MICRO AGENTS (Project Level)                      │    │
│  │                                                                      │    │
│  │  INTERNAL                          │  VISITING                       │    │
│  │  ────────                          │  ────────                       │    │
│  │  Scope: Single project             │  Scope: Single project          │    │
│  │  Entry: {project}/.claude/manifest │  Entry: {project}/.claude/manifest   │
│  │  Can: Modify source, artifacts     │  Can: Analyze, report           │    │
│  │  Cannot: Deploy (request only)     │  Cannot: Modify source          │    │
│  │                                    │                                 │    │
│  │  Examples:                         │  Examples:                      │    │
│  │  - solution-designer               │  - security-auditor             │    │
│  │  - business-analyst                │  - performance-analyst          │    │
│  │  - coding-agent                    │  - accessibility-auditor        │    │
│  │  - qa-reviewer                     │                                 │    │
│  │  - code-review-agent               │                                 │    │
│  │  - lessons-advisor                 │                                 │    │
│  │                                    │                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Macro Agent Characteristics

| Attribute | Description |
|-----------|-------------|
| **Scope** | Portfolio-wide (all projects) |
| **Entry Point** | Global manifest: `~/.claude/{domain}/manifest.yaml` |
| **Registry** | Maintains cross-project registry |
| **Exclusive Permissions** | May have capabilities no other agent has |
| **Consultation** | Other agents consult for approval |
| **Decisions** | Documents cross-project decisions |

### Current Macro Agents

| Agent | Domain | Exclusive Permission |
|-------|--------|---------------------|
| `devops-governor` | CI/CD & Deployment | Execute deployments |

### Consultation Flow (Macro ↔ Micro)

```
Solution Designer ──────► DevOps Governor ──────► Solution Designer
(proposes stack)         (reviews non-negotiables) (receives approval)
                                │
                                ▼
                         BA receives envelope
                         WITH DevOps stamp
```

### Identity Declaration

Every agent prompt MUST contain an identity statement:

**Internal Agents:**
```
You are an INTERNAL agent, part of the core development workflow.
You can read, execute, modify source code, and control workflow.
```

**Visiting Agents:**
```
You are a VISITING agent, here to provide specialized review.
You can read and execute (for verification), but cannot modify source code.
Your output is findings/reports, not fixes.
```

### Permission Matrix

```
┌───────────────────────────┬───────────────────┬───────────────────────────┐
│         ACTION            │  INTERNAL AGENT   │     VISITING AGENT        │
├───────────────────────────┼───────────────────┼───────────────────────────┤
│                           │                   │                           │
│  READ                     │                   │                           │
│  ────                     │                   │                           │
│  Read source code         │        ✓          │           ✓               │
│  Read manifest            │        ✓          │           ✓               │
│  Read evidence artifacts  │        ✓          │           ✓               │
│  Read remediation files   │        ✓          │           ✓               │
│                           │                   │                           │
├───────────────────────────┼───────────────────┼───────────────────────────┤
│                           │                   │                           │
│  EXECUTE                  │                   │                           │
│  ───────                  │                   │                           │
│  Run tests                │        ✓          │           ✓               │
│  Run quality gates        │        ✓          │           ✓               │
│  Run linters/type checks  │        ✓          │           ✓               │
│  Run security scanners    │        ✓          │           ✓               │
│  Run profilers            │        ✓          │           ✓               │
│  Start dev servers        │        ✓          │           ✓               │
│                           │                   │                           │
├───────────────────────────┼───────────────────┼───────────────────────────┤
│                           │                   │                           │
│  WRITE SOURCE             │                   │                           │
│  ────────────             │                   │                           │
│  Edit source code         │        ✓          │           ✗               │
│  Create source files      │        ✓          │           ✗               │
│  Delete source files      │        ✓          │           ✗               │
│                           │                   │                           │
├───────────────────────────┼───────────────────┼───────────────────────────┤
│                           │                   │                           │
│  WRITE ARTIFACTS          │                   │                           │
│  ───────────────          │                   │                           │
│  Update evidence/*.json   │        ✓          │           ✗               │
│  Update evolution.md      │        ✓          │           ✗               │
│  Update tasklist          │        ✓          │           ✗               │
│  Create review report     │        ✓          │           ✓               │
│  Append remediation_tasks │        ✓          │           ✓               │
│                           │                   │                           │
├───────────────────────────┼───────────────────┼───────────────────────────┤
│                           │                   │                           │
│  WORKFLOW CONTROL         │                   │                           │
│  ────────────────         │                   │                           │
│  Mark tasks complete      │        ✓          │           ✗               │
│  Change phase             │        ✓          │           ✗               │
│  Update artifact versions │        ✓          │           ✗               │
│  Create new tasks         │        ✓          │           ✗               │
│                           │                   │                           │
└───────────────────────────┴───────────────────┴───────────────────────────┘
```

### The Core Principle

```
VISITING AGENTS:

    ANALYZE  →  VERIFY  →  REPORT

    (run anything needed to understand and prove findings)


NOT:

    ANALYZE  →  FIX  →  SHIP

    (that's the internal agent's job)
```

### Why Visiting Agents Need Execute Permission

1. **Security Auditor**: Needs to RUN exploit to prove vulnerability is exploitable
2. **Performance Analyst**: Needs to RUN profiler to measure actual response times
3. **Test Specialist**: Needs to RUN test suite to identify flaky/missing tests
4. **A11y Auditor**: Needs to RUN lighthouse/axe to get accessibility scores
5. **All**: Need to SEE quality gate results to assess project health

Restricting execution would make visiting agents unable to verify their findings, reducing reports to speculation rather than evidence.

### Macro Agent List (Portfolio Level)

| Agent | Domain | Exclusive Permission | Entry Point |
|-------|--------|---------------------|-------------|
| devops-governor | CI/CD & Deployment | Execute deployments | `~/.claude/devops/manifest.yaml` |

### Internal Agent List (Project Level - Micro)

- solution_designer (MUST consult devops-governor for stack/deployment)
- business_analyst (MUST verify devops approval before proceeding)
- coding_agent (MUST request deployment via devops-governor)
- qa_reviewer
- code_review_agent
- lessons_advisor

### Visiting Agent Types (Project Level - Micro)

- security_auditor
- performance_analyst
- accessibility_auditor
- external_reviewer
- domain_expert
- compliance_auditor
- test_specialist

---

## 5.1 Worktree-Based Parallelization (v1.2)

Git worktrees enable parallel development streams where multiple features can be developed simultaneously.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WORKTREE ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  MAIN WORKTREE (Planning Hub)          FEATURE WORKTREES (Implementation)   │
│  ───────────────────────────          ──────────────────────────────────    │
│                                                                              │
│  ┌──────────────────────┐             ┌──────────────────────┐              │
│  │ myproject/           │             │ myproject-user-auth/ │              │
│  │ ├── .claude/         │             │ ├── .claude/         │              │
│  │ │   ├── manifest     │◄───────────►│ │   ├── manifest     │              │
│  │ │   └── artifacts/   │    sync     │ │   └── evidence/    │              │
│  │ └── src/             │             │ └── src/             │              │
│  └──────────────────────┘             └──────────────────────┘              │
│          │                                     ▲                             │
│          │ spawns                              │ registers                   │
│          ▼                                     │                             │
│  ┌──────────────────────┐             ┌──────────────────────┐              │
│  │ feature_backlog:     │             │ myproject-billing/   │              │
│  │ - auth [in_progress] │             │ └── .claude/         │              │
│  │ - billing [ready]    │             │     └── manifest     │              │
│  │ - notifs [blocked]   │             └──────────────────────┘              │
│  └──────────────────────┘                                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Parallel Workflow Timeline

```
Timeline:
═══════════════════════════════════════════════════════════════════════════════►

MAIN WORKTREE (BA + Solution Designer - Continuous Planning):
│
├─[sd]──► Solution Envelope: Auth
├─[ba]──► Spec + Tasklist: Auth ──────────► ADD TO BACKLOG (priority 1)
│
├─[sd]──► Solution Envelope: Billing
├─[ba]──► Spec + Tasklist: Billing ───────► ADD TO BACKLOG (priority 2)
│
│                              ◄── User: "Start coding" ──►
│                                         │
├─[ba]──► Handle drift from worktree      │
├─[ba]──► Continue planning Feature C     │
├─[ba]──► Merge completed features        │
                                          │
═══════════════════════════════════════════════════════════════════════════════

FEATURE WORKTREES (Coding Agents - Parallel Implementation):
│
│   WORKTREE: auth                       WORKTREE: billing
│   ─────────────                        ────────────────
│   │                                    │
│   ├─[coding]─► T001: Login             ├─[coding]─► T004: Stripe setup
│   ├─[coding]─► T002: Password reset    ├─[coding]─► T005: Subscriptions
│   ├─[coding]─► T003: Sessions          ├─[coding]─► T006: Invoices
│   ├─[qa]─────► Review                  ├─[qa]─────► Review
│   └─[complete]► Ready for merge        └─[complete]► Ready for merge
```

### Worktree Lifecycle States

```
┌──────────────┐
│   CREATED    │ ← BA creates worktree, initializes manifest
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   CODING     │ ← Coding agent implements tasks
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     QA       │ ← QA reviewer checks work
└──────┬───────┘
       │
       ├──── needs_work ────► back to CODING
       │
       ▼
┌──────────────┐
│   COMPLETE   │ ← Ready for merge
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   MERGED     │ ← Branch merged to main
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   REMOVED    │ ← Worktree cleaned up (if auto_cleanup)
└──────────────┘
```

### Manifest Hierarchy

**Main Manifest** (`.claude/manifest.yaml`):
```yaml
phase: "ba"  # Main stays in planning mode
feature_backlog: [...]        # Queue of ready features
active_worktrees: [...]       # Registry of spawned worktrees
worktree_governance:
  max_parallel: 3             # Limit concurrent worktrees
  auto_cleanup: true
```

**Worktree Manifest** (`../myproject-feature/.claude/manifest.yaml`):
```yaml
phase: "coding"               # Independent phase
worktree:
  is_worktree: true
  main_worktree_path: "../myproject"
  feature_scope: ["T001", "T002", "T003"]
```

### Agent Responsibilities by Worktree

| Agent | Main Worktree | Feature Worktree |
|-------|---------------|------------------|
| **BA** | Creates specs, spawns worktrees, merges | Updates feature artifacts if drift |
| **Coding** | Implements main-only tasks | Implements feature_scope tasks only |
| **QA** | Reviews main work, approves merges | Reviews worktree work |
| **Code Review** | Deep review after merge | Deep review before merge approval |

### Cross-Worktree Communication

Worktrees communicate via manifest updates:

1. **Coding Agent** updates worktree manifest phase
2. **Main manifest** `active_worktrees[].phase` reflects current state
3. **BA Agent** reads main manifest to see all worktree statuses
4. **QA Agent** discovers reviewable worktrees from main manifest

### Governance Rules

| Rule | Description |
|------|-------------|
| Max Parallelism | `worktree_governance.max_parallel` limits concurrent worktrees |
| Feature Scope | Tasks assigned to exactly one worktree |
| Independent State | Each worktree has complete `.claude/` state |
| Manifest as Contract | Phase changes sync to main manifest |
| Merge Prerequisites | QA must pass before merge approval |
| ID Sequencing | BUG/IMPROVE IDs are project-global across all worktrees |

### Helper Script

```bash
# Worktree management utility
~/.claude/scripts/worktree_manager.sh

# Commands:
create <project> <feature>    # Create new feature worktree
list                          # List all worktrees with phases
status [path]                 # Show worktree status
sync <path>                   # Sync shared artifacts
remove <path>                 # Remove worktree
backlog list                  # Show feature backlog
backlog next                  # Find next feature to spawn
spawn-from-backlog <slug>     # Create worktree from backlog
```

---

## 6. Manifest Structure for Agent Routing

### New Sections Required

```yaml
# .claude/manifest.yaml

# ═══════════════════════════════════════════════════════════════════════════
# AGENT ROUTING - READ THIS SECTION FIRST
# ═══════════════════════════════════════════════════════════════════════════

agent_routing:

  # ─────────────────────────────────────────────────────────────────────────
  # INTERNAL AGENTS (part of core workflow)
  # ─────────────────────────────────────────────────────────────────────────
  internal_agents:
    - solution_designer
    - business_analyst
    - coding_agent
    - qa_reviewer
    - code_review_agent
    - lessons_advisor

  internal_agent_protocol:
    entry_point: "manifest.yaml"
    must_read:
      - "agent_routing (this section)"
      - "artifact_versions (get file paths)"
      - "outstanding.remediation (handle critical first)"
      - "outstanding.tasks (resume work)"
    must_comply:
      - "prime_directive"
      - "hexagonal_architecture"
      - "tdd_requirements"
      - "quality_gates"
    prompt_location: "~/.claude/agents/{agent_name}.md"

  # ─────────────────────────────────────────────────────────────────────────
  # VISITING AGENTS (external reviewers, auditors, specialists)
  # ─────────────────────────────────────────────────────────────────────────
  visiting_agents:
    recognized_types:
      - security_auditor
      - performance_analyst
      - accessibility_auditor
      - external_reviewer
      - domain_expert
      - compliance_auditor
      - test_specialist

  visiting_agent_protocol:
    entry_point: "manifest.yaml"
    must_read:
      - "agent_routing.visiting_agent_protocol (this section)"
      - "project_context (quick orientation)"
      - "outstanding.remediation (avoid duplicates)"
      - "compliance_requirements (non-negotiable)"
      - "priority_scales (for classification)"
    must_comply:
      - "id_sequencing_protocol"
      - "output_format_requirements"
      - "priority_scale_for_domain"
    prompt_location: "~/.claude/agents/visiting-agent-template.md"
    output_location: ".claude/remediation/{type}_review_YYYY-MM-DD.md"
    can_do:
      - "read all project files"
      - "run tests and quality gates"
      - "run security scanners"
      - "run profilers and analysis tools"
      - "create review reports"
      - "append to remediation_tasks.md"
    must_not:
      - "modify source code"
      - "mark tasks complete"
      - "change artifact versions"
      - "change workflow phase"
      - "skip ID sequencing"
```

---

## 7. Compliance Requirements

### Non-Negotiable Standards

These apply to ALL agents (internal and visiting). Visiting agents must flag violations as findings.

```yaml
compliance_requirements:

  prime_directive:
    statement: "Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced."
    applies_to: "all_agents"
    violations_are: "blocking"

  hexagonal_architecture:
    core_rules:
      - "Core depends only on ports (protocols/interfaces)"
      - "Adapters implement ports and contain side effects"
      - "No framework imports in core"
    visiting_agent_note: "Flag violations, do not fix"

  determinism:
    forbidden_in_core:
      - "datetime.now() / datetime.utcnow()"
      - "uuid4() / random.*"
      - "global mutable state"
    required_pattern: "Inject via TimePort, UUIDPort, RandomPort"
    visiting_agent_note: "Flag violations as HIGH priority"

  testing_requirements:
    tdd_mandate: "Tests written before implementation"
    coverage_expectation: "All public functions in domain/services"
    evidence_artifacts:
      - ".claude/evidence/test_report.json"
      - ".claude/evidence/test_failures.json"
    visiting_agent_note: "Absence of tests is HIGH priority finding"

  quality_gates:
    must_pass:
      - "lint (ruff/eslint)"
      - "type check (mypy/tsc)"
      - "tests (pytest/jest)"
    evidence_artifact: ".claude/evidence/quality_gates_run.json"
    visiting_agent_note: "Missing/failing gates is CRITICAL finding"
```

---

## 8. Priority Scales by Domain

### Governance Scale (Universal - Applies to ALL)

```yaml
governance:
  critical:
    - "Quality gates not running or failing"
    - "No test coverage for changed code"
    - "Hexagonal boundary violation (core imports adapter)"
    - "Prime directive violation"
  high:
    - "Determinism violation (datetime/random in core)"
    - "Missing contract.md for component"
    - "TDD violation (tests after implementation)"
  medium:
    - "Missing type hints on public interface"
    - "Incomplete test coverage"
  low:
    - "Code style inconsistency"
    - "Documentation gaps"
```

### Security Scale (for security_auditor)

```yaml
security:
  critical:
    - "Remote Code Execution (RCE)"
    - "SQL Injection"
    - "Authentication bypass"
    - "Privilege escalation"
    - "Secrets in code/logs"
  high:
    - "Cross-Site Scripting (XSS)"
    - "CSRF vulnerability"
    - "Insecure direct object reference"
    - "Missing auth on endpoint"
  medium:
    - "Information disclosure"
    - "Missing rate limiting"
    - "Weak password policy"
  low:
    - "Security headers missing"
    - "Verbose error messages"
```

### Performance Scale (for performance_analyst)

```yaml
performance:
  critical:
    - "Response time > 10s"
    - "Memory leak causing OOM"
    - "Database connection exhaustion"
    - "Blocking main thread"
  high:
    - "Response time > 3s"
    - "N+1 query pattern"
    - "Missing database index"
    - "Unbounded query results"
  medium:
    - "Response time > 1s"
    - "Inefficient algorithm (O(n²) when O(n) possible)"
    - "Large bundle size"
  low:
    - "Minor optimization opportunity"
    - "Caching opportunity"
```

### Accessibility Scale (for accessibility_auditor)

```yaml
accessibility:
  critical:
    - "Core functionality inaccessible to screen readers"
    - "Keyboard trap (cannot escape focus)"
    - "No skip navigation on content-heavy pages"
    - "Form cannot be submitted without mouse"
  high:
    - "Images missing alt text"
    - "Form inputs missing labels"
    - "Color contrast below 4.5:1"
    - "Focus indicator not visible"
  medium:
    - "Heading hierarchy broken"
    - "Link text not descriptive"
    - "Touch targets < 44px"
  low:
    - "Decorative images not marked aria-hidden"
    - "Landmark regions incomplete"
```

### Domain/Business Scale (for domain_expert)

```yaml
domain:
  critical:
    - "Business logic produces incorrect results"
    - "Regulatory/compliance violation"
    - "Data integrity issue"
  high:
    - "Edge case not handled"
    - "Business rule not enforced"
    - "Workflow can reach invalid state"
  medium:
    - "User experience friction"
    - "Terminology inconsistency"
  low:
    - "Nice-to-have feature missing"
```

---

## 9. Coordination Layer

### Purpose

A mechanism that receives findings from ALL agents (internal + visiting) and:
- Deduplicates across sources
- Validates priority against scales
- Assigns sequential IDs
- Routes to appropriate handler
- Updates manifest consistently

### Flow Diagram

```
                              INTERNAL AGENTS
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │    QA    │ │   Code   │ │ Lessons  │
   │ Reviewer │ │  Review  │ │ Advisor  │
   └────┬─────┘ └────┬─────┘ └────┬─────┘
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
   ╔═══════════════════════════════════════════════════════════════════╗
   ║                                                                    ║
   ║                    REMEDIATION COORDINATOR                         ║
   ║                                                                    ║
   ║   1. Receive finding                                               ║
   ║   2. Check for duplicates (file:line fingerprint)                  ║
   ║   3. Validate priority against scale                               ║
   ║   4. Assign next available ID (BUG-XXX / IMPROVE-XXX)              ║
   ║   5. Append to remediation_tasks.md                                ║
   ║   6. Update manifest.outstanding.remediation                       ║
   ║   7. Route critical items to immediate attention                   ║
   ║                                                                    ║
   ╚═══════════════════════════════════════════════════════════════════╝
                     ▲
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐
   │ Security │ │   Perf   │ │   A11y   │
   │ Auditor  │ │ Analyst  │ │ Auditor  │
   └──────────┘ └──────────┘ └──────────┘
                              VISITING AGENTS
```

### Unified Output

```
.claude/remediation/remediation_tasks.md

┌───────────┬─────────────────┬──────────┬──────────┬─────────────────────┐
│ ID        │ Source          │ Priority │ Status   │ Summary             │
├───────────┼─────────────────┼──────────┼──────────┼─────────────────────┤
│ BUG-001   │ qa_review       │ critical │ pending  │ Test failures...    │
│ BUG-002   │ code_review     │ high     │ resolved │ Missing contract... │
│ BUG-003   │ security_review │ critical │ pending  │ SQL injection...    │
│ BUG-004   │ perf_review     │ high     │ pending  │ N+1 query...        │
│ BUG-005   │ a11y_review     │ high     │ pending  │ Missing alt text... │
└───────────┴─────────────────┴──────────┴──────────┴─────────────────────┘

ALL SOURCES UNIFIED. SINGLE ID SEQUENCE. CONSISTENT FORMAT.
```

---

## 10. Visual Reference Diagrams

### Document Lifecycle Flow

```
USER REQUEST
     │
     ▼
┌──────────────────┐
│ SOLUTION DESIGNER│
└────────┬─────────┘
         │
         ▼ Creates
┌──────────────────────────────────────┐
│ 001_solution_envelope_v1.md          │
└──────────────────────────────────────┘
         │
         ▼ Updates
┌──────────────────────────────────────┐
│ manifest.yaml (phase: ba)            │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│    BA AGENT      │
└────────┬─────────┘
         │
         ▼ Creates
┌──────────────────────────────────────┐
│ 002_spec_v1.md                       │
│ 003_tasklist_v1.md                   │
│ 004_rules_v1.yaml                    │
│ 005_quality_gates_v1.md              │
└──────────────────────────────────────┘
         │
         ▼ Updates
┌──────────────────────────────────────┐
│ manifest.yaml (phase: coding)        │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  CODING AGENT    │ ◄── Reads manifest FIRST
└────────┬─────────┘
         │
         ├──► Creates source code
         ├──► Updates evidence/*.json (after EVERY edit)
         ├──► Appends to evolution.md (if drift)
         └──► Updates manifest (tasks, last_updated)
         │
         ▼
┌──────────────────┐
│   QA REVIEWER    │ ◄── Reads manifest FIRST
└────────┬─────────┘
         │
         ├──► Creates qa_YYYY-MM-DD.md
         ├──► Appends to remediation_tasks.md
         └──► Updates manifest (reviews, remediation)
         │
         ▼
┌──────────────────┐
│ CODE REVIEW AGENT│ ◄── Reads manifest FIRST
└────────┬─────────┘
         │
         ├──► Creates code_review_YYYY-MM-DD.md
         ├──► Creates code_review_YYYY-MM-DD.json
         ├──► Appends to remediation_tasks.md
         └──► Updates manifest (reviews, remediation)
         │
         ▼ (if 3+ recurring issues)
┌──────────────────┐
│ LESSONS ADVISOR  │
└────────┬─────────┘
         │
         ├──► Creates 006_lessons_applied_v1.md
         ├──► Appends to devlessons.md (global)
         └──► Updates manifest (artifact_versions)


         │
         ▼ (when external review needed)
┌──────────────────┐
│ VISITING AGENT   │ ◄── Reads manifest FIRST
└────────┬─────────┘
         │
         ├──► Creates {type}_review_YYYY-MM-DD.md
         ├──► Appends to remediation_tasks.md
         └──► Updates manifest.reviews.external
```

### Folder Structure

```
{project}/
│
├── .claude/                          ◄── ALL CLAUDE ARTIFACTS
│   │
│   ├── manifest.yaml                 ◄── SOURCE OF TRUTH (read first!)
│   │
│   ├── artifacts/                    ◄── VERSIONED BA ARTIFACTS
│   │   ├── 001_solution_envelope_v1.md
│   │   ├── 002_spec_v1.md
│   │   ├── 003_tasklist_v1.md
│   │   ├── 004_rules_v1.yaml
│   │   ├── 005_quality_gates_v1.md
│   │   ├── 006_lessons_applied_v1.md
│   │   └── 007_coding_prompt_v1.md
│   │
│   ├── evolution/                    ◄── APPEND-ONLY LOGS
│   │   ├── evolution.md
│   │   └── decisions.md
│   │
│   ├── remediation/                  ◄── REVIEW OUTPUTS
│   │   ├── qa_2026-01-30.md
│   │   ├── code_review_2026-01-30.md
│   │   ├── security_review_2026-01-31.md    ◄── VISITING
│   │   ├── perf_review_2026-01-31.md        ◄── VISITING
│   │   └── remediation_tasks.md
│   │
│   └── evidence/                     ◄── QUALITY GATE OUTPUTS
│       ├── quality_gates_run.json
│       ├── test_report.json
│       ├── test_failures.json
│       └── lint_report.json
│
└── src/                              ◄── SOURCE CODE
```

---

## Appendix A: Migration from Legacy Model

If your project uses legacy naming (`{project}_spec.md` at root):

1. Create `.claude/` folder structure
2. Move and rename files with sequence numbers
3. Create manifest with current artifact versions
4. Update project CLAUDE.md to reference new locations

See: `~/.claude/docs/artifact_convention.md` for detailed migration steps.

---

## Appendix B: Validation Checklist

When reviewing this model's implementation:

- [ ] All agent prompts contain identity statement (INTERNAL or VISITING)
- [ ] All agents read manifest FIRST on session start
- [ ] Artifact paths come from manifest, not hardcoded
- [ ] Evidence files go to `.claude/evidence/`
- [ ] Remediation files go to `.claude/remediation/`
- [ ] ID sequencing searches for highest existing ID
- [ ] Priority scales are defined and referenced
- [ ] Compliance requirements are documented
- [ ] Visiting agent template exists

---

## Appendix C: Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-31 | Initial release - unified agent operating model |

---

**Document Location**: `~/.claude/docs/agent_operating_model.md`
**Related Documents**:
- `~/.claude/docs/document_consistency.md`
- `~/.claude/docs/artifact_convention.md`
- `~/.claude/agents/visiting-agent-template.md`
