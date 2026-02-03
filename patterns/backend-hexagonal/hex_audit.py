#!/usr/bin/env python3
"""
Hexagonal Architecture Auditor

Validates that backend components follow canonical hexagonal structure.
Run as: python hex_audit.py [components_dir]

Exit codes:
  0 = All rules passed
  1 = Violations found
"""

import ast
import sys
from pathlib import Path
from typing import NamedTuple


class Violation(NamedTuple):
    file: str
    line: int
    rule: str
    message: str


def audit_component(component_dir: Path) -> list[Violation]:
    violations = []

    # ── STRUCTURAL AUDIT ──────────────────────────────────
    required_dirs = ["domain", "ports", "tests"]
    required_files = {
        "domain/model.py": "Domain model file is required",
        "domain/service.py": "Domain service file is required",
        "ports/inbound.py": "Inbound port definition is required",
        "ports/outbound.py": "Outbound port definition is required",
        "tests/conftest.py": "Test fixtures file is required",
        "README.md": "Component README is required",
        "__init__.py": "Public API file is required",
    }

    for d in required_dirs:
        if not (component_dir / d).is_dir():
            violations.append(Violation(
                str(component_dir), 0, "HEX001",
                f"Missing required directory: {d}/"
            ))

    for f, msg in required_files.items():
        if not (component_dir / f).exists():
            violations.append(Violation(
                str(component_dir / f), 0, "HEX002", msg
            ))

    # ── PORT INTERFACE AUDIT ──────────────────────────────
    ports_dir = component_dir / "ports"
    if ports_dir.is_dir():
        for port_file in ports_dir.glob("*.py"):
            if port_file.name == "__init__.py":
                continue
            try:
                tree = ast.parse(port_file.read_text())
            except SyntaxError:
                violations.append(Violation(
                    str(port_file), 0, "HEX010",
                    f"Syntax error in port file"
                ))
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    has_abc = False
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "ABC":
                            has_abc = True
                        if isinstance(base, ast.Attribute) and base.attr == "ABC":
                            has_abc = True

                    if not has_abc:
                        violations.append(Violation(
                            str(port_file), node.lineno, "HEX003",
                            f"Port class '{node.name}' must inherit from ABC"
                        ))

                    # Check all methods are abstract
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            is_abstract = any(
                                (isinstance(d, ast.Name) and d.id == "abstractmethod")
                                or (isinstance(d, ast.Attribute) and d.attr == "abstractmethod")
                                for d in item.decorator_list
                            )
                            if not is_abstract and item.name not in ("__init__", "__str__", "__repr__"):
                                violations.append(Violation(
                                    str(port_file), item.lineno, "HEX004",
                                    f"Port method '{node.name}.{item.name}' must be @abstractmethod"
                                ))
                            # Check return type annotation exists
                            if item.returns is None and item.name not in ("__init__", "__str__", "__repr__"):
                                violations.append(Violation(
                                    str(port_file), item.lineno, "HEX005",
                                    f"Port method '{node.name}.{item.name}' must have return type annotation"
                                ))

    # ── IN-MEMORY ADAPTER AUDIT ───────────────────────────
    outbound_dir = component_dir / "adapters" / "outbound"
    if outbound_dir.is_dir():
        infra_adapters = [
            f for f in outbound_dir.glob("*.py")
            if f.name not in ("__init__.py",) and not f.name.startswith("memory_")
        ]
        memory_adapters = list(outbound_dir.glob("memory_*.py"))

        for adapter in infra_adapters:
            expected_memory = outbound_dir / f"memory_{adapter.name}"
            if not expected_memory.exists() and not memory_adapters:
                violations.append(Violation(
                    str(adapter), 0, "HEX006",
                    f"Infrastructure adapter '{adapter.name}' has no corresponding "
                    f"'memory_{adapter.name}' test double"
                ))

    # ── DOMAIN MODEL PURITY AUDIT ─────────────────────────
    model_file = component_dir / "domain" / "model.py"
    if model_file.exists():
        try:
            tree = ast.parse(model_file.read_text())
        except SyntaxError:
            violations.append(Violation(
                str(model_file), 0, "HEX010",
                f"Syntax error in domain model"
            ))
        else:
            forbidden_imports = {
                "sqlalchemy", "pydantic", "django", "flask", "fastapi",
                "celery", "redis", "boto3", "httpx", "requests", "aiohttp",
            }
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root = alias.name.split(".")[0]
                        if root in forbidden_imports:
                            violations.append(Violation(
                                str(model_file), node.lineno, "HEX007",
                                f"Domain model imports forbidden framework: {alias.name}"
                            ))
                if isinstance(node, ast.ImportFrom) and node.module:
                    root = node.module.split(".")[0]
                    if root in forbidden_imports:
                        violations.append(Violation(
                            str(model_file), node.lineno, "HEX007",
                            f"Domain model imports forbidden framework: {node.module}"
                        ))

    # ── TEST STRUCTURE AUDIT ──────────────────────────────
    tests_dir = component_dir / "tests"
    if tests_dir.is_dir():
        unit_dir = tests_dir / "unit"
        integration_dir = tests_dir / "integration"

        if not unit_dir.is_dir() or not list(unit_dir.glob("test_*.py")):
            violations.append(Violation(
                str(tests_dir), 0, "HEX008",
                "Component must have unit tests in tests/unit/"
            ))
        if not integration_dir.is_dir() or not list(integration_dir.glob("test_*.py")):
            violations.append(Violation(
                str(tests_dir), 0, "HEX009",
                "Component must have integration tests in tests/integration/"
            ))

    return violations


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("components")

    if not root.exists():
        print(f"Directory not found: {root}")
        return 1

    all_violations: list[Violation] = []

    for component_dir in sorted(root.iterdir()):
        if component_dir.is_dir() and not component_dir.name.startswith(("_", ".")):
            all_violations.extend(audit_component(component_dir))

    if all_violations:
        print(f"\n{'='*70}")
        print(f"HEXAGONAL ARCHITECTURE VIOLATIONS: {len(all_violations)} found")
        print(f"{'='*70}\n")
        for v in all_violations:
            print(f"  {v.rule} | {v.file}:{v.line} | {v.message}")
        print(f"\n{'='*70}")
        return 1
    else:
        print("✓ All hexagonal architecture rules passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
