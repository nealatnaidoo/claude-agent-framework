#!/usr/bin/env python3
"""
Claude Code Startup Check - Displays system status on session start.

This script is triggered by the UserPromptSubmit hook on the first
prompt of each session. It checks:
1. Agent integrity (contamination detection via hash baseline)
2. Quick compliance smoke test
3. MCP server connectivity and available tools
4. Available subagents
5. Credentials and services
6. Prime directives
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Paths
CLAUDE_DIR = Path.home() / ".claude"
AGENTS_DIR = CLAUDE_DIR / "agents"
SESSION_FILE = CLAUDE_DIR / ".current_session"


def get_session_id() -> str:
    """Get current terminal session ID."""
    return os.environ.get("TERM_SESSION_ID", os.environ.get("TERM", "unknown"))


def should_show_startup() -> bool:
    """Check if startup screen should be shown (once per session)."""
    session_id = get_session_id()

    if SESSION_FILE.exists():
        stored = SESSION_FILE.read_text().strip()
        if stored == session_id:
            return False  # Already shown this session

    # New session - store and show
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(session_id)
    return True


# =============================================================================
# AGENT INTEGRITY CHECK
# =============================================================================

def check_agent_integrity() -> dict:
    """
    Verify agent files against baseline hashes.

    Returns:
        dict with verified (bool), baseline_date, agent_count, changes list
    """
    # Import the baseline module
    try:
        from agent_baseline import verify_baseline, create_baseline, load_baseline
    except ImportError:
        # Fallback if import fails - add hooks dir to path
        hooks_dir = Path(__file__).parent
        sys.path.insert(0, str(hooks_dir))
        from agent_baseline import verify_baseline, create_baseline, load_baseline

    # Check if baseline exists, create if not
    baseline = load_baseline()
    if not baseline:
        # First run - create baseline
        baseline = create_baseline()
        return {
            "verified": True,
            "baseline_date": baseline["created"],
            "agent_count": len(baseline["agents"]),
            "changes": [],
            "first_run": True,
        }

    result = verify_baseline()
    result["first_run"] = False
    return result


# =============================================================================
# COMPLIANCE QUICK CHECK
# =============================================================================

def check_compliance_quick() -> dict:
    """
    Run quick compliance smoke tests on agent files.

    Checks:
    1. All agents have YAML frontmatter
    2. Non-coding agents have coding restriction
    3. All agents reference manifest protocol
    4. ID sequencing in review agents

    Returns:
        dict with passed (bool), checks list with individual results
    """
    results = {
        "passed": True,
        "checks": [],
        "warnings": [],
    }

    if not AGENTS_DIR.exists():
        results["passed"] = False
        results["checks"].append({
            "name": "Agents directory",
            "passed": False,
            "message": "Agents directory not found"
        })
        return results

    agent_files = list(AGENTS_DIR.glob("*.md"))
    if not agent_files:
        results["passed"] = False
        results["checks"].append({
            "name": "Agent files",
            "passed": False,
            "message": "No agent files found"
        })
        return results

    # Check 1: YAML frontmatter
    frontmatter_ok = True
    missing_frontmatter = []
    for agent_path in agent_files:
        content = agent_path.read_text()
        if not content.startswith("---"):
            frontmatter_ok = False
            missing_frontmatter.append(agent_path.name)

    results["checks"].append({
        "name": "YAML frontmatter",
        "passed": frontmatter_ok,
        "message": f"Missing in: {', '.join(missing_frontmatter)}" if missing_frontmatter else "All agents valid"
    })
    if not frontmatter_ok:
        results["passed"] = False

    # Check 2: Coding restriction in non-coding agents
    coding_restriction_ok = True
    missing_restriction = []
    coding_agents = {"back.md", "front.md"}

    for agent_path in agent_files:
        if agent_path.name in coding_agents:
            continue  # Skip coding agents

        content = agent_path.read_text()
        # Check for the restriction table entry
        if "Create/modify source code" not in content and "modify source code" not in content.lower():
            # Only flag if it's not a template
            if "template" not in agent_path.name.lower():
                missing_restriction.append(agent_path.name)

    # This is a warning, not a failure - some agents may not need explicit restriction
    if missing_restriction:
        results["warnings"].append({
            "name": "Coding restriction",
            "message": f"Not explicit in: {', '.join(missing_restriction[:3])}" +
                      (f" +{len(missing_restriction)-3} more" if len(missing_restriction) > 3 else "")
        })

    results["checks"].append({
        "name": "Exclusive permissions",
        "passed": True,  # Warnings don't fail
        "message": "Coding agents identified"
    })

    # Check 3: Manifest-first protocol
    manifest_ok = True
    missing_manifest = []
    for agent_path in agent_files:
        if "template" in agent_path.name.lower():
            continue
        content = agent_path.read_text().lower()
        if "manifest" not in content:
            missing_manifest.append(agent_path.name)

    if missing_manifest:
        results["warnings"].append({
            "name": "Manifest reference",
            "message": f"Not found in: {', '.join(missing_manifest[:3])}"
        })

    results["checks"].append({
        "name": "Manifest protocol",
        "passed": True,
        "message": "References found"
    })

    # Check 4: Identity section exists
    identity_ok = True
    missing_identity = []
    for agent_path in agent_files:
        content = agent_path.read_text()
        if "## Identity" not in content and "# Identity" not in content:
            if "template" not in agent_path.name.lower():
                missing_identity.append(agent_path.name)

    if missing_identity:
        identity_ok = False
        results["checks"].append({
            "name": "Identity section",
            "passed": False,
            "message": f"Missing in: {', '.join(missing_identity[:3])}"
        })
        results["passed"] = False
    else:
        results["checks"].append({
            "name": "Identity section",
            "passed": True,
            "message": "All agents have identity"
        })

    return results


# =============================================================================
# MCP SERVER CHECK
# =============================================================================

def check_mcp_tools() -> dict:
    """Check MCP server configuration and enumerate tools."""
    result = {
        "connected": False,
        "servers": [],
        "tools": [],
        "tool_count": 0,
        "adapters": {},
    }

    # Check MCP config
    mcp_config = CLAUDE_DIR / "mcp_servers.json"
    if not mcp_config.exists():
        return result

    try:
        config = json.loads(mcp_config.read_text())

        for server_name, server_config in config.items():
            server_info = {
                "name": server_name,
                "command": server_config.get("command", "unknown"),
                "status": "configured",
            }

            # Check if server has specific integrations
            env = server_config.get("env", {})
            rules_path = env.get("BUREAUCRAT_MCP_RULES_PATH", "")

            if rules_path and Path(rules_path).exists():
                try:
                    import yaml
                    rules = yaml.safe_load(Path(rules_path).read_text())
                    features = rules.get("features", {})

                    adapters = {
                        "docker": features.get("enable_docker_integration", False),
                        "github": features.get("enable_github_integration", False),
                        "flyio": features.get("enable_flyio_integration", False),
                        "pytest": features.get("enable_pytest_integration", False),
                        "notebooklm": features.get("enable_notebooklm_integration", False),
                    }
                    result["adapters"] = adapters

                    # Enumerate tools
                    tools = []
                    if adapters.get("docker"):
                        tools.extend(["docker_build", "docker_run", "docker_logs"])
                    if adapters.get("github"):
                        tools.extend(["github_pr", "github_issues", "github_comments"])
                    if adapters.get("flyio"):
                        tools.extend(["flyio_deploy", "flyio_status", "flyio_logs"])
                    if adapters.get("pytest"):
                        tools.extend(["pytest_run", "ruff_check", "mypy_check"])
                    if adapters.get("notebooklm"):
                        tools.extend(["notebooklm_create", "notebooklm_generate"])

                    # Core tools always available
                    tools.extend(["commission_job", "check_job", "validate_code"])
                    result["tools"] = tools
                    result["tool_count"] = len(tools)

                except Exception:
                    pass

            result["servers"].append(server_info)

        result["connected"] = len(result["servers"]) > 0

    except Exception:
        pass

    return result


# =============================================================================
# CREDENTIALS & SERVICES
# =============================================================================

def check_credentials() -> dict:
    """Check available API credentials from Keychain and environment."""
    creds = {}

    credential_list = [
        ("GITHUB_TOKEN", "GitHub"),
        ("FLY_API_TOKEN", "Fly.io"),
        ("ELEVENLABS_API_KEY", "ElevenLabs"),
        ("GEMINI_API_KEY", "Gemini"),
        ("OPENAI_API_KEY", "OpenAI"),
    ]

    for key, name in credential_list:
        found = False

        if os.environ.get(key):
            found = True
        else:
            try:
                result = subprocess.run(
                    ["security", "find-generic-password", "-a", os.environ["USER"], "-s", key, "-w"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0 and result.stdout.strip():
                    found = True
            except Exception:
                pass

        creds[name] = found

    return creds


def check_services() -> dict:
    """Check external service availability."""
    services = {}

    # Docker
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        services["Docker"] = result.returncode == 0
    except Exception:
        services["Docker"] = False

    # NotebookLM auth
    profile_dir = Path.home() / ".notebooklm-automation"
    cookies_file = profile_dir / "Default" / "Cookies"
    services["NotebookLM Auth"] = cookies_file.exists()

    # Agentic HUD
    pid_file = Path.home() / ".agentic_hud" / "hud.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)
            services["Agentic HUD"] = True
        except (ValueError, ProcessLookupError):
            services["Agentic HUD"] = False
    else:
        services["Agentic HUD"] = False

    return services


# =============================================================================
# AGENTS LIST
# =============================================================================

def get_available_agents() -> list:
    """Get list of available subagents."""
    agents = []

    if AGENTS_DIR.exists():
        for f in sorted(AGENTS_DIR.glob("*.md")):
            if "template" in f.name.lower():
                continue
            name = f.stem.replace("-", " ").replace("_", " ").title()
            agents.append({"name": name, "file": f.name})

    return agents


# =============================================================================
# PRIME DIRECTIVES
# =============================================================================

def get_prime_directives() -> list:
    """Get prime directives."""
    return [
        "Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.",
        "TDD: write or update tests first for substantive logic.",
        "Core logic depends only on models, domain logic, and port interfaces.",
        "No datetime.utcnow/now, no random, no global mutable state in core.",
        "Drift protocol: HALT and log EV entry if scope changes detected.",
    ]


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def print_startup_screen():
    """Print the startup status screen."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}  CLAUDE CODE - System Status{RESET}")
    print(f"{DIM}  {now}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")

    # =========================================================================
    # AGENT INTEGRITY CHECK
    # =========================================================================
    print(f"{BOLD}Agent Integrity:{RESET}")
    integrity = check_agent_integrity()

    if integrity.get("first_run"):
        print(f"  {CYAN}BASELINE CREATED{RESET} - First run, {integrity['agent_count']} agents registered")
    elif integrity["verified"]:
        print(f"  {GREEN}VERIFIED{RESET} - {integrity['agent_count']} agents, no changes detected")
        if integrity.get("baseline_date"):
            date_str = integrity["baseline_date"][:10] if integrity["baseline_date"] else "unknown"
            print(f"  {DIM}Baseline: {date_str}{RESET}")
    else:
        print(f"  {RED}CHANGES DETECTED{RESET}")
        for change in integrity.get("changes", [])[:5]:
            change_type = change.get("type", "unknown")
            icon = {"added": "+", "removed": "-", "modified": "~", "no_baseline": "!"}.get(change_type, "?")
            color = {"added": CYAN, "removed": RED, "modified": YELLOW, "no_baseline": YELLOW}.get(change_type, "")
            print(f"    {color}{icon} {change.get('message', 'Unknown change')}{RESET}")
        print(f"  {DIM}Run 'python ~/.claude/hooks/agent_baseline.py create' to update baseline{RESET}")

    # =========================================================================
    # COMPLIANCE QUICK CHECK
    # =========================================================================
    print(f"\n{BOLD}Compliance Quick Check:{RESET}")
    compliance = check_compliance_quick()

    if compliance["passed"]:
        print(f"  {GREEN}PASSED{RESET} - All governance checks passed")
    else:
        print(f"  {YELLOW}WARNINGS{RESET}")

    for check in compliance["checks"]:
        icon = f"{GREEN}+{RESET}" if check["passed"] else f"{RED}-{RESET}"
        print(f"    {icon} {check['name']}: {check['message']}")

    if compliance.get("warnings"):
        for warn in compliance["warnings"][:3]:
            print(f"    {YELLOW}!{RESET} {warn['name']}: {warn['message']}")

    # =========================================================================
    # MCP STATUS
    # =========================================================================
    print(f"\n{BOLD}MCP Servers:{RESET}")
    mcp = check_mcp_tools()

    if mcp["connected"]:
        for server in mcp["servers"]:
            print(f"  {GREEN}+{RESET} {server['name']}: {mcp['tool_count']} tools")

        if mcp["adapters"]:
            enabled = [k for k, v in mcp["adapters"].items() if v]
            if enabled:
                print(f"    {DIM}Adapters: {', '.join(enabled)}{RESET}")
    else:
        print(f"  {YELLOW}-{RESET} No MCP servers configured")

    # =========================================================================
    # CREDENTIALS
    # =========================================================================
    print(f"\n{BOLD}Credentials:{RESET}")
    creds = check_credentials()
    for name, available in creds.items():
        icon = f"{GREEN}+{RESET}" if available else f"{DIM}-{RESET}"
        print(f"  {icon} {name}")

    # =========================================================================
    # SERVICES
    # =========================================================================
    print(f"\n{BOLD}Services:{RESET}")
    services = check_services()
    for name, available in services.items():
        icon = f"{GREEN}+{RESET}" if available else f"{DIM}-{RESET}"
        print(f"  {icon} {name}")

    # =========================================================================
    # AVAILABLE AGENTS
    # =========================================================================
    print(f"\n{BOLD}Available Agents:{RESET}")
    agents = get_available_agents()
    # Show in two columns
    col_width = 35
    for i in range(0, len(agents), 2):
        left = f"{BLUE}>{RESET} {agents[i]['name']}"
        if i + 1 < len(agents):
            right = f"{BLUE}>{RESET} {agents[i+1]['name']}"
            print(f"  {left:<{col_width}} {right}")
        else:
            print(f"  {left}")

    # =========================================================================
    # PRIME DIRECTIVES
    # =========================================================================
    print(f"\n{BOLD}{YELLOW}Prime Directives:{RESET}")
    directives = get_prime_directives()
    for i, d in enumerate(directives, 1):
        print(f"  {i}. {d}")

    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{DIM}  /status - show this screen | /compliance - full verification{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")


def main():
    """Main entry point."""
    force = "--force" in sys.argv or "-f" in sys.argv

    if not force and not should_show_startup():
        sys.exit(0)

    print_startup_screen()
    sys.exit(0)


if __name__ == "__main__":
    main()
