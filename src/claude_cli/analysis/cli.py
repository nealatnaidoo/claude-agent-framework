"""CLI commands for dependency analysis."""

import json

import typer
from rich.console import Console
from rich.table import Table

from claude_cli.analysis.graph import build_graph, generate_mermaid, generate_dot
from claude_cli.analysis.impact import (
    analyze_modification_impact,
    analyze_deletion_impact,
    analyze_add_dependency,
    format_impact_report,
)

app = typer.Typer(help="Agent dependency analysis tools")
console = Console()


@app.command("graph")
def show_graph(
    mermaid: bool = typer.Option(False, "--mermaid", "-m", help="Output Mermaid diagram"),
    dot: bool = typer.Option(False, "--dot", "-d", help="Output Graphviz DOT"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output JSON structure"),
    agent: str = typer.Option(None, "--agent", "-a", help="Focus on specific agent"),
) -> None:
    """Show agent dependency graph."""
    graph = build_graph()

    if agent:
        if agent not in graph:
            console.print(f"[red]Agent not found: {agent}[/red]")
            console.print(f"Available: {', '.join(sorted(graph.keys()))}")
            raise typer.Exit(1)

        from claude_cli.analysis.graph import get_all_dependencies, get_all_dependents

        agent_info = graph[agent]
        deps = get_all_dependencies(graph, agent)
        dependents = get_all_dependents(graph, agent)

        console.print(f"\n[bold]Agent: {agent}[/bold]")
        console.print(f"Scope: {agent_info.get('scope', 'micro')}")
        if agent_info.get("exclusive_permission"):
            console.print(f"Exclusive Permission: {agent_info['exclusive_permission']}")
        console.print(f"\nDirect dependencies: {agent_info.get('depends_on', [])}")
        console.print(f"All dependencies (transitive): {sorted(deps)}")
        console.print(f"\nDirect dependents: {agent_info.get('depended_by', [])}")
        console.print(f"All dependents (transitive): {sorted(dependents)}")
        return

    if mermaid:
        console.print(generate_mermaid(graph))
    elif dot:
        console.print(generate_dot(graph))
    elif output_json:
        console.print(json.dumps(graph, indent=2))
    else:
        _print_text_graph(graph)


def _print_text_graph(graph: dict) -> None:
    """Print graph as formatted text."""
    agents = sorted(graph.items(), key=lambda x: (x[1].get("scope", "micro"), x[0]))

    console.print("\n[bold]Agent Dependency Graph[/bold]")
    console.print("=" * 60)

    current_scope = None
    for name, info in agents:
        if info.get("scope") != current_scope:
            current_scope = info.get("scope", "micro")
            console.print(f"\n[bold cyan][{current_scope.upper()} AGENTS][/bold cyan]")

        perm = f" [yellow]**{info['exclusive_permission']}**[/yellow]" if info.get("exclusive_permission") else ""
        console.print(f"\n  {name}{perm}")

        if info.get("depends_on"):
            console.print(f"    [dim]<- depends on: {', '.join(info['depends_on'])}[/dim]")
        if info.get("depended_by"):
            console.print(f"    [dim]-> depended by: {', '.join(info['depended_by'])}[/dim]")


@app.command("impact")
def analyze_impact(
    agent: str = typer.Argument(..., help="Agent to analyze"),
    delete: bool = typer.Option(False, "--delete", help="Analyze deletion impact"),
    add_dep: str = typer.Option(None, "--add-dep", help="Analyze adding this dependency"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Analyze impact of modifying, deleting, or adding dependencies to an agent."""
    graph = build_graph()

    if delete:
        impact = analyze_deletion_impact(graph, agent)
    elif add_dep:
        impact = analyze_add_dependency(graph, agent, add_dep)
    else:
        impact = analyze_modification_impact(graph, agent)

    if output_json:
        console.print(json.dumps(impact, indent=2))
    else:
        console.print(format_impact_report(impact))

    if impact.get("risk_level") in ("high", "critical"):
        raise typer.Exit(1)
    if impact.get("blocking_dependents"):
        raise typer.Exit(1)


@app.command("matrix")
def show_matrix(
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show full impact matrix for all agents."""
    graph = build_graph()

    if output_json:
        console.print(json.dumps(graph, indent=2))
        return

    table = Table(title="Agent Impact Matrix")
    table.add_column("Agent", style="cyan")
    table.add_column("Scope", style="dim")
    table.add_column("Permission", style="yellow")
    table.add_column("Depends On", style="green")
    table.add_column("Depended By", style="magenta")

    for name in sorted(graph.keys()):
        agent = graph[name]
        scope = "[M]" if agent.get("scope") == "macro" else ""
        perm = agent.get("exclusive_permission", "") or ""
        deps = ", ".join(agent.get("depends_on", [])) or "-"
        dependents = ", ".join(agent.get("depended_by", [])) or "-"

        if len(deps) > 25:
            deps = deps[:22] + "..."
        if len(dependents) > 25:
            dependents = dependents[:22] + "..."

        table.add_row(name, scope, perm, deps, dependents)

    console.print(table)

    # Risk summary
    high_risk = [n for n, a in graph.items() if a.get("scope") == "macro" or a.get("exclusive_permission")]
    medium_risk = [n for n, a in graph.items() if len(a.get("depended_by", [])) >= 2 and n not in high_risk]

    console.print("\n[bold]Risk Summary[/bold]")
    console.print(f"  [red]High risk (macro/exclusive):[/red] {', '.join(high_risk) or 'None'}")
    console.print(f"  [yellow]Medium risk (2+ dependents):[/yellow] {', '.join(medium_risk) or 'None'}")
