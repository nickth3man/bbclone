"""
Staging CSV loader contracts for DuckDB.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Sections:
    - 1) Ingestion & Staging:
      * read_csv_auto or COPY from ./csv with NULLSTRINGS
      * Casts: IDs BIGINT/HUGEINT, DECIMAL(9,3), DATE, jersey TEXT
      * Dedup via QUALIFY ROW_NUMBER
    - 2) Transform & Promote:
      * Promotion to curated via CTAS/MERGE (handled in transformer)
    - 5) CI/CD:
      * Artifact at ./data/hoarchive.duckdb

Only function signatures and docstrings are provided. No business logic implemented.
"""

from typing import Optional, Dict, Any, List
from .config import CsvLoadPlan


def plan_csv_loads() -> List[CsvLoadPlan]:
    """Return a list of CsvLoadPlan describing CSV -> staging mappings.

    Notes
    -----
    - Background and Ingestion scenario define the csv directory and nullstrings.
    - Red phase will specify detailed mappings: source file, staging table, types.
    - This stub returns no concrete plan to ensure tests fail until implemented.
    """
    return []


def load_csv_to_staging(table_name: str, *, options: Optional[Dict[str, Any]] = None) -> None:
    """Load a CSV file into a DuckDB staging table with appropriate options.

    Parameters
    ----------
    table_name : str
        Target staging table name (e.g., staging_player, staging_team).
    options : Optional[Dict[str, Any]]
        Placeholder for read_csv_auto/COPY options (delimiter, header, types, nullstrings).

    Behavior (per Gherkin, to be implemented in Red/Green)
    ------------------------------------------------------
    - Use read_csv_auto or COPY from CSV_DIR with NULLSTRINGS defined in config.
    - Ensure casts: IDs as BIGINT/HUGEINT, decimals as DECIMAL(9,3), dates as DATE, jersey as TEXT.
    - Preserve jersey leading zeros.
    - Handle empty CSVs gracefully (empty table).

    Acceptance References
    ---------------------
    - Ingestion: staging tables populated, type assertions, NULL mapping, jersey zeros preserved.

    This is a stub and intentionally does nothing to allow Red phase to create failing tests.
    """
    # Intentionally no implementation
    return None