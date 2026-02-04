"""Agent dependency graph generation and traversal."""

import re
from pathlib import Path
from typing import Optional

import yaml

from claude_cli.common.config import get_framework_paths


def parse_agent_metadata(file_path: Path, repo_root: Path) -> dict:
    """Extract metadata from agent file frontmatter and content."""
    content = file_path.read_text()

    metadata = {
        "name": file_path.stem,
        "file": str(file_path.relative_to(repo_root)),
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


def load_manifest_dependencies(manifest_file: Path) -> dict:
    """Load dependencies from manifest.yaml if available."""
    if not manifest_file.exists():
        return {}

    with open(manifest_file) as f:
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


def build_graph(agents_dir: Optional[Path] = None, manifest_file: Optional[Path] = None) -> dict:
    """Build complete dependency graph from agents and manifest."""
    paths = get_framework_paths()

    if agents_dir is None:
        agents_dir = Path(paths["agents"])
    if manifest_file is None:
        manifest_file = Path(paths["manifest"])

    repo_root = agents_dir.parent
    graph = {}

    manifest_deps = load_manifest_dependencies(manifest_file)

    for agent_file in agents_dir.glob("*.md"):
        if agent_file.name.startswith("."):
            continue

        metadata = parse_agent_metadata(agent_file, repo_root)
        name = metadata["name"]

        if name in manifest_deps:
            metadata["depends_on"] = manifest_deps[name].get("depends_on", metadata["depends_on"])
            metadata["depended_by"] = manifest_deps[name].get("depended_by", metadata["depended_by"])
            metadata["scope"] = manifest_deps[name].get("scope", metadata["scope"])
            metadata["exclusive_permission"] = manifest_deps[name].get(
                "exclusive_permission", metadata["exclusive_permission"]
            )

        graph[name] = metadata

    return graph


def get_all_dependents(graph: dict, agent_name: str, visited: Optional[set] = None) -> set:
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


def get_all_dependencies(graph: dict, agent_name: str, visited: Optional[set] = None) -> set:
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


def generate_mermaid(graph: dict) -> str:
    """Generate Mermaid diagram."""
    lines = ["graph TD"]
    lines.append("    %% Agent Dependency Graph")
    lines.append("")

    for name, info in graph.items():
        scope = info.get("scope", "micro")
        perm = info.get("exclusive_permission", "")

        if scope == "macro":
            lines.append(f'    {name}[["{name}<br/><small>{perm}</small>"]]')
        elif perm:
            lines.append(f'    {name}[("{name}<br/><small>{perm}</small>")]')
        else:
            lines.append(f'    {name}["{name}"]')

    lines.append("")

    for name, info in graph.items():
        for dep in info.get("depends_on", []):
            if dep in graph:
                lines.append(f"    {dep} --> {name}")

    lines.append("")
    lines.append("    %% Styling")
    lines.append("    classDef macro fill:#f9f,stroke:#333,stroke-width:2px")
    lines.append("    classDef exclusive fill:#ff9,stroke:#333,stroke-width:2px")

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
    lines.append('    node [shape=box, style=rounded];')
    lines.append("")

    for name, info in graph.items():
        scope = info.get("scope", "micro")
        perm = info.get("exclusive_permission", "")

        attrs = []
        if scope == "macro":
            attrs.append("shape=doubleoctagon")
            attrs.append("color=purple")
        if perm:
            attrs.append('style="rounded,filled"')
            attrs.append("fillcolor=lightyellow")

        label = name
        if perm:
            label = f"{name}\\n({perm})"

        attr_str = f' [{", ".join(attrs)}, label="{label}"]' if attrs else f' [label="{label}"]'
        lines.append(f"    {name.replace('-', '_')}{attr_str};")

    lines.append("")

    for name, info in graph.items():
        for dep in info.get("depends_on", []):
            if dep in graph:
                lines.append(f"    {dep.replace('-', '_')} -> {name.replace('-', '_')};")

    lines.append("}")
    return "\n".join(lines)
