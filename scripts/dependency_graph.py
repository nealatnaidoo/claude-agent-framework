#!/usr/bin/env python3
"""
Agent Dependency Graph Generator

Parses agent files to extract dependencies and generates visualization.

Usage:
    ./dependency_graph.py              # Print text graph
    ./dependency_graph.py --mermaid    # Output Mermaid diagram
    ./dependency_graph.py --dot        # Output Graphviz DOT
    ./dependency_graph.py --json       # Output JSON structure
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
AGENTS_DIR = REPO_ROOT / "agents"
MANIFEST_FILE = REPO_ROOT / "manifest.yaml"


def parse_agent_metadata(file_path: Path) -> dict:
    """Extract metadata from agent file frontmatter and content."""
    content = file_path.read_text()

    metadata = {
        "name": file_path.stem,
        "file": str(file_path.relative_to(REPO_ROOT)),
        "scope": "micro",
        "depends_on": [],
        "depended_by": [],
        "exclusive_permission": None,
        "consults": [],
        "hands_off_to": [],
    }

    # Parse YAML frontmatter if present
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            frontmatter = content[3:end]

            # Extract key fields
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip().strip('"').strip("'")

                    if key == "name":
                        metadata["name"] = value
                    elif key == "scope":
                        metadata["scope"] = value
                    elif key == "exclusive_permission":
                        metadata["exclusive_permission"] = value

    # Parse content for dependency patterns
    content_lower = content.lower()

    # Look for "depends on" patterns
    depends_patterns = [
        r"depends[_\s]on[:\s]+\[([^\]]+)\]",
        r"must consult[:\s]+(\w+[-\w]*)",
        r"requires[:\s]+(\w+[-\w]*)\s+approval",
        r"after[:\s]+(\w+[-\w]*)\s+completes",
    ]

    for pattern in depends_patterns:
        matches = re.findall(pattern, content_lower)
        for match in matches:
            if isinstance(match, str):
                deps = [d.strip() for d in match.split(",")]
                for dep in deps:
                    dep_clean = dep.strip().strip('"').strip("'")
                    if dep_clean and dep_clean not in metadata["depends_on"]:
                        metadata["depends_on"].append(dep_clean)

    # Look for "hands off to" patterns
    handoff_patterns = [
        r"hands[_\s]off[_\s]to[:\s]+(\w+[-\w]*)",
        r"passes[_\s]to[:\s]+(\w+[-\w]*)",
        r"triggers[:\s]+(\w+[-\w]*)",
    ]

    for pattern in handoff_patterns:
        matches = re.findall(pattern, content_lower)
        for match in matches:
            if match and match not in metadata["hands_off_to"]:
                metadata["hands_off_to"].append(match)

    # Look for consultation patterns
    consult_patterns = [
        r"consults?[:\s]+(\w+[-\w]*)",
        r"must consult[:\s]+(\w+[-\w]*)",
    ]

    for pattern in consult_patterns:
        matches = re.findall(pattern, content_lower)
        for match in matches:
            if match and match not in metadata["consults"]:
                metadata["consults"].append(match)

    return metadata


def load_manifest_dependencies() -> dict:
    """Load dependencies from manifest.yaml if available."""
    if not MANIFEST_FILE.exists():
        return {}

    import yaml
    with open(MANIFEST_FILE) as f:
        manifest = yaml.safe_load(f)

    agents = manifest.get("agents", {})
    deps = {}

    for name, info in agents.items():
        deps[name] = {
            "depends_on": info.get("depends_on", []),
            "depended_by": info.get("depended_by", []),
            "scope": info.get("scope", "micro"),
            "exclusive_permission": info.get("exclusive_permission"),
        }

    return deps


def build_graph() -> dict:
    """Build complete dependency graph from agents and manifest."""
    graph = {}

    # Load from manifest first (authoritative)
    manifest_deps = load_manifest_dependencies()

    # Parse each agent file
    for agent_file in AGENTS_DIR.glob("*.md"):
        if agent_file.name.startswith("."):
            continue

        metadata = parse_agent_metadata(agent_file)
        name = metadata["name"]

        # Merge with manifest data (manifest takes precedence)
        if name in manifest_deps:
            metadata["depends_on"] = manifest_deps[name].get("depends_on", metadata["depends_on"])
            metadata["depended_by"] = manifest_deps[name].get("depended_by", metadata["depended_by"])
            metadata["scope"] = manifest_deps[name].get("scope", metadata["scope"])
            metadata["exclusive_permission"] = manifest_deps[name].get("exclusive_permission", metadata["exclusive_permission"])

        graph[name] = metadata

    return graph


def get_all_dependents(graph: dict, agent_name: str, visited: set = None) -> set:
    """Recursively find all agents that depend on this one."""
    if visited is None:
        visited = set()

    if agent_name in visited:
        return set()

    visited.add(agent_name)
    dependents = set()

    agent = graph.get(agent_name, {})
    direct_dependents = agent.get("depended_by", [])

    for dep in direct_dependents:
        dependents.add(dep)
        dependents.update(get_all_dependents(graph, dep, visited))

    return dependents


def get_all_dependencies(graph: dict, agent_name: str, visited: set = None) -> set:
    """Recursively find all agents this one depends on."""
    if visited is None:
        visited = set()

    if agent_name in visited:
        return set()

    visited.add(agent_name)
    dependencies = set()

    agent = graph.get(agent_name, {})
    direct_deps = agent.get("depends_on", [])

    for dep in direct_deps:
        dependencies.add(dep)
        dependencies.update(get_all_dependencies(graph, dep, visited))

    return dependencies


def print_text_graph(graph: dict):
    """Print graph as formatted text."""
    # Sort by scope then name
    agents = sorted(graph.items(), key=lambda x: (x[1].get("scope", "micro"), x[0]))

    print("Agent Dependency Graph")
    print("=" * 60)

    current_scope = None
    for name, info in agents:
        if info.get("scope") != current_scope:
            current_scope = info.get("scope", "micro")
            print(f"\n[{current_scope.upper()} AGENTS]")

        perm = f" **{info['exclusive_permission']}**" if info.get("exclusive_permission") else ""
        print(f"\n  {name}{perm}")

        if info.get("depends_on"):
            print(f"    ← depends on: {', '.join(info['depends_on'])}")
        if info.get("depended_by"):
            print(f"    → depended by: {', '.join(info['depended_by'])}")

    print("\n" + "=" * 60)
    print("\nWorkflow Order:")
    print("  devops-governor (consult)")
    print("       ↓")
    print("  solution-designer → business-analyst → coding-agent")
    print("       ↓                                      ↓")
    print("  (approval stamp)                      qa-reviewer")
    print("                                             ↓")
    print("                                     code-review-agent")
    print("                                             ↓")
    print("                                      lessons-advisor")


def generate_mermaid(graph: dict) -> str:
    """Generate Mermaid diagram."""
    lines = ["graph TD"]
    lines.append("    %% Agent Dependency Graph")
    lines.append("")

    # Define nodes with styling
    for name, info in graph.items():
        scope = info.get("scope", "micro")
        perm = info.get("exclusive_permission", "")

        if scope == "macro":
            lines.append(f"    {name}[[\"{name}<br/><small>{perm}</small>\"]]")
        elif perm:
            lines.append(f"    {name}[(\"{name}<br/><small>{perm}</small>\")]")
        else:
            lines.append(f"    {name}[\"{name}\"]")

    lines.append("")

    # Define edges
    for name, info in graph.items():
        for dep in info.get("depends_on", []):
            if dep in graph:
                lines.append(f"    {dep} --> {name}")

    lines.append("")
    lines.append("    %% Styling")
    lines.append("    classDef macro fill:#f9f,stroke:#333,stroke-width:2px")
    lines.append("    classDef exclusive fill:#ff9,stroke:#333,stroke-width:2px")

    # Apply classes
    for name, info in graph.items():
        if info.get("scope") == "macro":
            lines.append(f"    class {name} macro")
        elif info.get("exclusive_permission"):
            lines.append(f"    class {name} exclusive")

    return "\n".join(lines)


def generate_dot(graph: dict) -> str:
    """Generate Graphviz DOT format."""
    lines = ["digraph AgentDependencies {"]
    lines.append("    rankdir=TB;")
    lines.append("    node [shape=box, style=rounded];")
    lines.append("")

    # Define nodes
    for name, info in graph.items():
        scope = info.get("scope", "micro")
        perm = info.get("exclusive_permission", "")

        attrs = []
        if scope == "macro":
            attrs.append('shape=doubleoctagon')
            attrs.append('color=purple')
        if perm:
            attrs.append('style="rounded,filled"')
            attrs.append('fillcolor=lightyellow')

        label = name
        if perm:
            label = f"{name}\\n({perm})"

        attr_str = f' [{", ".join(attrs)}, label="{label}"]' if attrs else f' [label="{label}"]'
        lines.append(f"    {name.replace('-', '_')}{attr_str};")

    lines.append("")

    # Define edges
    for name, info in graph.items():
        for dep in info.get("depends_on", []):
            if dep in graph:
                lines.append(f"    {dep.replace('-', '_')} -> {name.replace('-', '_')};")

    lines.append("}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate agent dependency graph")
    parser.add_argument("--mermaid", action="store_true", help="Output Mermaid diagram")
    parser.add_argument("--dot", action="store_true", help="Output Graphviz DOT")
    parser.add_argument("--json", action="store_true", help="Output JSON structure")
    parser.add_argument("--agent", help="Focus on specific agent")

    args = parser.parse_args()

    graph = build_graph()

    if args.agent:
        if args.agent not in graph:
            print(f"Agent not found: {args.agent}")
            print(f"Available: {', '.join(sorted(graph.keys()))}")
            return 1

        agent = graph[args.agent]
        deps = get_all_dependencies(graph, args.agent)
        dependents = get_all_dependents(graph, args.agent)

        print(f"Agent: {args.agent}")
        print(f"Scope: {agent.get('scope', 'micro')}")
        if agent.get("exclusive_permission"):
            print(f"Exclusive Permission: {agent['exclusive_permission']}")
        print(f"\nDirect dependencies: {agent.get('depends_on', [])}")
        print(f"All dependencies (transitive): {sorted(deps)}")
        print(f"\nDirect dependents: {agent.get('depended_by', [])}")
        print(f"All dependents (transitive): {sorted(dependents)}")
        return 0

    if args.mermaid:
        print(generate_mermaid(graph))
    elif args.dot:
        print(generate_dot(graph))
    elif args.json:
        print(json.dumps(graph, indent=2))
    else:
        print_text_graph(graph)

    return 0


if __name__ == "__main__":
    sys.exit(main())
