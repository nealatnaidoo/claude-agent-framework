#!/usr/bin/env python3
"""
Impact Analysis for Agent Changes

Analyzes the impact of modifying an agent before changes are made.
Shows which other agents would be affected and what updates may be needed.

Usage:
    ./impact_analysis.py <agent-name>              # Analyze impact of changing agent
    ./impact_analysis.py <agent-name> --delete     # Analyze impact of deleting agent
    ./impact_analysis.py <agent-name> --add-dep X  # Analyze adding dependency on X
    ./impact_analysis.py --all                     # Show full impact matrix
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Import from sibling module
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from dependency_graph import build_graph, get_all_dependents, get_all_dependencies

REPO_ROOT = SCRIPT_DIR.parent
AGENTS_DIR = REPO_ROOT / "agents"


def analyze_modification_impact(graph: dict, agent_name: str) -> dict:
    """Analyze the impact of modifying an agent."""
    if agent_name not in graph:
        return {"error": f"Agent not found: {agent_name}"}

    agent = graph[agent_name]
    direct_dependents = agent.get("depended_by", [])
    all_dependents = get_all_dependents(graph, agent_name)

    impact = {
        "agent": agent_name,
        "action": "modify",
        "scope": agent.get("scope", "micro"),
        "has_exclusive_permission": bool(agent.get("exclusive_permission")),
        "risk_level": "low",
        "direct_dependents": direct_dependents,
        "transitive_dependents": sorted(all_dependents - set(direct_dependents)),
        "total_affected": len(all_dependents),
        "required_reviews": [],
        "recommended_actions": [],
        "warnings": [],
    }

    # Determine risk level
    if agent.get("exclusive_permission"):
        impact["risk_level"] = "high"
        impact["warnings"].append(
            f"This agent has exclusive permission: {agent['exclusive_permission']}. "
            "Changes may affect system-wide governance."
        )

    if agent.get("scope") == "macro":
        impact["risk_level"] = "high"
        impact["warnings"].append(
            "This is a MACRO agent governing multiple projects. "
            "Changes affect portfolio-level consistency."
        )

    if len(all_dependents) >= 3:
        if impact["risk_level"] == "low":
            impact["risk_level"] = "medium"
        impact["warnings"].append(
            f"{len(all_dependents)} agents depend on this one (directly or transitively)."
        )

    # Determine required reviews
    if impact["risk_level"] == "high":
        impact["required_reviews"] = ["architecture_review", "governance_review"]
    elif impact["risk_level"] == "medium":
        impact["required_reviews"] = ["peer_review"]

    # Recommended actions
    impact["recommended_actions"] = [
        "1. Create a snapshot before making changes: ./scripts/snapshot.sh 'pre-change'",
        "2. Update version in manifest.yaml after changes",
        "3. Run validation: python3 scripts/validate_agents.py",
        "4. Record changes: python3 scripts/version_tracker.py scan",
    ]

    if direct_dependents:
        impact["recommended_actions"].append(
            f"5. Review dependent agents for compatibility: {', '.join(direct_dependents)}"
        )

    return impact


def analyze_deletion_impact(graph: dict, agent_name: str) -> dict:
    """Analyze the impact of deleting an agent."""
    if agent_name not in graph:
        return {"error": f"Agent not found: {agent_name}"}

    agent = graph[agent_name]
    all_dependents = get_all_dependents(graph, agent_name)
    all_dependencies = get_all_dependencies(graph, agent_name)

    impact = {
        "agent": agent_name,
        "action": "delete",
        "risk_level": "critical" if all_dependents else "medium",
        "blocking_dependents": sorted(all_dependents),
        "dependencies_to_update": sorted(all_dependencies),
        "can_delete": len(all_dependents) == 0,
        "required_actions": [],
        "warnings": [],
    }

    if all_dependents:
        impact["warnings"].append(
            f"BLOCKING: {len(all_dependents)} agents depend on this one. "
            "Cannot delete without updating them first."
        )
        impact["required_actions"].append(
            f"Update or remove dependencies in: {', '.join(sorted(all_dependents))}"
        )

    if agent.get("exclusive_permission"):
        impact["warnings"].append(
            f"This agent has exclusive permission '{agent['exclusive_permission']}'. "
            "Deletion requires reassigning this permission."
        )
        impact["required_actions"].append(
            f"Reassign exclusive permission '{agent['exclusive_permission']}' to another agent"
        )

    if agent.get("scope") == "macro":
        impact["warnings"].append(
            "This is a MACRO agent. Deletion affects portfolio governance."
        )

    if impact["can_delete"]:
        impact["required_actions"] = [
            "1. Create snapshot: ./scripts/snapshot.sh 'pre-deletion'",
            "2. Remove agent file",
            "3. Update manifest.yaml to remove agent entry",
            "4. Update any agents that list this in 'depends_on'",
            "5. Record change: python3 scripts/version_tracker.py scan",
        ]

    return impact


def analyze_add_dependency(graph: dict, agent_name: str, new_dep: str) -> dict:
    """Analyze the impact of adding a new dependency."""
    if agent_name not in graph:
        return {"error": f"Agent not found: {agent_name}"}

    if new_dep not in graph:
        return {"error": f"Dependency agent not found: {new_dep}"}

    agent = graph[agent_name]
    current_deps = set(agent.get("depends_on", []))

    if new_dep in current_deps:
        return {"info": f"{agent_name} already depends on {new_dep}"}

    # Check for circular dependency
    new_dep_deps = get_all_dependencies(graph, new_dep)
    if agent_name in new_dep_deps:
        return {
            "error": "CIRCULAR DEPENDENCY DETECTED",
            "detail": f"{new_dep} already depends on {agent_name} (directly or transitively)",
            "chain": f"{new_dep} → ... → {agent_name} → {new_dep}",
        }

    impact = {
        "agent": agent_name,
        "action": "add_dependency",
        "new_dependency": new_dep,
        "risk_level": "low",
        "creates_cycle": False,
        "current_dependencies": sorted(current_deps),
        "new_dependencies": sorted(current_deps | {new_dep}),
        "transitive_dependencies_added": sorted(get_all_dependencies(graph, new_dep)),
        "required_actions": [
            f"1. Add '{new_dep}' to depends_on in {agent_name}.md frontmatter",
            f"2. Add '{agent_name}' to depended_by in {new_dep} manifest entry",
            "3. Update manifest.yaml with new dependency",
            "4. Validate: python3 scripts/validate_agents.py",
        ],
    }

    # Check if new dep has exclusive permissions
    new_dep_agent = graph[new_dep]
    if new_dep_agent.get("exclusive_permission"):
        impact["warnings"] = [
            f"New dependency has exclusive permission: {new_dep_agent['exclusive_permission']}. "
            "Ensure your agent respects this boundary."
        ]

    return impact


def print_impact_matrix(graph: dict):
    """Print full impact matrix showing all dependencies."""
    agents = sorted(graph.keys())

    print("Impact Matrix: Who affects whom")
    print("=" * 70)
    print()

    # Header
    print(f"{'Agent':<25} {'Direct Deps':<20} {'Dependents':<20}")
    print("-" * 70)

    for name in agents:
        agent = graph[name]
        deps = ", ".join(agent.get("depends_on", [])) or "-"
        dependents = ", ".join(agent.get("depended_by", [])) or "-"

        # Truncate if too long
        if len(deps) > 18:
            deps = deps[:15] + "..."
        if len(dependents) > 18:
            dependents = dependents[:15] + "..."

        scope_marker = "[M]" if agent.get("scope") == "macro" else "   "
        perm_marker = "*" if agent.get("exclusive_permission") else " "

        print(f"{scope_marker}{perm_marker}{name:<21} {deps:<20} {dependents:<20}")

    print()
    print("Legend: [M] = Macro agent, * = Has exclusive permission")
    print()

    # Risk summary
    print("Risk Summary:")
    print("-" * 40)

    high_risk = [n for n, a in graph.items()
                 if a.get("scope") == "macro" or a.get("exclusive_permission")]
    medium_risk = [n for n, a in graph.items()
                   if len(a.get("depended_by", [])) >= 2 and n not in high_risk]

    print(f"  High risk (macro/exclusive): {', '.join(high_risk)}")
    print(f"  Medium risk (2+ dependents): {', '.join(medium_risk)}")


def format_impact_report(impact: dict) -> str:
    """Format impact analysis as readable report."""
    lines = []

    if "error" in impact:
        lines.append(f"ERROR: {impact['error']}")
        if "detail" in impact:
            lines.append(f"  {impact['detail']}")
        return "\n".join(lines)

    if "info" in impact:
        lines.append(f"INFO: {impact['info']}")
        return "\n".join(lines)

    lines.append("=" * 60)
    lines.append(f"Impact Analysis: {impact['action'].upper()} {impact['agent']}")
    lines.append("=" * 60)
    lines.append("")

    if "risk_level" in impact:
        risk = impact["risk_level"].upper()
        lines.append(f"Risk Level: {risk}")
        lines.append("")

    if impact.get("warnings"):
        lines.append("WARNINGS:")
        for warning in impact["warnings"]:
            lines.append(f"  ⚠️  {warning}")
        lines.append("")

    if impact.get("blocking_dependents"):
        lines.append(f"Blocking Dependents ({len(impact['blocking_dependents'])}):")
        for dep in impact["blocking_dependents"]:
            lines.append(f"  • {dep}")
        lines.append("")

    if impact.get("direct_dependents"):
        lines.append(f"Direct Dependents ({len(impact['direct_dependents'])}):")
        for dep in impact["direct_dependents"]:
            lines.append(f"  • {dep}")
        lines.append("")

    if impact.get("transitive_dependents"):
        lines.append(f"Transitive Dependents ({len(impact['transitive_dependents'])}):")
        for dep in impact["transitive_dependents"]:
            lines.append(f"  • {dep}")
        lines.append("")

    if impact.get("required_reviews"):
        lines.append("Required Reviews:")
        for review in impact["required_reviews"]:
            lines.append(f"  □ {review}")
        lines.append("")

    if impact.get("required_actions"):
        lines.append("Required Actions:")
        for action in impact["required_actions"]:
            lines.append(f"  {action}")
        lines.append("")
    elif impact.get("recommended_actions"):
        lines.append("Recommended Actions:")
        for action in impact["recommended_actions"]:
            lines.append(f"  {action}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze impact of agent changes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s coding-agent              # Impact of modifying coding-agent
  %(prog)s coding-agent --delete     # Impact of deleting coding-agent
  %(prog)s qa-reviewer --add-dep X   # Impact of adding dependency
  %(prog)s --all                     # Full impact matrix
        """
    )

    parser.add_argument("agent", nargs="?", help="Agent to analyze")
    parser.add_argument("--delete", action="store_true", help="Analyze deletion impact")
    parser.add_argument("--add-dep", metavar="AGENT", help="Analyze adding this dependency")
    parser.add_argument("--all", action="store_true", help="Show full impact matrix")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    graph = build_graph()

    if args.all:
        if args.json:
            print(json.dumps(graph, indent=2))
        else:
            print_impact_matrix(graph)
        return 0

    if not args.agent:
        parser.print_help()
        print("\nAvailable agents:", ", ".join(sorted(graph.keys())))
        return 1

    # Perform analysis
    if args.delete:
        impact = analyze_deletion_impact(graph, args.agent)
    elif args.add_dep:
        impact = analyze_add_dependency(graph, args.agent, args.add_dep)
    else:
        impact = analyze_modification_impact(graph, args.agent)

    # Output
    if args.json:
        print(json.dumps(impact, indent=2))
    else:
        print(format_impact_report(impact))

    # Return non-zero if high risk or blocking
    if impact.get("risk_level") in ("high", "critical"):
        return 1
    if impact.get("blocking_dependents"):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
