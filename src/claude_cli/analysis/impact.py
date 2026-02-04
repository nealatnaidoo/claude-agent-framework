"""Impact analysis for agent changes."""

from claude_cli.analysis.graph import get_all_dependencies, get_all_dependents


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

    if impact["risk_level"] == "high":
        impact["required_reviews"] = ["architecture_review", "governance_review"]
    elif impact["risk_level"] == "medium":
        impact["required_reviews"] = ["peer_review"]

    impact["recommended_actions"] = [
        "1. Create a snapshot before making changes",
        "2. Update version in manifest.yaml after changes",
        "3. Run validation: claude agents validate",
        "4. Record changes: claude version scan",
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
        impact["warnings"].append("This is a MACRO agent. Deletion affects portfolio governance.")

    if impact["can_delete"]:
        impact["required_actions"] = [
            "1. Create snapshot before deletion",
            "2. Remove agent file",
            "3. Update manifest.yaml to remove agent entry",
            "4. Update any agents that list this in 'depends_on'",
            "5. Record change: claude version scan",
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

    new_dep_deps = get_all_dependencies(graph, new_dep)
    if agent_name in new_dep_deps:
        return {
            "error": "CIRCULAR DEPENDENCY DETECTED",
            "detail": f"{new_dep} already depends on {agent_name} (directly or transitively)",
            "chain": f"{new_dep} -> ... -> {agent_name} -> {new_dep}",
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
            "4. Validate: claude agents validate",
        ],
    }

    new_dep_agent = graph[new_dep]
    if new_dep_agent.get("exclusive_permission"):
        impact["warnings"] = [
            f"New dependency has exclusive permission: {new_dep_agent['exclusive_permission']}. "
            "Ensure your agent respects this boundary."
        ]

    return impact


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
            lines.append(f"  - {warning}")
        lines.append("")

    if impact.get("blocking_dependents"):
        lines.append(f"Blocking Dependents ({len(impact['blocking_dependents'])}):")
        for dep in impact["blocking_dependents"]:
            lines.append(f"  - {dep}")
        lines.append("")

    if impact.get("direct_dependents"):
        lines.append(f"Direct Dependents ({len(impact['direct_dependents'])}):")
        for dep in impact["direct_dependents"]:
            lines.append(f"  - {dep}")
        lines.append("")

    if impact.get("transitive_dependents"):
        lines.append(f"Transitive Dependents ({len(impact['transitive_dependents'])}):")
        for dep in impact["transitive_dependents"]:
            lines.append(f"  - {dep}")
        lines.append("")

    if impact.get("required_reviews"):
        lines.append("Required Reviews:")
        for review in impact["required_reviews"]:
            lines.append(f"  [ ] {review}")
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
