"""CLI subcommands for pattern compliance linting."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from claude_cli.cockpit.generator import find_project_root
from claude_cli.lint.checker import RULES, lint_project

app = typer.Typer(help="Pattern compliance linting")
console = Console()


@app.command("check")
def check(
    project_root: Path = typer.Option(
        None, "--project-root", "-p", help="Project root directory"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Check project for pattern compliance violations."""
    root = _resolve_root(project_root)
    report = lint_project(root)

    if json_output:
        console.print(report.to_json())
    else:
        console.print(report.to_markdown())

    if report.has_errors:
        raise typer.Exit(code=1)


@app.command("rules")
def rules() -> None:
    """List all lint rules."""
    console.print("\n[bold]Pattern Lint Rules[/bold]\n")
    for rule_id, rule in sorted(RULES.items()):
        severity = rule["severity"]
        color = "red" if severity == "error" else "yellow"
        console.print(f"  [{color}]{rule_id}[/{color}] ({severity}): {rule['description']}")
    console.print()


def _resolve_root(project_root: Path | None) -> Path:
    """Resolve project root, raising if not found."""
    if project_root is not None:
        if not project_root.exists():
            console.print(f"[red]Directory not found: {project_root}[/red]")
            raise typer.Exit(code=1)
        return project_root

    root = find_project_root()
    if root is None:
        console.print("[red]No .claude/manifest.yaml found in any parent directory[/red]")
        raise typer.Exit(code=1)
    return root
