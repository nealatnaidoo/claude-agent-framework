"""CLI commands for version tracking."""

from datetime import datetime, timezone

import typer
from rich.console import Console
from rich.table import Table

from claude_cli.versioning.tracker import (
    load_history,
    save_history,
    scan_changes,
    apply_changes,
    get_state_at,
    get_current_components,
    get_history_file,
)

app = typer.Typer(help="Bi-temporal version tracking")
console = Console()


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime."""
    if date_str.lower() == "now":
        return datetime.now(timezone.utc)
    for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {date_str}. Expected: YYYY-MM-DD")


@app.command("init")
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Reinitialize even if history exists"),
) -> None:
    """Initialize version tracking with current state."""
    history = load_history()

    if history["records"] and not force:
        console.print("[yellow]History already exists. Use --force to reinitialize.[/yellow]")
        raise typer.Exit(1)

    if force:
        history = {"schema_version": "1.0", "records": [], "snapshots": []}

    current = get_current_components()
    now = datetime.now(timezone.utc).isoformat()

    for file_path, component in current.items():
        history["records"].append({
            **component,
            "version": "1.0.0",
            "valid_from": now,
            "valid_to": None,
            "recorded_at": now,
            "change_type": "initial",
            "change_summary": "Initial tracking",
        })

    save_history(history)
    console.print(f"[green]Initialized tracking for {len(current)} components.[/green]")
    console.print(f"History saved to: {get_history_file()}")


@app.command("scan")
def scan(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show changes without recording"),
) -> None:
    """Scan for changes and record them."""
    history = load_history()
    changes = scan_changes(history)

    if not changes:
        console.print("[dim]No changes detected.[/dim]")
        return

    new_records = [c for c in changes if c.get("action") != "close"]

    console.print(f"\n[bold]Detected {len(new_records)} change(s):[/bold]\n")
    for change in new_records:
        symbol = {"initial": "+", "modified": "~", "deleted": "-"}.get(change["change_type"], "?")
        color = {"initial": "green", "modified": "yellow", "deleted": "red"}.get(change["change_type"], "white")
        console.print(f"  [{color}][{symbol}] {change['component_type']}/{change['component_name']}[/{color}]")
        console.print(f"      [dim]{change['change_summary']}[/dim]")

    if not dry_run:
        applied = apply_changes(history, changes)
        save_history(history)
        console.print(f"\n[green]Recorded {applied} change(s)[/green]")
    else:
        console.print("\n[dim](dry-run mode - no changes saved)[/dim]")


@app.command("history")
def show_history(
    component_type: str = typer.Option(None, "--type", "-t", help="Filter by component type"),
) -> None:
    """Show version history."""
    history = load_history()

    if not history["records"]:
        console.print("[yellow]No history recorded yet. Run 'init' or 'scan' first.[/yellow]")
        return

    by_component: dict = {}
    for record in history["records"]:
        key = f"{record['component_type']}/{record['component_name']}"
        if key not in by_component:
            by_component[key] = []
        by_component[key].append(record)

    if component_type:
        by_component = {k: v for k, v in by_component.items() if k.startswith(component_type)}

    for component, records in sorted(by_component.items()):
        console.print(f"\n[bold cyan]{component}[/bold cyan]")
        for record in records:
            valid_from = record["valid_from"][:10]
            valid_to = record["valid_to"][:10] if record["valid_to"] else "current"
            version = record.get("version", "?")
            change_type = record.get("change_type", "")
            console.print(f"  v{version} | {valid_from} -> {valid_to} | {change_type}")


@app.command("query")
def query(
    date: str = typer.Argument(..., help="Date to query (YYYY-MM-DD or 'now')"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show more details"),
) -> None:
    """Query system state at a point in time."""
    history = load_history()

    try:
        target = parse_date(date)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    state = get_state_at(history, target)

    if not state:
        console.print(f"[yellow]No records found for date: {date}[/yellow]")
        return

    console.print(f"\n[bold]System state at {target.strftime('%Y-%m-%d %H:%M:%S UTC')}:[/bold]\n")

    table = Table()
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")
    if verbose:
        table.add_column("Checksum", style="dim")
        table.add_column("Change", style="yellow")

    current_type = None
    for record in state:
        if record["component_type"] != current_type:
            current_type = record["component_type"]
            table.add_row(f"[bold][{current_type}][/bold]", "", "" if not verbose else "", "" if not verbose else "")

        name = record["component_name"]
        version = record.get("version", "?")
        if verbose:
            checksum = record.get("checksum", "")[:8] if record.get("checksum") else "deleted"
            change = record.get("change_type", "")
            table.add_row(f"  {name}", version, checksum, change)
        else:
            table.add_row(f"  {name}", version)

    console.print(table)
    console.print(f"\n[dim]Total: {len(state)} components[/dim]")


@app.command("diff")
def diff(
    date1: str = typer.Argument(..., help="First date (YYYY-MM-DD or 'now')"),
    date2: str = typer.Argument(..., help="Second date (YYYY-MM-DD or 'now')"),
) -> None:
    """Compare system state between two dates."""
    history = load_history()

    try:
        d1 = parse_date(date1)
        d2 = parse_date(date2)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    state1 = {r["file_path"]: r for r in get_state_at(history, d1)}
    state2 = {r["file_path"]: r for r in get_state_at(history, d2)}

    all_paths = set(state1.keys()) | set(state2.keys())

    added = []
    removed = []
    modified = []

    for path in all_paths:
        in_1 = path in state1
        in_2 = path in state2

        if in_2 and not in_1:
            added.append(state2[path])
        elif in_1 and not in_2:
            removed.append(state1[path])
        elif state1[path].get("checksum") != state2[path].get("checksum"):
            modified.append((state1[path], state2[path]))

    console.print(f"\n[bold]Diff: {d1.strftime('%Y-%m-%d')} -> {d2.strftime('%Y-%m-%d')}[/bold]\n")

    if added:
        console.print(f"[green]Added ({len(added)}):[/green]")
        for r in added:
            console.print(f"  + {r['component_type']}/{r['component_name']}")

    if removed:
        console.print(f"\n[red]Removed ({len(removed)}):[/red]")
        for r in removed:
            console.print(f"  - {r['component_type']}/{r['component_name']}")

    if modified:
        console.print(f"\n[yellow]Modified ({len(modified)}):[/yellow]")
        for old, new in modified:
            console.print(f"  ~ {old['component_type']}/{old['component_name']}")
            console.print(f"    v{old.get('version', '?')} -> v{new.get('version', '?')}")

    if not (added or removed or modified):
        console.print("[dim]No differences found.[/dim]")
