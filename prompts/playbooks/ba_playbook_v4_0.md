# BA Playbook (v4.1 - Manifest-Aligned)

## What "Good" Looks Like
- Stories are provably testable: every AC maps to TA IDs.
- Rules.yaml is referenced explicitly by TA IDs.
- Tasklist is small, dependency-safe, and produces evidence artifacts.
- **Tasklist is structured for Task tool hydration by coding agent.**
- **All artifacts are versioned and tracked in manifest.**

---

## Document Location Standard

All BA artifacts live in `.claude/` folder with sequence numbers and versions:

| Seq | Artifact | Location |
|-----|----------|----------|
| 001 | Solution Envelope | `.claude/artifacts/001_solution_envelope_v{N}.md` |
| 002 | Spec | `.claude/artifacts/002_spec_v{N}.md` |
| 003 | Tasklist | `.claude/artifacts/003_tasklist_v{N}.md` |
| 004 | Rules | `.claude/artifacts/004_rules_v{N}.yaml` |
| 005 | Quality Gates | `.claude/artifacts/005_quality_gates_v{N}.md` |
| 006 | Lessons Applied | `.claude/artifacts/006_lessons_applied_v{N}.md` |
| 007 | Coding Prompt | `.claude/artifacts/007_coding_prompt_v{N}.md` |

Evolution logs (append-only):
- `.claude/evolution/evolution.md`
- `.claude/evolution/decisions.md`

Evidence artifacts:
- `.claude/evidence/quality_gates_run.json`
- `.claude/evidence/test_report.json`
- `.claude/evidence/test_failures.json`
- `.claude/evidence/lint_report.json`

---

## Manifest Update (MANDATORY)

After creating/updating any artifact:

```yaml
# .claude/manifest.yaml
schema_version: "1.0"
project_slug: "{project}"
last_updated: "YYYY-MM-DDTHH:MM:SSZ"
phase: "ba|coding|qa|remediation"

artifact_versions:
  spec:
    version: 1
    file: ".claude/artifacts/002_spec_v1.md"
    created: "YYYY-MM-DDTHH:MM:SSZ"
  tasklist:
    version: 1
    file: ".claude/artifacts/003_tasklist_v1.md"
    created: "YYYY-MM-DDTHH:MM:SSZ"
  rules:
    version: 1
    file: ".claude/artifacts/004_rules_v1.yaml"
    created: "YYYY-MM-DDTHH:MM:SSZ"
  quality_gates:
    version: 1
    file: ".claude/artifacts/005_quality_gates_v1.md"
    created: "YYYY-MM-DDTHH:MM:SSZ"

outstanding:
  tasks: []
  remediation: []
```

---

## Tasklist Structure for Task Tool Hydration

The coding agent hydrates tasklist into runtime Task tools at session start. Structure your tasklist to enable this:

### Required Task Format

```markdown
## Task T001: [Imperative Title]

**Status**: pending | in_progress | completed (YYYY-MM-DD)
**Blocked By**: T000 (or "none")
**Estimated Scope**: 30-120 minutes

### Description
[What needs to be done - enough context for coding agent to work autonomously]

### Acceptance Criteria
- [ ] AC1: [Specific, testable criterion]
- [ ] AC2: [Maps to TA IDs in rules.yaml]

### Evidence Required
- [ ] Tests pass: `.claude/evidence/test_report.json`
- [ ] Quality gates pass: `.claude/evidence/quality_gates_run.json`
```

### Dependency Specification

Express dependencies explicitly for `blockedBy` hydration:

```markdown
## Task T003: Implement validation logic
**Blocked By**: T001, T002

## Task T004: Add API endpoint
**Blocked By**: T003
```

This creates the dependency graph:
```
T001 ──┐
       ├──► T003 ──► T004
T002 ──┘
```

### Task Sizing Guidelines

| Size | Duration | Scope |
|------|----------|-------|
| Small | 30-60 min | Single function/component |
| Medium | 60-90 min | Component + tests |
| Large | 90-120 min | Feature slice (split if larger) |

**If a task exceeds 120 minutes, split it.** Large tasks cause drift.

---

## EV Triage Cheat-Sheet
- Clarification: missing acceptance detail; add AC/TA + task.
- Local change: additive feature that does not alter core model/boundaries.
- Escalate: anything that changes flows, objects, boundaries, or threat model.

---

## Output Discipline
- Preserve IDs forever.
- Append new stories/tasks; never renumber completed work.
- **Mark completed tasks with date**: `**Status**: completed (2026-01-24)`
- **NEVER overwrite existing artifacts** - create new versions (v1 → v2)
- **Update manifest** after every artifact change

---

## Handoff to Coding Agent

When handing off to the coding agent, ensure:

### Pre-Handoff Checklist

| Check | Purpose |
|-------|---------|
| All tasks have unique IDs (T001, T002...) | Enables TaskCreate mapping |
| Dependencies are explicit | Enables blockedBy hydration |
| Each task has acceptance criteria | Defines "done" for TaskUpdate |
| Evidence artifacts specified with `.claude/evidence/` paths | Coding agent knows what to produce |
| No circular dependencies | Task loop can complete |
| **Manifest updated with all artifact versions** | Coding agent can find files |

### Handoff Note Template

Add to top of tasklist when ready for coding:

```markdown
## Coding Agent Handoff

**Date**: YYYY-MM-DD
**Manifest Version**: [last_updated from manifest]
**Ready Tasks**: T001, T002 (no blockers)
**Dependency Chain**: T001 → T003 → T004; T002 → T003

### Session Goals
1. Complete T001 and T002 (unblocked)
2. T003 becomes unblocked after both complete

### Artifact Paths (from manifest)
- Spec: .claude/artifacts/002_spec_v1.md
- Rules: .claude/artifacts/004_rules_v1.yaml
- Gates: .claude/artifacts/005_quality_gates_v1.md

### Known Risks
- [Any technical risks or ambiguities]
```

---

## Receiving Updates from Coding Agent

After a coding session, the coding agent syncs back:

### What to Expect

1. **Task status updates** in tasklist (pending → completed)
2. **Manifest updates** with task completion status
3. **Evolution entries** if drift was detected
4. **New tasks** if dependencies were discovered
5. **Evidence artifacts** in `.claude/evidence/`

### BA Review Checklist

| Item | Action |
|------|--------|
| Completed tasks | Verify evidence artifacts exist in `.claude/evidence/` |
| Manifest updated | Verify last_updated timestamp changed |
| New EV entries | Triage per EV cheat-sheet |
| New tasks discovered | Add to tasklist with proper IDs |
| Blockers reported | Update dependencies or escalate |

### Sync Verification

```markdown
## Post-Session Review YYYY-MM-DD

### Verified Complete
- [x] T001: Evidence in .claude/evidence/, tests pass
- [x] T002: Evidence in .claude/evidence/, tests pass

### New Tasks Added
- T005: [Discovered during T003 implementation]

### EV Entries to Triage
- EV-007: [Scope change detected in T003]

### Manifest Verified
- last_updated: YYYY-MM-DDTHH:MM:SSZ
- outstanding.tasks updated
```

---

## Task Tool Integration Summary

```
BA Creates                         Coding Agent Consumes
───────────────────────────────────────────────────────────
.claude/manifest.yaml         ───► Source of truth (paths)
.claude/artifacts/003_tasklist_v1.md ───► TaskCreate (hydrate)
  - Task IDs                         - subject
  - Dependencies                     - blockedBy
  - Acceptance Criteria              - description
  - Evidence Requirements (.claude/evidence/)
                                         │
                                    [Execute Task Loop]
                                         │
.claude/artifacts/003_tasklist_v1.md ◄─── Sync status back
.claude/manifest.yaml           ◄─── Update task status
.claude/evolution/evolution.md  ◄─── Drift entries
.claude/evidence/*.json         ◄─── Gate results
```

**BA owns the artifacts. Manifest is source of truth. Coding agent executes with discipline.**
