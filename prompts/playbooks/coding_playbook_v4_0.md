# Coding Playbook (v4.1 - Manifest-Aligned)

## Session Startup - Manifest First

At the start of each coding session:

### 1. Read Manifest (Source of Truth)
```
Read: .claude/manifest.yaml
Extract:
  - artifact_versions.tasklist.file → path to tasklist
  - artifact_versions.spec.file → path to spec
  - artifact_versions.rules.file → path to rules
  - artifact_versions.quality_gates.file → path to gates
  - outstanding.tasks → any in-progress work
  - outstanding.remediation → any pending bug fixes (handle FIRST)
```

### 2. Handle Outstanding Remediation
If `outstanding.remediation` has items with status "pending":
- Critical/High priority → MUST fix before new work
- Medium → Fix if related to current tasks
- Low → Note but can proceed

### 3. Hydrate Pending Tasks
Read tasklist from path in manifest, then for each pending task:
```
TaskCreate:
  subject: "Task title from tasklist"
  description: "Full task description including acceptance criteria"
  activeForm: "Working on [task title]..."
```

### 4. Set Dependencies
After all tasks created, establish ordering:
```
TaskUpdate:
  taskId: "2"
  addBlockedBy: ["1"]  # Task 2 blocked by Task 1
```

### 5. Claim First Unblocked Task
```
TaskList → Find first task with no blockedBy
TaskUpdate: status → "in_progress"
```

### Why Manifest First Matters
| Without | With |
|---------|------|
| May miss path changes | Always correct file paths |
| Missing remediation items | Bug fixes prioritized |
| Stale artifact versions | Current artifact versions |
| Session amnesia | Continuity across sessions |

---

## Practical Operating Rules
- One task at a time (enforced via Task tools - only one `in_progress`).
- Tests first for domain logic; adapters get contract/integration tests.
- Keep fixes local to the failing test + touched component contract.
- **TaskUpdate → completed** only after evidence artifacts generated.

## Task Loop Discipline

For each task, follow this exact sequence:

```
┌─────────────────────────────────────────────────────────────┐
│  1. CLAIM                                                   │
│     TaskUpdate: taskId, status: "in_progress"               │
│     Verify: no blockedBy tasks remain pending               │
├─────────────────────────────────────────────────────────────┤
│  2. READ                                                    │
│     TaskGet: taskId → read full description                 │
│     Read spec/rules sections from manifest paths            │
├─────────────────────────────────────────────────────────────┤
│  3. TDD                                                     │
│     Write/update test FIRST                                 │
│     Run test → confirm it FAILS                             │
│     Implement minimal code to pass                          │
├─────────────────────────────────────────────────────────────┤
│  4. EVIDENCE                                                │
│     Run quality gates                                       │
│     Output to: .claude/evidence/quality_gates_run.json      │
│     Output to: .claude/evidence/test_report.json            │
│     All gates must PASS                                     │
├─────────────────────────────────────────────────────────────┤
│  5. COMPLETE                                                │
│     TaskUpdate: taskId, status: "completed"                 │
│     Update tasklist file (path from manifest)               │
│     Update manifest.outstanding.tasks                       │
├─────────────────────────────────────────────────────────────┤
│  6. NEXT                                                    │
│     TaskList → find next unblocked pending task             │
│     Loop back to step 1                                     │
└─────────────────────────────────────────────────────────────┘
```

### Drift Detection During Task Loop

If while working you discover:
- Task requires changes outside its scope → **HALT**
- New dependency not in original tasklist → **HALT**
- Acceptance criteria are ambiguous → **HALT**

On HALT:
1. Do NOT mark task completed
2. Log EV entry in `.claude/evolution/evolution.md`
3. Create new task if needed: `TaskCreate` with dependency
4. Escalate to user for guidance

---

## Debug Order (Minimize Search Space)
1) Read `.claude/evidence/test_failures.json`
2) Open the specific failing test file
3) Check the component contract invariants
4) Check the port contract (ports.py / interface)
5) Implement the smallest change that makes the test pass

## Common Failure Prevention
- Inject time via TimePort (never call datetime in core)
- No module-level mutable state
- Maintain clean component API surface (avoid direct _impl imports)

## Component Structure Checklist (Prevents Governance Drift)

When implementing a new component or adapter:

### Pre-Implementation (before writing any code)
1. Create component directory: `src/components/<ComponentName>/`
2. Create ALL required file stubs:
   ```
   component.py     # def run(input: Input) -> Output: pass
   models.py        # class Input: ... class Output: ...
   ports.py         # (can be empty or with Protocol stubs)
   contract.md      # Purpose, Input/Output sections minimum
   __init__.py      # from .component import run
   ```
3. Add manifest entry with status: "in_progress"
4. Create one test file that validates component signature

### During Implementation
- Keep contract.md in sync with code
- If contract.md needs to change: log EV entry first
- Add tests as you add behavior (TDD)

### Post-Implementation (before marking task done)
- Run quality gates: `python scripts/run_quality_gates.py --phase=per-task`
- Verify G3_manifest_validation passes
- Update manifest entry: status "in_progress" → "complete"
- Verify contract.md matches actual input/output types
- Verify no unused imports (ruff check)

### Why This Prevents Drift
- Files exist from day 1 (won't be forgotten at end)
- contract.md acts as specification (reviewed before code)
- Manifest stays in sync (updated incrementally, not post-hoc)
- Quality gates catch structural issues before they accumulate

---

## Session Completion - Sync Back (MANDATORY)

Before ending a coding session, sync runtime state to persistent artifacts:

### 1. Review Task Status
```
TaskList → Review all tasks
```

### 2. Update BA Tasklist
Update tasklist file (path from manifest) for each completed task:
```markdown
## Task T001: [Title]
**Status**: completed (YYYY-MM-DD)
```

### 3. Update Manifest
```yaml
# .claude/manifest.yaml
last_updated: "YYYY-MM-DDTHH:MM:SSZ"
outstanding:
  tasks:
    - id: "T001"
      status: "completed"
      completed_date: "YYYY-MM-DD"
    - id: "T002"
      status: "in_progress"
```

### 4. Log Session Summary
Append to `.claude/evolution/evolution.md`:
```markdown
## Session YYYY-MM-DD

### Completed
- T001: Brief summary of what was done

### In Progress
- T002: Current state, what remains

### Blocked/Discovered
- New dependency found: [description]
- EV entry logged for: [drift item]
```

### 5. Verify Evidence Artifacts
These must exist in `.claude/evidence/`:
- `quality_gates_run.json`
- `test_report.json`
- `test_failures.json` (if any failures)
- `lint_report.json`

### Why Sync Matters
| Runtime (Task tools) | Persistent (BA artifacts) |
|---------------------|---------------------------|
| Session-scoped | Cross-session |
| Live progress | Historical record |
| Enforces discipline | Enables handoff |

**The manifest is the source of truth. Task tools enforce discipline during execution.**

---

## Verification Discipline: The Checkpoint Habit

### Why This Matters
Long conversations cause instruction drift. After 30-40 turns, you will start forgetting rules. This is not a character flaw—it's how attention works. The countermeasure is **proactive re-anchoring**.

### The Verification Loop (after every file edit)

```
Edit/Write file
    ↓
Run gates (ruff/mypy/pytest OR npm build/lint)
    ↓
Check .claude/evidence/test_failures.json
    ↓
If failures → fix immediately (do not proceed)
    ↓
If pass → continue to next edit
    ↓
Update .claude/evidence/quality_gates_run.json
```

### Turn-Based Checkpoints

| Turn Count | Action |
|------------|--------|
| 1-15 | Normal operation (fresh context) |
| 15 | **Checkpoint**: Re-read rules + system prompt |
| 16-30 | Normal operation |
| 30 | **Checkpoint**: Re-read + self-audit |
| 31-40 | Recommend wrapping up current task |
| 40+ | **Strongly recommend fresh conversation** |

### Event-Based Checkpoints

Trigger a checkpoint whenever:
- You're about to start a new task
- You just finished debugging (took >3 turns)
- User asked a tangential question and you're returning to work
- You catch yourself thinking "I'll skip tests for this simple change"
- You're tempted to make a "quick fix" outside task scope

### Checkpoint Protocol

```
1. State: "Checkpoint: re-reading governance rules."
2. Re-read: rules.yaml, quality_gates.md (paths from manifest)
3. Self-audit:
   - [ ] Following TDD?
   - [ ] Within task scope?
   - [ ] Hexagonal architecture?
   - [ ] Contracts updated?
   - [ ] Evidence exists in .claude/evidence/?
4. If violations: acknowledge and correct
5. Resume work
```

### Common Failure Modes This Prevents

| Failure | How Checkpoints Help |
|---------|---------------------|
| Tests written after code | Self-audit catches TDD violations |
| "While I'm here" edits | Scope check catches drift |
| Forgotten contract updates | Evidence check catches missing artifacts |
| Ignored linter warnings | Verification loop catches immediately |
| Accumulated tech debt | Regular gates prevent backlog |
