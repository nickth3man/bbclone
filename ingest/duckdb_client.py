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

from typing import Any, Optional


def connect(db_path: Optional[str] = None) -> Any:
    """Return a DuckDB connection object.

    Parameters
    ----------
    db_path : Optional[str]
        Path to the DuckDB database file, defaulting to configuration value.
        Refer to Background: target at ./data/hoarchive.duckdb.

    Returns
    -------
    Any
        A DuckDB connection-like object. In scaffolding this is intentionally untyped
        to avoid introducing external dependencies.

    Notes
    -----
    - This is a stub for Red phase tests to drive implementation.
    - No connection is opened here. Tests should fail until implemented.
    - Related Gherkin acceptance IDs:
        * Ingestion Scenario: staging population and type assertions
        * Transform Scenario: curated tables creation and constraints
        * CI/CD: artifact existence at ./data/hoarchive.duckdb
    """
    raise NotImplementedError("connect() not implemented. Provide a DuckDB connection in Red/Green phases.")