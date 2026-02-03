# Migration: Project Artifacts to .claude/ Folder

**Version**: 1.0
**Date**: 2026-01-30
**Purpose**: Migrate legacy project artifacts from root directory to `.claude/` folder structure

## Overview

This migration moves project artifacts from the legacy flat structure at project root to the new organized `.claude/` folder with proper sequencing and versioning.

## Before (Legacy Structure)

```
{project}/
├── {project}_spec.md
├── {project}_tasklist.md
├── {project}_rules.yaml
├── {project}_evolution.md
├── {project}_decisions.md
├── {project}_quality_gates.md
├── {project}_coding_agent_system_prompt.md
├── {project}_lessons_applied.md
├── artifacts/
│   ├── quality_gates_run.json
│   ├── test_report.json
│   └── test_failures.json
└── src/
```

## After (New Structure)

```
{project}/
├── .claude/
│   ├── manifest.yaml
│   ├── artifacts/
│   │   ├── 002_spec_v1.md
│   │   ├── 003_tasklist_v1.md
│   │   ├── 004_rules_v1.yaml
│   │   ├── 005_quality_gates_v1.md
│   │   ├── 006_lessons_applied_v1.md
│   │   └── 007_coding_prompt_v1.md
│   ├── evolution/
│   │   ├── evolution.md
│   │   └── decisions.md
│   ├── remediation/
│   │   └── remediation_tasks.md
│   └── evidence/
│       ├── quality_gates_run.json
│       ├── test_report.json
│       └── test_failures.json
└── src/
```

## Migration Steps

### Step 1: Create Folder Structure

```bash
cd {project_root}
mkdir -p .claude/{artifacts,evolution,remediation,evidence}
```

### Step 2: Move and Rename Artifacts

```bash
# Spec
mv {project}_spec.md .claude/artifacts/002_spec_v1.md

# Tasklist
mv {project}_tasklist.md .claude/artifacts/003_tasklist_v1.md

# Rules
mv {project}_rules.yaml .claude/artifacts/004_rules_v1.yaml

# Quality Gates
mv {project}_quality_gates.md .claude/artifacts/005_quality_gates_v1.md

# Lessons Applied (if exists)
[ -f {project}_lessons_applied.md ] && \
  mv {project}_lessons_applied.md .claude/artifacts/006_lessons_applied_v1.md

# Coding Prompt (if exists)
[ -f {project}_coding_agent_system_prompt.md ] && \
  mv {project}_coding_agent_system_prompt.md .claude/artifacts/007_coding_prompt_v1.md
```

### Step 3: Move Evolution Logs

```bash
# Evolution
mv {project}_evolution.md .claude/evolution/evolution.md

# Decisions
mv {project}_decisions.md .claude/evolution/decisions.md
```

### Step 4: Move Evidence Artifacts

```bash
# Move from artifacts/ to .claude/evidence/
mv artifacts/quality_gates_run.json .claude/evidence/
mv artifacts/test_report.json .claude/evidence/
mv artifacts/test_failures.json .claude/evidence/
[ -f artifacts/coverage.json ] && mv artifacts/coverage.json .claude/evidence/

# Remove old artifacts folder if empty
rmdir artifacts 2>/dev/null || true
```

### Step 5: Create Manifest

Create `.claude/manifest.yaml`:

```yaml
schema_version: "1.0"
project_slug: "{project_slug}"
project_name: "{Project Name}"
created: "{original_creation_date}"  # From git history or file dates
last_updated: "{current_timestamp}"
phase: "coding"  # Or current phase
phase_started: "{current_timestamp}"

artifact_versions:
  spec:
    version: 1
    file: ".claude/artifacts/002_spec_v1.md"
    created: "{file_date}"
  tasklist:
    version: 1
    file: ".claude/artifacts/003_tasklist_v1.md"
    created: "{file_date}"
  rules:
    version: 1
    file: ".claude/artifacts/004_rules_v1.yaml"
    created: "{file_date}"
  quality_gates:
    version: 1
    file: ".claude/artifacts/005_quality_gates_v1.md"
    created: "{file_date}"
  # Add if exists:
  lessons_applied:
    version: 1
    file: ".claude/artifacts/006_lessons_applied_v1.md"
    created: "{file_date}"
  coding_prompt:
    version: 1
    file: ".claude/artifacts/007_coding_prompt_v1.md"
    created: "{file_date}"

outstanding:
  tasks: []  # Populate from tasklist - pending/in_progress tasks
  remediation: []

reviews:
  last_qa_review: null
  last_code_review: null

evidence:
  quality_gates_run: ".claude/evidence/quality_gates_run.json"
  test_report: ".claude/evidence/test_report.json"
  test_failures: ".claude/evidence/test_failures.json"
```

### Step 6: Parse Outstanding Tasks

Read the tasklist and populate `outstanding.tasks` in manifest:

```python
# Pseudocode
for task in parse_tasklist(".claude/artifacts/003_tasklist_v1.md"):
    if task.status in ["pending", "in_progress"]:
        manifest.outstanding.tasks.append({
            "id": task.id,
            "status": task.status,
            "blocked_by": task.blocked_by or []
        })
```

### Step 7: Create Remediation Tasks File

Create `.claude/remediation/remediation_tasks.md`:

```markdown
# Remediation Tasks

Last updated: {timestamp}

## Critical / High Priority

| ID | Type | Summary | Source | Status |
|----|------|---------|--------|--------|
| - | - | No critical items | - | - |

## Medium Priority

| ID | Type | Summary | Source | Status |
|----|------|---------|--------|--------|
| - | - | No medium items | - | - |

## Low Priority

| ID | Type | Summary | Source | Status |
|----|------|---------|--------|--------|
| - | - | No low items | - | - |

## Resolved

| ID | Type | Summary | Resolved | Resolution |
|----|------|---------|----------|------------|
| - | - | No resolved items | - | - |
```

### Step 8: Update .gitignore (Optional)

Add to `.gitignore` if desired:

```gitignore
# Large coverage file
.claude/evidence/coverage.json
```

### Step 9: Verify Migration

```bash
# Check structure
tree .claude/

# Verify manifest
cat .claude/manifest.yaml

# Check artifacts exist
ls -la .claude/artifacts/

# Verify evidence
ls -la .claude/evidence/
```

### Step 10: Commit Migration

```bash
git add .claude/
git add -u  # Stage deletions of old files
git commit -m "Migrate project artifacts to .claude/ folder structure

- Move BA artifacts to .claude/artifacts/ with sequence numbers
- Move evolution logs to .claude/evolution/
- Move evidence to .claude/evidence/
- Create manifest.yaml for restart checkpoint
- Create remediation_tasks.md for QA/Code Review findings

Follows artifact convention v1.0"
```

## Automated Migration Script

Save as `migrate_to_claude_folder.sh`:

```bash
#!/bin/bash
set -e

PROJECT_SLUG="$1"
if [ -z "$PROJECT_SLUG" ]; then
    echo "Usage: $0 <project_slug>"
    exit 1
fi

echo "Migrating $PROJECT_SLUG to .claude/ structure..."

# Create folders
mkdir -p .claude/{artifacts,evolution,remediation,evidence}

# Move artifacts
[ -f "${PROJECT_SLUG}_spec.md" ] && mv "${PROJECT_SLUG}_spec.md" .claude/artifacts/002_spec_v1.md
[ -f "${PROJECT_SLUG}_tasklist.md" ] && mv "${PROJECT_SLUG}_tasklist.md" .claude/artifacts/003_tasklist_v1.md
[ -f "${PROJECT_SLUG}_rules.yaml" ] && mv "${PROJECT_SLUG}_rules.yaml" .claude/artifacts/004_rules_v1.yaml
[ -f "${PROJECT_SLUG}_quality_gates.md" ] && mv "${PROJECT_SLUG}_quality_gates.md" .claude/artifacts/005_quality_gates_v1.md
[ -f "${PROJECT_SLUG}_lessons_applied.md" ] && mv "${PROJECT_SLUG}_lessons_applied.md" .claude/artifacts/006_lessons_applied_v1.md
[ -f "${PROJECT_SLUG}_coding_agent_system_prompt.md" ] && mv "${PROJECT_SLUG}_coding_agent_system_prompt.md" .claude/artifacts/007_coding_prompt_v1.md

# Move evolution logs
[ -f "${PROJECT_SLUG}_evolution.md" ] && mv "${PROJECT_SLUG}_evolution.md" .claude/evolution/evolution.md
[ -f "${PROJECT_SLUG}_decisions.md" ] && mv "${PROJECT_SLUG}_decisions.md" .claude/evolution/decisions.md

# Move evidence
[ -f "artifacts/quality_gates_run.json" ] && mv artifacts/quality_gates_run.json .claude/evidence/
[ -f "artifacts/test_report.json" ] && mv artifacts/test_report.json .claude/evidence/
[ -f "artifacts/test_failures.json" ] && mv artifacts/test_failures.json .claude/evidence/
[ -f "artifacts/coverage.json" ] && mv artifacts/coverage.json .claude/evidence/

# Remove empty artifacts folder
rmdir artifacts 2>/dev/null || true

echo "Migration complete. Please create .claude/manifest.yaml manually."
echo "See: ~/.claude/docs/artifact_convention.md"
```

## Rollback

If migration fails, restore from git:

```bash
git checkout -- .
git clean -fd .claude/
```

## Post-Migration Checklist

- [ ] `.claude/manifest.yaml` created with correct versions
- [ ] All artifacts moved to `.claude/artifacts/` with sequence numbers
- [ ] Evolution logs moved to `.claude/evolution/`
- [ ] Evidence moved to `.claude/evidence/`
- [ ] `outstanding.tasks` populated from tasklist
- [ ] Old files at root removed
- [ ] Migration committed to git
- [ ] Team notified of new structure
