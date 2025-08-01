"""
DuckDB client connection contract.

Traceability:
- See docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Sections:
    * Background (DuckDB database at ./data/hoarchive.duckdb)
    * 1) Ingestion & Staging
    * 2) Transform & Promote
    * 5) CI/CD (artifact path verification)

This module exposes a connect() function signature only. No business logic is implemented.
"""

import duckdb
import logging
from pathlib import Path
from typing import Any, Optional

from .config import DUCKDB_PATH

logger = logging.getLogger(__name__)


def connect(db_path: Optional[str] = None) -> duckdb.DuckDBPyConnection:
    """Return a DuckDB connection object.

    Parameters
    ----------
    db_path : Optional[str]
        Path to the DuckDB database file, defaulting to configuration value.
        Refer to Background: target at ./data/hoarchive.duckdb.

    Returns
    -------
    duckdb.DuckDBPyConnection
        A DuckDB connection object ready for queries.

    Notes
    -----
    - Creates database directory if it doesn't exist
    - Related Gherkin acceptance IDs:
        * Ingestion Scenario: staging population and type assertions
        * Transform Scenario: curated tables creation and constraints
        * CI/CD: artifact existence at ./data/hoarchive.duckdb
    """
    if db_path is None:
        db_path = DUCKDB_PATH
    
    try:
        # Ensure the database directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create connection
        conn = duckdb.connect(str(db_file))
        logger.info(f"Connected to DuckDB at {db_path}")
        return conn
        
    except Exception as e:
        logger.error(f"Failed to connect to DuckDB at {db_path}: {e}")
        raise


def health_check(db_path: Optional[str] = None) -> bool:
    """Check if DuckDB connection is healthy.
    
    Parameters
    ----------
    db_path : Optional[str]
        Path to the DuckDB database file, defaulting to configuration value.
    
    Returns
    -------
    bool
        True if connection is healthy, False otherwise.
    """
    try:
        conn = connect(db_path)
        # Simple query to test connection
        result = conn.execute("SELECT 1 as test").fetchone()
        conn.close()
        return result is not None and result[0] == 1
    except Exception as e:
        logger.error(f"DuckDB health check failed: {e}")
        return False