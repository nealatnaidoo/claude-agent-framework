"""Schema drift detection for database harness."""

from dataclasses import dataclass, field
from typing import Any
import json


@dataclass
class DriftReport:
    """Report of schema differences between databases."""

    missing_tables: list[str] = field(default_factory=list)
    missing_columns: dict[str, list[str]] = field(default_factory=dict)
    type_mismatches: list[dict[str, str]] = field(default_factory=list)
    index_differences: list[dict[str, Any]] = field(default_factory=list)

    @property
    def has_breaking_changes(self) -> bool:
        """Check if there are breaking schema changes."""
        return bool(self.missing_tables or self.type_mismatches)

    def to_json(self) -> str:
        """Export report as JSON."""
        return json.dumps({
            "missing_tables": self.missing_tables,
            "missing_columns": self.missing_columns,
            "type_mismatches": self.type_mismatches,
            "index_differences": self.index_differences,
            "has_breaking_changes": self.has_breaking_changes,
        }, indent=2)


def detect_schema_drift(source_conn: str, target_conn: str) -> DriftReport:
    """Detect schema differences between source and target databases.

    Args:
        source_conn: Source database connection string (e.g., dev)
        target_conn: Target database connection string (e.g., staging)

    Returns:
        DriftReport with all detected differences.
    """
    # TODO: Implement actual database introspection
    # This is a stub that would connect to both databases and compare schemas

    # Example implementation outline:
    # 1. Connect to both databases
    # 2. Get list of tables from both
    # 3. Compare table lists
    # 4. For matching tables, compare columns
    # 5. Compare column types
    # 6. Compare indexes

    # For now, return empty report (no drift detected)
    return DriftReport()


def get_table_schema(conn: str, table: str) -> dict[str, Any]:
    """Get schema for a single table.

    Returns dict with:
    - columns: list of {name, type, nullable, default}
    - indexes: list of {name, columns, unique}
    - constraints: list of {name, type, definition}
    """
    # TODO: Implement actual schema introspection
    return {"columns": [], "indexes": [], "constraints": []}
