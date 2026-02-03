# Claude Project Artifact Convention v1.1

## Overview

All Claude-generated project artifacts are stored in a `.claude/` folder at the project root. This eliminates clutter and provides clear sequencing, versioning, and restart capability.

## Folder Structure

```
{project_root}/
├── .claude/                              # All Claude artifacts
│   ├── manifest.yaml                     # Restart checkpoint (single source of truth)
│   │
│   ├── artifacts/                        # BA artifacts (sequenced, versioned)
│   │   ├── 001_solution_envelope_v1.md
│   │   ├── 002_spec_v1.md
│   │   ├── 002_spec_v2.md                # Updated version
│   │   ├── 003_tasklist_v1.md
│   │   ├── 004_rules_v1.yaml
│   │   ├── 005_quality_gates_v1.md
│   │   └── 006_lessons_applied_v1.md
│   │
│   ├── evolution/                        # Append-only logs
│   │   ├── evolution.md                  # Drift and scope changes
│   │   └── decisions.md                  # Architectural decisions
│   │
│   ├── remediation/                      # QA + Code Review findings
│   │   ├── qa_YYYY-MM-DD.md              # QA review reports
│   │   ├── code_review_YYYY-MM-DD.md     # Code review reports
│   │   ├── project_review_YYYY-MM-DD.md  # Full project reviews
│   │   └── remediation_tasks.md          # Consolidated outstanding fixes
│   │
│   └── evidence/                         # Quality gate outputs
│       ├── quality_gates_run.json
│       ├── test_report.json
│       ├── test_failures.json
│       └── coverage.json                 # Optional
│
└── src/                                  # Actual code
```

## Naming Convention

### Artifact Files: `NNN_type_vM.ext`

| Component | Description | Example |
|-----------|-------------|---------|
| `NNN` | Sequence number (workflow order) | `001`, `002`, `003` |
| `type` | Artifact type (snake_case) | `solution_envelope`, `spec`, `tasklist` |
| `vM` | Version number | `v1`, `v2`, `v3` |
| `ext` | File extension | `md`, `yaml` |

### Sequence Numbers (Workflow Order)

| Seq | Artifact | Created By | Purpose |
|-----|----------|------------|---------|
| 001 | `solution_envelope` | Solution Designer | Problem scope, architecture proposal |
| 002 | `spec` | Business Analyst | Requirements, epics, NFRs |
| 003 | `tasklist` | Business Analyst | Dependency-ordered implementation tasks |
| 004 | `rules` | Business Analyst | Domain rules, policies (YAML) |
| 005 | `quality_gates` | Business Analyst | Lint, type, test requirements |
| 006 | `lessons_applied` | Lessons Advisor | Applicable lessons from devlessons.md |
| 007 | `coding_prompt` | Business Analyst | Project-specific coding instructions |

### Review Files: `type_YYYY-MM-DD.md`

- `qa_2026-01-30.md` - QA review from January 30
- `code_review_2026-01-30.md` - Code review from January 30
- `project_review_2026-01-30.md` - Full project review

### Remediation IDs

- `BUG-001`, `BUG-002` - Bugs requiring fixes
- `IMPROVE-001`, `IMPROVE-002` - Improvements to consider

## Versioning Rules

### When to Increment Version

1. **Spec changes**: Any requirement, AC, or architecture change
2. **Tasklist changes**: New tasks, reordering, dependency changes
3. **Rules changes**: New rules, policy updates
4. **Quality gates changes**: New gate requirements

### Version History

- Keep ALL versions in `artifacts/` folder
- Never overwrite - always create new version file
- `manifest.yaml` tracks current version for each artifact

### Example Version Evolution

```
.claude/artifacts/
├── 002_spec_v1.md          # Initial spec
├── 002_spec_v2.md          # Added auth requirements
├── 002_spec_v3.md          # Clarified API contract
├── 003_tasklist_v1.md      # Initial tasks
└── 003_tasklist_v2.md      # Added T015-T018 after drift
```

## Manifest (Restart Checkpoint)

The `manifest.yaml` file is the single source of truth for:

1. **Project phase** - Where we are in the workflow
2. **Current artifact versions** - Which version is active
3. **Outstanding work** - Tasks and remediation items pending
4. **Review history** - Last QA/Code Review results

### Restart Protocol

When resuming work (new session or after context compress):

1. **Read `.claude/manifest.yaml`**
2. **Check `phase`** - Determines which agent should be active
3. **Check `outstanding.remediation`** - Handle bugs first (priority order)
4. **Check `outstanding.tasks`** - Continue with pending tasks
5. **Update manifest** before ending session

See: `~/.claude/docs/restart_protocol.md`

## Agent Responsibilities

### Solution Designer

**Creates:**
- `.claude/artifacts/001_solution_envelope_v1.md`

**Updates manifest:**
- `phase: solution_design` -> `phase: ba`
- `artifact_versions.solution_envelope`

### Business Analyst

**Creates:**
- `.claude/artifacts/002_spec_vN.md`
- `.claude/artifacts/003_tasklist_vN.md`
- `.claude/artifacts/004_rules_vN.yaml`
- `.claude/artifacts/005_quality_gates_vN.md`
- `.claude/artifacts/007_coding_prompt_vN.md` (optional)
- `.claude/evolution/evolution.md`
- `.claude/evolution/decisions.md`

**Updates manifest:**
- `phase: ba` -> `phase: coding`
- All artifact versions created/updated
- `outstanding.tasks` populated from tasklist

### Coding Agent

**Creates:**
- Source code in `src/`
- `.claude/evidence/quality_gates_run.json`
- `.claude/evidence/test_report.json`
- `.claude/evidence/test_failures.json`

**Updates manifest:**
- `outstanding.tasks[].status` as tasks complete
- `evidence` paths

### QA Reviewer

**Creates:**
- `.claude/remediation/qa_YYYY-MM-DD.md`
- Updates `.claude/remediation/remediation_tasks.md`

**Updates manifest:**
- `reviews.last_qa_review`
- `outstanding.remediation` (adds BUG/IMPROVE items)
- `phase: coding` if needs_work, else continues

### Code Review Agent

**Creates:**
- `.claude/remediation/code_review_YYYY-MM-DD.md`
- Updates `.claude/remediation/remediation_tasks.md`

**Updates manifest:**
- `reviews.last_code_review`
- `outstanding.remediation` (adds BUG/IMPROVE items)
- `phase: coding` if needs_work, else continues

### Lessons Advisor

**Creates:**
- `.claude/artifacts/006_lessons_applied_vN.md`

**Updates manifest:**
- `artifact_versions.lessons_applied`

## Git Integration

### Recommended `.gitignore`

```gitignore
# Include Claude artifacts in version control (recommended)
# Only ignore session-specific files

.claude/evidence/coverage.json     # Large file
.claude/sessions/                  # If you track session history locally
```

### Recommended to Commit

- `.claude/manifest.yaml` - Critical for team sync
- `.claude/artifacts/` - All versioned artifacts
- `.claude/evolution/` - Change history
- `.claude/remediation/` - Review findings
- `.claude/evidence/*.json` - Quality gate results (except large coverage)

## Worktree Artifact Structure (v1.2)

When using git worktrees for parallel development, each worktree maintains independent `.claude/` state.

### Main Worktree (Planning Hub)

The main worktree stores feature specs in its artifacts folder:

```
myproject/
└── .claude/
    ├── manifest.yaml                    # Contains feature_backlog, active_worktrees
    └── artifacts/
        ├── 002_spec_v1.md               # Main project spec
        ├── 002_spec_user_auth_v1.md     # Feature: user-auth spec
        ├── 002_spec_billing_v1.md       # Feature: billing spec
        ├── 003_tasklist_v1.md           # Main orchestration tasklist
        ├── 003_tasklist_user_auth_v1.md # Feature: user-auth tasks
        └── 003_tasklist_billing_v1.md   # Feature: billing tasks
```

### Feature Worktree (Implementation)

Each feature worktree has independent state:

```
myproject-user-auth/                     # Sibling directory
└── .claude/
    ├── manifest.yaml                    # Contains worktree.is_worktree: true
    ├── artifacts/
    │   ├── 002_spec_user_auth_v1.md     # Copied from main
    │   ├── 003_tasklist_user_auth_v1.md # Copied from main
    │   ├── 004_rules_v1.yaml            # Synced from main
    │   └── 005_quality_gates_v1.md      # Synced from main
    ├── evolution/
    │   ├── evolution.md                 # Feature-specific drift
    │   └── decisions.md                 # Feature-specific decisions
    ├── remediation/
    │   └── qa_YYYY-MM-DD.md             # Feature QA reports
    └── evidence/
        ├── quality_gates_run.json
        ├── test_report.json
        └── test_failures.json
```

### Feature-Specific Artifact Naming

Feature specs and tasklists include the feature slug:

| Artifact | Naming Pattern | Example |
|----------|---------------|---------|
| Feature Spec | `002_spec_{feature}_vN.md` | `002_spec_user_auth_v1.md` |
| Feature Tasklist | `003_tasklist_{feature}_vN.md` | `003_tasklist_user_auth_v1.md` |

### Shared vs Independent Artifacts

| Artifact Type | Behavior | Synced? |
|---------------|----------|---------|
| Rules (`004_rules_*.yaml`) | Shared across worktrees | Yes (copy) |
| Quality Gates (`005_quality_gates_*.md`) | Shared across worktrees | Yes (copy) |
| Lessons Applied (`006_lessons_*.md`) | Shared across worktrees | Yes (copy) |
| Evidence (`evidence/*.json`) | Independent per worktree | No |
| Evolution logs | Independent per worktree | No |
| Remediation | Independent per worktree | No |

### ID Sequencing Across Worktrees

**CRITICAL**: BUG-XXX and IMPROVE-XXX IDs are **project-global**, not worktree-local.

When creating IDs in a worktree:
1. Search main worktree's remediation for highest ID
2. Search all active worktrees' remediation
3. Increment from the highest found

```bash
# From any worktree, search all remediation locations
grep -rh "BUG-[0-9]" ../myproject*/.claude/remediation/ 2>/dev/null | sort -u
```

### Sync Protocol

When shared artifacts are updated in main:

```bash
~/.claude/scripts/worktree_manager.sh sync ../myproject-user-auth
```

This copies:
- `004_rules_*.yaml`
- `005_quality_gates_*.md`
- `006_lessons_applied_*.md`

---

## Migration from Legacy Structure

For existing projects with `{project}_spec.md` at root:

1. Create `.claude/` folder structure
2. Move and rename artifacts:
   ```
   {project}_spec.md -> .claude/artifacts/002_spec_v1.md
   {project}_tasklist.md -> .claude/artifacts/003_tasklist_v1.md
   etc.
   ```
3. Create `manifest.yaml` from current state
4. Update any hardcoded paths in project

See: `/Users/naidooone/Developer/claude/prompts/migrations/MIGRATE_PROJECT_ARTIFACTS.md`
