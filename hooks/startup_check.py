#!/usr/bin/env python3
"""
Claude Code Startup Check - Displays system status on session start.

This script is triggered by the user-prompt-submit hook on the first
prompt of each session. It checks:
1. MCP server connectivity and available tools
2. Available subagents from the prompts folder
3. Prime directives from the coding system prompt
"""

import json
import os
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
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Session tracking file
SESSION_FILE = Path.home() / ".claude" / ".current_session"


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


def check_mcp_tools() -> dict:
    """Check MCP server and get available tools."""
    result = {
        "connected": False,
        "tools": [],
        "adapters": {},
    }

    # Check if bureaucrat MCP is configured
    mcp_config = Path.home() / ".claude" / "mcp_servers.json"
    if not mcp_config.exists():
        return result

    try:
        config = json.loads(mcp_config.read_text())
        if "bureaucrat" in config:
            result["connected"] = True

            # Get rules path to check loaded integrations
            rules_path = config["bureaucrat"].get("env", {}).get(
                "BUREAUCRAT_MCP_RULES_PATH", ""
            )
            if rules_path and Path(rules_path).exists():
                import yaml
                rules = yaml.safe_load(Path(rules_path).read_text())

                # Extract enabled integrations
                features = rules.get("features", {})
                integrations = rules.get("integrations", {})

                adapters = {
                    "docker": features.get("enable_docker_integration", False),
                    "github": features.get("enable_github_integration", False),
                    "flyio": features.get("enable_flyio_integration", False),
                    "pytest": features.get("enable_pytest_integration", False),
                    "notebooklm": features.get("enable_notebooklm_integration", False),
                    "voice": "voice" in integrations,
                }
                result["adapters"] = adapters

                # List tool categories
                tools = []
                if adapters.get("docker"):
                    tools.extend(["docker_build", "docker_run", "docker_logs"])
                if adapters.get("github"):
                    tools.extend(["github_create_pr", "github_list_prs", "github_add_comment"])
                if adapters.get("flyio"):
                    tools.extend(["flyio_deploy", "flyio_status", "flyio_logs"])
                if adapters.get("pytest"):
                    tools.extend(["pytest_run", "ruff_check", "mypy_check"])
                if adapters.get("notebooklm"):
                    tools.extend(["notebooklm_create_notebook", "notebooklm_generate_artifact"])
                if adapters.get("voice"):
                    tools.extend(["voice_listen", "voice_speak"])

                # Always available
                tools.extend(["commission_job", "check_job", "validate_code"])
                result["tools"] = tools
    except Exception:
        pass

    return result


def check_credentials() -> dict:
    """Check available API credentials from Keychain and environment."""
    creds = {}

    # Credentials to check (key_name, display_name)
    credential_list = [
        ("GITHUB_TOKEN", "GitHub"),
        ("FLY_API_TOKEN", "Fly.io"),
        ("ELEVENLABS_API_KEY", "ElevenLabs"),
        ("GEMINI_API_KEY", "Gemini"),
        ("OPENAI_API_KEY", "OpenAI"),
    ]

    for key, name in credential_list:
        found = False

        # First check environment variable
        if os.environ.get(key):
            found = True
        else:
            # Check Keychain
            try:
                result = subprocess.run(
                    ["security", "find-generic-password", "-a", os.environ["USER"], "-s", key, "-w"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                # Check if we got actual output (password found) with exit code 0
                if result.returncode == 0 and result.stdout.strip():
                    found = True
            except Exception:
                pass

        creds[name] = found

    return creds


def check_agentic_hud() -> dict:
    """Check Agentic HUD status.

    Returns dict with:
        - running: bool - whether service is running
        - pid: int | None - process ID if running
        - dashboard_url: str | None - dashboard URL if running
    """
    result = {
        "running": False,
        "pid": None,
        "dashboard_url": None,
    }

    # Check PID file
    pid_file = Path.home() / ".agentic_hud" / "hud.pid"
    if not pid_file.exists():
        return result

    try:
        pid = int(pid_file.read_text().strip())
        # Check if process is alive
        os.kill(pid, 0)
        result["running"] = True
        result["pid"] = pid

        # Try to get dashboard URL from config
        config_file = Path.home() / ".agentic_hud" / "config.yaml"
        if config_file.exists():
            try:
                import yaml
                config = yaml.safe_load(config_file.read_text())
                host = config.get("dashboard", {}).get("host", "127.0.0.1")
                port = config.get("dashboard", {}).get("port", 8080)
                result["dashboard_url"] = f"http://{host}:{port}"
            except Exception:
                result["dashboard_url"] = "http://127.0.0.1:8080"

    except (ValueError, ProcessLookupError):
        # Invalid PID or process not found
        pass

    return result


def check_services() -> dict:
    """Check external service availability."""
    services = {}

    # Docker
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
        )
        services["Docker"] = result.returncode == 0
    except Exception:
        services["Docker"] = False

    # NotebookLM auth
    profile_dir = Path.home() / ".notebooklm-automation"
    cookies_file = profile_dir / "Default" / "Cookies"
    services["NotebookLM Auth"] = cookies_file.exists()

    # Agentic HUD
    hud_status = check_agentic_hud()
    services["Agentic HUD"] = hud_status["running"]

    return services


def get_available_agents() -> list:
    """Get list of available subagents from prompts folder."""
    agents_dir = Path.home() / "Developer" / "claude" / "prompts" / "agents"
    agents = []

    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            name = f.stem.replace("-", " ").replace("_", " ").title()
            agents.append({"name": name, "file": f.name})

    return agents


def get_prime_directives() -> list:
    """Extract prime directives from coding system prompt."""
    prompt_path = (
        Path.home() / "Developer" / "claude" / "prompts" /
        "system-prompts-v2" / "coding_system_prompt_v4_0_hex_tdd_8k.md"
    )

    directives = [
        "Every change must be task-scoped, atomic, deterministic, hexagonal, and evidenced.",
        "TDD: write or update tests first for substantive logic.",
        "Core logic depends only on models, domain logic, and port interfaces.",
        "No datetime.utcnow/now, no random, no global mutable state in core.",
        "Drift protocol: HALT and log EV entry if scope changes detected.",
    ]

    return directives


def print_startup_screen():
    """Print the startup status screen."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}  CLAUDE CODE - System Status{RESET}")
    print(f"{DIM}  {now}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")

    # MCP Status
    mcp = check_mcp_tools()
    print(f"{BOLD}MCP Server:{RESET}")
    status = f"{GREEN}Connected{RESET}" if mcp["connected"] else f"{RED}Disconnected{RESET}"
    print(f"  Status: {status}")

    if mcp["adapters"]:
        print(f"\n{BOLD}Adapters:{RESET}")
        for adapter, enabled in mcp["adapters"].items():
            icon = f"{GREEN}+{RESET}" if enabled else f"{RED}-{RESET}"
            print(f"  {icon} {adapter}")

    if mcp["tools"]:
        print(f"\n{BOLD}Available Tools:{RESET} {len(mcp['tools'])} registered")
        # Group by category
        categories = {
            "Docker": [t for t in mcp["tools"] if t.startswith("docker")],
            "GitHub": [t for t in mcp["tools"] if t.startswith("github")],
            "Fly.io": [t for t in mcp["tools"] if t.startswith("flyio")],
            "Quality": [t for t in mcp["tools"] if t in ["pytest_run", "ruff_check", "mypy_check"]],
            "NotebookLM": [t for t in mcp["tools"] if t.startswith("notebooklm")],
            "Voice": [t for t in mcp["tools"] if t.startswith("voice")],
            "Core": [t for t in mcp["tools"] if t in ["commission_job", "check_job", "validate_code"]],
        }
        for cat, tools in categories.items():
            if tools:
                print(f"  {DIM}{cat}:{RESET} {', '.join(tools)}")

    # Credentials
    print(f"\n{BOLD}Credentials:{RESET}")
    creds = check_credentials()
    for name, available in creds.items():
        icon = f"{GREEN}+{RESET}" if available else f"{YELLOW}?{RESET}"
        print(f"  {icon} {name}")

    # Services
    print(f"\n{BOLD}Services:{RESET}")
    services = check_services()
    for name, available in services.items():
        icon = f"{GREEN}+{RESET}" if available else f"{RED}-{RESET}"
        print(f"  {icon} {name}")

    # Agentic HUD details (if running)
    hud_status = check_agentic_hud()
    if hud_status["running"]:
        print(f"\n{BOLD}Agentic HUD:{RESET}")
        print(f"  PID: {hud_status['pid']}")
        if hud_status["dashboard_url"]:
            print(f"  Dashboard: {CYAN}{hud_status['dashboard_url']}{RESET}")

    # Agents
    print(f"\n{BOLD}Available Agents:{RESET}")
    agents = get_available_agents()
    for agent in agents:
        print(f"  {BLUE}>{RESET} {agent['name']}")

    # Prime Directives
    print(f"\n{BOLD}{YELLOW}Prime Directives:{RESET}")
    directives = get_prime_directives()
    for i, d in enumerate(directives, 1):
        print(f"  {i}. {d}")

    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{DIM}  Type /help for commands, /status for this screen anytime{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")


def main():
    """Main entry point."""
    # Check for force flag (used by /status command)
    force = "--force" in sys.argv or "-f" in sys.argv

    # Check if this is first prompt of session (unless forced)
    if not force and not should_show_startup():
        sys.exit(0)  # Already shown, silent exit

    print_startup_screen()
    sys.exit(0)


if __name__ == "__main__":
    main()
