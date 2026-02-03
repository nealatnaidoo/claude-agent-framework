# Restart Protocol v1.1

## Purpose

This protocol ensures work can resume correctly after:
- New Claude Code session
- Context compression
- Session interruption
- Agent handoff

## Restart Sequence

### Step 0: Detect Context (v1.2)

Before proceeding, determine if you are in a worktree:

```yaml
# Check manifest for worktree section
worktree:
  is_worktree: true  # ← If true, you're in a worktree
  name: "user-auth"
  branch: "feature/user-auth"
  main_worktree_path: "../myproject"
  feature_scope:
    - "T001"
    - "T002"
    - "T003"
```

**If `worktree.is_worktree: true`**:

1. You are in a **feature worktree**, not the main project
2. Your scope is limited to tasks in `feature_scope`
3. Verify registration in main manifest:
   ```bash
   cat {main_worktree_path}/.claude/manifest.yaml | grep -A5 "active_worktrees"
   ```
4. If not registered: HALT. Report: "Worktree not registered in main manifest."

**If `worktree.is_worktree: false` or section absent**:

- You are in the **main worktree** or a single-worktree project
- Continue with normal restart protocol

### Step 1: Locate Manifest

```
{project_root}/.claude/manifest.yaml
```

If manifest doesn't exist, this is either:
- A new project (start with Solution Designer)
- A legacy project (needs migration)

### Step 2: Read Current State

Extract from manifest:
```yaml
phase: coding              # Current workflow phase
outstanding:
  remediation: [...]       # BUG/IMPROVE items (priority)
  tasks: [...]             # Pending implementation tasks
reviews:
  last_qa_review: {...}    # Recent review results
  last_code_review: {...}
```

### Step 3: Determine Priority Order

Work is processed in this order:

1. **Critical remediation** (`priority: critical`)
2. **High remediation** (`priority: high`)
3. **In-progress tasks** (`status: in_progress`)
4. **Medium remediation** (`priority: medium`)
5. **Pending tasks** (`status: pending`, respect `blocked_by`)
6. **Low remediation** (`priority: low`)

### Step 4: Hydrate Task List

For pending work, create in-session tasks:

```python
# Pseudocode for restart hydration
for item in outstanding.remediation:
    if item.priority in ['critical', 'high']:
        TaskCreate(
            subject=f"[{item.id}] {item.summary}",
            description=f"Source: {item.source}\nFile: {item.file}",
            activeForm=f"Fixing {item.id}"
        )

for task in outstanding.tasks:
    if not task.blocked_by or all_resolved(task.blocked_by):
        TaskCreate(
            subject=f"[{task.id}] {task_subject_from_tasklist}",
            description=task_description_from_tasklist,
            activeForm=f"Implementing {task.id}"
        )
```

### Step 5: Resume Work

1. **Claim next task** (TaskUpdate status: in_progress)
2. **Read relevant artifacts** (spec, rules, quality gates)
3. **Implement/fix** following TDD and quality gates
4. **Complete task** (TaskUpdate status: completed)
5. **Update manifest** before moving to next task

## Phase-Specific Restart

### Phase: `solution_design`

Active agent: **Solution Designer**

Actions:
1. Read any existing `001_solution_envelope_*.md`
2. Continue discovery workflow
3. On completion, update `phase: ba`

### Phase: `ba`

Active agent: **Business Analyst**

Actions:
1. Read existing artifacts (spec, tasklist, rules)
2. Check for incomplete sections
3. Continue artifact creation
4. On completion, populate `outstanding.tasks` and set `phase: coding`

### Phase: `coding`

Active agent: **Coding Agent**

Actions:
1. Check remediation first (see priority order)
2. Process tasks in dependency order
3. Run quality gates after each task
4. Update manifest with completed tasks

### Phase: `qa`

Active agent: **QA Reviewer**

Actions:
1. Run quality gate checks
2. Create `qa_YYYY-MM-DD.md` report
3. Add findings to `outstanding.remediation`
4. Set `phase: coding` if needs_work, else `phase: code_review`

### Phase: `code_review`

Active agent: **Code Review Agent**

Actions:
1. Deep verification against spec/stories
2. Create `code_review_YYYY-MM-DD.md` report
3. Add findings to `outstanding.remediation`
4. Set `phase: coding` if needs_work, else evaluate completion

### Phase: `paused`

No active agent. Check `pause_reason` in manifest.

## Manifest Update Protocol

### On Task Start

```yaml
outstanding:
  tasks:
    - id: "T003"
      status: "in_progress"  # Changed from pending
      assignee: "session-abc123"
```

### On Task Complete

```yaml
outstanding:
  tasks:
    - id: "T003"
      status: "completed"  # Or remove from list
```

Also update `sessions` array if tracking:
```yaml
sessions:
  - session_id: "abc123"
    started: "2026-01-30T14:00:00Z"
    tasks_completed: ["T003"]
```

### On Remediation Complete

```yaml
outstanding:
  remediation:
    - id: "BUG-001"
      status: "resolved"  # Or remove from list
      resolved: "2026-01-30T15:30:00Z"
```

### On Review Complete

```yaml
reviews:
  last_qa_review:
    date: "2026-01-30T16:00:00Z"
    result: "pass_with_notes"
    report_file: ".claude/remediation/qa_2026-01-30.md"
```

## Conflict Resolution

### Multiple Sessions

If manifest shows `outstanding.tasks[].assignee` from another session:
1. Check if session is still active (ask user)
2. If abandoned, clear assignee and claim task
3. Never work on tasks assigned to active sessions

### Stale Manifest

If manifest `last_updated` is old but code has changed:
1. Run quality gates to assess current state
2. Compare `evidence/` timestamps to manifest
3. If mismatched, run QA review before resuming

### Missing Artifacts

If manifest references artifacts that don't exist:
1. Check git history (were they deleted?)
2. Ask user for guidance
3. May need BA agent to recreate

## Session Completion Checklist

Before ending a session:

- [ ] All in-progress tasks either completed or set back to pending
- [ ] Manifest `last_updated` timestamp current
- [ ] Manifest `outstanding` reflects true state
- [ ] Evidence artifacts up to date
- [ ] Any new remediation items added to manifest
- [ ] Session recorded in `sessions` array (if tracking)

## Quick Reference Commands

### Check Project State
```bash
cat {project}/.claude/manifest.yaml | head -30
```

### List Outstanding Work
```bash
yq '.outstanding' {project}/.claude/manifest.yaml
```

### Check Last Review
```bash
yq '.reviews' {project}/.claude/manifest.yaml
```

### Update Phase (manual)
```bash
yq -i '.phase = "coding"' {project}/.claude/manifest.yaml
yq -i '.last_updated = now' {project}/.claude/manifest.yaml
```
