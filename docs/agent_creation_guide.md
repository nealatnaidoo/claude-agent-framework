# Agent Creation Guide

**Version**: 1.0
**Date**: 2026-01-31
**Purpose**: Mandatory guide for creating new agents that ensures consistency with the agent operating model

---

## Before You Begin

**STOP.** Before creating a new agent, answer these questions:

1. **Does this agent already exist?** Check `~/.claude/agents/` for existing agents
2. **Can an existing agent be extended?** Prefer extending over creating new
3. **Is this internal or visiting?** This fundamentally changes the agent's capabilities
4. **What is the single responsibility?** One agent = one clear purpose

---

## Agent Classification

### Internal Agents

**Definition**: Part of the core development workflow. Can modify source code and control workflow.

**Examples**: solution-designer, business-analyst, coding-agent, qa-reviewer, code-review-agent, lessons-advisor

**Characteristics**:
- Full read/write access to source code
- Can create/modify artifacts
- Can change workflow phase
- Can mark tasks complete
- Participates in the SDLC loop

### Visiting Agents

**Definition**: External specialists who analyze and report. Cannot modify source code.

**Examples**: security-auditor, performance-analyst, accessibility-auditor, test-specialist

**Characteristics**:
- Full read access to all files
- Can execute tests, scanners, quality gates
- Can only CREATE reports (not modify source)
- Cannot change workflow state
- Findings processed by internal agents

---

## Mandatory File Structure

Every agent prompt MUST be located at:
```
~/.claude/agents/{agent-name}.md
```

Every agent prompt MUST have this structure:

```markdown
---
name: {agent-name}
description: {One-line description for Task tool}
tools: {Comma-separated list of allowed tools}
model: {sonnet|opus|haiku}
---

## Identity

{Identity section - see template below}

---

# {Agent Name} Agent

{Main content following the template}
```

---

## Identity Section (MANDATORY)

### For Internal Agents

```markdown
## Identity

You are an **INTERNAL agent**, part of the core development workflow.

| Capability | Permitted |
|------------|-----------|
| Read all project files | Yes |
| Execute tests and quality gates | Yes |
| Create/modify source code | Yes |
| Create/modify artifacts | Yes |
| Control workflow phase | Yes |
| Mark tasks complete | Yes |

**You are NOT a visiting agent.** Visiting agents can only analyze and report - you have full implementation authority.
```

### For Visiting Agents

```markdown
## Identity

You are a **VISITING agent**, not an internal agent.

| Capability | Permitted |
|------------|-----------|
| Read all project files | Yes |
| Execute tests and quality gates | Yes |
| Run security/perf/a11y scanners | Yes |
| Create/modify source code | **NO** |
| Create/modify BA artifacts | **NO** |
| Control workflow phase | **NO** |
| Mark tasks complete | **NO** |

**You ANALYZE and REPORT. Internal agents FIX.**
```

---

## Entry Protocol (MANDATORY)

Every agent MUST have a startup protocol that begins with reading the manifest.

### Required Entry Protocol

```markdown
## Startup Protocol

1. **Read manifest FIRST**: `{project_root}/.claude/manifest.yaml`
2. **Extract from manifest**:
   - `phase` - Current workflow phase
   - `artifact_versions` - Paths to current artifacts
   - `outstanding.tasks` - Pending work
   - `outstanding.remediation` - Bugs to fix
3. **Read artifacts** at paths specified in manifest (NOT hardcoded paths)
4. **Check for blockers** before starting work
```

### Forbidden Patterns

| Pattern | Why Forbidden | Correct Pattern |
|---------|---------------|-----------------|
| `{project}_spec.md` | Hardcoded path | `manifest.artifact_versions.spec.file` |
| `artifacts/test_report.json` | Wrong location | `.claude/evidence/test_report.json` |
| Skip manifest read | Misses current state | Always read manifest first |
| Assume file exists | May have different version | Check manifest for current version |

---

## Output Locations (MANDATORY)

All agents MUST use these standardized output locations:

### Artifacts (Versioned BA Documents)

```
Location: {project_root}/.claude/artifacts/
Pattern: NNN_type_vM.md
Examples:
  - 001_solution_envelope_v1.md
  - 002_spec_v2.md
  - 003_tasklist_v1.md
```

**Rules**:
- NEVER overwrite - create new version (v1 → v2)
- Update manifest with new version
- Sequence numbers are fixed (001=envelope, 002=spec, etc.)

### Evidence (Quality Gate Outputs)

```
Location: {project_root}/.claude/evidence/
Files:
  - quality_gates_run.json
  - test_report.json
  - test_failures.json
  - lint_report.json
  - coverage.json (optional)
```

**Rules**:
- Overwrite on each run (these are current state, not history)
- Timestamps must be recent (after latest code changes)

### Remediation (Review Findings)

```
Location: {project_root}/.claude/remediation/
Files:
  - qa_YYYY-MM-DD.md
  - code_review_YYYY-MM-DD.md
  - code_review_YYYY-MM-DD.json
  - {type}_review_YYYY-MM-DD.md (visiting agents)
  - remediation_tasks.md (consolidated)
```

**Rules**:
- Date-stamped reports (never overwrite)
- Append to remediation_tasks.md (never overwrite existing items)
- Follow ID sequencing protocol

### Evolution (Append-Only Logs)

```
Location: {project_root}/.claude/evolution/
Files:
  - evolution.md (drift entries)
  - decisions.md (architectural decisions)
```

**Rules**:
- APPEND ONLY - never edit existing entries
- Each entry has unique ID (EV-XXXX, D-XXXX)
- Timestamps required

---

## ID Sequencing Protocol (MANDATORY)

When creating BUG-XXX or IMPROVE-XXX IDs:

### Step 1: Search for Existing IDs

```bash
grep -r "BUG-[0-9]" .claude/remediation/ | sort
grep -r "IMPROVE-[0-9]" .claude/remediation/ | sort
```

### Step 2: Find Highest Number

Extract the highest BUG-XXX and IMPROVE-XXX numbers found.

### Step 3: Increment from Highest

- New bugs: highest_bug + 1
- New improvements: highest_improve + 1

### Rules

| Rule | Rationale |
|------|-----------|
| IDs are project-global | Same ID space across all reviews |
| IDs are never reused | Even for resolved items |
| IDs are sequential | No gaps in new assignments |
| Search before creating | Prevent duplicates |

### Example

```
Existing: BUG-001, BUG-002, BUG-003 (resolved), BUG-015
Your new bugs start at: BUG-016

Existing: IMPROVE-001, IMPROVE-002
Your new improvements start at: IMPROVE-003
```

---

## Manifest Update Protocol (MANDATORY)

After completing work, agents MUST update the manifest.

### What to Update

| Agent Type | Updates These Manifest Sections |
|------------|--------------------------------|
| Solution Designer | `phase`, `artifact_versions.solution_envelope` |
| Business Analyst | `phase`, `artifact_versions.*`, `outstanding.tasks` |
| Coding Agent | `last_updated`, `outstanding.tasks`, evidence paths |
| QA Reviewer | `reviews.last_qa_review`, `outstanding.remediation` |
| Code Review Agent | `reviews.last_code_review`, `outstanding.remediation` |
| Visiting Agent | `reviews.external`, `outstanding.remediation` |

### Update Format

```yaml
# Always update timestamp
last_updated: "YYYY-MM-DDTHH:MM:SSZ"

# Update phase if transitioning
phase: "coding"  # or ba, qa, code_review, remediation, complete
phase_started: "YYYY-MM-DDTHH:MM:SSZ"

# Update artifact versions when creating new versions
artifact_versions:
  spec:
    version: 2  # incremented
    file: ".claude/artifacts/002_spec_v2.md"
    updated: "YYYY-MM-DDTHH:MM:SSZ"

# Update reviews after completing review
reviews:
  last_qa_review:
    date: "YYYY-MM-DDTHH:MM:SSZ"
    result: "pass_with_notes"
    report_file: ".claude/remediation/qa_YYYY-MM-DD.md"

# Update outstanding work
outstanding:
  tasks:
    - id: "T001"
      status: "completed"  # was in_progress
  remediation:
    - id: "BUG-017"  # new finding
      source: "qa_review"
      priority: "high"
      status: "pending"
```

---

## Output Format Standards

### Review Reports

All review reports (QA, code review, visiting) MUST include:

```markdown
# {Type} Review: YYYY-MM-DD

**Reviewer Type**: {internal|visiting} - {specific_type}
**Scope**: {What was reviewed}

## Summary

| Metric | Value |
|--------|-------|
| Result | PASS | PASS_WITH_NOTES | NEEDS_WORK | BLOCKED |
| Critical Findings | N |
| High Findings | N |
| Medium Findings | N |
| Low Findings | N |

## Prime Directive Compliance

| Check | Status | Notes |
|-------|--------|-------|
| Task-Scoped | PASS/FAIL | |
| Atomic | PASS/FAIL | |
| Deterministic | PASS/FAIL | |
| Hexagonal | PASS/FAIL | |
| Evidenced | PASS/FAIL | |

## Findings

### BUG-XXX: {Title}

**Priority**: critical | high | medium | low
**File**: {path/to/file.py:line}
**Evidence**: {What you observed}
**Impact**: {What happens if not fixed}
**Recommendation**: {How to fix}

### IMPROVE-XXX: {Title}

**Priority**: should | could | won't
**File**: {path/to/file.py}
**Current**: {Current state}
**Proposed**: {Proposed change}
**Rationale**: {Why this matters}
```

### Remediation Tasks Entry

When appending to `remediation_tasks.md`:

```markdown
### BUG-XXX: {Title}
**Source**: {qa_review|code_review|security_review|...}
**Priority**: {critical|high|medium|low}
**Status**: pending
**File**: {path/to/file.py:line}
**Created**: YYYY-MM-DD

**Summary**: {One sentence description}
```

---

## Compliance Requirements

All agents MUST understand and enforce these requirements.

### Prime Directive

> **Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.**

| Dimension | Meaning | How to Verify |
|-----------|---------|---------------|
| Task-Scoped | Changes map 1:1 to task | No "while I'm here" edits |
| Atomic | Smallest meaningful increment | Clear rollback path |
| Deterministic | No datetime.now/uuid4/random in core | Use ports |
| Hexagonal | Core imports only ports | Adapters implement ports |
| Evidenced | Test artifacts exist | Quality gates pass |

### Hexagonal Architecture

```
ALLOWED:
  core → ports (protocols/interfaces)
  adapters → ports
  adapters → core

FORBIDDEN:
  core → adapters
  core → frameworks (fastapi, requests, etc.)
```

### Determinism

```python
# FORBIDDEN in core
datetime.now()
datetime.utcnow()
uuid4()
random.*

# REQUIRED pattern
class MyService:
    def __init__(self, time_port: TimePort, uuid_port: UUIDPort):
        self._time = time_port
        self._uuid = uuid_port
```

---

## Agent Creation Checklist

Before registering a new agent, verify ALL items:

### Structure
- [ ] File located at `~/.claude/agents/{agent-name}.md`
- [ ] YAML frontmatter with name, description, tools, model
- [ ] Identity section immediately after frontmatter
- [ ] Identity correctly declares internal or visiting

### Entry Protocol
- [ ] Startup protocol reads manifest FIRST
- [ ] No hardcoded artifact paths
- [ ] Paths read from `manifest.artifact_versions`
- [ ] Evidence paths use `.claude/evidence/`

### Output Locations
- [ ] Artifacts go to `.claude/artifacts/`
- [ ] Evidence goes to `.claude/evidence/`
- [ ] Remediation goes to `.claude/remediation/`
- [ ] Evolution goes to `.claude/evolution/`

### ID Sequencing
- [ ] Documents search for existing IDs before creating new
- [ ] Documents increment from highest found
- [ ] Uses project-global ID space

### Manifest Updates
- [ ] Documents what manifest sections to update
- [ ] Includes manifest update format/example

### Compliance
- [ ] References Prime Directive
- [ ] Documents hexagonal architecture compliance
- [ ] Documents determinism requirements (if applicable)

### Testing
- [ ] Run `~/.claude/scripts/validate_agents.py`
- [ ] All validation checks pass

---

## Quick Reference

| Need | Location |
|------|----------|
| Agent prompts | `~/.claude/agents/` |
| Agent template | `~/.claude/templates/new_agent_template.md` |
| Agent schema | `~/.claude/schemas/agent_prompt.schema.yaml` |
| Validation script | `~/.claude/scripts/validate_agents.py` |
| Operating model | `~/.claude/docs/agent_operating_model.md` |
| Document consistency | `~/.claude/docs/document_consistency.md` |
| Visiting agent template | `~/.claude/agents/visiting-agent-template.md` |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-31 | Initial release |
