"""CLI subcommands for project audit."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from claude_cli.audit.auditor import audit_project
from claude_cli.cockpit.generator import find_project_root
from claude_cli.cockpit.portfolio import discover_projects

app = typer.Typer(help="Prime Directive compliance audit")
console = Console()


@app.command("check")
def check(
    project_root: Path = typer.Option(
        None, "--project-root", "-p", help="Project root directory"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Run full project audit."""
    root = _resolve_root(project_root)
    report = audit_project(root)

    if json_output:
        console.print(report.to_json())
    else:
        console.print(report.to_markdown())

    if report.critical > 0:
        raise typer.Exit(code=2)
    if report.high > 0:
        raise typer.Exit(code=1)


@app.command("score")
def score(
    project_root: Path = typer.Option(
        None, "--project-root", "-p", help="Project root directory"
    ),
) -> None:
    """Show quick audit score."""
    root = _resolve_root(project_root)
    report = audit_project(root)

    color = "green" if report.grade in ("A", "B") else "yellow" if report.grade == "C" else "red"
    console.print(
        f"[{color}]{report.project_slug}: {report.score}/100 "
        f"(Grade {report.grade})[/{color}] - "
        f"{report.total_findings} findings"
    )


@app.command("portfolio")
def portfolio(
    base_dir: Path = typer.Option(
        None, "--base-dir", "-b", help="Base directory to scan"
    ),
) -> None:
    """Audit all discovered projects."""
    projects = discover_projects(base_dir)

    if not projects:
        console.print("[yellow]No governed projects found.[/yellow]")
        return

    console.print(f"\n[bold]Portfolio Audit: {len(projects)} projects[/bold]\n")

    for project_root in projects:
        try:
            report = audit_project(project_root)
            color = (
                "green" if report.grade in ("A", "B")
                else "yellow" if report.grade == "C"
                else "red"
            )
            console.print(
                f"  [{color}]{report.project_slug}: {report.score}/100 "
                f"(Grade {report.grade})[/{color}] - "
                f"{report.total_findings} findings "
                f"(C:{report.critical} H:{report.high} M:{report.medium} L:{report.low})"
            )
        except Exception as e:
            console.print(f"  [red]{project_root.name}: ERROR - {e}[/red]")

    console.print()


def _resolve_root(project_root: Path | None) -> Path:
    """Resolve project root, raising if not found."""
    if project_root is not None:
        if not (project_root / ".claude" / "manifest.yaml").exists():
            console.print(f"[red]No .claude/manifest.yaml found at {project_root}[/red]")
            raise typer.Exit(code=1)
        return project_root

    root = find_project_root()
    if root is None:
        console.print("[red]No .claude/manifest.yaml found in any parent directory[/red]")
        raise typer.Exit(code=1)
    return root
