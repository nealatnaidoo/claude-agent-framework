"""Batch processing with parallel headless agents.

Provides ledger-tracked batch execution where each item is processed
by an independent headless Claude instance. Results are written to disk
(not parent context) to prevent context window overflow.
"""

from claude_cli.batch.broker import (
    collect_summaries,
    generate_report,
    read_result,
    sanitize_item_name,
    write_result,
)
from claude_cli.batch.ledger import (
    create_ledger,
    generate_batch_id,
    get_ledger_summary,
    get_resumable_items,
    load_ledger,
    reset_stale_active,
    update_item_status,
)

__all__ = [
    "collect_summaries",
    "create_ledger",
    "generate_batch_id",
    "generate_report",
    "get_ledger_summary",
    "get_resumable_items",
    "load_ledger",
    "read_result",
    "reset_stale_active",
    "sanitize_item_name",
    "update_item_status",
    "write_result",
]
