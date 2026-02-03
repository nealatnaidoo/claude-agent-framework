# Document Consistency Guide

**Version**: 1.0
**Date**: 2026-01-31
**Purpose**: Canonical reference for document locations across all agents

---

## Core Principle: Manifest as Source of Truth

The `.claude/manifest.yaml` file is the **single source of truth** for:
- Current artifact versions and their file paths
- Project phase and workflow state
- Outstanding tasks and remediation items
- Review history

**All agents MUST read the manifest first** to get correct file paths.

---

## Folder Structure

```
{project}/
├── .claude/
│   ├── manifest.yaml                 # Source of truth (read first)
│   ├── artifacts/                    # Versioned BA artifacts
│   │   ├── 001_solution_envelope_v1.md
│   │   ├── 002_spec_v1.md
│   │   ├── 003_tasklist_v1.md
│   │   ├── 004_rules_v1.yaml
│   │   ├── 005_quality_gates_v1.md
│   │   ├── 006_lessons_applied_v1.md
│   │   └── 007_coding_prompt_v1.md
│   ├── evolution/                    # Append-only logs
│   │   ├── evolution.md
│   │   └── decisions.md
│   ├── remediation/                  # QA + Code Review findings
│   │   ├── qa_YYYY-MM-DD.md
│   │   ├── code_review_YYYY-MM-DD.md
│   │   ├── code_review_YYYY-MM-DD.json
│   │   └── remediation_tasks.md
│   └── evidence/                     # Quality gate outputs
│       ├── quality_gates_run.json
│       ├── test_report.json
│       ├── test_failures.json
│       ├── lint_report.json
│       └── coverage.json (optional)
└── src/
```

---

## Document Type Reference

### Versioned Artifacts (in `.claude/artifacts/`)

| Seq | Type | Naming Convention | Created By |
|-----|------|-------------------|------------|
| 001 | Solution Envelope | `001_solution_envelope_v{N}.md` | Solution Designer |
| 002 | Spec | `002_spec_v{N}.md` | BA Agent |
| 003 | Tasklist | `003_tasklist_v{N}.md` | BA Agent |
| 004 | Rules | `004_rules_v{N}.yaml` | BA Agent |
| 005 | Quality Gates | `005_quality_gates_v{N}.md` | BA Agent |
| 006 | Lessons Applied | `006_lessons_applied_v{N}.md` | Lessons Advisor |
| 007 | Coding Prompt | `007_coding_prompt_v{N}.md` | BA Agent |

**Versioning Rules:**
- NEVER overwrite existing artifacts
- Create new version: `v1` → `v2` → `v3`
- Update manifest with new version number
- Keep all versions for audit trail

**Multi-Variant Projects:**
For projects with multiple work streams, include variant in name:
- `002_spec_audience_growth_v1.md`
- `002_spec_newsletter_v1.md`

---

### Evolution Logs (in `.claude/evolution/`)

| File | Purpose | Modified By |
|------|---------|-------------|
| `evolution.md` | Drift entries, scope changes | Coding Agent (append) |
| `decisions.md` | Architectural decisions | BA Agent (append) |

**Rules:**
- Append-only (never edit existing entries)
- Each entry has unique ID (EV-XXXX, D-XXXX)
- Timestamps required

---

### Remediation Files (in `.claude/remediation/`)

| File | Purpose | Created By |
|------|---------|------------|
| `qa_YYYY-MM-DD.md` | QA review report | QA Reviewer |
| `code_review_YYYY-MM-DD.md` | Code review report | Code Review Agent |
| `code_review_YYYY-MM-DD.json` | Machine-readable summary | Code Review Agent |
| `remediation_tasks.md` | Consolidated bug/improve list | QA/Code Review (append) |

**ID Sequencing Rules:**
- IDs are project-global (not per-review)
- IDs are never reused (even for resolved items)
- Before creating new ID: search all remediation files for highest existing ID
- Increment from highest found

---

### Evidence Artifacts (in `.claude/evidence/`)

| File | Purpose | Created By |
|------|---------|------------|
| `quality_gates_run.json` | Gate execution results | Coding Agent |
| `test_report.json` | Test execution results | Coding Agent |
| `test_failures.json` | Failed tests (if any) | Coding Agent |
| `lint_report.json` | Linter output | Coding Agent |
| `coverage.json` | Code coverage (optional) | Coding Agent |

**Rules:**
- Updated after EVERY verification run (not just at task end)
- Timestamps must correlate with file edits
- QA/Code Review verify timestamps for checkpoint compliance

---

## Agent Document Flow

### What Each Agent Reads

| Agent | First Read | Then Read |
|-------|------------|-----------|
| Solution Designer | User input | Existing envelopes (if updating) |
| BA Agent | Solution envelope | Manifest, existing artifacts |
| Coding Agent | **Manifest** | Artifact paths from manifest |
| QA Reviewer | **Manifest** | Evidence, diff, artifact paths from manifest |
| Code Review Agent | **Manifest** | Evidence, spec, tasklist from manifest |
| Lessons Advisor | Project context | devlessons.md, existing 006 artifacts |

### What Each Agent Writes

| Agent | Creates | Updates |
|-------|---------|---------|
| Solution Designer | `001_solution_envelope_v{N}.md` | Manifest (phase, artifact version) |
| BA Agent | `002-007` artifacts | Manifest, evolution, decisions |
| Coding Agent | Source code, evidence files | Manifest, tasklist, evolution |
| QA Reviewer | `qa_YYYY-MM-DD.md` | Manifest (reviews), remediation_tasks.md |
| Code Review Agent | `code_review_YYYY-MM-DD.md/.json` | Manifest (reviews), remediation_tasks.md |
| Lessons Advisor | `006_lessons_applied_v{N}.md` | Manifest, devlessons.md (global) |

---

## Manifest Schema

```yaml
schema_version: "1.0"
project_slug: "{project}"
project_name: "{Project Name}"
created: "YYYY-MM-DDTHH:MM:SSZ"
last_updated: "YYYY-MM-DDTHH:MM:SSZ"
phase: "solution_design|ba|coding|qa|code_review|remediation|paused"
phase_started: "YYYY-MM-DDTHH:MM:SSZ"

# For multi-variant projects
variants:
  - slug: "variant_name"
    status: "active|paused|complete"

# Artifact paths - AGENTS READ THESE
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

# Review history
reviews:
  last_qa_review:
    date: "YYYY-MM-DDTHH:MM:SSZ"
    result: "PASS|PASS_WITH_NOTES|NEEDS_WORK|BLOCKED"
    report_file: ".claude/remediation/qa_YYYY-MM-DD.md"
  last_code_review:
    date: "YYYY-MM-DDTHH:MM:SSZ"
    result: "PASS|PASS_WITH_NOTES|NEEDS_WORK|BLOCKED"
    report_file: ".claude/remediation/code_review_YYYY-MM-DD.md"
    json_file: ".claude/remediation/code_review_YYYY-MM-DD.json"

# Outstanding work
outstanding:
  tasks:
    - id: "T001"
      status: "pending|in_progress|completed"
      variant: "variant_name"  # for multi-variant
  remediation:
    - id: "BUG-001"
      source: "qa_review|code_review"
      priority: "critical|high|medium|low"
      status: "pending|resolved|deferred"
      summary: "Brief description"
      file: "affected/path.py"
      created: "YYYY-MM-DD"
      resolved: "YYYY-MM-DD"  # if resolved
      resolution: "Description"  # if resolved
```

---

## Session Protocols

### Session Start (All Agents)

1. **Read Manifest First**
   ```
   .claude/manifest.yaml → Get artifact paths
   ```

2. **Check Outstanding Items**
   - `outstanding.remediation` → Handle critical/high items first
   - `outstanding.tasks` → Resume in-progress work

3. **Read Artifacts from Manifest Paths**
   - NOT from hardcoded filenames
   - Manifest tells you the current version

### Session End (Coding Agent)

1. **Update Tasklist** (path from manifest)
2. **Update Manifest**
   - `last_updated` timestamp
   - `outstanding.tasks` status
3. **Append to Evolution Log** (if drift detected)
4. **Verify Evidence Artifacts** exist in `.claude/evidence/`

### After Review (QA/Code Review)

1. **Create Dated Report** in `.claude/remediation/`
2. **Append to remediation_tasks.md** (don't overwrite)
3. **Update Manifest**
   - `reviews.last_*_review`
   - `outstanding.remediation` (new items)

---

## Migration from Legacy Naming

If you encounter projects with legacy naming (`{project}_spec.md` at root):

1. Run migration script or manually:
   ```bash
   mkdir -p .claude/{artifacts,evolution,remediation,evidence}
   mv {project}_spec.md .claude/artifacts/002_spec_v1.md
   mv {project}_tasklist.md .claude/artifacts/003_tasklist_v1.md
   # etc.
   ```

2. Create manifest with current artifact versions

3. Update any hardcoded references in project CLAUDE.md

See: `~/.claude/docs/artifact_convention.md` for full migration guide

---

## Checklist for New Agents

When creating or updating an agent prompt:

- [ ] Agent reads `.claude/manifest.yaml` FIRST
- [ ] Agent gets artifact paths FROM manifest (not hardcoded)
- [ ] Evidence paths use `.claude/evidence/` (not `artifacts/`)
- [ ] Agent updates manifest after completing work
- [ ] ID sequencing searches for highest existing ID
- [ ] Version control: new versions, never overwrite

---

## Quick Reference

| Need to find... | Look in... |
|-----------------|------------|
| Current spec path | `manifest.artifact_versions.spec.file` |
| Current tasklist path | `manifest.artifact_versions.tasklist.file` |
| Evidence files | `.claude/evidence/*.json` |
| Bug/improvement list | `.claude/remediation/remediation_tasks.md` |
| Drift history | `.claude/evolution/evolution.md` |
| Review reports | `.claude/remediation/qa_*.md` or `code_review_*.md` |
| Next BUG ID | Search `.claude/remediation/` for highest BUG-XXX |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-31 | Initial release - consolidating document locations |
