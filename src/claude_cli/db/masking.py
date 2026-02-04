"""PII masking operations for database harness."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class MaskingResult:
    """Result of PII masking operation."""

    changes: list[dict[str, Any]] = field(default_factory=list)
    total_rows: int = 0
    dry_run: bool = True


@dataclass
class MaskingRule:
    """A single PII masking rule."""

    table: str
    column: str
    pattern: str  # 'email', 'phone', 'name', 'address', 'custom'
    replacement: str  # Replacement pattern or value


def load_masking_rules(rules_path: str) -> list[MaskingRule]:
    """Load masking rules from YAML file."""
    path = Path(rules_path)
    if not path.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_path}")

    with open(path) as f:
        config = yaml.safe_load(f)

    rules = []
    for rule_def in config.get("rules", []):
        rules.append(MaskingRule(
            table=rule_def["table"],
            column=rule_def["column"],
            pattern=rule_def.get("pattern", "custom"),
            replacement=rule_def.get("replacement", "***MASKED***"),
        ))

    return rules


def apply_pii_masking(
    connection: str,
    rules_path: str,
    dry_run: bool = True,
) -> MaskingResult:
    """Apply PII masking rules to database.

    Args:
        connection: Database connection string.
        rules_path: Path to masking rules YAML.
        dry_run: If True, only preview changes.

    Returns:
        MaskingResult with affected rows.
    """
    rules = load_masking_rules(rules_path)

    # TODO: Implement actual masking
    # For each rule:
    # 1. Count rows that would be affected
    # 2. If not dry_run, apply UPDATE with masking function

    result = MaskingResult(dry_run=dry_run)

    for rule in rules:
        # Simulate finding rows to mask
        # In real implementation, this would query the database
        result.changes.append({
            "table": rule.table,
            "column": rule.column,
            "rows": 0,  # Would be actual count
        })

    return result


def mask_email(email: str) -> str:
    """Mask an email address."""
    if "@" not in email:
        return "***@***.***"
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain}"


def mask_phone(phone: str) -> str:
    """Mask a phone number."""
    # Keep last 4 digits
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    return "***-***-****"


def mask_name(name: str) -> str:
    """Mask a name."""
    parts = name.split()
    if parts:
        return f"{parts[0][0]}. {'*' * 5}"
    return "*** ***"
