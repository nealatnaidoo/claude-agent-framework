# Claude Code Global Instructions

**Version**: v3.1 (audit-clean) - Updated 2026-02-06
**Location**: `~/Developer/claude-agent-framework/` (or `~/.claude/` via symlinks)

## Prime Directive (Non-Negotiable)

> **Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.**

This is the foundational rule. All other instructions derive from it.

---

## Agent Routing

Invoke agents via the Task tool: `subagent_type: "agent-name"`.

### Macro Agents (Portfolio Level)

| Agent | Model | When to Use | Exclusive Permission |
|-------|-------|-------------|---------------------|
| `devops-governor` | opus | CI/CD governance, deployments, stack approval | **Execute deployments** |
| `compliance-verifier` | haiku | Validate agent governance compliance | - (visiting) |

### Micro Agents (Project Level)

| Agent | Model | When to Use | Exclusive Permission |
|-------|-------|-------------|---------------------|
| `project-initializer` | haiku | **New projects** - scaffold .claude/ structure and manifest | - |
| `persona-evaluator` | opus | Define user journeys before solution design | **Define user journeys** |
| `solution-designer` | opus | Turn ideas into bounded solutions (consult devops-governor) | - |
| `business-analyst` | opus | Create spec, tasklist, rules, quality gates | - |
| `backend-coding-agent` | opus | Python backend (hexagonal architecture) | **Write backend code** |
| `frontend-coding-agent` | opus | React/TypeScript frontend (FSD) | **Write frontend code** |
| `qa-reviewer` | sonnet | Quick governance check (5-10 min) after each task | - |
| `code-review-agent` | opus | Deep task completion verification (60 min) after feature | - |
| `lessons-advisor` | haiku | Consult past lessons before decisions (recommended before BA) | - |

### Exclusive Permissions (CRITICAL)

- **Backend Code**: ONLY `backend-coding-agent` can write/modify Python backend code
- **Frontend Code**: ONLY `frontend-coding-agent` can write/modify React/TypeScript frontend code
- **Deployments**: ONLY `devops-governor` can execute deployments
- **User Journeys**: ONLY `persona-evaluator` can define user journeys and personas

### BA-Only Input Constraint

Coding agents accept work ONLY from BA-produced artifacts (spec, tasklist). Users MUST NOT request coding directly - redirect them to create a spec first.

### Task Assignment

- Backend tasks (Python, API, database): `backend-coding-agent`
- Frontend tasks (React, TypeScript, UI): `frontend-coding-agent`
- Full-stack integration tasks: `backend-coding-agent` (owns integration tests)

### Review Workflow (QA vs Code Review)

| Aspect | QA Reviewer | Code Review Agent |
|--------|------------|-------------------|
| When | After **each task** completes | After **feature** completes |
| Duration | 5-10 min | 60 min |
| Focus | Governance gates (TDD, hexagonal, quality) | Spec fidelity, AC coverage, bug docs |
| Model | Sonnet (fast, cheap) | Opus (thorough) |
| Output | Quick pass/fail + remediation items | Deep verification + feedback envelope |

### Visiting Agent Roles

The `visiting-agent-template` supports specialized read-only reviews:

| Role | Invocation | Focus |
|------|-----------|-------|
| `security_auditor` | "Run security audit on this project" | OWASP, input validation, auth flows, secrets |
| `performance_analyst` | "Run performance analysis on {feature}" | N+1 queries, bundle size, caching |
| `accessibility_auditor` | "Run accessibility audit on {feature}" | ARIA, keyboard nav, color contrast |

---

## Agent Lifecycle

```
project-initializer → persona-evaluator → lessons-advisor (recommended)
                                               ↓
                           solution-designer → DevOps Governor (consult, REQUIRED)
                                               ↓
                                     business-analyst
                                               ↓
                              ┌─────── coding (parallel) ───────┐
                              │  backend-coding-agent            │
                              │  frontend-coding-agent           │
                              └─────────────┬───────────────────┘
                                            ↓
                                    qa-reviewer (per-task, 5-10 min)
                                            ↓
                                   code-review-agent (per-feature, 60 min)
                                            ↓
                                    feedback → solution-designer (next sprint)
```

**Fast-Track Path** (for bug fixes, single-file changes, config/doc updates):
Skip project-init/persona/solution/BA. Go directly to coding -> QA -> code review.
- Single file or minor multi-file change (max 3 files)
- Bug fix with existing tests
- Configuration or documentation update
- No new user journeys or architecture changes

---

## Mechanical Enforcement (Hooks)

| Hook | Trigger | What It Does | Strength |
|------|---------|-------------|----------|
| `verify_ba_artifacts.py` | Coding agent start | Blocks if spec/tasklist missing | **BLOCKS** |
| `verify_devops_approval.py` | BA agent start | Blocks if solution envelope lacks DevOps stamp | **BLOCKS** |
| `verify_evidence_exists.py` | QA reviewer start | Blocks if no evidence artifacts exist | **BLOCKS** |
| `verify_phase_transition.py` | Any agent start | Blocks if agent doesn't match current phase | **BLOCKS** |
| `verify_manifest_updated.py` | Session stop | Warns if manifest not updated in >1 hour | Advisory |
| `save_manifest_state.py` | Context compress | Backs up manifest (keeps 3 most recent) | Protective |

---

## Manifest-First Restart Protocol

After context compress or session restart:
1. **Read `.claude/manifest.yaml` FIRST** - single source of truth
2. Check `outstanding.remediation` - handle bugs before new tasks
3. Check `outstanding.tasks` - continue pending work
4. Read current artifact versions from manifest

---

## Available Commands

| Command | Purpose |
|---------|---------|
| `/review-project` | Prime Directive compliance and spec drift check |
| `/status` | Display system status (MCP, agents, credentials) |
| `/commit` | Create git commit |
| `/save-state` | Save session state for resumption |
| `/resume-state` | Resume from saved state |

---

## Key Knowledge Files

| When | Consult |
|------|---------|
| Starting new project | `project-initializer` agent, then `lessons-advisor` |
| During coding | `~/.claude/knowledge/coding_standards.md` |
| Architecture decisions | `~/.claude/docs/agent_operating_model.md` |
| Agent handoffs | `~/.claude/docs/handoff_envelope_format.md` |
| Creating agents | `~/.claude/docs/agent_creation_guide.md` |
| Governance rules | `~/.claude/docs/agent_governance.md` |
| Permissions/setup | `~/.claude/knowledge/operational.md` |
| Tech-specific gotchas | `~/.claude/knowledge/devlessons.md` (see topic index) |
| Parallel development | `~/.claude/docs/agent_teams.md` |

---

## Governance Essentials

- **Manifest as Universal Entry Gate**: ALL agents read manifest FIRST on start/restart/resume
- **Phase enforcement**: Hooks block agents from running in wrong phase
- **Document Locations**: All outputs use `.claude/` folder (artifacts, evidence, remediation, evolution)
- **Never overwrite artifacts**: Always create new versions (v1 -> v2)
- **ID Sequencing**: BUG/IMPROVE IDs are project-global, never reused
- **Evolution logs are append-only**: Never rewrite history

### Persona Lens Packs

Available at `~/.claude/lenses/`: `creator_publishing.yaml`, `fitness_training.yaml`, `saas_b2b.yaml`
Project-specific: Create `.claude/persona_lenses.yaml` in your project.

---

## Project Artifact Structure

```
{project}/.claude/
  manifest.yaml                    # Restart checkpoint (SINGLE SOURCE OF TRUTH)
  artifacts/                       # Sequenced: 000_user_journeys through 007_coding_prompt
  evolution/                       # Append-only: evolution.md, decisions.md
  remediation/                     # QA/review findings + feedback envelopes
  evidence/                        # Quality gates: quality_gates_run.json, test_report.json
```

Naming: `NNN_type_vM.ext` (e.g., `002_spec_v1.md`). See `~/.claude/docs/artifact_convention.md`.

---

## Validation

```bash
python ~/.claude/scripts/validate_agents.py          # Validate all agents
python ~/.claude/scripts/validate_agents.py agent.md  # Validate specific agent
```

Before modifying CLAUDE.md or agent prompts: follow `~/.claude/docs/claude_md_change_protocol.md`.

---

## Startup

Status screen displays automatically on first prompt (via UserPromptSubmit hook).
Manual: `python3 ~/.claude/hooks/startup_check.py --force`
