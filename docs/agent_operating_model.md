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

1. [The Unified Entry Model](#4-the-unified-entry-model)
2. [Agent Taxonomy: Macro, Micro, and Visiting](#5-agent-taxonomy-macro-micro-and-visiting)
3. [Manifest Structure for Agent Routing](#6-manifest-structure-for-agent-routing)
4. [Compliance Requirements](#7-compliance-requirements)
5. [Priority Scales by Domain](#8-priority-scales-by-domain)
6. [Coordination Layer](#9-coordination-layer)
7. [Visual Reference Diagrams](#10-visual-reference-diagrams)
- [Appendix D: Historical Context and Design Decisions](#appendix-d-historical-context-and-design-decisions)

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
| 1.2 | 2026-02-07 | Removed deprecated worktree section (S5.1), moved historical context to appendix |

---

## Appendix D: Historical Context and Design Decisions

This model was developed during the Research Lab project (2026-01-30) to address five key pain points: session amnesia, document location confusion, lack of external review integration, compliance inconsistency, and ID collision risk. Seven design decisions were made:

1. **Manifest as Universal Entry Gate** — single source of truth for all agents
2. **Clear Internal vs Visiting Distinction** — different permission sets
3. **Visiting Agents CAN Execute** — run tests/scanners but cannot modify code
4. **Domain-Specific Priority Scales** — consistent classification across domains
5. **Governance Scale Applies to ALL** — Prime Directive is non-negotiable
6. **Coordination Layer for Unified Feedback** — deduplication, sequential IDs
7. **Manifest Contains Routing Instructions** — self-describing entry gate

For full details on the original pain points and decision rationale, see git history for this file (pre-v1.2).

---

**Document Location**: `~/.claude/docs/agent_operating_model.md`
**Related Documents**:
- `~/.claude/docs/document_consistency.md`
- `~/.claude/docs/artifact_convention.md`
- `~/.claude/agents/visiting-agent-template.md`
