"""CLI commands for agent management."""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.table import Table

from claude_cli.common.config import get_framework_paths
from claude_cli.agents.validator import AgentValidator

app = typer.Typer(help="Agent validation and management")
console = Console()


@app.command("list")
def list_agents() -> None:
    """List all registered agents."""
    paths = get_framework_paths()
    agents_dir = Path(paths["agents"])

    if not agents_dir.exists():
        console.print("\n[red]Agents directory not found.[/red]\n")
        raise typer.Exit(1)

    agents = list(agents_dir.glob("*.md"))

    table = Table(title="Registered Agents")
    table.add_column("Agent", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("File", style="white")

    for agent_file in sorted(agents):
        name = agent_file.stem
        agent_type = _detect_agent_type(agent_file)
        table.add_row(name, agent_type, agent_file.name)

    console.print()
    console.print(table)
    console.print()


@app.command()
def validate(
    agent: Optional[str] = typer.Argument(None, help="Agent name (or all if not specified)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Validate agent prompt files."""
    paths = get_framework_paths()
    agents_dir = Path(paths["agents"])

    if not agents_dir.exists():
        console.print("\n[red]Agents directory not found.[/red]\n")
        raise typer.Exit(1)

    validator = AgentValidator(verbose=verbose)
    all_passed = True

    if agent:
        agent_file = agents_dir / f"{agent}.md"
        if not agent_file.exists():
            console.print(f"\n[red]Agent not found: {agent}[/red]\n")
            raise typer.Exit(1)

        results = validator.validate_file(agent_file)
        passed = _print_results(results, agent_file.name, verbose)
        all_passed = passed
    else:
        console.print("\n[bold]Validating all agents in ~/.claude/agents/[/bold]")
        all_results = validator.validate_all_agents(agents_dir)

        if not all_results:
            console.print("[yellow]No agent files found.[/yellow]")
            raise typer.Exit(2)

        for filename, results in all_results.items():
            passed = _print_results(results, filename, verbose)
            if not passed:
                all_passed = False

        console.print("\n" + "=" * 60)
        if all_passed:
            console.print("[green]Overall: ALL PASSED[/green]")
        else:
            console.print("[red]Overall: SOME FAILED[/red]")
        console.print("=" * 60)

    if not all_passed:
        raise typer.Exit(1)


def _print_results(results: list, filename: str, verbose: bool) -> bool:
    """Print validation results and return whether all passed."""
    console.print(f"\n{'=' * 60}")
    console.print(f"Validating: [cyan]{filename}[/cyan]")
    console.print("=" * 60)

    errors = [r for r in results if not r.passed and r.severity == "error"]
    warnings = [r for r in results if not r.passed and r.severity == "warning"]
    passed = [r for r in results if r.passed]

    if verbose and passed:
        console.print("\n[dim]Passed checks:[/dim]")
        for r in passed:
            console.print(f"  [green][PASS][/green] {r.name}: {r.message}")

    if warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for r in warnings:
            console.print(f"  [yellow][WARN][/yellow] {r.name}: {r.message}")

    if errors:
        console.print("\n[red]Errors:[/red]")
        for r in errors:
            console.print(f"  [red][FAIL][/red] {r.name}: {r.message}")

    console.print(
        f"\nSummary: [green]{len(passed)} passed[/green], "
        f"[yellow]{len(warnings)} warnings[/yellow], "
        f"[red]{len(errors)} errors[/red]"
    )

    return len(errors) == 0


@app.command()
def new(
    name: str = typer.Argument(..., help="Agent name (e.g., 'my-agent')"),
    agent_type: str = typer.Option("micro", "--type", "-t", help="Agent type: micro/macro/visiting"),
    description: str = typer.Option("", "--description", "-d", help="Agent description"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be created"),
) -> None:
    """Create a new agent from template."""
    paths = get_framework_paths()
    agents_dir = Path(paths["agents"])

    slug = _slugify(name)
    if not slug:
        console.print("[red]Invalid agent name[/red]")
        raise typer.Exit(1)

    agent_file = agents_dir / f"{slug}.md"
    if agent_file.exists():
        console.print(f"[red]Agent already exists: {slug}[/red]")
        raise typer.Exit(1)

    content = _generate_agent_content(slug, agent_type, description)

    if dry_run:
        console.print(f"\n[bold]Would create: {agent_file}[/bold]\n")
        console.print(content[:500])
        if len(content) > 500:
            console.print(f"... ({len(content) - 500} more characters)")
        console.print("\n[dim](dry-run mode - no files created)[/dim]")
        return

    agent_file.write_text(content)
    console.print(f"\n[green]Created agent: {agent_file}[/green]\n")

    console.print("[bold]Next steps:[/bold]")
    console.print("  1. Edit the agent file to add responsibilities and constraints")
    console.print(f"  2. Validate: claude agents validate {slug}")
    console.print("  3. Commit your changes")


@app.command()
def show(
    name: str = typer.Argument(..., help="Agent name"),
) -> None:
    """Show agent details."""
    paths = get_framework_paths()
    agents_dir = Path(paths["agents"])
    agent_file = agents_dir / f"{name}.md"

    if not agent_file.exists():
        console.print(f"\n[red]Agent not found: {name}[/red]\n")
        raise typer.Exit(1)

    content = agent_file.read_text()
    frontmatter = _parse_frontmatter(content)

    console.print(f"\n[bold]Agent: {name}[/bold]\n")

    if frontmatter:
        for key, value in frontmatter.items():
            console.print(f"  {key}: {value}")

    console.print(f"\n  File: {agent_file}")
    console.print()


def _detect_agent_type(agent_file: Path) -> str:
    """Detect agent type from file content."""
    content = agent_file.read_text()

    if "MACRO" in content or "portfolio" in content.lower():
        return "macro"
    elif "visiting" in content.lower() or "external" in content.lower():
        return "visiting"
    else:
        return "micro"


def _parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown."""
    if not content.startswith("---"):
        return {}

    try:
        end = content.index("---", 3)
        frontmatter_text = content[3:end].strip()
        return yaml.safe_load(frontmatter_text) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def _slugify(name: str) -> str:
    """Convert name to valid agent slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def _generate_agent_content(name: str, agent_type: str, description: str) -> str:
    """Generate agent markdown content."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    desc = description or f"[Description for {name}]"

    return f"""---
name: {name}
description: {desc}
scope: {agent_type}
created: {now}
version: 1.0.0
tools: [Read, Glob, Grep]
model: sonnet
---

# {name}

> {desc}

## Identity

You are **{name}**, a {'macro' if agent_type == 'macro' else 'micro'} agent in the Claude Agent Framework.

This is an **INTERNAL agent** that participates in the core development workflow.

## Entry Protocol

On activation, you MUST:

1. Read the project manifest: `{{project}}/.claude/manifest.yaml`
2. Check your scope and permissions
3. Verify any dependencies are satisfied

## Responsibilities

### Primary Tasks

1. [Define primary responsibility]
2. [Define secondary responsibility]
3. [Define tertiary responsibility]

### Output Artifacts

This agent produces:

- `[artifact_name]`: [description]

## Handoff

When complete, this agent hands off to: [next-agent or 'user']

## Constraints

- [Define what this agent must NOT do]
- [Define boundaries with other agents]

## Evidence

Task completion requires:

- [ ] [Evidence item 1]
- [ ] [Evidence item 2]

## Manifest Update

After completing work, update the project manifest with:
- Task status
- Evidence locations
- Any findings or recommendations
"""
