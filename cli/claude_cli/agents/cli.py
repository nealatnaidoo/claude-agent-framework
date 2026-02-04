"""CLI commands for agent management."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from claude_cli.common.config import get_framework_paths

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
) -> None:
    """Validate agent prompt files."""
    import subprocess

    paths = get_framework_paths()
    scripts_dir = Path(paths["root"]) / "scripts"
    validate_script = scripts_dir / "validate_agents.py"

    if not validate_script.exists():
        console.print("\n[red]Validation script not found.[/red]\n")
        raise typer.Exit(1)

    cmd = ["python3", str(validate_script)]
    if agent:
        cmd.append(f"{agent}.md")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(f"[red]{result.stderr}[/red]")

    if result.returncode != 0:
        raise typer.Exit(result.returncode)


@app.command()
def new(
    name: str = typer.Argument(..., help="Agent name (e.g., 'my-agent')"),
    agent_type: str = typer.Option("micro", "--type", "-t", help="Agent type: micro/macro/visiting"),
) -> None:
    """Create a new agent from template."""
    import subprocess

    paths = get_framework_paths()
    scripts_dir = Path(paths["root"]) / "scripts"
    new_agent_script = scripts_dir / "new_agent.py"

    if not new_agent_script.exists():
        console.print("\n[red]new_agent.py script not found.[/red]\n")
        raise typer.Exit(1)

    cmd = ["python3", str(new_agent_script), name, "--type", agent_type]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(f"[red]{result.stderr}[/red]")

    if result.returncode == 0:
        console.print(f"\n[green]✓[/green] Created agent: {name}\n")
    else:
        raise typer.Exit(result.returncode)


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

    # Parse frontmatter
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
    import yaml

    if not content.startswith("---"):
        return {}

    try:
        end = content.index("---", 3)
        frontmatter_text = content[3:end].strip()
        return yaml.safe_load(frontmatter_text) or {}
    except (ValueError, yaml.YAMLError):
        return {}
