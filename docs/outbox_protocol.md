# Outbox Protocol v1.0

**Version**: 1.0
**Date**: 2026-02-11
**Purpose**: Commission read-only research tasks to external agents (e.g., Google Antigravity / Gemini 3)

---

## Overview

The outbox protocol enables Claude Code agents to commission work to an external language model operating outside the Claude Code session. The external agent performs **read-only** tasks (research, data gathering, analysis, validation) and delivers structured results back through the existing remediation inbox.

```
Claude Code (commissioner)          External Agent (executor)
         │                                   │
         ├─── writes task ──▶ outbox/pending/ │
         │                                   │
         │                   ◀── reads task ──┤
         │                                   │
         │                   (performs research)
         │                                   │
         │  inbox/{ID}_{source}_{date}.md ◀──┤
         │  outbox/completed/{task}.md    ◀──┤
         │                                   │
         ├─── reads result ──────────────────┘
```

### Design Principles

1. **File-based, async** — No real-time connection; files are the protocol
2. **Self-contained tasks** — Each task file carries all context; no conversation history
3. **Strict read-only** — External agents MUST NOT modify source code, manifest, or project state
4. **Inbox convergence** — Results flow into the existing `remediation/inbox/` for BA triage
5. **Model-agnostic** — Any agent that reads Markdown + YAML frontmatter can participate

---

## Directory Structure

```
{project}/.claude/
  outbox/
    pending/                    # Tasks awaiting pickup by external agent
    active/                     # Currently being worked (claim lock)
    completed/                  # Finished tasks (audit trail)
    rejected/                   # Tasks the external agent could not fulfil
```

All four subdirectories MUST exist. The `init` agent creates them during scaffold.

---

## Task Specification Format

### Filename Convention

```
OBX-{NNN}_{type}_{YYYY-MM-DD}.md
```

- `OBX-NNN`: Sequential ID, project-global, never reused
- `type`: One of `research`, `data_gathering`, `analysis`, `validation`
- `YYYY-MM-DD`: Creation date

Examples:
- `OBX-001_research_2026-02-11.md`
- `OBX-002_data_gathering_2026-02-11.md`
- `OBX-003_validation_2026-02-12.md`

### YAML Frontmatter (Required)

```yaml
---
# ============================================================
# OUTBOX TASK SPECIFICATION v1.0
# ============================================================
id: "OBX-001"
created: "2026-02-11T14:30:00Z"
project_slug: "risk_engine"
commissioner: "back"
task_type: "research"
priority: "normal"
status: "pending"

# DELIVERY CONTRACT
delivery:
  format: "yaml"
  target: ".claude/remediation/inbox/"
  target_filename: "OBX-001_external_research_2026-02-11.md"
  schema_ref: null
  max_items: null

# CONSTRAINTS (NON-NEGOTIABLE)
constraints:
  read_only: true
  no_code_changes: true
  no_manifest_updates: true
  scope: "external_research_only"
  timeout_hours: 24

# CONTEXT
context:
  project_description: "Brief project description for external agent"
  current_phase: "coding"
  relevant_files: []
  additional_context: |
    Any extra context the external agent needs to understand
    the request. This should be self-contained.
---
```

### Field Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `id` | Yes | string | `OBX-NNN` format, sequential |
| `created` | Yes | datetime | ISO 8601 timestamp |
| `project_slug` | Yes | string | Project identifier |
| `commissioner` | Yes | string | Agent that created the task |
| `task_type` | Yes | enum | `research`, `data_gathering`, `analysis`, `validation` |
| `priority` | Yes | enum | `urgent`, `normal`, `low` |
| `status` | Yes | enum | `pending`, `active`, `completed`, `rejected`, `expired` |
| `delivery.format` | Yes | enum | `yaml`, `markdown`, `json_in_markdown` |
| `delivery.target` | Yes | string | Directory path for result delivery |
| `delivery.target_filename` | Yes | string | Exact filename for delivery |
| `delivery.schema_ref` | No | string | Path to expected response shape |
| `delivery.max_items` | No | int/null | Cap on result items (null = unlimited) |
| `constraints.read_only` | Yes | boolean | Must be `true` |
| `constraints.no_code_changes` | Yes | boolean | Must be `true` |
| `constraints.no_manifest_updates` | Yes | boolean | Must be `true` |
| `constraints.scope` | Yes | string | Scope boundary descriptor |
| `constraints.timeout_hours` | Yes | integer | Auto-expire threshold |
| `context.project_description` | Yes | string | One-line project description |
| `context.current_phase` | No | string | Current manifest phase |
| `context.relevant_files` | No | array | Files the external agent MAY read |
| `context.additional_context` | No | string | Free-form context block |

### Task Body (Markdown)

Below the frontmatter, the task body MUST contain:

1. **Title** — `# Task: {descriptive title}`
2. **Objective** — What needs to be accomplished (2-5 sentences)
3. **Specific Questions** — Numbered list of concrete questions to answer
4. **Expected Output Shape** — Exact YAML/Markdown/JSON structure in a code fence
5. **What NOT To Do** — Explicit prohibitions

```markdown
# Task: {Descriptive Title}

## Objective

{2-5 sentences describing what needs to be accomplished and why}

## Specific Questions

1. {Concrete question 1}
2. {Concrete question 2}
3. {Concrete question 3}

## Expected Output Shape

Deliver results in this exact structure:

```yaml
research_results:
  query_summary: "string"
  date_researched: "YYYY-MM-DD"
  items:
    - name: "string"
      # ... shape definition ...
  summary: "string"
  confidence: "high | medium | low"
  sources:
    - "url"
```

## What NOT To Do

- Do NOT modify any files in this repository
- Do NOT create pull requests or branches
- Do NOT install packages or run code
- Do NOT access files outside `.claude/outbox/`
- ONLY deliver your findings file to the specified target location
```

---

## Task Types

### research

Web-based research to answer questions, compare options, or gather information.

**Typical use**: Library comparison, vendor evaluation, API documentation lookup, market research.

**Delivery format**: Usually `yaml` (structured list) or `markdown` (prose report).

### data_gathering

Collect specific data points from known sources.

**Typical use**: Company lists, pricing data, feature matrices, compatibility tables.

**Delivery format**: Usually `yaml` (structured data) or `json_in_markdown`.

### analysis

Analyze provided information and produce insights.

**Typical use**: Risk assessment of a technology choice, trade-off analysis, gap analysis.

**Delivery format**: Usually `markdown` (analytical report with recommendations).

### validation

Verify claims, check facts, or validate assumptions.

**Typical use**: "Is this library still maintained?", "Does this API support X?", "Are these companies real?"

**Delivery format**: Usually `yaml` (pass/fail per item with evidence).

---

## Delivery Protocol

### Result File Format

The external agent delivers results to `delivery.target` + `delivery.target_filename`. The file MUST use the standard inbox envelope format:

```yaml
---
id: "{OBX-NNN}"
source: "external_research"
severity: "low"
created: "{ISO timestamp}"
context: "{task objective — one line}"
commissioned_by: "{commissioner from task}"
task_type: "{task_type from task}"
delivery_format: "{format from task}"
---
```

Below the frontmatter, include the research results in EXACTLY the format specified in the task's "Expected Output Shape" section.

### Completion Annotation

When the external agent completes a task, it moves the task file from `active/` to `completed/` and appends:

```yaml
# COMPLETION
completed_at: "{ISO timestamp}"
delivery_file: "{path to delivered file}"
items_returned: {count}
executor: "antigravity/gemini-3"
```

### Rejection Protocol

If the external agent cannot fulfil a task:

1. Move task file from `pending/` (or `active/`) to `rejected/`
2. Update `status: "rejected"`
3. Append rejection reason:

```yaml
# REJECTION
rejected_at: "{ISO timestamp}"
rejection_reason: "{clear explanation of why task cannot be fulfilled}"
executor: "antigravity/gemini-3"
```

---

## Expiry Protocol

Tasks with `constraints.timeout_hours` that remain in `pending/` past their timeout are considered expired. On next outbox scan:

1. Check `created` + `timeout_hours` against current time
2. If expired, move to `rejected/` with `status: "expired"`
3. Append: `rejection_reason: "Task expired after {N} hours without pickup"`

---

## ID Sequencing

Outbox IDs follow the same project-global, never-reused pattern as BUG/IMPROVE IDs.

- Format: `OBX-NNN` (zero-padded to 3 digits)
- Tracked in manifest: `outbox.next_id`
- Discovery fallback: scan `outbox/` subdirectories for highest ID

---

## Who Can Commission Tasks

| Agent | Can Commission | Typical Task Types |
|-------|---------------|-------------------|
| `back` | Yes | research, validation |
| `front` | Yes | research, validation |
| `design` | Yes | research, analysis |
| `ba` | Yes | data_gathering, research |
| `qa` | No | — |
| `review` | No | — |
| `ops` | Yes | validation, analysis |

QA and Code Review agents do not commission outbox tasks — they operate on existing project state only.

---

## How Claude Code Consumes Results

Results land in `remediation/inbox/` using the existing envelope format with `source: "external_research"`.

### BA Triage Rules for External Research

The BA agent handles external research results differently from bug/improvement findings:

| Finding Type | BA Action |
|-------------|-----------|
| Research data | Incorporate into context, archive as `"context_incorporated"` |
| Data gathering | Attach to relevant task, archive with task reference |
| Analysis report | Feed into solution design, archive as `"analysis_consumed"` |
| Validation result | Update assumptions, archive with validation outcome |

### Archive Annotation for Outbox Results

```yaml
---
# ... original frontmatter preserved ...
resolved_as: "context_incorporated"    # or task ID if directly actionable
picked_up: "2026-02-12T09:00:00Z"
tasklist_version: "003_tasklist_v3.md"
triage_decision: "Research data incorporated into T005 context"
source_outbox_id: "OBX-001"           # Cross-link back to outbox task
---
```

---

## Manifest Integration

See `schemas/project_manifest.schema.yaml` (v1.4) for the full schema. Summary:

```yaml
outbox:
  next_id: 2
  pending:
    - id: "OBX-001"
      task_type: "research"
      status: "completed"
      commissioner: "back"
      created: "2026-02-11T14:30:00Z"
      completed: "2026-02-11T16:00:00Z"
      delivery_file: ".claude/remediation/inbox/OBX-001_external_research_2026-02-11.md"
```

---

## Security Considerations

1. **No code execution** — External agents must never run code in the project
2. **No manifest mutation** — Only Claude Code agents update the manifest
3. **Scoped file access** — External agents should only read files listed in `context.relevant_files`
4. **Result validation** — BA agent should sanity-check delivered data before incorporating
5. **No secrets in tasks** — Never include API keys, credentials, or PII in outbox tasks
6. **Timeout enforcement** — Expired tasks prevent stale work from being delivered late

---

## External Agent Setup

### Google Antigravity

See `examples/antigravity-skill/outbox-poller/SKILL.md` for the complete skill definition.

Setup:
1. Copy `examples/antigravity-skill/outbox-poller/` to `{project}/.agent/skills/outbox-poller/`
2. Open the project in Google Antigravity
3. Say "check outbox" or "poll for tasks"

### Other Agents

Any language model with file read/write access can participate. Requirements:
- Ability to read Markdown files with YAML frontmatter
- Ability to write Markdown files with YAML frontmatter
- Web search capability (for research tasks)
- Understanding of the delivery contract

Provide the agent with `docs/outbox_protocol.md` as system context.
