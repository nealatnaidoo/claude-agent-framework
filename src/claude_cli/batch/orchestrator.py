"""Batch orchestrator for parallel headless Claude instances.

Discovers items via glob, spawns `claude -p` processes with controlled
parallelism, and tracks completion via the ledger.
"""

from __future__ import annotations

import glob as globmod
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable

from claude_cli.batch.broker import sanitize_item_name
from claude_cli.batch.ledger import (
    get_resumable_items,
    load_ledger,
    reset_stale_active,
    update_item_status,
)


def discover_items(pattern: str, base_dir: Path | None = None) -> list[str]:
    """Glob-expand a pattern to find items.

    Args:
        pattern: Glob pattern (e.g., "src/**/*.py").
        base_dir: Base directory for the glob (defaults to cwd).

    Returns:
        Sorted list of matching file paths (relative to base_dir).
    """
    base = base_dir or Path.cwd()
    matches = sorted(globmod.glob(pattern, root_dir=str(base), recursive=True))
    return matches


def build_command(
    item: str,
    prompt_template: str,
    allowed_tools: list[str] | None = None,
    max_turns: int = 20,
    output_file: Path | None = None,
) -> list[str]:
    """Build the `claude -p` command for a single item.

    Args:
        item: Item path/name to substitute into the prompt template.
        prompt_template: Template with $item placeholder.
        allowed_tools: List of tools to pre-approve.
        max_turns: Maximum conversation turns.
        output_file: Path for JSON output (used for shell redirection, not in command).

    Returns:
        Command as list of strings for subprocess.Popen.
    """
    prompt = prompt_template.replace("$item", item)
    cmd = ["claude", "-p", prompt, "--output-format", "json"]

    if allowed_tools:
        cmd.extend(["--allowedTools", ",".join(allowed_tools)])

    cmd.extend(["--max-turns", str(max_turns)])

    return cmd


def find_claude_binary() -> str | None:
    """Check if the claude CLI is available on PATH."""
    return shutil.which("claude")


def run_batch(
    batch_dir: Path,
    parallel: int = 5,
    on_complete: Callable[[str, int], None] | None = None,
    poll_interval: float = 2.0,
) -> dict:
    """Spawn and manage parallel headless instances.

    Args:
        batch_dir: Batch directory containing ledger.yaml.
        parallel: Maximum concurrent processes.
        on_complete: Callback(item_name, exit_code) called per completion.
        poll_interval: Seconds between polling cycles.

    Returns:
        Final ledger summary dict.
    """
    ledger_path = batch_dir / "ledger.yaml"
    results_dir = batch_dir / "results"
    results_dir.mkdir(exist_ok=True)

    ledger = load_ledger(ledger_path)
    config = ledger.get("config", {})
    prompt_template = config.get("prompt_template", "")
    allowed_tools = config.get("allowed_tools")
    max_turns = config.get("max_turns", 20)

    # Get items to process
    pending = get_resumable_items(ledger_path)
    if not pending:
        return ledger.get("summary", {})

    # Active process pool: {item_name: (Popen, output_path)}
    active: dict[str, tuple[subprocess.Popen, Path]] = {}
    remaining = list(pending)

    while remaining or active:
        # Spawn new processes up to parallel limit
        while remaining and len(active) < parallel:
            item = remaining.pop(0)
            safe_name = sanitize_item_name(item)
            output_path = results_dir / f"{safe_name}.json"

            cmd = build_command(
                item, prompt_template, allowed_tools, max_turns, output_path
            )

            output_fh = open(output_path, "w")
            proc = subprocess.Popen(
                cmd,
                stdout=output_fh,
                stderr=subprocess.STDOUT,
                cwd=str(batch_dir.parent.parent.parent),  # project root
            )

            active[item] = (proc, output_path)
            update_item_status(ledger_path, item, "active", pid=proc.pid)

        # Poll for completions
        completed = []
        for item, (proc, output_path) in active.items():
            retcode = proc.poll()
            if retcode is not None:
                completed.append(item)
                status = "done" if retcode == 0 else "failed"
                summary = _extract_summary(output_path)

                update_item_status(
                    ledger_path,
                    item,
                    status,
                    result_summary=summary,
                    exit_code=retcode,
                )

                if on_complete:
                    on_complete(item, retcode)

        for item in completed:
            # Close the file handle
            proc, output_path = active.pop(item)
            # stdout file handle was already closed by Popen when process ended

        if active and not completed:
            time.sleep(poll_interval)

    return load_ledger(ledger_path).get("summary", {})


def resume_batch(
    batch_dir: Path,
    parallel: int = 5,
    on_complete: Callable[[str, int], None] | None = None,
) -> dict:
    """Resume a batch from its ledger, skipping completed items.

    Detects stale 'active' items (dead PIDs) and resets them to pending.

    Args:
        batch_dir: Batch directory containing ledger.yaml.
        parallel: Maximum concurrent processes.
        on_complete: Callback per item completion.

    Returns:
        Final ledger summary dict.
    """
    ledger_path = batch_dir / "ledger.yaml"

    # Reset stale active items
    reset_items = reset_stale_active(ledger_path)

    return run_batch(batch_dir, parallel, on_complete)


def _extract_summary(output_path: Path) -> str:
    """Extract a one-line summary from a result file.

    Tries to parse JSON and find a summary field, otherwise
    takes the first non-empty line of output.
    """
    if not output_path.exists():
        return "No output"

    try:
        import json
        data = json.loads(output_path.read_text())
        # Claude --output-format json wraps result
        if isinstance(data, dict):
            if "result" in data:
                result_text = str(data["result"])
                return result_text[:200] if len(result_text) > 200 else result_text
            if "content" in data:
                content = str(data["content"])
                return content[:200] if len(content) > 200 else content
    except (json.JSONDecodeError, OSError, KeyError):
        pass

    # Fallback: first non-empty line
    try:
        for line in output_path.read_text().splitlines():
            stripped = line.strip()
            if stripped:
                return stripped[:200]
    except OSError:
        pass

    return "No summary available"
