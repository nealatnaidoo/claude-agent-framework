"""CLI subcommands for agent metrics."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from claude_cli.common.config import get_db_path
from claude_cli.metrics.collector import (
    aggregate_metrics,
    collect_from_batch_ledgers,
    collect_from_evidence,
    load_metrics_history,
    store_metrics,
)

app = typer.Typer(help="Agent performance metrics")
console = Console()


@app.command("collect")
def collect(
    base_dir: Path = typer.Option(
        None, "--base-dir", "-b", help="Base directory to scan for projects"
    ),
) -> None:
    """Scan projects and collect agent run metrics."""
    if base_dir is None:
        base_dir = Path.home() / "Developer"

    if not base_dir.exists():
        console.print(f"[red]Directory not found:[/red] {base_dir}")
        raise typer.Exit(code=1)

    runs = collect_from_batch_ledgers(base_dir)

    # Also collect from evidence files in discovered projects
    for manifest in sorted(base_dir.glob("*/.claude/manifest.yaml")):
        project_root = manifest.parent.parent
        runs.extend(collect_from_evidence(project_root))

    if not runs:
        console.print("[yellow]No agent runs found.[/yellow]")
        return

    report = aggregate_metrics(runs)
    db_path = get_db_path("metrics.duckdb")
    store_metrics(report, db_path)

    projects_count = len(report.by_project)
    console.print(f"[green]Collected {len(runs)} runs from {projects_count} projects.[/green]")
    console.print(f"[dim]Stored in {db_path}[/dim]")


@app.command("report")
def report(
    days: int = typer.Option(30, "--days", "-d", help="Number of recent reports to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Show aggregated metrics report."""
    db_path = get_db_path("metrics.duckdb")
    history = load_metrics_history(db_path, days=days)

    if not history:
        console.print("[yellow]No metrics history found. Run 'caf metrics collect' first.[/yellow]")
        return

    latest = history[0]
    if json_output:
        console.print(latest.to_json())
    else:
        console.print(latest.to_markdown())


@app.command("dashboard")
def dashboard() -> None:
    """Show one-line summary stats."""
    db_path = get_db_path("metrics.duckdb")
    history = load_metrics_history(db_path, days=1)

    if not history:
        console.print("[yellow]No metrics data. Run 'caf metrics collect' first.[/yellow]")
        return

    latest = history[0]
    agents = len(latest.by_agent)
    projects = len(latest.by_project)

    avg_success = 0.0
    if latest.by_agent:
        avg_success = sum(s.success_rate for s in latest.by_agent.values()) / agents

    console.print(
        f"[bold]Metrics:[/bold] {latest.total_runs} runs | "
        f"{agents} agent types | {projects} projects | "
        f"{avg_success:.0%} avg success"
    )
