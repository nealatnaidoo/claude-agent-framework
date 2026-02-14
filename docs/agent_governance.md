# Agent Governance Documentation

**Version**: 1.0
**Date**: 2026-01-31
**Purpose**: Consolidated governance rules for all agents in the Claude Code ecosystem

---

## Governance Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRIME DIRECTIVE                                     │
│    "Every change must be task-scoped, atomic, deterministic,                │
│     hexagonal, and evidenced."                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            ┌───────▼───────┐               ┌───────▼───────┐
            │    MACRO      │               │    MICRO      │
            │   Agents      │               │   Agents      │
            │ (Portfolio)   │               │  (Project)    │
            └───────┬───────┘               └───────┬───────┘
                    │                               │
          ┌─────────┴──────────┐         ┌─────────┴──────────┐
          │                    │         │                    │
    ┌─────▼─────┐        ┌─────▼─────┐   │              ┌─────▼─────┐
    │  DevOps   │        │  Future   │   │              │ Visiting  │
    │ Governor  │        │  Macro    │   │              │  Agents   │
    └───────────┘        │  Agents   │   │              └───────────┘
          │              └───────────┘   │
   EXCLUSIVE:                       ┌────┴────────────────────────┐
   Deployments                      │                              │
                              ┌─────▼─────┐                  ┌─────▼─────┐
                              │  Coding   │                  │  Other    │
                              │   Agent   │                  │ Internal  │
                              └───────────┘                  │  Agents   │
                                    │                        └───────────┘
                             EXCLUSIVE:
                             Source Code
```

---

## Exclusive Permissions (NON-NEGOTIABLE)

### Source Code Modification

| Rule | Enforcement |
|------|-------------|
| **ONLY `coding-agent` can write/modify source code** | All other agents have identity table row: `Create/modify source code: NO - Coding Agent only` |
| Source code = `src/`, `lib/`, `app/`, `components/` | CI/CD configs are NOT source code |
| Tests are source code | Only coding-agent writes tests |

**Violation Response**: If any agent attempts to write source code, it MUST halt and report the violation.

### Deployment Execution

| Rule | Enforcement |
|------|-------------|
| **ONLY `ops` can execute deployments** | All other agents have identity table row: `Execute deployments: NO - DevOps Governor only` |
| Deployments include: fly deploy, docker push, npm publish | All production AND dev deployments |
| Other agents must REQUEST deployment | Via deployment request format |

**Violation Response**: If any agent attempts to deploy, it MUST halt and redirect to DevOps Governor.

---

## BA-Only Input Constraint (NON-NEGOTIABLE)

The `coding-agent` operates under a strict input constraint:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         INPUT ALLOWED                                     │
│                                                                          │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐         │
│   │     Spec      │     │   Tasklist    │     │    Rules      │         │
│   │ (002_spec_v*.md)    │ (003_tasklist_v*.md) │ (004_rules_v*.yaml)    │
│   └───────────────┘     └───────────────┘     └───────────────┘         │
│           │                     │                     │                  │
│           └─────────────────────┼─────────────────────┘                  │
│                                 │                                        │
│                                 ▼                                        │
│                       ┌─────────────────┐                                │
│                       │  Coding Agent   │                                │
│                       └─────────────────┘                                │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                         INPUT REJECTED                                    │
│                                                                          │
│   ┌───────────────────────────────────────────────────────────┐         │
│   │              Direct User Coding Requests                   │         │
│   │                                                           │         │
│   │  "Write a function that..."                               │         │
│   │  "Add a feature to..."                                    │         │
│   │  "Fix this bug by changing..."                            │         │
│   │  "Implement authentication..."                            │         │
│   └───────────────────────────────────────────────────────────┘         │
│                                 │                                        │
│                                 ▼                                        │
│                       REDIRECT TO BA WORKFLOW                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### User Rejection Message

When users request coding directly, respond with:

> I cannot accept coding requests directly from users. All code changes must be specified in BA artifacts (spec, tasklist).
>
> **To request this change:**
> 1. Work with the BA agent to add this to the specification
> 2. Create a task in the tasklist with acceptance criteria
> 3. Then I can implement from that task
>
> Would you like me to invoke the BA agent to help create the specification?

---

## Agent Identity Requirements

Every agent prompt MUST include an Identity section with:

### 1. Scope Declaration

```markdown
You are an **INTERNAL agent** operating at **MICRO (project) level**
```

OR

```markdown
You are an **INTERNAL agent** operating at **MACRO (portfolio) level**
```

OR

```markdown
You are a **VISITING agent**, not an internal agent.
```

### 2. Permission Table

```markdown
| Capability | Permitted |
|------------|-----------|
| Read all project files | Yes |
| Execute tests and quality gates | Yes |
| **Create/modify source code** | **NO - Coding Agent only** |
| Create/modify {domain} artifacts | Yes |
| **Execute deployments** | **NO - DevOps Governor only** |
```

### 3. Restriction Notes

```markdown
**CODING RESTRICTION**: You MUST NOT write source code. Only the Coding Agent is permitted to write code.

**You are NOT a visiting agent.** (for internal agents)
```

---

## Manifest Entry Protocol

### For Macro Agents

1. Read `~/.claude/{domain}/manifest.yaml` FIRST
2. Extract: non_negotiables, active work, pending consultations
3. Check for pending requests before starting new work

### For Micro Internal Agents

1. Read `{project}/.claude/manifest.yaml` FIRST
2. Extract:
   - `agent_routing` - protocol and permissions
   - `artifact_versions` - current files to read
   - `outstanding.remediation` - bugs to handle first
   - `outstanding.tasks` - work to continue
3. Read artifacts from manifest paths (never hardcode)

### For Visiting Agents

1. Read `{project}/.claude/manifest.yaml` FIRST
2. Extract:
   - `agent_routing.visiting_agent_protocol` - your instructions
   - `compliance_requirements` - rules to check
   - `priority_scales.{your_domain}` - how to classify findings
   - `outstanding.remediation` - existing bugs (avoid duplicates)
3. Follow ID sequencing protocol

---

## ID Sequencing Protocol

Before creating ANY new BUG-XXX or IMPROVE-XXX ID:

```bash
# Step 1: Search for existing IDs
grep -r "BUG-[0-9]" .claude/remediation/ | sort
grep -r "IMPROVE-[0-9]" .claude/remediation/ | sort

# Step 2: Find highest numbers
# Extract highest BUG-XXX and IMPROVE-XXX

# Step 3: Increment from highest
# New bugs: highest_bug + 1
# New improvements: highest_improve + 1
```

**Rules:**
- IDs are **project-global** (not per-review)
- IDs are **never reused** (even for resolved items)
- IDs are **sequential** (no gaps in new assignments)

---

## Consultation Requirements

### DevOps Governor Consultation

| Agent | Must Consult When |
|-------|-------------------|
| `design` | Proposing tech stack, deployment architecture, CI/CD platform |
| `ba` | MUST verify DevOps approval stamp exists before proceeding |
| `coding-agent` | Requesting deployment after task completion |
| `qa` | Requesting deployment after gates pass |

### Consultation Request Format

```yaml
devops_consultation:
  project_slug: "{slug}"
  requesting_agent: "{agent_type}"
  topic: "tech_stack" | "deployment" | "ci_cd"
  proposal:
    stack: "{proposed stack}"
    deployment: "{deployment plan}"
    ci_cd: "{CI/CD platform}"
```

### Deployment Request Format

```yaml
deployment_request:
  project_slug: "{slug}"
  environment: "dev" | "staging" | "prod"
  commit_sha: "{sha}"
  quality_gates_evidence: ".claude/evidence/quality_gates_run.json"
  requesting_agent: "{agent_type}"
  reason: "{why deployment needed}"
```

---

## Document Locations (Canonical)

| Document Type | Location | Owner |
|---------------|----------|-------|
| BA Artifacts | `.claude/artifacts/00N_*.md` | BA |
| Evidence | `.claude/evidence/*.json` | Coding Agent |
| Remediation | `.claude/remediation/*.md` | QA/Review Agents |
| Evolution | `.claude/evolution/evolution.md` | All (append-only) |
| Decisions | `.claude/evolution/decisions.md` | All (append-only) |
| Manifest | `.claude/manifest.yaml` | All (update per protocol) |

### Forbidden Locations

- `artifacts/` without `.claude/` prefix
- `{project}_spec.md` at root
- `{project}_tasklist.md` at root
- Any hardcoded project-slug paths

---

## Workflow Phase Transitions

```
solution_design ──► ba ──► coding ──► qa ──► code_review ──► complete
       │            │        │        │          │
       │            │        │        │          └── remediation (if findings)
       │            │        │        └── remediation (if findings)
       │            │        └── remediation (if findings)
       │            └── paused (if blocked)
       └── paused (if blocked)
```

**Phase Change Rules:**
- Only internal agents can change phase
- Visiting agents CANNOT change phase
- Phase must be updated in manifest
- `phase_started` timestamp required

---

## Evidence Requirements

A task is NOT complete unless:

```
[ ] .claude/evidence/quality_gates_run.json exists
[ ] .claude/evidence/test_report.json exists
[ ] .claude/evidence/test_failures.json exists (even if empty)
[ ] All tests relevant to the task pass
[ ] New code has corresponding new tests
[ ] manifest.yaml updated with task status
```

---

## Validation

### Agent Prompt Validation

```bash
python ~/.claude/scripts/validate_agents.py [agent_file.md]
```

**Checks:**
- Frontmatter valid (name, description, tools, model)
- Identity section exists and declares type
- Entry protocol reads manifest first
- No hardcoded paths
- Correct output locations
- ID sequencing documented (if creates BUG/IMPROVE)
- Compliance referenced

### Before Modifying Governance

1. Run validation script (must pass)
2. Follow change protocol
3. Update affected agents FIRST
4. Run validation script again

---

## Compliance Checklist

### For Internal Agents

- [ ] Identity section declares INTERNAL and scope (MACRO/MICRO)
- [ ] Permission table includes source code and deployment rows
- [ ] Coding restriction note present (if not coding-agent)
- [ ] Entry protocol reads manifest first
- [ ] Output locations use `.claude/` prefix
- [ ] Manifest update documented

### For Visiting Agents

- [ ] Identity section declares VISITING
- [ ] Permission table denies source code modification
- [ ] Permission table denies deployment
- [ ] Permission table denies workflow phase changes
- [ ] ID sequencing protocol documented
- [ ] Output format follows template

### For DevOps Governor

- [ ] Entry protocol reads DevOps manifest first
- [ ] Non-negotiables checklist present
- [ ] Consultation response format documented
- [ ] Deployment verification checklist present
- [ ] Decision capture documented

### For Coding Agent

- [ ] Entry protocol reads project manifest first
- [ ] BA-only input constraint documented
- [ ] User rejection message provided
- [ ] TDD workflow documented
- [ ] Evidence artifact requirements listed
- [ ] Drift protocol documented
