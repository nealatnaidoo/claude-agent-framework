"""CLI commands for cockpit dashboard generation."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def project(
    project_root: Optional[Path] = typer.Option(None, "--project-root", "-p", help="Project root directory"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output HTML path"),
) -> None:
    """Generate cockpit dashboard for a single project."""
    from claude_cli.cockpit.generator import generate_cockpit

    try:
        path = generate_cockpit(project_root=project_root, output=output)
        console.print(f"[green]Cockpit generated:[/green] {path}")
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def portfolio(
    base_dir: Optional[Path] = typer.Option(None, "--base-dir", "-b", help="Base directory to scan for projects"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output HTML path"),
) -> None:
    """Generate portfolio-level cockpit across all governed projects."""
    from claude_cli.cockpit.portfolio import generate_portfolio_cockpit

    path = generate_portfolio_cockpit(base_dir=base_dir, output=output)
    console.print(f"[green]Portfolio cockpit generated:[/green] {path}")
