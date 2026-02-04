"""CLI commands for git worktree management."""

import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Git worktree management for parallel development")
console = Console()


@app.command("list")
def list_worktrees() -> None:
    """List all git worktrees."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        console.print(f"\n[red]Error: {result.stderr}[/red]\n")
        raise typer.Exit(1)

    worktrees = _parse_worktree_list(result.stdout)

    if not worktrees:
        console.print("\n[yellow]No worktrees found.[/yellow]\n")
        return

    table = Table(title="Git Worktrees")
    table.add_column("Path", style="cyan")
    table.add_column("Branch", style="green")
    table.add_column("Commit", style="yellow", width=8)

    for wt in worktrees:
        table.add_row(wt["path"], wt["branch"], wt["commit"][:8])

    console.print()
    console.print(table)
    console.print()


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name for the worktree"),
    base: str = typer.Option("main", "--base", "-b", help="Base branch to create from"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Custom worktree path"),
) -> None:
    """Create a new worktree for a feature."""
    # Determine worktree path
    if path:
        worktree_path = Path(path)
    else:
        # Default: sibling directory with feature name
        cwd = Path.cwd()
        project_name = cwd.name
        worktree_path = cwd.parent / f"{project_name}-{feature}"

    branch_name = f"feature/{feature}"

    console.print(f"\nCreating worktree for [cyan]{feature}[/cyan]...")
    console.print(f"  Path: {worktree_path}")
    console.print(f"  Branch: {branch_name}")
    console.print(f"  Base: {base}")

    # Create the worktree with a new branch
    result = subprocess.run(
        ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        console.print(f"\n[red]Error: {result.stderr}[/red]\n")
        raise typer.Exit(1)

    console.print(f"\n[green]✓[/green] Created worktree at {worktree_path}\n")


@app.command()
def remove(
    path: str = typer.Argument(..., help="Path to worktree to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal"),
) -> None:
    """Remove a worktree."""
    cmd = ["git", "worktree", "remove", path]
    if force:
        cmd.append("--force")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        console.print(f"\n[red]Error: {result.stderr}[/red]\n")
        raise typer.Exit(1)

    console.print(f"\n[green]✓[/green] Removed worktree: {path}\n")


@app.command()
def sync(
    path: str = typer.Argument(..., help="Path to worktree to sync"),
) -> None:
    """Sync shared artifacts to a worktree."""
    from claude_cli.common.config import get_framework_paths

    worktree_path = Path(path)
    if not worktree_path.exists():
        console.print(f"\n[red]Worktree not found: {path}[/red]\n")
        raise typer.Exit(1)

    # Artifacts to sync
    artifacts = [".claude/artifacts", ".claude/rules"]

    synced = 0
    for artifact in artifacts:
        src = Path.cwd() / artifact
        dst = worktree_path / artifact

        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["cp", "-r", str(src), str(dst.parent)])
            synced += 1

    console.print(f"\n[green]✓[/green] Synced {synced} artifact directories to {path}\n")


@app.command()
def status() -> None:
    """Show status of all worktrees."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
    )

    worktrees = _parse_worktree_list(result.stdout)

    for wt in worktrees:
        wt_path = Path(wt["path"])
        console.print(f"\n[bold]{wt['path']}[/bold] ({wt['branch']})")

        # Check for uncommitted changes
        status_result = subprocess.run(
            ["git", "-C", str(wt_path), "status", "--porcelain"],
            capture_output=True,
            text=True,
        )

        if status_result.stdout.strip():
            changes = len(status_result.stdout.strip().split("\n"))
            console.print(f"  [yellow]⚠ {changes} uncommitted changes[/yellow]")
        else:
            console.print(f"  [green]✓ Clean[/green]")

    console.print()


def _parse_worktree_list(output: str) -> list[dict]:
    """Parse git worktree list --porcelain output."""
    worktrees = []
    current = {}

    for line in output.strip().split("\n"):
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[9:]}
        elif line.startswith("HEAD "):
            current["commit"] = line[5:]
        elif line.startswith("branch "):
            current["branch"] = line[7:].replace("refs/heads/", "")
        elif line == "detached":
            current["branch"] = "(detached)"

    if current:
        worktrees.append(current)

    return worktrees
