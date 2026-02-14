"""CLI subcommands for drift detection."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from claude_cli.cockpit.generator import find_project_root
from claude_cli.drift.detector import create_rules_template, detect_drift

app = typer.Typer(help="Drift detection: decisions vs code")
console = Console()


@app.command("check")
def check(
    project_root: Path = typer.Option(None, "--project-root", "-p", help="Project root directory"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Check for drift between architectural decisions and code."""
    root = _resolve_root(project_root)
    report = detect_drift(root)

    if json_output:
        console.print(report.to_json())
    else:
        console.print(report.to_markdown())

    if report.has_drift:
        raise typer.Exit(code=1)


@app.command("init")
def init(
    project_root: Path = typer.Option(None, "--project-root", "-p", help="Project root directory"),
) -> None:
    """Create a drift_rules.yaml template."""
    root = _resolve_root(project_root)
    path = create_rules_template(root)
    console.print(f"[green]Created drift rules template:[/green] {path}")


@app.command("report")
def report(
    project_root: Path = typer.Option(None, "--project-root", "-p", help="Project root directory"),
) -> None:
    """Generate and save a drift report to .claude/evidence/."""
    root = _resolve_root(project_root)
    drift_report = detect_drift(root)

    evidence_dir = root / ".claude" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    md_path = evidence_dir / "drift_report.md"
    md_path.write_text(drift_report.to_markdown())
    console.print(f"[green]Markdown report saved:[/green] {md_path}")

    json_path = evidence_dir / "drift_report.json"
    json_path.write_text(drift_report.to_json())
    console.print(f"[green]JSON report saved:[/green] {json_path}")

    if drift_report.has_drift:
        console.print(f"[red]Drift detected:[/red] {drift_report.failed} failed checks")
    else:
        console.print(f"[green]No drift detected.[/green] {drift_report.passed} checks passed.")


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
