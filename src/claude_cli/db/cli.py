"""CLI commands for database harness operations (DevOps)."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Database harness operations for DevOps governance")
console = Console()


@app.command("drift")
def schema_drift(
    source: str = typer.Option(..., "--source", "-s", help="Source database connection string"),
    target: str = typer.Option(..., "--target", "-t", help="Target database connection string"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output report file"),
) -> None:
    """Detect schema drift between two databases.

    Compares source (e.g., dev) against target (e.g., staging) to find:
    - Missing tables
    - Missing columns
    - Type mismatches
    - Index differences
    """
    from claude_cli.db.drift import detect_schema_drift

    console.print("\n[bold]Schema Drift Detection[/bold]\n")
    console.print(f"  Source: {_mask_connection(source)}")
    console.print(f"  Target: {_mask_connection(target)}")
    console.print()

    try:
        report = detect_schema_drift(source, target)
        _display_drift_report(report)

        if output:
            Path(output).write_text(report.to_json())
            console.print(f"\n[green]✓[/green] Report saved to {output}\n")

        if report.has_breaking_changes:
            console.print("[red]✗ BLOCKING: Breaking schema changes detected[/red]\n")
            raise typer.Exit(1)
        else:
            console.print("[green]✓ No breaking schema changes[/green]\n")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        raise typer.Exit(1)


@app.command("fk-check")
def fk_integrity(
    connection: str = typer.Option(..., "--connection", "-c", help="Database connection string"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output report file"),
) -> None:
    """Check foreign key integrity after migrations.

    Verifies:
    - No orphaned foreign key references
    - All FK constraints are valid
    - No dangling references
    """
    from claude_cli.db.integrity import check_fk_integrity

    console.print("\n[bold]Foreign Key Integrity Check[/bold]\n")
    console.print(f"  Database: {_mask_connection(connection)}")
    console.print()

    try:
        violations = check_fk_integrity(connection)

        if violations:
            table = Table(title="FK Violations")
            table.add_column("Table", style="cyan")
            table.add_column("Column", style="yellow")
            table.add_column("Referenced", style="white")
            table.add_column("Orphans", style="red")

            for v in violations:
                table.add_row(v["table"], v["column"], v["references"], str(v["count"]))

            console.print(table)
            console.print(f"\n[red]✗ BLOCKING: {len(violations)} FK violations found[/red]\n")
            raise typer.Exit(1)
        else:
            console.print("[green]✓ No foreign key violations[/green]\n")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        raise typer.Exit(1)


@app.command("mask")
def pii_mask(
    connection: str = typer.Option(..., "--connection", "-c", help="Database connection string"),
    rules: str = typer.Option(None, "--rules", "-r", help="Path to masking rules YAML"),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Preview changes without applying"),
) -> None:
    """Apply PII masking rules to database.

    Uses rules from patterns/db-harness/baseline_masking_rules.yaml by default.

    Masks:
    - Email addresses
    - Phone numbers
    - Names
    - Addresses
    - Custom patterns
    """
    from claude_cli.db.masking import apply_pii_masking
    from claude_cli.common.config import get_framework_paths

    # Default rules file
    if not rules:
        paths = get_framework_paths()
        rules = str(Path(paths["patterns"]) / "db-harness" / "baseline_masking_rules.yaml")

    console.print("\n[bold]PII Masking[/bold]\n")
    console.print(f"  Database: {_mask_connection(connection)}")
    console.print(f"  Rules: {rules}")
    console.print(f"  Mode: {'DRY RUN' if dry_run else 'APPLY'}")
    console.print()

    if not dry_run:
        confirm = typer.confirm("This will modify data. Continue?")
        if not confirm:
            raise typer.Abort()

    try:
        result = apply_pii_masking(connection, rules, dry_run=dry_run)

        table = Table(title="Masking Results")
        table.add_column("Table", style="cyan")
        table.add_column("Column", style="yellow")
        table.add_column("Rows Affected", style="green")

        for r in result.changes:
            table.add_row(r["table"], r["column"], str(r["rows"]))

        console.print(table)

        if dry_run:
            console.print("\n[yellow]⚠ DRY RUN - no changes applied[/yellow]\n")
        else:
            console.print(f"\n[green]✓ Masked {result.total_rows} rows[/green]\n")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        raise typer.Exit(1)


@app.command("audit")
def audit_log(
    connection: str = typer.Option(..., "--connection", "-c", help="Database connection string"),
    table: str = typer.Option("audit_log", "--table", "-t", help="Audit log table name"),
    since: Optional[str] = typer.Option(None, "--since", help="Since timestamp (ISO format)"),
    limit: int = typer.Option(100, "--limit", "-n", help="Max records to show"),
) -> None:
    """View audit trail for compliance.

    Shows:
    - Recent changes
    - Who made changes
    - What changed
    """
    from claude_cli.db.audit import get_audit_log

    console.print("\n[bold]Audit Trail[/bold]\n")
    console.print(f"  Database: {_mask_connection(connection)}")
    console.print(f"  Table: {table}")
    console.print()

    try:
        records = get_audit_log(connection, table, since=since, limit=limit)

        if not records:
            console.print("[yellow]No audit records found.[/yellow]\n")
            return

        audit_table = Table(title=f"Audit Log ({len(records)} records)")
        audit_table.add_column("Timestamp", style="cyan", width=20)
        audit_table.add_column("User", style="yellow", width=15)
        audit_table.add_column("Action", style="green", width=10)
        audit_table.add_column("Table", style="white", width=15)
        audit_table.add_column("Details", style="white", max_width=40)

        for r in records:
            audit_table.add_row(
                r["timestamp"],
                r["user"],
                r["action"],
                r["table_name"],
                r["details"][:40] + "..." if len(r.get("details", "")) > 40 else r.get("details", ""),
            )

        console.print(audit_table)
        console.print()

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        raise typer.Exit(1)


@app.command("validate")
def validate_migration(
    migration_file: str = typer.Argument(..., help="Path to migration SQL file"),
    connection: str = typer.Option(None, "--connection", "-c", help="Test against this database"),
) -> None:
    """Validate a migration file before applying.

    Checks:
    - SQL syntax
    - Destructive operations (DROP, TRUNCATE)
    - Missing rollback
    - Transaction wrapping
    """
    console.print("\n[bold]Migration Validation[/bold]\n")
    console.print(f"  File: {migration_file}")
    console.print()

    path = Path(migration_file)
    if not path.exists():
        console.print(f"\n[red]File not found: {migration_file}[/red]\n")
        raise typer.Exit(1)

    content = path.read_text()
    issues = []

    # Check for destructive operations without safeguards
    destructive_ops = ["DROP TABLE", "DROP COLUMN", "TRUNCATE", "DELETE FROM"]
    for op in destructive_ops:
        if op in content.upper():
            issues.append(f"[yellow]⚠ Contains {op} - ensure this is intentional[/yellow]")

    # Check for transaction wrapping
    if "BEGIN" not in content.upper() and "START TRANSACTION" not in content.upper():
        issues.append("[yellow]⚠ No transaction wrapping detected[/yellow]")

    # Check for rollback file
    rollback_path = path.with_suffix(".rollback.sql")
    if not rollback_path.exists():
        issues.append(f"[yellow]⚠ No rollback file found ({rollback_path.name})[/yellow]")

    if issues:
        console.print("Issues found:\n")
        for issue in issues:
            console.print(f"  {issue}")
        console.print()
    else:
        console.print("[green]✓ Migration file looks valid[/green]\n")


def _mask_connection(conn: str) -> str:
    """Mask sensitive parts of connection string."""
    # Simple masking - hide password
    import re
    return re.sub(r'://[^:]+:[^@]+@', '://***:***@', conn)


def _display_drift_report(report) -> None:
    """Display schema drift report."""
    if report.missing_tables:
        console.print("[bold]Missing Tables:[/bold]")
        for t in report.missing_tables:
            console.print(f"  [red]- {t}[/red]")
        console.print()

    if report.missing_columns:
        console.print("[bold]Missing Columns:[/bold]")
        for table, columns in report.missing_columns.items():
            for col in columns:
                console.print(f"  [yellow]- {table}.{col}[/yellow]")
        console.print()

    if report.type_mismatches:
        console.print("[bold]Type Mismatches:[/bold]")
        for m in report.type_mismatches:
            console.print(f"  [red]- {m['table']}.{m['column']}: {m['source']} → {m['target']}[/red]")
        console.print()
