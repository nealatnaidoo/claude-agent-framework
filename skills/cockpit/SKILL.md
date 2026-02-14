---
name: cockpit
description: "Generate an interactive HTML dashboard for a governed project"
user_invocable: true
---

# /cockpit — Project Dashboard Generator

You are executing the `/cockpit` skill. Generate a self-contained HTML dashboard for the current project.

## Step 1: Locate Project

Find the project root by looking for `.claude/manifest.yaml` in the current directory or parent directories.

If no manifest found: report error and stop.

## Step 2: Gather Data

Read the following sources and collect data into a JSON object:

### From `.claude/manifest.yaml`
- `project_slug`, `project_name`
- `phase`, `phase_started`
- `last_updated`
- `outstanding.tasks[]` — count by status (pending, in_progress, completed, blocked)
- `outstanding.remediation[]` — count and severity breakdown
- `artifact_versions` — list with version numbers

### From `.claude/evidence/quality_gates_run.json` (if exists)
- Latest pass/fail result
- Timestamp
- Gate details

### From `.claude/remediation/inbox/` (if exists)
- Count of outstanding findings
- Severity breakdown

### From `.claude/outbox/` (if exists)
- Count files in `pending/`, `active/`, `completed/`, `rejected/`

### From `git log`
```bash
git log --oneline -20 --format="%h|%s|%ai"
```

## Step 3: Generate HTML

Run the cockpit generator:

```bash
cd <project_root> && python3 -m claude_cli.cockpit.generator
```

If the generator module is not available, construct the HTML inline using the template below.

### HTML Template Structure

Create a self-contained HTML file with:
- Dark theme (background: #0f172a, cards: #1e293b, accent: #3b82f6)
- No external dependencies (inline CSS, inline JS)
- Data embedded as `const COCKPIT_DATA = {...}` in a script tag

### Sections

1. **Header Bar**: Project name, phase badge (color-coded by phase), generated timestamp
2. **Task Progress**: Horizontal stacked bar chart showing pending/in-progress/completed/blocked counts
3. **Quality Gates**: Latest pass/fail with timestamp and gate details
4. **Remediation**: Outstanding BUG/IMPROVE items with severity badges (critical=red, high=orange, medium=yellow, low=blue)
5. **Agent Activity**: Outbox summary table (pending/active/completed/rejected counts)
6. **Recent Commits**: Last 10-20 commits as a compact monospace list
7. **Artifact Versions**: Table of artifact types and their current versions

### Phase Badge Colors

| Phase | Color |
|-------|-------|
| initialized | #6b7280 (gray) |
| solution_design | #8b5cf6 (purple) |
| ba | #f59e0b (amber) |
| coding | #3b82f6 (blue) |
| qa | #10b981 (green) |
| code_review | #06b6d4 (cyan) |
| complete | #22c55e (green) |
| paused | #ef4444 (red) |

## Step 4: Save and Open

Save the HTML to `.claude/cockpit.html` in the project root.

Report the file path and offer to open it:
```bash
open .claude/cockpit.html  # macOS
```

## Rules

- Output MUST be a single self-contained HTML file
- No external CDN links or dependencies
- Dark theme only (executive dashboard aesthetic)
- All data embedded as JSON in script tag
- Gracefully handle missing data sources (show "No data" instead of crashing)
