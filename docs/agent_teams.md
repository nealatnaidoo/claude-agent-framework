# Agent Teams: Parallel Development

**Version**: 2.0
**Status**: Framework feature (uses Claude Code agent teams + governance hooks)
**Date**: 2026-02-14

---

## Overview

Agent Teams enable multiple Claude Code instances to work in parallel within a single session. Each teammate gets its own context window, can communicate directly, and coordinates via a shared task list. Combined with hooks, teams provide mechanical quality enforcement during parallel coding.

## When to Use

| Scenario | Recommended Approach |
|----------|---------------------|
| Frontend + backend in parallel (same feature) | **Agent Teams** |
| Many identical items to process (batch hydration) | **`/batch` skill** (headless micro-jobs) |
| Independent features in parallel | Git worktrees |
| Competing hypotheses / debugging | **Agent Teams** |
| CI/CD + coding in parallel | **Agent Teams** |
| Long-running BA + coding overlap | Git worktrees |

### Batch vs Teams

| Aspect | `/batch` Skill | Agent Teams |
|--------|---------------|-------------|
| Use case | Many identical items (N > 5) | Heterogeneous parallel work (2-5 tasks) |
| Execution | Headless `claude -p`, no UI | Interactive, split-pane UI |
| Resume | Ledger-based, survives session loss | Session-only, no resume |
| Context | Each item gets fresh context | Each teammate shares session context |
| Tracking | YAML ledger with pending/active/done/failed | Shared task list |
| Quality | Results broker collects summaries | `TaskCompleted` hook runs gates |

---

## Setup

### Display Modes

```bash
# Auto-detect (tmux or iTerm2 for split panes, else in-process)
# Default behavior — no config needed

# Force split panes (requires tmux or iTerm2)
export CLAUDE_CODE_AGENT_TEAMS_DISPLAY=split-panes

# Force in-process (all in one terminal, shift+up/down to switch)
export CLAUDE_CODE_AGENT_TEAMS_DISPLAY=in-process
```

---

## Creating Teams

Teams are created via natural language. The team lead coordinates while teammates execute.

### Delegate Mode

Press **Shift+Tab** to toggle delegate mode. In delegate mode, the team lead is restricted to coordination only — it cannot write code, only assign tasks and communicate with teammates.

### Example: Full-Stack Feature Development

```
Create a team with two teammates:
- "back-worker" for backend Python tasks
- "front-worker" for frontend React tasks

I'll coordinate in delegate mode. Read the tasklist from .claude/artifacts/003_tasklist_v1.md
and assign backend tasks to back-worker and frontend tasks to front-worker.
```

### Example: Code Review Team

```
Create a team:
- "governance-reviewer" to check TDD and hexagonal compliance
- "spec-reviewer" to verify spec fidelity and AC coverage
- "journey-reviewer" to validate user journey E2E paths
```

### Example: Debug Team

```
Create a team:
- "hypothesis-a" to test whether the bug is in the auth middleware
- "hypothesis-b" to test whether it's a database connection pool issue
```

---

## Communication

Teammates communicate **directly** via Claude Code's native messaging — not through files. The team lead can:

- Send tasks to specific teammates
- Receive status updates from teammates
- Broadcast messages to all teammates
- Query teammate progress

The **shared task list** tracks which tasks are claimed, in progress, and completed.

---

## Hook Integration

Two hooks automate the coordination loop:

### `TeammateIdle` Hook

Fires when a teammate completes work and becomes idle.

**What it does**:
1. Reads the project manifest
2. Maps the teammate to a domain (backend/frontend)
3. Finds the next unblocked pending task
4. Suggests the task to the team lead

**Registered in**: `settings.local.json` under `TeammateIdle`

### `TaskCompleted` Hook

Fires when a teammate marks a task as done.

**What it does**:
1. Reads manifest to identify newly unblocked tasks (read-only, no manifest write)
2. Appends completion entry to the evolution log
3. Reports completion and newly unblocked tasks to team lead
4. Team lead is responsible for updating manifest status (governance compliance)

**Registered in**: `settings.local.json` under `TaskCompleted`

### Quality Gates via Hooks

For automated quality enforcement during parallel work:

```
TaskCompleted hook flow:
  Teammate marks task done
    → Hook reads manifest (no write — governance compliance)
    → Hook checks for unblocked tasks
    → Team lead sees: "T002 completed. Update manifest. T004 now unblocked."
    → Team lead updates manifest and assigns T004 to idle teammate
```

---

## Integration with Existing Framework

### Prerequisites

Before using Agent Teams, the full lifecycle must have run:

1. `init` — `.claude/` structure exists
2. `persona` — User journeys defined
3. `design` — Solution envelope with DevOps approval
4. `ba` — Spec, tasklist, and tasks loaded into manifest

Agent Teams operate during the **coding phase** only.

### Manifest Compatibility

Agent Teams use the same manifest.yaml:
- `phase: coding` for team-based development
- `outstanding.tasks` split across teammates by `domain` tag
- `TaskCompleted` hook reports completions; team lead updates manifest

### Exclusive Permissions Still Apply

- Only the backend teammate can write Python code
- Only the frontend teammate can write TypeScript code
- `ops` still required for deployments

### BA-Only Constraint Still Applies

Agent Teams do not bypass the BA workflow. The team lead loads BA artifacts and distributes tasks.

---

## Limitations

- **Session-only**: Teams do not survive session loss. For resumable parallel work, use `/batch`
- **No nested teams**: Teammates cannot spawn their own teams
- **One team per session**: Cannot run multiple teams simultaneously
- **Task status sync**: `TaskCompleted` hook handles most cases, but manual sync may be needed for complex dependencies

---

## Comparison: Agent Teams vs Git Worktrees

| Aspect | Agent Teams | Git Worktrees |
|--------|------------|---------------|
| Setup | Native, no config | Shell script + git |
| Context | Each teammate gets own 200K window | Each worktree is separate session |
| Communication | Direct messaging (native) | Via manifest + artifacts (file-based) |
| Merge | Automatic (same branch) | Manual merge required |
| Persistence | Session only | Persists across sessions |
| Hooks | `TeammateIdle`, `TaskCompleted` | None (manual coordination) |
| Best for | Same-feature parallel work | Independent features, separate branches |

## Recommendation

Use **Agent Teams** for within-session parallel work (same feature, same branch, 2-5 heterogeneous tasks). Use **`/batch`** for many identical items (batch processing, hydration, reviews). Keep **git worktrees** for cross-session parallel work (independent features, separate branches).

All three approaches coexist. The manifest schema supports all of them.
