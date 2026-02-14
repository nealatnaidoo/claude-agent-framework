"""Collect framework documentation for cockpit dashboards.

Parses framework files (tools registry, agent prompts, CLAUDE.md, patterns,
coding standards) at cockpit generation time and returns a structured dict
for injection into dashboard templates.
"""

from __future__ import annotations

import re
from pathlib import Path


def collect_docs_data(framework_root: Path | None = None) -> dict:
    """Main entry point. Collect all documentation data from framework sources.

    Each parser returns empty defaults on missing files (graceful degradation).
    """
    if framework_root is None:
        from claude_cli.common.config import get_framework_root

        framework_root = get_framework_root()

    tools_data = _parse_tools_registry(framework_root / "tools" / "registry.yaml")
    agents = _parse_agents(framework_root / "agents")
    commands = _parse_commands(framework_root / "CLAUDE.md")
    patterns = _parse_patterns_index(framework_root / "patterns" / "PATTERNS_INDEX.md")
    coding_tips = _parse_coding_tips(framework_root / "knowledge" / "coding_standards.md")
    governance = _parse_governance(framework_root / "CLAUDE.md")

    return {
        "tools": tools_data,
        "agents": agents,
        "commands": commands,
        "patterns": patterns,
        "coding_tips": coding_tips,
        "governance": governance,
    }


def _parse_tools_registry(path: Path) -> dict:
    """Parse tools/registry.yaml for scripts, packages, and planned tools.

    Returns {"scripts": [...], "packages": [...], "planned": [...]}.
    """
    result: dict = {"scripts": [], "packages": [], "planned": []}
    if not path.exists():
        return result

    try:
        import yaml

        data = yaml.safe_load(path.read_text()) or {}
    except ImportError:
        # Fallback: skip YAML parsing if PyYAML not available
        return result

    # Scripts
    scripts = data.get("scripts", {})
    if isinstance(scripts, dict):
        for name, info in scripts.items():
            if isinstance(info, dict):
                result["scripts"].append({
                    "name": name,
                    "path": info.get("path", ""),
                    "description": info.get("description", ""),
                    "usage": info.get("usage", ""),
                    "used_by": info.get("used_by", []),
                })

    # Packages
    packages = data.get("packages", {})
    if isinstance(packages, dict):
        for name, info in packages.items():
            if isinstance(info, dict):
                result["packages"].append({
                    "name": info.get("name", name),
                    "version": info.get("version", ""),
                    "description": info.get("description", ""),
                    "commands": list(info.get("commands", {}).keys())
                    if isinstance(info.get("commands"), dict)
                    else info.get("commands", []),
                })

    # Planned
    planned = data.get("planned", {})
    if isinstance(planned, dict):
        for name, info in planned.items():
            if isinstance(info, dict):
                result["planned"].append({
                    "name": name,
                    "purpose": info.get("purpose", ""),
                    "status": info.get("status", "planned"),
                })

    return result


# Agent scope and permission mapping from CLAUDE.md
_AGENT_SCOPE_MAP: dict[str, str] = {
    "ops": "macro",
    "audit": "macro",
}
_AGENT_PERMISSION_MAP: dict[str, str] = {
    "back": "Write backend code",
    "front": "Write frontend code",
    "ops": "Execute deployments",
    "persona": "Define user journeys",
}


def _parse_agents(agents_dir: Path) -> list[dict]:
    """Read YAML frontmatter from each .md agent file.

    Returns [{name, model, description, scope, exclusive_permission}].
    """
    if not agents_dir.exists() or not agents_dir.is_dir():
        return []

    agents: list[dict] = []
    for md_file in sorted(agents_dir.glob("*.md")):
        text = md_file.read_text()
        # Extract YAML frontmatter between --- delimiters
        match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not match:
            continue

        frontmatter: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                key, _, value = line.partition(":")
                frontmatter[key.strip()] = value.strip().strip("\"'")

        name = frontmatter.get("name", md_file.stem)
        agents.append({
            "name": name,
            "model": frontmatter.get("model", ""),
            "description": frontmatter.get("description", ""),
            "scope": _AGENT_SCOPE_MAP.get(name, "micro"),
            "exclusive_permission": _AGENT_PERMISSION_MAP.get(name, ""),
        })

    return agents


def _parse_commands(claude_md_path: Path) -> list[dict]:
    """Extract Available Commands table from CLAUDE.md.

    Returns [{name, description}].
    """
    if not claude_md_path.exists():
        return []

    text = claude_md_path.read_text()

    # Find "Available Commands" section
    match = re.search(
        r"##\s+Available Commands\s*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL
    )
    if not match:
        return []

    commands: list[dict] = []
    # Parse markdown table rows: | `command` | description |
    for row_match in re.finditer(
        r"\|\s*`([^`]+)`\s*\|\s*([^|]+)\|", match.group(1)
    ):
        name = row_match.group(1).strip()
        desc = row_match.group(2).strip()
        if name and desc and not name.startswith("-"):
            commands.append({"name": name, "description": desc})

    return commands


def _parse_patterns_index(path: Path) -> list[dict]:
    """Parse PATTERNS_INDEX.md for pattern categories.

    Returns [{category, templates: [{name, purpose}]}].
    """
    if not path.exists():
        return []

    text = path.read_text()
    categories: list[dict] = []

    # Find h3 headings under "Pattern Categories" that contain tables
    # Pattern: ### N. Category Name (`dir/`)
    sections = re.split(r"###\s+\d+\.\s+", text)
    for section in sections[1:]:  # Skip content before first ###
        # Extract category name
        name_match = re.match(r"([^(]+?)(?:\s*\(`[^`]*`\))?\s*\n", section)
        if not name_match:
            continue
        category_name = name_match.group(1).strip()

        # Extract table rows: | `template` | purpose | ... |
        templates: list[dict] = []
        for row_match in re.finditer(
            r"\|\s*`([^`]+)`\s*\|\s*([^|]+)\|", section
        ):
            tpl_name = row_match.group(1).strip()
            purpose = row_match.group(2).strip()
            if tpl_name and purpose and tpl_name != "Template":
                templates.append({"name": tpl_name, "purpose": purpose})

        if templates:
            categories.append({"category": category_name, "templates": templates})

    return categories


def _parse_coding_tips(path: Path) -> list[dict]:
    """Extract key sections from coding_standards.md.

    Returns [{category, items: [str]}].
    """
    if not path.exists():
        return []

    text = path.read_text()
    tips: list[dict] = []

    # Extract specific sections by heading
    section_headings = [
        "Verification Checkpoints",
        "Self-Audit Questions",
        "Strict Prohibitions",
    ]

    for heading in section_headings:
        # Match ## heading, **bold heading**, or **bold heading:** formats
        prefix = r"(?:#{1,3}\s*|(?<=\n)\*\*)"
        suffix = r".*?\n(.*?)(?=\n#{1,3}\s|\n\*\*[A-Z]|\Z)"
        pattern = re.compile(
            prefix + re.escape(heading) + suffix, re.DOTALL,
        )
        match = pattern.search(text)
        if not match:
            continue

        items: list[str] = []
        for line in match.group(1).splitlines():
            line = line.strip()
            # Capture bullet items (- item) and checkbox items (- [ ] item)
            bullet_match = re.match(r"^[-*]\s+(?:\[.\]\s+)?(.+)$", line)
            if bullet_match:
                items.append(bullet_match.group(1).strip())

        if items:
            tips.append({"category": heading, "items": items})

    return tips


def _parse_governance(claude_md_path: Path) -> dict:
    """Extract governance data from CLAUDE.md.

    Returns {prime_directive, permissions, lifecycle, rules}.
    """
    result: dict = {
        "prime_directive": "",
        "permissions": [],
        "lifecycle": "",
        "rules": [],
    }
    if not claude_md_path.exists():
        return result

    text = claude_md_path.read_text()

    # Prime Directive - extract quoted block
    pd_match = re.search(r">\s*\*\*(.+?)\*\*", text)
    if pd_match:
        result["prime_directive"] = pd_match.group(1).strip()

    # Exclusive Permissions table from Micro Agents table
    # Parse the micro agents table: | `agent` | model | description | permission |
    micro_match = re.search(
        r"###\s+Micro Agents.*?\n(.*?)(?=\n###|\n---|\Z)", text, re.DOTALL
    )
    if micro_match:
        for row in re.finditer(
            r"\|\s*`(\w+)`\s*\|\s*(\w+)\s*\|[^|]*\|\s*\*?\*?([^|]*?)\*?\*?\s*\|",
            micro_match.group(1),
        ):
            agent = row.group(1).strip()
            model = row.group(2).strip()
            perm = row.group(3).strip().strip("*")
            if perm and perm != "-":
                result["permissions"].append({
                    "agent": agent,
                    "model": model,
                    "exclusive_permission": perm,
                })

    # Agent Lifecycle diagram
    lifecycle_match = re.search(
        r"##\s+Agent Lifecycle\s*\n\s*```\s*\n(.*?)```",
        text,
        re.DOTALL,
    )
    if lifecycle_match:
        result["lifecycle"] = lifecycle_match.group(1).strip()

    # Governance Essentials - extract bullet items
    gov_match = re.search(
        r"##\s+Governance Essentials\s*\n(.*?)(?=\n---|\n##\s|\Z)",
        text,
        re.DOTALL,
    )
    if gov_match:
        rules: list[dict] = []
        for line in gov_match.group(1).splitlines():
            line = line.strip()
            bullet_match = re.match(r"^[-*]\s+\*\*(.+?)\*\*:\s*(.+)$", line)
            if bullet_match:
                rules.append({
                    "section": bullet_match.group(1).strip(),
                    "content": bullet_match.group(2).strip(),
                })
        if rules:
            result["rules"] = rules

    return result
