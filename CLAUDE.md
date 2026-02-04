# Claude Code Global Instructions

## Central Knowledge Base

Always reference the development prompts folder for established patterns, lessons, and agent prompts:

**Location**: `~/Developer/claude-agent-framework/` (or `~/.claude/` via symlinks)

**Version**: v2.7 (split_coding_agents) - Updated 2026-02-04

### Agent Taxonomy: Macro vs Micro

Agents are classified by scope:

| Scope | Entry Point | Characteristics |
|-------|-------------|-----------------|
| **MACRO (Portfolio)** | `~/.claude/{domain}/manifest.yaml` | Cross-project governance, exclusive permissions |
| **MICRO (Project)** | `{project}/.claude/manifest.yaml` | Single project, internal or visiting |

### Macro Agents (Portfolio Level)

| Agent | Domain | Exclusive Permission | Prompt File |
|-------|--------|---------------------|-------------|
| `devops-governor` | CI/CD & Deployment | **Execute deployments** | `~/.claude/agents/devops-governor.md` |

**Macro agents** manage consistency across all projects. Other agents MUST consult them for their domain.

### Micro Agents (Project Level)

| Agent | When to Use | Exclusive Permission | Prompt File |
|-------|-------------|---------------------|-------------|
| `persona-evaluator` | First step - define user journeys and personas before solution design | **Define user journeys** | `~/.claude/agents/persona-evaluator.md` |
| `solution-designer` | Turn ideas into bounded solutions (MUST consult devops-governor) | - | `~/.claude/agents/solution-designer.md` |
| `business-analyst` | Create/update BA artifacts (MUST verify devops approval) | - | `~/.claude/agents/business-analyst.md` |
| `backend-coding-agent` | Implement Python backend code (hexagonal architecture) - **NEVER accepts direct user requests** | **Write backend code** | `~/.claude/agents/backend-coding-agent.md` |
| `frontend-coding-agent` | Implement React/TypeScript frontend (FSD architecture) - **NEVER accepts direct user requests** | **Write frontend code** | `~/.claude/agents/frontend-coding-agent.md` |
| `qa-reviewer` | After code changes - governance check (TDD, hexagonal, gates) + persona validation | - | `~/.claude/agents/qa-reviewer.md` |
| `code-review-agent` | Deep task completion verification - interpret specs/stories/tests, produce bug docs | - | `~/.claude/agents/code-review-agent.md` |
| `lessons-advisor` | Before decisions - consult past lessons and operationalize into gates | - | `~/.claude/agents/lessons-advisor.md` |

**CRITICAL - Exclusive Permissions:**
- **Backend Code**: ONLY `backend-coding-agent` can write/modify Python backend code
- **Frontend Code**: ONLY `frontend-coding-agent` can write/modify React/TypeScript frontend code
- **Deployments**: ONLY `devops-governor` can execute deployments
- **User Journeys**: ONLY `persona-evaluator` can define user journeys and personas

**CRITICAL - BA-Only Input Constraint:**
- Coding agents accept work ONLY from BA-produced artifacts (spec, tasklist)
- Users MUST NOT request coding directly - they must go through BA workflow
- If a user requests code changes, redirect them to create a spec first

**Task Assignment:**
- Backend tasks (Python, API, database): `backend-coding-agent`
- Frontend tasks (React, TypeScript, UI): `frontend-coding-agent`
- Full-stack tasks: Split between agents with clear handoff

### Persona Lens Packs

Lens packs define domain-specific evaluation perspectives. Available at `~/.claude/lenses/`:

| Pack | Domain | Lenses |
|------|--------|--------|
| `creator_publishing.yaml` | Blogs, newsletters, content | Operator, Marketer, Editor, Platform, Trust |
| `fitness_training.yaml` | PT apps, gyms, coaching | Coach, Business Owner, Trainee, Payer, Safety |
| `saas_b2b.yaml` | Business software, tools | Buyer, Admin, Power User, Casual User, Support |

**Usage:**
- Default: `"Run QA with persona validation"` → uses creator_publishing
- Specific: `"Run QA with fitness lens pack"` → uses fitness_training
- Project: Create `.claude/persona_lenses.yaml` in your project → auto-detected

**Custom lenses:** Copy a template to your project's `.claude/persona_lenses.yaml` and modify for your domain.

**Agent Prompt Files Location**: `~/.claude/agents/` (registered subagents)
**Detailed Prompts Location**: `~/.claude/prompts/` (system prompts and playbooks)

To invoke a subagent, use the Task tool with `subagent_type` matching the agent name (e.g., `subagent_type: "lessons-advisor"`).

### Agent Governance & Contamination Protection

All agents (internal and visiting) operate under strict governance to prevent configuration drift and document contamination.

**Key Principles:**
- **Manifest as Universal Entry Gate**: ALL agents read their scope's manifest FIRST on start/restart/resume
  - Macro agents: `~/.claude/{domain}/manifest.yaml`
  - Micro agents: `{project}/.claude/manifest.yaml`
- **Macro vs Micro Scope**: Macro agents govern portfolios; micro agents work within projects
- **Exclusive Permissions**: Four capabilities are exclusively reserved:
  - Backend code modification → `backend-coding-agent` ONLY
  - Frontend code modification → `frontend-coding-agent` ONLY
  - Deployment execution → `devops-governor` ONLY
  - User journey definition → `persona-evaluator` ONLY
- **Consultation Required**: Micro agents MUST consult relevant macro agents before certain decisions
- **Internal vs Visiting**: Internal agents work within the workflow; visiting agents analyze and report only
- **BA-Only Input for Coding**: Coding agents accept work ONLY from BA specs - users must go through BA workflow
- **ID Sequencing**: BUG/IMPROVE IDs are project-global, never reused, always search before creating
- **Document Locations**: All outputs use `.claude/` folder structure (artifacts, evidence, remediation, evolution)

**Governance Documentation:**

| Document | Location | Purpose |
|----------|----------|---------|
| **Agent Governance** | `~/.claude/docs/agent_governance.md` | **MASTER** governance rules, exclusive permissions, compliance checklists |
| Agent Operating Model | `~/.claude/docs/agent_operating_model.md` | Complete model with history, diagrams, design decisions |
| Agent Creation Guide | `~/.claude/docs/agent_creation_guide.md` | **MANDATORY** guide for creating new agents |
| Document Consistency | `~/.claude/docs/document_consistency.md` | Canonical reference for document locations |
| CLAUDE.md Change Protocol | `~/.claude/docs/claude_md_change_protocol.md` | Rules for modifying this file |
| Handoff Envelope Format | `~/.claude/docs/handoff_envelope_format.md` | Standardized agent-to-agent handoff specifications |
| Agent Prompt Schema | `~/.claude/schemas/agent_prompt.schema.yaml` | Validation rules for agent prompts |
| DevOps Manifest Schema | `~/.claude/schemas/devops_manifest.schema.yaml` | Validation rules for DevOps Governor manifest |
| Project Manifest Schema | `~/.claude/schemas/project_manifest.schema.yaml` | Validation rules for project manifests |
| New Agent Template | `~/.claude/templates/new_agent_template.md` | Starting point for new agents |
| Visiting Agent Template | `~/.claude/agents/visiting-agent-template.md` | Template for external reviewers |
| **Governance Test Schedule** | `~/.claude/docs/agent_governance_test_schedule.md` | Verification tests for agent governance rules |
| MCP Integration | `~/.claude/docs/mcp_integration.md` | How MCP servers integrate with agent ecosystem |

**Validation Script:**
```bash
# Validate all agents conform to operating model
python ~/.claude/scripts/validate_agents.py

# Validate specific agent
python ~/.claude/scripts/validate_agents.py agent-name.md
```

**Before Modifying CLAUDE.md or Agent Prompts:**
1. Run validation script (must pass)
2. Follow change protocol in `~/.claude/docs/claude_md_change_protocol.md`
3. Update affected agents FIRST if making structural changes
4. Run validation script again after changes

### Key Files to Consult (v2.0)

| File | Purpose |
|------|---------|
| `~/.claude/knowledge/devlessons.md` | Hard-won lessons from past projects - consult before making architectural decisions |
| `~/.claude/prompts/system/coding_system_prompt_v4_0_hex_tdd_8k.md` | Coding standards: TDD, hexagonal architecture, atomic components |
| `~/.claude/prompts/playbooks/coding_playbook_v4_0.md` | How to implement: task loop, drift governance, component structure |
| `~/.claude/prompts/system/ba_system_prompt_v4_0_8k.md` | BA workflow: spec creation, tasklist management, EV/D governance |
| `~/.claude/prompts/playbooks/ba_playbook_v4_0.md` | BA practical guide: artifact creation, drift handling, escalation |
| `~/.claude/prompts/system/solution_designer_system_prompt_v2_0.md` | Solution design patterns, handoff envelope format |
| `~/.claude/prompts/playbooks/solution_designer_playbook_v2_0.md` | Solution design: scoping, architecture decisions, tradeoffs |
| `~/.claude/prompts/system/persona_evaluator_system_prompt_v2_0.md` | Persona-based evaluation methodology (embedded in qa-reviewer) |
| `~/.claude/prompts/system/qa_system_prompt_v2_0.md` | QA review: quick governance, TDD, hexagonal compliance |
| `~/.claude/prompts/system/code_review_system_prompt_v1_0.md` | Deep code review: task completion verification, bug docs, improvements |
| `~/.claude/prompts/playbooks/code_review_playbook_v1_0.md` | Code review practical guide: verification process, templates, patterns |
| `~/.claude/prompts/system/lessons_system_prompt_v2_0.md` | Lessons operationalization into gates and checklists |
| `~/.claude/docs/agent_operating_model.md` | **Lifecycle playbook**: Persona -> Solution -> BA -> Coding -> QA -> Lessons |

### Agent Lifecycle (v2.6)

```
                                    ┌─────────────────┐
                                    │ DevOps Governor │ (MACRO - consult for stack/deployment)
                                    └────────┬────────┘
                                             │ approves
                                             ▼
Persona ──► Solution Designer ──► DevOps ──► BA ──► Coding ──► QA ──► Code Review ──► Lessons
   │               │             consult      │        │         │          │             │
journeys      architecture     stack/deploy  spec   backend   gates    deep verify    improve
+ personas    + scenarios      approval     tasks   frontend   pass    + completion    gates
                + handoff                          (parallel)  /fail   + bug docs
```

**Coding Phase Detail:**
- `backend-coding-agent`: Python/FastAPI, hexagonal architecture
- `frontend-coding-agent`: React/TypeScript, Feature-Sliced Design
- Both can run in parallel via git worktrees

**DevOps Governor Integration:**
- Solution Designer MUST consult DevOps Governor before finalizing stack/deployment
- BA MUST verify DevOps approval stamp before proceeding
- Coding/QA agents MUST request deployment via DevOps Governor (cannot deploy directly)

**QA Reviewer vs Code Review Agent:**
- `qa-reviewer`: Quick governance check (5-10 min) - TDD, hexagonal, gates compliance
- `code-review-agent`: Deep verification (60 min) - actual task completion, spec fidelity, bug docs

### Worktree Parallelization (v1.2)

Git worktrees enable parallel development: BA can work ahead creating specs while Coding agents implement in separate worktrees.

**Key Concepts:**
- **Feature Backlog**: Queue of fully-specified features ready for implementation
- **Active Worktrees**: Feature worktrees currently being implemented
- **Main Worktree**: Planning hub where BA and Solution Designer work

**Workflow:**
```
MAIN WORKTREE (BA Planning)           FEATURE WORKTREES (Coding)
│                                     │
├─ Create spec for Feature A         │
├─ Add to BACKLOG ────────────────────┼──► Spawn worktree-A
├─ Create spec for Feature B         │    └─ Coding Agent implements
├─ Add to BACKLOG ────────────────────┼──► Spawn worktree-B
│                                     │    └─ Coding Agent implements
├─ Handle drift from worktrees       │
├─ Merge completed features ◄────────┼─── QA passes, merge
```

**Manifest Additions** (schema v1.2):
```yaml
feature_backlog:
  - slug: "user-auth"
    status: ready | in_progress | complete
    priority: 1

active_worktrees:
  - name: "user-auth"
    path: "../myproject-user-auth"
    phase: coding | qa | complete

worktree_governance:
  max_parallel: 3
```

**Helper Script:**
```bash
~/.claude/scripts/worktree_manager.sh

# Commands:
create <project> <feature>     # Create worktree
backlog list                   # Show backlog
backlog next                   # Find next to spawn
spawn-from-backlog <feature>   # Create from backlog
sync <path>                    # Sync shared artifacts
remove <path>                  # Remove worktree
```

**Documentation:**
- Agent Operating Model: Section 5.1 Worktree-Based Parallelization
- Artifact Convention: Worktree Artifact Structure
- Handoff Envelope Format: BA to Worktree Handoff, Worktree Completion

### Handoff Contracts

Agents communicate via standardized "Handoff Envelopes". Full specification: `~/.claude/docs/handoff_envelope_format.md`

**Envelope Types:**
| Type | From → To | Key Contents |
|------|-----------|--------------|
| Solution Envelope | Solution Designer → BA | Problem, personas, flows, architecture, **DevOps approval stamp** |
| BA Handoff | BA → Coding Agent | Spec, tasklist, rules, quality gates |
| Coding Completion | Coding Agent → QA | Evidence files, manifest updates |
| QA/Review Handoff | QA → Coding Agent | Findings, BUG/IMPROVE entries |
| Drift Report | Coding Agent → BA | EV entries, scope changes |
| DevOps Consultation | Solution Designer → DevOps | Stack proposal, deployment architecture |
| Deployment Request | Any Agent → DevOps | Project, environment, evidence path |

**Key Rules:**
- Solution envelopes MUST have DevOps approval before BA proceeds
- All envelopes are versioned (never overwrite)
- Manifest MUST reflect current artifact versions

### Mandatory Lesson Consultation

**CRITICAL**: Lessons must be consulted at these points:

#### Before Starting ANY New Project
1. Run `lessons-advisor` agent with project context/tech stack
2. Create `.claude/artifacts/006_lessons_applied_v1.md` documenting applicable lessons
3. Add lesson-derived checks to `.claude/artifacts/005_quality_gates_v1.md`
4. Initialize manifest with lesson references

#### After Context Compress or Session Restart
1. **Read `.claude/manifest.yaml` FIRST** - single source of truth
2. Check `outstanding.remediation` - handle bugs before new tasks
3. Check `outstanding.tasks` - continue pending work
4. Read current artifact versions from manifest

#### After Project Completion
1. Run lessons-advisor to capture new lessons learned
2. Append to `devlessons.md` with evidence from project
3. Update topic index if new categories emerge

**The `.claude/manifest.yaml` file is the key artifact that survives context compresses.**

### Available Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/review-project` | Full project review for Prime Directive compliance and spec drift | After completing features, before releases, periodic health checks |
| `/status` | Display system status (MCP, agents, credentials) | Check environment health |
| `/commit` | Create git commit | After completing work |
| `/learn` | Capture lesson to devlessons.md | After discovering reusable insight |

**Command Locations:**
- `/review-project`: `~/.claude/commands/review-project.md`
- Prompt template: `~/.claude/commands/review-project.md`

### DevOps Governance (Portfolio Level)

The DevOps Governor is a **macro agent** that ensures CI/CD consistency across all projects.

**Entry Point**: `~/.claude/devops/manifest.yaml`

**Infrastructure:**
```
~/.claude/devops/
├── manifest.yaml           # Portfolio state (read FIRST)
├── project_registry.yaml   # All registered projects
├── decisions.md            # Append-only decision log
├── evolution.md            # Pattern evolution history
└── patterns/               # Canonical CI/CD templates
    ├── gitlab-ci/*.yml
    ├── github-actions/*.yml
    └── quality-gates/*.yaml
```

**Non-Negotiables (ALL projects must meet):**
- Quality Gates: lint, type check, unit tests, security tests
- Security Scanning: SAST, secret detection, dependency scanning
- Deployment: environment separation, progressive deployment, health checks, rollback docs
- Metrics: test coverage, pipeline success rate

**Exclusive Permissions:**
- **Only devops-governor can execute deployments**
- Other agents must request deployment via devops-governor

**Consultation Required:**
| Agent | Must Consult DevOps When |
|-------|-------------------------|
| `solution-designer` | Proposing tech stack, deployment architecture, CI/CD platform |
| `business-analyst` | Must verify DevOps approval stamp before proceeding |
| `backend-coding-agent` | Requesting deployment after task completion |
| `frontend-coding-agent` | Requesting deployment after task completion |

**Invocation:**
```
"DevOps review for {project} architecture proposal"
"Request deployment of {project} to dev"
"Run DevOps audit on {project}"
"Register {project} in DevOps portfolio"
```

### When to Reference

1. **Starting a new project** - Read `devlessons.md` for framework selection, deployment, and architecture lessons
2. **Before coding** - Check coding agent prompt AND playbook for TDD, hexagonal architecture, and quality gate requirements
3. **During implementation** - Follow coding agent playbook for task loop discipline, drift governance, and component structure
4. **Planning features** - Consult BA agent prompt + playbook for spec/tasklist structure
5. **Making architectural decisions** - Review past decisions and their outcomes in `devlessons.md`
6. **Evaluating product from user perspective** - Use persona evaluator to generate scenarios, user stories, and QA test packs
7. **After code changes (quick check)** - Run QA reviewer to verify governance compliance
8. **After task completion (deep verification)** - Run code-review-agent to verify actual task completion against specs/stories/tests
9. **After recurring issues** - Consult lessons-advisor to operationalize fixes into gates
10. **Project health check** - Run `/review-project` to verify Prime Directive compliance and detect spec drift

### Prime Directive (Non-Negotiable)

> **Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.**

This is the foundational rule. All other instructions derive from it.

### Standing Instructions

- Follow hexagonal architecture: core depends only on ports; adapters depend on core
- Follow the atomic component pattern from the coding agent prompt + playbook
- Use strict task loop discipline: one task at a time, TDD, evidence artifacts
- Run quality gates after every task - must produce machine-readable artifacts:
  - `.claude/evidence/quality_gates_run.json`
  - `.claude/evidence/test_report.json`
  - `.claude/evidence/test_failures.json`
- **Update manifest** after completing tasks or reviews
- Use drift detection - halt and create EV entries when scope changes
- Keep domain rules in YAML files, not hardcoded (rules-first execution)
- Maintain component contracts and manifests
- Pin dependencies appropriately based on past version issues
- For Fly.io deployments, review the deployment lessons before configuring
- Evolution and decisions logs are append-only - never rewrite history
- **Never overwrite artifacts** - always create new versions (v1 → v2)

### Verification Checkpoints (Non-Negotiable)

**After ANY file edit (Edit/Write tool), you MUST run verification:**

```bash
# Python projects
ruff check . && mypy . && pytest

# Frontend projects
npm run build && npm run lint

# Full-stack
# Run both as appropriate
```

**Checkpoint Triggers (must re-read system prompt + project artifacts):**

| Trigger | Action |
|---------|--------|
| Every 15 substantive turns | Re-anchor: read rules.yaml, quality_gates.md, system prompt |
| Before starting each new task | Re-anchor + verify no blockedBy tasks |
| After error recovery (>3 turns debugging) | Re-anchor + self-audit |
| After any tangent or user question | Re-anchor before resuming |
| When tempted to say "just this once" | STOP. Re-anchor. |

**Self-Audit Questions (at each checkpoint):**
- Am I following TDD (tests before implementation)?
- Am I staying within task scope (no "while I'm here" edits)?
- Are my changes hexagonal (core depends only on ports)?
- Have I updated contracts for any changed components?
- Do evidence artifacts exist for completed work?

**Strict Prohibitions:**
- **NEVER skip the verification checkpoint**
- **NEVER mark a task done without evidence artifacts**
- **NEVER continue past 40 turns without fresh conversation**

---

## Non-Negotiable Testing Requirements

Testing requirements vary by layer. These are **hard requirements**, not suggestions.

### Layer-Specific Testing (Mandatory)

| Layer | Test Type | Coverage Requirement | Tool |
|-------|-----------|---------------------|------|
| **Domain (entities, policies)** | Unit tests | 100% of public functions | pytest |
| **Services (use cases)** | Integration tests with fakes | All happy paths + error paths | pytest |
| **Adapters (I/O)** | Contract tests | Verify port protocol compliance | pytest |
| **API Endpoints** | HTTP integration tests | All routes, all status codes | pytest + httpx |
| **UI Components** | E2E tests | Critical user flows | Playwright |

### Test Evidence Requirements

A task is **NOT COMPLETE** unless:

```
[ ] .claude/evidence/test_report.json exists
[ ] .claude/evidence/test_failures.json exists (even if empty)
[ ] .claude/evidence/quality_gates_run.json exists
[ ] All tests relevant to the task pass
[ ] New code has corresponding new tests
[ ] manifest.yaml updated with task status
```

### E2E Test Mandates (Lessons 44, 53-57)

- **All interactive elements MUST have `data-testid` attributes**
- Selectors: Prefer `data-testid` over CSS classes or text content
- Authentication: Create reusable auth helpers, not copy-paste login sequences
- Port conflicts: Check ports before starting test servers
- Database: Test seed scripts must match actual schema

### Contract Testing for APIs (Lessons 108, 109, 113)

**Every API endpoint MUST have:**

1. **Pydantic response model** - defines the contract
2. **Integration test validating ALL fields** - catches field mismatches
3. **TypeScript types generated from Pydantic** - never hand-write frontend types

```python
# REQUIRED pattern for API responses
def test_projects_response_has_all_required_fields():
    response = client.get("/api/projects")
    for project in response.json():
        ProjectResponse(**project)  # Validates contract
```

### Filter Parameter Testing (Lesson 109)

**Every filter/query parameter MUST have a test proving it works:**

```python
def test_filter_actually_filters():
    # Create data spanning the filter range
    # Apply filter
    # Assert ONLY filtered data returned
```

---

## Atomic Component Enforcement (Strict)

### Required Files (No Exceptions)

Every component in `src/components/<ComponentName>/` MUST have:

| File | Purpose | Created When |
|------|---------|--------------|
| `component.py` | Pure entry point with `run()` | Before implementation |
| `models.py` | Frozen dataclass Input/Output | Before implementation |
| `ports.py` | Protocol interfaces | Before implementation |
| `contract.md` | Human-readable specification | Before implementation |
| `__init__.py` | Re-exports public API | Before implementation |

**Enforcement:** Create ALL stubs BEFORE writing implementation code.

### contract.md Template (Required Sections)

```markdown
# ComponentName Contract

## Purpose
[One sentence describing what this component does]

## Input
[Frozen dataclass with all inputs]

## Output
[Frozen dataclass with all outputs]

## Ports (Dependencies)
[Protocol interfaces required]

## Error Cases
[What can fail and how it's signaled]

## Evidence
[How to verify this component works]
```

### Manifest Synchronization

- Manifest entry MUST exist before implementation starts (status: "in_progress")
- Manifest entry MUST be updated when complete (status: "complete")
- G3_manifest_validation MUST pass - no phantom components

---

## Determinism Requirements (Lessons 27, 107)

### Forbidden in Core/Domain Code

| Forbidden | Reason | Alternative |
|-----------|--------|-------------|
| `datetime.now()` | Non-deterministic | Inject `TimePort` |
| `datetime.utcnow()` | Deprecated in Python 3.12 | Use `datetime.now(UTC)` via `TimePort` |
| `uuid4()` | Non-deterministic | Inject `UUIDPort` |
| `random.*` | Non-deterministic | Inject `RandomPort` |
| Module-level mutable state | Hidden coupling | Inject `StoragePort` |

### Required Port Pattern

```python
# ports.py
from typing import Protocol
from datetime import datetime

class TimePort(Protocol):
    def now(self) -> datetime: ...

class UUIDPort(Protocol):
    def generate(self) -> str: ...
```

```python
# component.py
class MyService:
    def __init__(self, time_port: TimePort, uuid_port: UUIDPort):
        self._time = time_port
        self._uuid = uuid_port

    def create_event(self) -> Event:
        return Event(
            id=self._uuid.generate(),
            timestamp=self._time.now()
        )
```

### Detection Command

```bash
grep -r "datetime\.now\|datetime\.utcnow\|uuid4" src/*/core/ --include="*.py" | grep -v import
# Count MUST be zero
```

---

## API Contract Requirements (Lessons 108-113)

### Response Schema Validation

Every API callback/endpoint MUST:

1. Define explicit Pydantic response model
2. Have integration test validating ALL fields
3. Log observable data flow (not silent defaults)

### Field Naming Consistency

| Backend Returns | Frontend Expects | Status |
|-----------------|------------------|--------|
| `updated` | `updated` | ✓ Match |
| `last_updated` | `updated` | ✗ BROKEN |

**Rule:** Define field names in Pydantic model FIRST, then implement.

### Callback Type Safety (Lesson 109)

```python
# REQUIRED: Protocol-based callback typing
class DriftCallback(Protocol):
    def __call__(self, project_id: str | None, days: int) -> list[dict]: ...

def set_drift_callback(self, callback: DriftCallback) -> None:
    self._drift_callback = callback
```

Run `mypy --strict` to catch signature mismatches.

---

## Technology Quick Reference

### Databricks (Lessons 88-95)

| Issue | Solution |
|-------|----------|
| DBFS public access disabled | Use Unity Catalog Volumes |
| INT vs BIGINT mismatch | Check Spark SQL introspection types |
| Decimal precision drift | Match config and table schema exactly |
| Null in arrays | Use `filter()` expression |
| Widget defaults | Must match actual file names in Volume |
| Serverless-only workspace | Check compute capabilities first |

### MCP Server Development (Lessons 19-24, 104)

| Pattern | Requirement |
|---------|-------------|
| Token budget | Enforce max response size (e.g., 4000 tokens) |
| Response time | Target <2s for interactive tools |
| Fallback | Implement provider fallback chain |
| Atomic adapters | One adapter per external service |
| Config location | Use `~/.config/` or XDG paths |

### React/Next.js (Lessons 18, 38-43, 59, 81, 85)

| Issue | Solution |
|-------|----------|
| Radix Select empty value | Cannot use empty string as value |
| TipTap server rendering | Install `@tiptap/html` separately |
| shadcn/ui deps | Add incrementally, check peer deps |
| `"use client"` | Affects ALL exports in file |
| Static page stale data | Use `export const dynamic = 'force-dynamic'` |
| setState in useEffect | Use `useMemo` for derived state instead |

### Fly.io Deployment (Lesson Section 3)

Pre-deploy checklist:
```
[ ] Volume created BEFORE first deploy
[ ] PYTHONPATH set in fly.toml AND Dockerfile
[ ] Health check endpoint returns 200
[ ] Memory >= 512mb for Python apps
[ ] README.md exists if referenced in pyproject.toml
```

---

## Dependency Pinning Strategy (Lessons 2, 23)

### Pin Everything That Can Break

```toml
# pyproject.toml - GOOD
dependencies = [
    "fastapi>=0.109.0,<0.115.0",   # Pin major+minor range
    "websockets>=12.0,<14.0",      # Known breaking change at 14
    "pydantic>=2.0.0,<3.0.0",      # Pin major version
]

# BAD - too loose
dependencies = ["fastapi>=0.100.0"]
```

### Document WHY Each Pin Exists

```toml
# websockets<14 - Flet 0.28 incompatible with websockets 14+ (see devlessons #2)
```

### Lock File Requirement

After confirming working state:
```bash
pip freeze > requirements.lock
# OR use uv/poetry lockfile
```

---

## Quick Reference Links

### Top 30 Rules Summary

See `devlessons.md` lines 1209-1241 for the curated "Top 30 Rules for Future Projects" derived from 113 lessons.

### Lesson Topic Index

| Topic | Lessons |
|-------|---------|
| Risk Engine/Finance | 96, 97, 99 |
| Databricks | 88-95 |
| MCP/Claude | 19-24, 30, 104 |
| Testing | 44-62, 76, 78, 82, 97, 99, 108-112 |
| React/Next.js | 18, 38-43, 59, 81, 85 |
| Hexagonal/Architecture | 4, 8-13, 24, 31, 79, 87, 100, 103, 107 |
| API Design | 108, 109, 113 |
| Quality Gates | 5, 36, 51 |

Full index at `devlessons.md` lines 114-143.

## Project Artifact Standards (v1.0)

### New Project Structure: `.claude/` Folder

All Claude-generated artifacts now live in a `.claude/` folder at project root:

```
{project}/
├── .claude/
│   ├── manifest.yaml                 # Restart checkpoint (single source of truth)
│   ├── artifacts/                    # Sequenced, versioned BA artifacts
│   │   ├── 001_solution_envelope_v1.md
│   │   ├── 002_spec_v1.md
│   │   ├── 003_tasklist_v1.md
│   │   ├── 004_rules_v1.yaml
│   │   ├── 005_quality_gates_v1.md
│   │   ├── 006_lessons_applied_v1.md
│   │   └── 007_coding_prompt_v1.md
│   ├── evolution/                    # Append-only logs
│   │   ├── evolution.md
│   │   └── decisions.md
│   ├── remediation/                  # QA + Code Review findings
│   │   ├── qa_YYYY-MM-DD.md
│   │   ├── code_review_YYYY-MM-DD.md
│   │   └── remediation_tasks.md
│   └── evidence/                     # Quality gate outputs
│       ├── quality_gates_run.json
│       ├── test_report.json
│       └── test_failures.json
└── src/
```

### Naming Convention: `NNN_type_vM.ext`

| Seq | Artifact | Created By |
|-----|----------|------------|
| 001 | solution_envelope | Solution Designer |
| 002 | spec | Business Analyst |
| 003 | tasklist | Business Analyst |
| 004 | rules | Business Analyst |
| 005 | quality_gates | Business Analyst |
| 006 | lessons_applied | Lessons Advisor |
| 007 | coding_prompt | Business Analyst |

### Manifest: Restart Checkpoint

The `manifest.yaml` is the single source of truth for:
- Current workflow phase
- Active artifact versions
- Outstanding tasks and remediation items
- Review history

**Always read manifest first** when resuming work.

### Restart Priority Order

1. **Critical/High remediation** (BUG-XXX items)
2. **In-progress tasks**
3. **Medium remediation**
4. **Pending tasks** (respect blocked_by)
5. **Low remediation**

### Documentation

- Artifact Convention: `~/.claude/docs/artifact_convention.md`
- Restart Protocol: `~/.claude/docs/restart_protocol.md`
- Remediation Format: `~/.claude/docs/remediation_format.md`
- Manifest Schema: `~/.claude/schemas/project_manifest.schema.yaml`

### Legacy Projects

For projects with old `{project}_spec.md` at root:
- Migration guide: `~/.claude/migrations/MIGRATE_PROJECT_ARTIFACTS.md`

## Archive Information

Previous v3_atomic configuration archived at:
`~/Developer/claude-agent-framework/archive/v3_atomic_backup_2026-01-16/`

Rollback instructions available at:
`~/Developer/claude-agent-framework/migrations/ROLLBACK_PROMPT.md`

## Permissions Configuration

Settings file: `~/.claude/settings.local.json`

### Two Permission Layers

1. **Bash Command Permissions** - which shell commands can execute
2. **Directory Access Permissions** - which paths Claude can read/write/create files in

Both must be configured for full access. See devlessons.md #28-29 for details.

### Auto-Allowed Commands (no prompts)
- **Testing**: pytest, npm test, bun test, ruff, mypy
- **Build**: npm run build, bun run build, docker build
- **Git (read)**: git status, git diff, git log, git branch, git fetch
- **Git (write)**: git add, git commit, git checkout, git stash, git pull
- **Package managers**: npm install, pip install, bun install, uv, poetry
- **Utilities**: ls, cat, head, tail, grep, find, curl, tree, mkdir, cp, mv
- **Deployment**: fly deploy, fly logs, docker compose, docker ps

### Directory Access (Write/Edit permissions)
- `~/Developer/**` - Full write/edit access to Developer folder
- `~/Documents/**` - Full write/edit access to Documents folder (legacy)

### Ask-First Commands (prompts before running)
- `git push` - Prompts before pushing to remote
- `npm publish` - Prompts before publishing packages
- `fly deploy --force` - Prompts before force deployments
- `docker push` - Prompts before pushing images
- `docker rm/rmi/stop` - Container destruction operations
- `git rebase` - History rewriting
- `psql/mysql/mongosh/redis-cli` - Database clients

### Denied Commands (never allowed)
- `Read(.env*)` - Prevents reading environment files with secrets
- `rm -rf` - Prevents dangerous recursive deletions
- `sudo rm` - Prevents privileged deletions
- `chmod 777` - Prevents insecure permissions

### Enabled Plugins
- `frontend-design@claude-plugins-official` - Production-grade UI components
- `github@claude-plugins-official` - GitHub integration
- `typescript-lsp@claude-plugins-official` - TypeScript language server
- `rust-analyzer-lsp@claude-plugins-official` - Rust language server

## Startup Screen & Status Command

A startup status screen automatically displays on the first prompt of each Claude Code session, showing:
- MCP server connection and available tools
- Available agents/subagents
- Credential status (API keys in Keychain)
- Service status (Docker, NotebookLM auth)
- Prime directives

### `/status` Command

When the user types `/status` or asks to "show status", run:
```bash
python3 ~/.claude/hooks/startup_check.py --force
```

This displays the full system status screen on demand.

### Startup Hook Configuration

The startup screen is triggered by a `UserPromptSubmit` hook in `~/.claude/settings.local.json`. The screen only shows once per terminal session (tracked via `~/.claude/.current_session`).

## Migrations

### Moving Development Folders

When relocating development projects to a new directory:

1. Run the migration prompt: `migrations/MIGRATE_DEV_FOLDERS.md`
2. Update directory permissions in `~/.claude/settings.local.json`
3. Restart Claude Code session

**Migration Prompt Location**: `~/.claude/migrations/MIGRATE_DEV_FOLDERS.md`

### Migrating Project Artifacts to .claude/ Folder

For projects with legacy `{project}_spec.md` artifacts at root:

1. Run the migration prompt: `migrations/MIGRATE_PROJECT_ARTIFACTS.md`
2. Create folder structure: `.claude/{artifacts,evolution,remediation,evidence}`
3. Move and rename files with sequence numbers
4. Create `manifest.yaml` with current state
5. Commit migration to git

**Migration Prompt Location**: `~/.claude/migrations/MIGRATE_PROJECT_ARTIFACTS.md`

### Automated Migration Script

```bash
# From project root:
bash ~/.claude/scripts/migrate_to_claude_folder.sh {project_slug}
```
