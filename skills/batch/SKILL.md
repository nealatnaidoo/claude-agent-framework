---
name: batch
description: "Run parallel headless batch jobs with ledger tracking and resume"
user_invocable: true
---

# /batch — Parallel Headless Batch Processor

You are executing the `/batch` skill. This processes multiple items in parallel using headless Claude instances, with a YAML ledger for tracking and resume.

## Step 1: Parse Arguments

Extract from the user's command:
- `--items` (required): Glob pattern for items (e.g., `"src/**/*.py"`, `"profiles/*.yaml"`)
- `--prompt` (required): Prompt template with `$item` placeholder
- `--parallel` (optional, default 5): Max concurrent processes
- `--max-turns` (optional, default 20): Max turns per item
- `--allowed-tools` (optional): Comma-separated tool list for headless instances
- `--resume` (optional flag): Resume an existing batch instead of starting new

If arguments are unclear, ask the user to clarify.

## Step 2: Validate Prerequisites

```bash
which claude  # Verify claude CLI is available
```

If `claude` is not on PATH, inform the user and stop.

Expand the glob pattern to verify items exist:
```bash
cd <project_root> && python3 -c "
import glob
items = sorted(glob.glob('PATTERN', recursive=True))
print(f'{len(items)} items found')
for i in items[:10]:
    print(f'  {i}')
if len(items) > 10:
    print(f'  ... and {len(items) - 10} more')
"
```

If no items match, report and stop.

## Step 3: Initialize Batch

Run the batch init command:
```bash
cd <project_root> && caf batch init \
  --pattern "PATTERN" \
  --prompt "PROMPT_TEMPLATE" \
  --parallel N \
  --max-turns M \
  --allowed-tools "TOOLS"
```

Note the batch ID from the output.

## Step 4: Execute Batch

Run the batch:
```bash
cd <project_root> && caf batch run \
  --batch-id BATCH_ID
```

Monitor progress periodically:
```bash
cd <project_root> && caf batch status \
  --batch-id BATCH_ID
```

## Step 5: Report Results

When complete, generate the report:
```bash
cd <project_root> && caf batch report \
  --batch-id BATCH_ID
```

Display the summary to the user. Highlight:
- Total items processed
- Success/failure counts
- Any failed items that may need retry

## Step 6: Resume (if applicable)

If `--resume` was specified or there are failed items the user wants to retry:
```bash
cd <project_root> && caf batch run \
  --batch-id BATCH_ID \
  --resume
```

## Rules

- **NEVER** read full result files into your context — use summaries only via `status` and `report`
- **NEVER** spawn more than `--parallel` concurrent instances
- Always use the ledger to track state — do not try to manage batch state in your context
- On interrupt or error, the ledger reflects the accurate state for resume
- The batch directory is at `{project}/.claude/batch/{batch_id}/`
- Results are at `{project}/.claude/batch/{batch_id}/results/`
- The ledger is at `{project}/.claude/batch/{batch_id}/ledger.yaml`

## Example Usage

```
/batch --items "src/**/*.py" --prompt "Review $item for security vulnerabilities" --parallel 3
/batch --items "profiles/*.yaml" --prompt "Enrich $item with registry data" --parallel 10 --max-turns 30
/batch --resume --batch-id batch-20260214-143022
```
