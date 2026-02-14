"""Results broker for batch processing.

Manages result file I/O, summary extraction, and report generation.
Sub-agents write full results to disk; the broker collects summaries
so the parent context only sees compact data.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from claude_cli.batch.ledger import load_ledger


def sanitize_item_name(item: str) -> str:
    """Convert item path to a safe filename (without extension).

    Examples:
        src/auth/service.py -> src_auth_service_py
        profiles/user.yaml -> profiles_user_yaml
    """
    return item.replace("/", "_").replace("\\", "_").replace(".", "_").rstrip("_")


def write_result(
    results_dir: Path,
    item_name: str,
    result: dict,
) -> Path:
    """Write a result JSON file to disk.

    Args:
        results_dir: Directory for result files.
        item_name: Original item path/name.
        result: Result data to write.

    Returns:
        Path to the written result file.
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    safe_name = sanitize_item_name(item_name)
    result_path = results_dir / f"{safe_name}.json"

    result_with_meta = {
        "schema_version": "1.0",
        "item": item_name,
        "written_at": datetime.now(timezone.utc).isoformat(),
        **result,
    }

    result_path.write_text(json.dumps(result_with_meta, indent=2, default=str))
    return result_path


def read_result(results_dir: Path, item_name: str) -> dict | None:
    """Read a single result file.

    Args:
        results_dir: Directory containing result files.
        item_name: Original item path/name.

    Returns:
        Parsed result dict, or None if file doesn't exist.
    """
    safe_name = sanitize_item_name(item_name)
    result_path = results_dir / f"{safe_name}.json"

    if not result_path.exists():
        return None

    try:
        return json.loads(result_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def collect_summaries(results_dir: Path) -> list[dict]:
    """Read all result files and extract compact summaries.

    Returns a list of dicts with: item, summary, exit_code, completed_at.
    This is what the parent context should read instead of full results.
    """
    summaries = []
    if not results_dir.exists():
        return summaries

    for result_file in sorted(results_dir.glob("*.json")):
        try:
            data = json.loads(result_file.read_text())
            summaries.append({
                "item": data.get("item", result_file.stem),
                "summary": data.get("summary", "No summary"),
                "exit_code": data.get("exit_code"),
                "completed_at": data.get("completed_at"),
            })
        except (json.JSONDecodeError, OSError):
            summaries.append({
                "item": result_file.stem,
                "summary": "Error reading result file",
                "exit_code": None,
                "completed_at": None,
            })

    return summaries


def generate_report(batch_dir: Path) -> str:
    """Produce a markdown summary report from ledger + results.

    Args:
        batch_dir: Root directory of the batch (contains ledger.yaml and results/).

    Returns:
        Markdown-formatted report string.
    """
    ledger_path = batch_dir / "ledger.yaml"
    results_dir = batch_dir / "results"

    ledger = load_ledger(ledger_path)
    config = ledger.get("config", {})
    summary = ledger.get("summary", {})
    items = ledger.get("items", [])

    lines = [
        f"# Batch Report: {ledger.get('batch_id', 'unknown')}",
        "",
        f"**Created**: {ledger.get('created_at', 'unknown')}",
        f"**Updated**: {ledger.get('updated_at', 'unknown')}",
        f"**Pattern**: `{config.get('pattern', 'N/A')}`",
        f"**Parallel**: {config.get('parallel', 'N/A')}",
        "",
        "## Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| Total | {summary.get('total', 0)} |",
        f"| Done | {summary.get('done', 0)} |",
        f"| Failed | {summary.get('failed', 0)} |",
        f"| Pending | {summary.get('pending', 0)} |",
        f"| Active | {summary.get('active', 0)} |",
        "",
    ]

    # Done items
    done_items = [i for i in items if i.get("status") == "done"]
    if done_items:
        lines.append("## Completed Items")
        lines.append("")
        for item in done_items:
            lines.append(f"- **{item['name']}**: {item.get('summary', 'No summary')}")
        lines.append("")

    # Failed items
    failed_items = [i for i in items if i.get("status") == "failed"]
    if failed_items:
        lines.append("## Failed Items")
        lines.append("")
        for item in failed_items:
            lines.append(f"- **{item['name']}**: {item.get('summary', 'Unknown error')}")
        lines.append("")

    # Pending items (not yet processed)
    pending_items = [i for i in items if i.get("status") in ("pending", "active")]
    if pending_items:
        lines.append("## Remaining Items")
        lines.append("")
        for item in pending_items:
            lines.append(f"- {item['name']} ({item.get('status', 'pending')})")
        lines.append("")

    return "\n".join(lines)
