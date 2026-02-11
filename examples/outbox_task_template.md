---
# ============================================================
# OUTBOX TASK SPECIFICATION v1.0
# ============================================================
# Copy this template to {project}/.claude/outbox/pending/
# Filename: OBX-{NNN}_{type}_{YYYY-MM-DD}.md
# ============================================================
id: "OBX-XXX"                         # Replace XXX with next sequential ID
created: "YYYY-MM-DDTHH:MM:SSZ"       # ISO 8601 timestamp
project_slug: "your_project"          # From manifest.yaml
commissioner: "backend-coding-agent"   # Agent placing this task
task_type: "research"                  # research | data_gathering | analysis | validation
priority: "normal"                     # urgent | normal | low
status: "pending"                      # Always "pending" when creating

# DELIVERY CONTRACT
delivery:
  format: "yaml"                       # yaml | markdown | json_in_markdown
  target: ".claude/remediation/inbox/" # Standard delivery location
  target_filename: "OBX-XXX_external_research_YYYY-MM-DD.md"
  schema_ref: null                     # Optional: path to response schema
  max_items: null                      # null = unlimited, or integer cap

# CONSTRAINTS (NON-NEGOTIABLE — do not change these)
constraints:
  read_only: true
  no_code_changes: true
  no_manifest_updates: true
  scope: "external_research_only"
  timeout_hours: 24

# CONTEXT
context:
  project_description: "Brief description of the project"
  current_phase: "coding"              # From manifest.yaml
  relevant_files: []                   # Files the external agent MAY read for context
  additional_context: |
    Any extra context the external agent needs.
    This must be self-contained — the agent has no
    access to your conversation history.
---

# Task: [Descriptive Title Here]

## Objective

[2-5 sentences describing what needs to be accomplished and why. Be specific
about what you need — the external agent has no prior context about your project.]

## Specific Questions

1. [Concrete, answerable question]
2. [Concrete, answerable question]
3. [Concrete, answerable question]

## Expected Output Shape

Deliver results in this exact structure:

```yaml
research_results:
  query_summary: "one-line summary of what was researched"
  date_researched: "YYYY-MM-DD"
  items:
    - name: "item name"
      # Add fields appropriate to your task type.
      # Be explicit about every field you expect.
      # The external agent will fill this shape exactly.
  summary: "2-3 sentence overall summary"
  confidence: "high | medium | low"
  sources:
    - "https://source-url-1"
    - "https://source-url-2"
```

## What NOT To Do

- Do NOT modify any files in this repository
- Do NOT create pull requests or branches
- Do NOT install packages or run code
- Do NOT access files outside `.claude/outbox/` unless listed in `relevant_files`
- ONLY deliver your findings file to the specified target location
