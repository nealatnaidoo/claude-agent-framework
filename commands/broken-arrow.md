---
allowed-tools: Read, Write, Glob, Grep, Bash(pwd), Bash(date:*), Bash(ls:*), Bash(find:*), Bash(git:*), Bash(wc:*), Bash(mkdir:*), Bash(python3:*)
description: Assess and plan governance retrofit for existing non-compliant projects
---

## Context

- Current directory: !`pwd`
- Timestamp: !`date -u +"%Y-%m-%dT%H:%M:%SZ"`
- Git info: !`git log --oneline -5 2>/dev/null || echo "not a git repo"`

## Your Task

Assess an existing project that lacks governance scaffolding and create a retrofit migration plan. This is the deliberate path for bringing pre-existing codebases into compliance.

### Phase 1: Assessment

Scan the project and gather:

1. **Tech stack detection**
   - Look for: `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Dockerfile`, `docker-compose.yml`
   - Identify languages, frameworks, package managers

2. **Code inventory**
   - Count source files by type (`.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.rs`, `.go`, etc.)
   - Count total lines of code (approximate via `wc -l`)
   - Identify main entry points

3. **Test coverage**
   - Look for test directories (`tests/`, `test/`, `__tests__/`, `spec/`)
   - Count test files
   - Check for test config (`pytest.ini`, `jest.config.*`, `vitest.config.*`)

4. **Existing `.claude/` state**
   - Check if `.claude/` directory exists
   - Check for `manifest.yaml`, any artifacts, evidence
   - Check for `.lost_lamb` (note if exception clock is ticking)
   - Check for `.broken_arrow` (previous assessment)

5. **Git history**
   - First commit date, total commits
   - Number of contributors
   - Last commit date

### Phase 2: Create Marker

Create `.claude/` directory if needed, then use Bash with python3 to write `.claude/.broken_arrow` (JSON):

```bash
python3 -c "
import json
from datetime import datetime, timezone
data = {
    'assessed_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'project_path': '<PROJECT_PATH>',
    'tech_stack': ['<detected technologies>'],
    'source_files': <count>,
    'test_files': <count>,
    'has_existing_claude_dir': <true/false>,
    'has_manifest': <true/false>,
    'git_commits': <count>,
    'status': 'assessed'
}
with open('.claude/.broken_arrow', 'w') as f:
    json.dump(data, f, indent=2)
print('Assessment marker written to .claude/.broken_arrow')
"
```

### Phase 3: Create Migration Plan

Write `.claude/migration_plan.md` with the Write tool. Structure:

```markdown
# Governance Migration Plan

**Project**: <name>
**Assessed**: <timestamp>
**Status**: Pending migration

## Current State

- Tech stack: ...
- Source files: X files, ~Y lines
- Test files: X files
- Existing governance: none / partial

## Migration Steps

### Step 1: Initialize governance scaffold
Run `init` to create manifest and folder structure.

### Step 2: Define user journeys
Run `persona` to identify users and their journeys.
(Note: for retrofit projects, focus on documenting existing behavior)

### Step 3: Solution design
Run `design` to document the existing architecture.
(Focus on as-is documentation, not redesign)

### Step 4: Create BA artifacts
Run `ba` to create spec and tasklist from existing code.
(Reverse-engineer spec from implementation)

### Step 5: Establish test baseline
Ensure existing tests pass. Add missing critical tests.

### Step 6: Enter coding phase
With governance in place, future changes go through the standard lifecycle.

## Recommendations

<project-specific recommendations based on assessment>

## Notes

<any caveats, risks, or special considerations>
```

### Phase 4: Report

Display a summary to the user:

```
BROKEN ARROW ASSESSMENT COMPLETE

Project: <name>
Tech: <stack summary>
Size: X source files, Y test files
Governance: <current state>

Migration plan: .claude/migration_plan.md
Assessment: .claude/.broken_arrow

NEXT STEP: Run init to begin the retrofit.
```

If `.lost_lamb` exists, note: "Active lost-lamb exception expires at <time>. Complete at least Step 1 before it expires."

### Rules

- This command is **read-only on source code** — only create/modify files under `.claude/`
- Do NOT modify any source code, tests, or configuration files
- Do NOT start the actual migration — only assess and plan
- Be honest about the project's state — don't sugarcoat missing tests or governance gaps
- If a previous `.broken_arrow` exists, show the diff from last assessment
