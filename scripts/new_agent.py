#!/usr/bin/env python3
"""
Guided Agent Creation Tool

Creates new agents with proper structure, dependencies, and manifest entries.
Ensures governance rules are followed and impact is analyzed before creation.

Usage:
    ./new_agent.py                     # Interactive guided creation
    ./new_agent.py --name my-agent     # Create with specified name
    ./new_agent.py --from-template X   # Clone from existing agent
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
AGENTS_DIR = REPO_ROOT / "agents"
TEMPLATES_DIR = REPO_ROOT / "templates"
MANIFEST_FILE = REPO_ROOT / "manifest.yaml"

sys.path.insert(0, str(SCRIPT_DIR))
from dependency_graph import build_graph
from impact_analysis import analyze_add_dependency


def slugify(name: str) -> str:
    """Convert name to valid agent slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def validate_name(name: str, existing_agents: set) -> tuple[bool, str]:
    """Validate agent name."""
    slug = slugify(name)

    if not slug:
        return False, "Name cannot be empty"

    if len(slug) < 3:
        return False, "Name must be at least 3 characters"

    if len(slug) > 30:
        return False, "Name must be 30 characters or less"

    if slug in existing_agents:
        return False, f"Agent '{slug}' already exists"

    if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', slug):
        return False, "Name must start with letter, contain only lowercase letters, numbers, and hyphens"

    return True, slug


def get_input(prompt: str, default: str = None, required: bool = True) -> str:
    """Get user input with optional default."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    while True:
        value = input(prompt).strip()

        if not value and default:
            return default

        if not value and required:
            print("  This field is required.")
            continue

        return value


def get_choice(prompt: str, choices: list, default: int = 0) -> str:
    """Get user choice from list."""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices):
        marker = "*" if i == default else " "
        print(f"  {marker} {i + 1}. {choice}")

    while True:
        value = input(f"Enter choice [1-{len(choices)}] (default: {default + 1}): ").strip()

        if not value:
            return choices[default]

        try:
            idx = int(value) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass

        print(f"  Please enter a number between 1 and {len(choices)}")


def get_multi_choice(prompt: str, choices: list) -> list:
    """Get multiple choices from list."""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices):
        print(f"  {i + 1}. {choice}")
    print("  (Enter numbers separated by commas, or 'none')")

    while True:
        value = input("Your choices: ").strip().lower()

        if value == "none" or value == "":
            return []

        try:
            indices = [int(x.strip()) - 1 for x in value.split(",")]
            selected = []
            for idx in indices:
                if 0 <= idx < len(choices):
                    selected.append(choices[idx])
                else:
                    raise ValueError()
            return selected
        except ValueError:
            print(f"  Please enter valid numbers between 1 and {len(choices)}")


def generate_agent_content(config: dict) -> str:
    """Generate agent markdown content from config."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Build frontmatter
    frontmatter_lines = [
        "---",
        f"name: {config['name']}",
        f"description: {config['description']}",
        f"scope: {config['scope']}",
        f"created: {now}",
        f"version: 1.0.0",
    ]

    if config.get("exclusive_permission"):
        frontmatter_lines.append(f"exclusive_permission: {config['exclusive_permission']}")

    if config.get("depends_on"):
        frontmatter_lines.append(f"depends_on: [{', '.join(config['depends_on'])}]")

    if config.get("tools"):
        frontmatter_lines.append(f"tools: [{', '.join(config['tools'])}]")

    frontmatter_lines.append(f"model: {config.get('model', 'sonnet')}")
    frontmatter_lines.append("---")

    # Build content
    content_lines = [
        "",
        f"# {config['name']}",
        "",
        f"> {config['description']}",
        "",
        "## Identity",
        "",
        f"You are **{config['name']}**, a {'macro' if config['scope'] == 'macro' else 'micro'} agent in the Claude Agent Framework.",
        "",
    ]

    if config.get("exclusive_permission"):
        content_lines.extend([
            f"**Exclusive Permission**: {config['exclusive_permission']}",
            "",
            "This permission is exclusively yours. No other agent may perform this action.",
            "",
        ])

    content_lines.extend([
        "## Entry Protocol",
        "",
        "On activation, you MUST:",
        "",
        "1. Read the project manifest: `{project}/.claude/manifest.yaml`",
        "2. Check your scope and permissions",
        "3. Verify any dependencies are satisfied",
        "",
    ])

    if config.get("depends_on"):
        content_lines.extend([
            "## Dependencies",
            "",
            "This agent depends on:",
            "",
        ])
        for dep in config["depends_on"]:
            content_lines.append(f"- **{dep}**: Must complete before this agent can proceed")
        content_lines.append("")

    content_lines.extend([
        "## Responsibilities",
        "",
        "### Primary Tasks",
        "",
        "1. [Define primary responsibility]",
        "2. [Define secondary responsibility]",
        "3. [Define tertiary responsibility]",
        "",
        "### Output Artifacts",
        "",
        "This agent produces:",
        "",
        "- `[artifact_name]`: [description]",
        "",
        "## Handoff",
        "",
        "When complete, this agent hands off to: [next-agent or 'user']",
        "",
        "## Constraints",
        "",
        "- [Define what this agent must NOT do]",
        "- [Define boundaries with other agents]",
        "",
        "## Evidence",
        "",
        "Task completion requires:",
        "",
        "- [ ] [Evidence item 1]",
        "- [ ] [Evidence item 2]",
        "",
    ])

    return "\n".join(frontmatter_lines) + "\n".join(content_lines)


def update_manifest(config: dict) -> bool:
    """Update manifest.yaml with new agent entry."""
    try:
        import yaml
    except ImportError:
        print("Warning: PyYAML not installed. Please update manifest.yaml manually.")
        return False

    if not MANIFEST_FILE.exists():
        print("Warning: manifest.yaml not found. Please create entry manually.")
        return False

    with open(MANIFEST_FILE) as f:
        manifest = yaml.safe_load(f)

    # Add agent entry
    if "agents" not in manifest:
        manifest["agents"] = {}

    manifest["agents"][config["name"]] = {
        "version": "1.0.0",
        "file": f"agents/{config['name']}.md",
        "scope": config["scope"],
        "depends_on": config.get("depends_on", []),
        "depended_by": [],
    }

    if config.get("exclusive_permission"):
        manifest["agents"][config["name"]]["exclusive_permission"] = config["exclusive_permission"]

    # Update depended_by for dependencies
    for dep in config.get("depends_on", []):
        if dep in manifest["agents"]:
            if "depended_by" not in manifest["agents"][dep]:
                manifest["agents"][dep]["depended_by"] = []
            if config["name"] not in manifest["agents"][dep]["depended_by"]:
                manifest["agents"][dep]["depended_by"].append(config["name"])

    with open(MANIFEST_FILE, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    return True


def interactive_creation(graph: dict) -> dict:
    """Guide user through agent creation interactively."""
    existing = set(graph.keys())

    print("\n" + "=" * 60)
    print("New Agent Creation Wizard")
    print("=" * 60)

    # Name
    print("\n1. AGENT NAME")
    while True:
        name = get_input("Enter agent name (e.g., 'my-new-agent')")
        valid, result = validate_name(name, existing)
        if valid:
            name = result
            break
        print(f"  Error: {result}")

    # Description
    print("\n2. DESCRIPTION")
    description = get_input("Brief description of what this agent does")

    # Scope
    print("\n3. SCOPE")
    scope = get_choice(
        "What is this agent's scope?",
        ["micro", "macro"],
        default=0
    )

    # Exclusive permission
    print("\n4. EXCLUSIVE PERMISSION")
    print("Does this agent need an exclusive permission?")
    print("(Exclusive permissions can only be held by one agent)")
    has_perm = get_choice(
        "Has exclusive permission?",
        ["No", "Yes"],
        default=0
    )

    exclusive_permission = None
    if has_perm == "Yes":
        exclusive_permission = get_input("What is the exclusive permission? (e.g., 'write_tests')")

    # Dependencies
    print("\n5. DEPENDENCIES")
    available_deps = sorted(existing)
    if available_deps:
        depends_on = get_multi_choice(
            "Which agents must complete before this one?",
            available_deps
        )
    else:
        depends_on = []

    # Check for circular dependencies
    for dep in depends_on:
        result = analyze_add_dependency(graph, dep, name)
        if "error" in result:
            print(f"\n  Warning: Cannot depend on {dep}: {result['error']}")
            depends_on.remove(dep)

    # Tools
    print("\n6. TOOLS")
    available_tools = ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebSearch", "WebFetch"]
    tools = get_multi_choice(
        "Which tools does this agent need?",
        available_tools
    )

    # Model
    print("\n7. MODEL")
    model = get_choice(
        "Which model should this agent use?",
        ["sonnet", "opus", "haiku"],
        default=0
    )

    return {
        "name": name,
        "description": description,
        "scope": scope,
        "exclusive_permission": exclusive_permission,
        "depends_on": depends_on,
        "tools": tools,
        "model": model,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Create new agent with governance checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--name", help="Agent name")
    parser.add_argument("--description", help="Agent description")
    parser.add_argument("--scope", choices=["micro", "macro"], default="micro")
    parser.add_argument("--depends-on", nargs="*", default=[], help="Dependencies")
    parser.add_argument("--from-template", metavar="AGENT", help="Clone from existing agent")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    parser.add_argument("--json", action="store_true", help="Output config as JSON")

    args = parser.parse_args()

    graph = build_graph()
    existing = set(graph.keys())

    # If cloning from template
    if args.from_template:
        if args.from_template not in existing:
            print(f"Template agent not found: {args.from_template}")
            print(f"Available: {', '.join(sorted(existing))}")
            return 1

        template_file = AGENTS_DIR / f"{args.from_template}.md"
        if not template_file.exists():
            print(f"Template file not found: {template_file}")
            return 1

        print(f"Cloning from: {args.from_template}")
        # For now, just copy the file structure
        # User will need to modify

    # Interactive or CLI mode
    if args.name:
        # CLI mode
        valid, result = validate_name(args.name, existing)
        if not valid:
            print(f"Error: {result}")
            return 1

        config = {
            "name": result,
            "description": args.description or f"[Description for {result}]",
            "scope": args.scope,
            "depends_on": args.depends_on,
            "tools": ["Read", "Glob", "Grep"],
            "model": "sonnet",
        }
    else:
        # Interactive mode
        config = interactive_creation(graph)

    if args.json:
        print(json.dumps(config, indent=2))
        return 0

    # Generate content
    content = generate_agent_content(config)

    # Show preview
    print("\n" + "=" * 60)
    print("PREVIEW")
    print("=" * 60)
    print(f"\nFile: agents/{config['name']}.md")
    print("-" * 40)
    print(content[:1000])
    if len(content) > 1000:
        print(f"... ({len(content) - 1000} more characters)")

    if args.dry_run:
        print("\n(dry-run mode - no files created)")
        return 0

    # Confirm
    print()
    confirm = input("Create this agent? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return 0

    # Create file
    agent_file = AGENTS_DIR / f"{config['name']}.md"
    agent_file.write_text(content)
    print(f"\nCreated: {agent_file}")

    # Update manifest
    if update_manifest(config):
        print(f"Updated: {MANIFEST_FILE}")
    else:
        print(f"\nManual step required: Add entry to {MANIFEST_FILE}")

    # Record in version history
    print("\nRecording in version history...")
    os.system(f"python3 {SCRIPT_DIR}/version_tracker.py scan")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print(f"""
1. Edit the agent file to add:
   - Detailed responsibilities
   - Output artifacts
   - Constraints and boundaries
   - Evidence requirements

2. Validate the agent:
   python3 scripts/validate_agents.py agents/{config['name']}.md

3. Update dependent agents if needed:
   python3 scripts/impact_analysis.py {config['name']}

4. Commit your changes:
   git add agents/{config['name']}.md manifest.yaml versions/history.json
   git commit -m "Add {config['name']} agent"
""")

    return 0


if __name__ == "__main__":
    sys.exit(main())
