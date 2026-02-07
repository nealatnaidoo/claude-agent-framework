---
description: Review entire project for Prime Directive compliance and spec drift
allowed-tools: Bash(ls:*), Bash(find:*), Bash(grep:*), Bash(cat:*), Bash(head:*), Bash(git:*)
---

<review-project>

## Context Discovery

Project files in current directory:
!`ls -la *_spec.md *_tasklist.md *_quality_gates.md *_rules.yaml *_evolution.md *_decisions.md *_lessons_applied.md 2>/dev/null || echo "No BA artifacts found - checking for standard project structure..."`

Source structure:
!`ls -la src/ 2>/dev/null || ls -la . | head -20`

Evidence artifacts:
!`ls -la artifacts/ 2>/dev/null || echo "No artifacts/ directory found"`

Git status:
!`git status --short 2>/dev/null | head -20 || echo "Not a git repository"`

## Your Task

You are invoking a **Project Review** to verify Prime Directive compliance and detect spec drift.

### Step 1: Detect Project Context

Identify which project you're reviewing by finding:
- `{project}_spec.md` - The project specification
- `{project}_tasklist.md` - Task tracking
- Source code in `src/` or project root

If no BA artifacts found, identify the project from:
- `package.json` or `pyproject.toml` name field
- Directory name
- README.md project description

### Step 2: Ask Review Scope

Use AskUserQuestion to ask:

```
Question: "What type of review do you want?"
Options:
1. Quick governance check (Recommended) - Fast check of TDD, hexagonal, quality gates (~5-10 min)
2. Full comprehensive review - Deep verification including spec fidelity, task completion, bug docs (~30-60 min)
3. Focused review - Specify which aspects to check (determinism, hexagonal, etc.)
```

### Step 3: Run Appropriate Review

**For Quick Review:**
Use Task tool with `subagent_type: "qa-reviewer"`:

```
Review the entire project codebase for Prime Directive compliance.

Prime Directive: Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.

Check all source files for:
1. Task discipline - changes map to tasks, no scope creep
2. TDD compliance - tests exist for functionality
3. Hexagonal integrity - core doesn't import adapters/frameworks
4. Determinism - no datetime.now/random/uuid4 in core
5. Quality gates - evidence artifacts exist and pass

Project spec: {spec_file_if_found}
Tasklist: {tasklist_file_if_found}

Output findings to: artifacts/project_review_report.md
Include machine-readable summary: artifacts/project_review_summary.json
```

**For Full Review:**
1. First run qa-reviewer for governance check
2. Then run qa-reviewer again with deep verification prompt (code-review methodology):

```
Perform deep verification of the project against its specification.

After the quick governance review, now verify:
1. User story implementation - trace each story to working code
2. Acceptance criteria coverage - map ACs to tests that validate them
3. Spec fidelity - implementation matches specification exactly
4. Task completion - all "done" tasks are actually complete
5. Bug documentation - document any defects found with severity

Append deep findings to: artifacts/project_review_report.md
Update: artifacts/project_review_summary.json with completion data
```

**For Focused Review:**
Run qa-reviewer with specific focus areas based on user selection.

### Step 4: Write Artifacts

Ensure these files are created/updated:
- `artifacts/project_review_report.md` - Human-readable report
- `artifacts/project_review_summary.json` - Machine-readable summary

Create `artifacts/` directory if it doesn't exist.

### Step 5: Display Summary

After review completes, display a concise summary:

```
## Project Review Summary

**Project:** {name}
**Review Type:** Quick | Full
**Status:** PASS | PASS_WITH_NOTES | NEEDS_WORK | BLOCKED

### Prime Directive Compliance
- Task-Scoped: {status}
- Atomic: {status}
- Deterministic: {status}
- Hexagonal: {status}
- Evidenced: {status}

### Issues Found
- Critical: {count}
- Major: {count}
- Minor: {count}

### Top Issues (if any)
1. {most critical issue}
2. {second issue}
3. {third issue}

**Full report:** artifacts/project_review_report.md
```

## Reference

Full prompt template with customization options:
`~/.claude/commands/review-project.md`

Agent prompts:
- QA Reviewer: `~/.claude/agents/qa-reviewer.md`
- Code Review: `~/.claude/agents/code-review-agent.md`

</review-project>
