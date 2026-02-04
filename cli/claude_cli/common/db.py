"""DuckDB connection management."""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import duckdb


@contextmanager
def get_connection(db_path: Path) -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """Get a DuckDB connection context manager."""
    conn = duckdb.connect(str(db_path))
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Path, schema_sql: str) -> None:
    """Initialize a database with schema."""
    with get_connection(db_path) as conn:
        conn.execute(schema_sql)
        conn.commit()
