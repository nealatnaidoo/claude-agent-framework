"""Main CLI entry point for Claude Agent Framework."""

import typer
from rich.console import Console

from claude_cli.lessons.cli import app as lessons_app
from claude_cli.agents.cli import app as agents_app
from claude_cli.worktree.cli import app as worktree_app
from claude_cli.db.cli import app as db_app

app = typer.Typer(
    name="claude",
    help="Claude Agent Framework CLI",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

# Register subcommands
app.add_typer(lessons_app, name="lessons", help="Manage development lessons")
app.add_typer(agents_app, name="agents", help="Agent validation and management")
app.add_typer(worktree_app, name="worktree", help="Git worktree management")
app.add_typer(db_app, name="db", help="Database harness operations (DevOps)")


@app.command()
def version() -> None:
    """Show CLI version."""
    from claude_cli import __version__
    console.print(f"claude-cli v{__version__}")


@app.command()
def status() -> None:
    """Show framework status."""
    from claude_cli.common.config import get_framework_paths
    from pathlib import Path

    paths = get_framework_paths()
    console.print("\n[bold]Claude Agent Framework Status[/bold]\n")

    for name, path in paths.items():
        exists = Path(path).exists()
        status_icon = "[green]✓[/green]" if exists else "[red]✗[/red]"
        console.print(f"  {status_icon} {name}: {path}")

    console.print()


if __name__ == "__main__":
    app()
