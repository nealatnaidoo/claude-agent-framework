#!/usr/bin/env python3
"""
Agent Prompt Validator v1.0

Validates that agent prompt files conform to the agent operating model.

Usage:
    python validate_agents.py                    # Validate all agents
    python validate_agents.py agent.md           # Validate specific agent
    python validate_agents.py --verbose          # Show detailed output

Exit codes:
    0 - All validations passed
    1 - Validation errors found
    2 - File not found or unreadable
"""

import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    name: str
    passed: bool
    severity: str  # "error" or "warning"
    message: str


class AgentValidator:
    """Validates agent prompt files against the agent operating model."""

    AGENTS_DIR = Path.home() / ".claude" / "agents"

    # Forbidden patterns that indicate hardcoded paths
    FORBIDDEN_PATTERNS = [
        (r'\{project\}_spec\.md', "Use manifest.artifact_versions.spec.file"),
        (r'\{project\}_tasklist\.md', "Use manifest.artifact_versions.tasklist.file"),
        (r'\{project_slug\}_spec', "Use manifest.artifact_versions.spec.file"),
        (r'\{project_slug\}_tasklist', "Use manifest.artifact_versions.tasklist.file"),
        (r'artifacts/test_report\.json', "Use .claude/evidence/test_report.json"),
        (r'artifacts/quality_gates', "Use .claude/evidence/quality_gates_run.json"),
        (r'artifacts/lint_report', "Use .claude/evidence/lint_report.json"),
        (r'^artifacts/', "Use .claude/artifacts/ with full path"),
        (r'^evidence/', "Use .claude/evidence/ with full path"),
        (r'^remediation/', "Use .claude/remediation/ with full path"),
    ]

    # Required patterns for different checks
    IDENTITY_INTERNAL = [
        r'\*\*INTERNAL agent\*\*',
        r'core development workflow',
    ]

    IDENTITY_VISITING = [
        r'\*\*VISITING agent\*\*',
        r'not an internal agent',
    ]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[ValidationResult] = []

    def validate_file(self, filepath: Path) -> list[ValidationResult]:
        """Validate a single agent prompt file."""
        self.results = []

        if not filepath.exists():
            return [ValidationResult(
                name="file_exists",
                passed=False,
                severity="error",
                message=f"File not found: {filepath}"
            )]

        content = filepath.read_text()

        # Run all validations
        self._check_frontmatter(content, filepath)
        self._check_identity_section(content)
        self._check_entry_protocol(content)
        self._check_forbidden_patterns(content)
        self._check_output_locations(content)
        self._check_id_sequencing(content)
        self._check_manifest_update(content)
        self._check_compliance_reference(content)

        return self.results

    def _check_frontmatter(self, content: str, filepath: Path):
        """Check YAML frontmatter exists and has required fields."""
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)

        if not frontmatter_match:
            self.results.append(ValidationResult(
                name="frontmatter_exists",
                passed=False,
                severity="error",
                message="Missing YAML frontmatter (---)"
            ))
            return

        frontmatter = frontmatter_match.group(1)

        # Check required fields
        required_fields = ['name', 'description', 'tools', 'model']
        for field in required_fields:
            if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
                self.results.append(ValidationResult(
                    name=f"frontmatter_{field}",
                    passed=False,
                    severity="error",
                    message=f"Missing required frontmatter field: {field}"
                ))
            else:
                self.results.append(ValidationResult(
                    name=f"frontmatter_{field}",
                    passed=True,
                    severity="error",
                    message=f"Frontmatter field '{field}' present"
                ))

        # Check model is valid
        model_match = re.search(r'^model:\s*(\w+)', frontmatter, re.MULTILINE)
        if model_match:
            model = model_match.group(1)
            if model not in ['sonnet', 'opus', 'haiku']:
                self.results.append(ValidationResult(
                    name="frontmatter_model_valid",
                    passed=False,
                    severity="error",
                    message=f"Invalid model '{model}'. Must be sonnet, opus, or haiku"
                ))

    def _check_identity_section(self, content: str):
        """Check identity section exists and declares type."""
        # Check for identity section
        if not re.search(r'##\s*Identity', content, re.IGNORECASE):
            self.results.append(ValidationResult(
                name="identity_section_exists",
                passed=False,
                severity="error",
                message="Missing '## Identity' section"
            ))
            return

        self.results.append(ValidationResult(
            name="identity_section_exists",
            passed=True,
            severity="error",
            message="Identity section present"
        ))

        # Check for identity type declaration
        is_internal = any(re.search(p, content) for p in self.IDENTITY_INTERNAL)
        is_visiting = any(re.search(p, content) for p in self.IDENTITY_VISITING)

        if not is_internal and not is_visiting:
            self.results.append(ValidationResult(
                name="identity_type_declared",
                passed=False,
                severity="error",
                message="Identity must declare INTERNAL or VISITING agent type"
            ))
        elif is_internal and is_visiting:
            self.results.append(ValidationResult(
                name="identity_type_declared",
                passed=False,
                severity="error",
                message="Identity declares both INTERNAL and VISITING - choose one"
            ))
        else:
            agent_type = "INTERNAL" if is_internal else "VISITING"
            self.results.append(ValidationResult(
                name="identity_type_declared",
                passed=True,
                severity="error",
                message=f"Identity declares {agent_type} agent"
            ))

    def _check_entry_protocol(self, content: str):
        """Check entry/startup protocol exists and reads manifest first."""
        # Check for startup/entry protocol section
        has_protocol = bool(re.search(
            r'##\s*(Startup Protocol|Entry Protocol|Startup|Entry)',
            content, re.IGNORECASE
        ))

        if not has_protocol:
            self.results.append(ValidationResult(
                name="entry_protocol_exists",
                passed=False,
                severity="error",
                message="Missing startup/entry protocol section"
            ))
            return

        self.results.append(ValidationResult(
            name="entry_protocol_exists",
            passed=True,
            severity="error",
            message="Entry protocol section present"
        ))

        # Check manifest is read first
        manifest_patterns = [
            r'read manifest.*first',
            r'manifest\.yaml',
            r'Read manifest FIRST',
            r'\.claude/manifest\.yaml',
        ]

        reads_manifest = any(re.search(p, content, re.IGNORECASE) for p in manifest_patterns)

        if not reads_manifest:
            self.results.append(ValidationResult(
                name="manifest_read_first",
                passed=False,
                severity="error",
                message="Entry protocol must read manifest.yaml first"
            ))
        else:
            self.results.append(ValidationResult(
                name="manifest_read_first",
                passed=True,
                severity="error",
                message="Entry protocol references manifest"
            ))

    def _check_forbidden_patterns(self, content: str):
        """Check for forbidden hardcoded path patterns."""
        found_violations = []

        for pattern, fix in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                found_violations.append((pattern, fix))

        if found_violations:
            for pattern, fix in found_violations:
                self.results.append(ValidationResult(
                    name="no_hardcoded_paths",
                    passed=False,
                    severity="error",
                    message=f"Forbidden pattern '{pattern}' found. {fix}"
                ))
        else:
            self.results.append(ValidationResult(
                name="no_hardcoded_paths",
                passed=True,
                severity="error",
                message="No forbidden hardcoded path patterns found"
            ))

    def _check_output_locations(self, content: str):
        """Check output paths use correct .claude/ prefix."""
        # Look for output location section
        output_patterns = [
            r'\.claude/artifacts/',
            r'\.claude/evidence/',
            r'\.claude/remediation/',
            r'\.claude/evolution/',
        ]

        has_correct_paths = any(re.search(p, content) for p in output_patterns)

        if not has_correct_paths:
            self.results.append(ValidationResult(
                name="correct_output_locations",
                passed=False,
                severity="warning",
                message="No .claude/ output paths found. Ensure outputs use .claude/{folder}/"
            ))
        else:
            self.results.append(ValidationResult(
                name="correct_output_locations",
                passed=True,
                severity="warning",
                message="Output paths use .claude/ prefix"
            ))

    def _check_id_sequencing(self, content: str):
        """Check ID sequencing protocol if agent creates BUG/IMPROVE IDs."""
        # Check if this agent creates bugs or improvements
        creates_ids = bool(re.search(r'BUG-|IMPROVE-', content))

        if not creates_ids:
            # Skip this check if agent doesn't create IDs
            return

        # Check for ID sequencing documentation
        sequencing_patterns = [
            r'ID Sequencing',
            r'search.*existing.*ID',
            r'increment.*highest',
            r'project-global',
            r'never reused',
        ]

        has_sequencing = sum(1 for p in sequencing_patterns if re.search(p, content, re.IGNORECASE))

        if has_sequencing < 2:
            self.results.append(ValidationResult(
                name="id_sequencing_documented",
                passed=False,
                severity="warning",
                message="Agent creates BUG/IMPROVE IDs but lacks ID sequencing documentation"
            ))
        else:
            self.results.append(ValidationResult(
                name="id_sequencing_documented",
                passed=True,
                severity="warning",
                message="ID sequencing protocol documented"
            ))

    def _check_manifest_update(self, content: str):
        """Check manifest update protocol is documented."""
        update_patterns = [
            r'Manifest Update',
            r'update.*manifest',
            r'manifest\.yaml.*update',
        ]

        has_update_doc = any(re.search(p, content, re.IGNORECASE) for p in update_patterns)

        if not has_update_doc:
            self.results.append(ValidationResult(
                name="manifest_update_documented",
                passed=False,
                severity="warning",
                message="Missing manifest update protocol documentation"
            ))
        else:
            self.results.append(ValidationResult(
                name="manifest_update_documented",
                passed=True,
                severity="warning",
                message="Manifest update protocol documented"
            ))

    def _check_compliance_reference(self, content: str):
        """Check for Prime Directive or compliance reference."""
        compliance_patterns = [
            r'Prime Directive',
            r'task-scoped.*atomic.*deterministic.*hexagonal.*evidenced',
            r'Compliance',
            r'hexagonal architecture',
        ]

        has_compliance = any(re.search(p, content, re.IGNORECASE) for p in compliance_patterns)

        if not has_compliance:
            self.results.append(ValidationResult(
                name="compliance_referenced",
                passed=False,
                severity="warning",
                message="No Prime Directive or compliance reference found"
            ))
        else:
            self.results.append(ValidationResult(
                name="compliance_referenced",
                passed=True,
                severity="warning",
                message="Compliance requirements referenced"
            ))

    def validate_all_agents(self) -> dict[str, list[ValidationResult]]:
        """Validate all agent files in the agents directory."""
        results = {}

        if not self.AGENTS_DIR.exists():
            print(f"Agents directory not found: {self.AGENTS_DIR}")
            return results

        for agent_file in self.AGENTS_DIR.glob("*.md"):
            # Skip template files
            if "template" in agent_file.name.lower():
                continue

            results[agent_file.name] = self.validate_file(agent_file)

        return results

    def print_results(self, results: list[ValidationResult], filename: str = ""):
        """Print validation results."""
        if filename:
            print(f"\n{'='*60}")
            print(f"Validating: {filename}")
            print('='*60)

        errors = [r for r in results if not r.passed and r.severity == "error"]
        warnings = [r for r in results if not r.passed and r.severity == "warning"]
        passed = [r for r in results if r.passed]

        if self.verbose:
            print("\nPassed checks:")
            for r in passed:
                print(f"  [PASS] {r.name}: {r.message}")

        if warnings:
            print("\nWarnings:")
            for r in warnings:
                print(f"  [WARN] {r.name}: {r.message}")

        if errors:
            print("\nErrors:")
            for r in errors:
                print(f"  [FAIL] {r.name}: {r.message}")

        # Summary
        print(f"\nSummary: {len(passed)} passed, {len(warnings)} warnings, {len(errors)} errors")

        return len(errors) == 0


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    validator = AgentValidator(verbose=verbose)

    if args:
        # Validate specific file(s)
        all_passed = True
        for filepath in args:
            path = Path(filepath)
            if not path.is_absolute():
                # Try relative to agents dir
                agents_path = validator.AGENTS_DIR / filepath
                if agents_path.exists():
                    path = agents_path
                else:
                    path = Path(filepath)

            results = validator.validate_file(path)
            passed = validator.print_results(results, path.name)
            if not passed:
                all_passed = False

        sys.exit(0 if all_passed else 1)
    else:
        # Validate all agents
        print("Validating all agents in ~/.claude/agents/")
        all_results = validator.validate_all_agents()

        if not all_results:
            print("No agent files found.")
            sys.exit(2)

        all_passed = True
        for filename, results in all_results.items():
            passed = validator.print_results(results, filename)
            if not passed:
                all_passed = False

        print("\n" + "="*60)
        print(f"Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
        print("="*60)

        sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
