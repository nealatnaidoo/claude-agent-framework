#!/usr/bin/env python3
"""CLI script to validate agent prompts against governance rules.

Usage:
    python validate_agents.py                    # Validate all agents
    python validate_agents.py path/to/agent.md  # Validate specific agent
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from claude_cli.agents.validator import AgentValidator, ValidationResult


def print_result(result: ValidationResult) -> None:
    """Print a single validation result."""
    status = "PASS" if result.passed else "FAIL"
    severity = result.severity.upper()
    print(f"  [{status}] {severity}: {result.message}")


def main() -> int:
    """CLI entry point."""
    # Default agents directory
    agents_dir = Path.home() / ".claude" / "agents"

    validator = AgentValidator()

    if len(sys.argv) > 1:
        # Validate specific file
        filepath = Path(sys.argv[1]).expanduser()
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            return 1

        print(f"\nValidating: {filepath.name}")
        print("=" * 50)
        results = validator.validate_file(filepath)

        errors = [r for r in results if not r.passed and r.severity == "error"]
        warnings = [r for r in results if not r.passed and r.severity == "warning"]
        passed = [r for r in results if r.passed]

        if errors:
            print("\nErrors:")
            for r in errors:
                print_result(r)

        if warnings:
            print("\nWarnings:")
            for r in warnings:
                print_result(r)

        print(f"\nSummary: {len(passed)} passed, {len(errors)} errors, {len(warnings)} warnings")

        return 1 if errors else 0

    else:
        # Validate all agents
        if not agents_dir.exists():
            print(f"Error: Agents directory not found: {agents_dir}")
            return 1

        print(f"\nValidating all agents in: {agents_dir}")
        print("=" * 60)

        all_results = validator.validate_all_agents(agents_dir)

        total_errors = 0
        total_warnings = 0
        total_agents = 0

        for agent_name, results in sorted(all_results.items()):
            total_agents += 1
            errors = [r for r in results if not r.passed and r.severity == "error"]
            warnings = [r for r in results if not r.passed and r.severity == "warning"]

            total_errors += len(errors)
            total_warnings += len(warnings)

            status = "PASS" if not errors else "FAIL"
            print(f"\n{agent_name}: {status}")

            if errors:
                for r in errors:
                    print_result(r)

            if warnings:
                for r in warnings:
                    print_result(r)

        print("\n" + "=" * 60)
        print(f"Total: {total_agents} agents, {total_errors} errors, {total_warnings} warnings")

        if total_errors == 0:
            print("All agents passed validation!")
            return 0
        else:
            print(f"Validation failed with {total_errors} error(s)")
            return 1


if __name__ == "__main__":
    sys.exit(main())
