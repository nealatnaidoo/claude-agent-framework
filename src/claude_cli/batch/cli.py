"""CLI subcommands for batch processing."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Batch processing with parallel headless agents")
console = Console()


def _find_project_root() -> Path | None:
    """Walk up from cwd to find .claude/manifest.yaml."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude" / "manifest.yaml").exists():
            return parent
        if parent == Path.home():
            break
    return None


def _get_batch_dir(project_root: Path, batch_id: str) -> Path:
    """Get the batch directory for a given batch ID."""
    return project_root / ".claude" / "batch" / batch_id


@app.command("init")
def init_batch(
    pattern: str = typer.Option(..., "--pattern", "-p", help="Glob pattern for items"),
    prompt: str = typer.Option(..., "--prompt", help="Prompt template ($item placeholder)"),
    parallel: int = typer.Option(5, "--parallel", "-n", help="Max parallel processes"),
    max_turns: int = typer.Option(20, "--max-turns", help="Max turns per item"),
    allowed_tools: Optional[str] = typer.Option(
        None, "--allowed-tools", help="Comma-separated tool list"
    ),
) -> None:
    """Initialize a new batch from a glob pattern and prompt template."""
    from claude_cli.batch.ledger import create_ledger, generate_batch_id
    from claude_cli.batch.orchestrator import discover_items

    project_root = _find_project_root()
    if project_root is None:
        console.print("[red]No .claude/manifest.yaml found in parent directories[/red]")
        raise typer.Exit(1)

    items = discover_items(pattern, project_root)
    if not items:
        console.print(f"[yellow]No items match pattern: {pattern}[/yellow]")
        raise typer.Exit(1)

    batch_id = generate_batch_id()
    batch_dir = _get_batch_dir(project_root, batch_id)

    tools = [t.strip() for t in allowed_tools.split(",")] if allowed_tools else []

    config = {
        "pattern": pattern,
        "parallel": parallel,
        "max_turns": max_turns,
        "allowed_tools": tools,
    }

    ledger_path = create_ledger(batch_id, items, prompt, config, batch_dir)

    console.print(f"\n[green]Batch initialized:[/green] {batch_id}")
    console.print(f"  Items: {len(items)}")
    console.print(f"  Parallel: {parallel}")
    console.print(f"  Ledger: {ledger_path}")
    console.print(f"\nRun with: [bold]caf batch run --batch-id {batch_id}[/bold]\n")


@app.command("run")
def run(
    batch_id: str = typer.Option(..., "--batch-id", "-b", help="Batch ID to run"),
    parallel: Optional[int] = typer.Option(None, "--parallel", "-n", help="Override parallel limit"),
    resume: bool = typer.Option(False, "--resume", "-r", help="Resume from ledger state"),
) -> None:
    """Execute (or resume) a batch of headless jobs."""
    from claude_cli.batch.orchestrator import find_claude_binary, resume_batch, run_batch

    project_root = _find_project_root()
    if project_root is None:
        console.print("[red]No project root found[/red]")
        raise typer.Exit(1)

    batch_dir = _get_batch_dir(project_root, batch_id)
    ledger_path = batch_dir / "ledger.yaml"

    if not ledger_path.exists():
        console.print(f"[red]Batch not found: {batch_id}[/red]")
        raise typer.Exit(1)

    if not find_claude_binary():
        console.print("[red]claude CLI not found on PATH[/red]")
        raise typer.Exit(1)

    # Read parallel from ledger config if not overridden
    if parallel is None:
        from claude_cli.batch.ledger import load_ledger
        ledger = load_ledger(ledger_path)
        parallel = ledger.get("config", {}).get("parallel", 5)

    def on_complete(item: str, exit_code: int) -> None:
        status_icon = "[green]done[/green]" if exit_code == 0 else "[red]FAIL[/red]"
        console.print(f"  {status_icon} {item}")

    console.print(f"\n[bold]Running batch: {batch_id}[/bold] (parallel={parallel})")

    if resume:
        summary = resume_batch(batch_dir, parallel, on_complete)
    else:
        summary = run_batch(batch_dir, parallel, on_complete)

    console.print(f"\n[bold]Complete:[/bold] {summary.get('done', 0)} done, "
                  f"{summary.get('failed', 0)} failed, "
                  f"{summary.get('pending', 0)} pending\n")


@app.command("status")
def status(
    batch_id: str = typer.Option(..., "--batch-id", "-b", help="Batch ID to check"),
) -> None:
    """Show current ledger status for a batch."""
    from claude_cli.batch.ledger import get_ledger_summary, load_ledger

    project_root = _find_project_root()
    if project_root is None:
        console.print("[red]No project root found[/red]")
        raise typer.Exit(1)

    batch_dir = _get_batch_dir(project_root, batch_id)
    ledger_path = batch_dir / "ledger.yaml"

    if not ledger_path.exists():
        console.print(f"[red]Batch not found: {batch_id}[/red]")
        raise typer.Exit(1)

    ledger = load_ledger(ledger_path)
    summary = ledger.get("summary", {})

    console.print(f"\n[bold]Batch: {batch_id}[/bold]")
    console.print(f"Created: {ledger.get('created_at', 'unknown')}")
    console.print(f"Updated: {ledger.get('updated_at', 'unknown')}")
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Status")
    table.add_column("Count", justify="right")

    for key in ("total", "done", "failed", "active", "pending"):
        style = {"done": "green", "failed": "red", "active": "blue"}.get(key, "")
        table.add_row(key.capitalize(), str(summary.get(key, 0)), style=style)

    console.print(table)

    # Show individual items
    items = ledger.get("items", [])
    if items:
        console.print()
        item_table = Table(show_header=True, header_style="bold")
        item_table.add_column("Item")
        item_table.add_column("Status")
        item_table.add_column("Summary")

        for item in items:
            status_style = {
                "done": "green", "failed": "red",
                "active": "blue", "pending": "dim",
            }.get(item.get("status", ""), "")
            item_table.add_row(
                item["name"],
                item.get("status", "unknown"),
                item.get("summary", "") or "",
                style=status_style,
            )

        console.print(item_table)
    console.print()


@app.command("report")
def report(
    batch_id: str = typer.Option(..., "--batch-id", "-b", help="Batch ID to report on"),
) -> None:
    """Generate a summary report for a batch."""
    from claude_cli.batch.broker import generate_report

    project_root = _find_project_root()
    if project_root is None:
        console.print("[red]No project root found[/red]")
        raise typer.Exit(1)

    batch_dir = _get_batch_dir(project_root, batch_id)
    if not (batch_dir / "ledger.yaml").exists():
        console.print(f"[red]Batch not found: {batch_id}[/red]")
        raise typer.Exit(1)

    report_text = generate_report(batch_dir)
    console.print(report_text)

    # Also write to file
    report_path = batch_dir / "report.md"
    report_path.write_text(report_text)
    console.print(f"\n[dim]Report saved to: {report_path}[/dim]\n")
