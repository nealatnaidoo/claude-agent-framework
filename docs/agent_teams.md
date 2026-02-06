# Agent Teams: Parallel Development

**Version**: 1.1
**Status**: Experimental (requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
**Date**: 2026-02-06

---

## Overview

Agent Teams enable multiple Claude Code instances to work in parallel within a single session. This is an alternative to git worktree-based parallelism for frontend/backend development.

## When to Use

| Scenario | Recommended Approach |
|----------|---------------------|
| Frontend + backend in parallel (same feature) | **Agent Teams** |
| Independent features in parallel | Git worktrees (existing) |
| Competing hypotheses / debugging | **Agent Teams** |
| CI/CD + coding in parallel | **Agent Teams** |
| Long-running BA + coding overlap | Git worktrees (existing) |

## Setup

### Enable Agent Teams

```bash
# Set environment variable before starting Claude Code
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Or add to your shell profile
echo 'export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1' >> ~/.zshrc
```

### Display Modes

```bash
# Auto-detect (tmux or iTerm2 for split panes, else in-process)
# Default behavior

# Force split panes (requires tmux or iTerm2)
export CLAUDE_CODE_AGENT_TEAMS_DISPLAY=split-panes

# Force in-process (all in one terminal, shift+up/down to switch)
export CLAUDE_CODE_AGENT_TEAMS_DISPLAY=in-process
```

## Team Configurations

### Full-Stack Feature Development

**Team Lead**: Orchestrator (reads manifest, splits tasks, coordinates)
**Teammates**:
- `backend-worker`: Backend coding agent (Python, hexagonal architecture)
- `frontend-worker`: Frontend coding agent (React/TypeScript, FSD)

**Workflow**:
1. Team lead reads BA spec and tasklist from manifest
2. Team lead splits tasks by domain tag (backend/frontend)
3. Backend worker implements Python components
4. Frontend worker implements React components
5. Team lead runs QA reviewer after both complete
6. Team lead creates integration tests for the connection points

### Code Review Team

**Team Lead**: Review coordinator
**Teammates**:
- `governance-reviewer`: QA governance checks (TDD, hexagonal, gates)
- `spec-reviewer`: Deep spec fidelity verification
- `journey-reviewer`: User journey E2E validation

### Debug Team

**Team Lead**: Investigation coordinator
**Teammates**:
- `hypothesis-a`: Tests first theory about the bug
- `hypothesis-b`: Tests alternative theory

## Integration with Existing Framework

### Prerequisites

Before using Agent Teams, the full lifecycle must have run:

1. `project-initializer` - `.claude/` structure exists
2. `persona-evaluator` - User journeys defined
3. `solution-designer` - Solution envelope with DevOps approval
4. `business-analyst` - Spec, tasklist, and tasks loaded into manifest

Agent Teams operate during the **coding phase** only.

### Manifest Compatibility

Agent Teams use the same manifest.yaml:
- `phase: coding` for team-based development
- `outstanding.tasks` split across teammates by `domain` tag
- Team lead updates manifest on completion

### Exclusive Permissions Still Apply

- Only the backend teammate can write Python code
- Only the frontend teammate can write TypeScript code
- DevOps Governor still required for deployments

### BA-Only Constraint Still Applies

Agent Teams do not bypass the BA workflow. The team lead loads BA artifacts and distributes tasks.

## Limitations

- **No session resumption** with in-process teammates
- **No nested teams** (teammates cannot spawn their own teams)
- **Task status can lag** (manual sync may be needed)
- **One team per session**
- **Experimental**: API may change

## Comparison: Agent Teams vs Git Worktrees

| Aspect | Agent Teams | Git Worktrees |
|--------|------------|---------------|
| Setup | Environment variable | Shell script + git |
| Context | Each teammate gets own 200K window | Each worktree is separate session |
| Communication | Direct messaging | Via manifest + artifacts |
| Merge | Automatic (same branch) | Manual merge |
| Persistence | Session only | Persists across sessions |
| Maturity | Experimental | Production-ready |

## Recommendation

Use **Agent Teams** for within-session parallel work (same feature, same branch). Keep **git worktrees** for cross-session parallel work (independent features, separate branches).

Both approaches coexist. The manifest schema (v1.3) supports both.
