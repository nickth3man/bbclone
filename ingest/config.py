"""
Configuration constants and types for DuckDB ingestion pipeline.

Traceability:
- Refer to docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Sections:
    - 1) Ingestion & Staging (types, NULLSTRINGS, CSV directory)
    - 2) Transform & Promote (DECIMAL and DATE preservation)
    - 5) CI/CD (artifact path ./data/hoarchive.duckdb)

This module defines only constants and type hints. No runtime logic.
"""

import os
from typing import Final, List, Tuple, TypedDict, NotRequired

# File system paths - environment configurable with fallbacks
DUCKDB_PATH: Final[str] = os.getenv('DUCKDB_PATH', 'data/hoarchive.duckdb')
CSV_DIR: Final[str] = os.getenv('CSV_DIR', 'csv')

# Backward compatibility
DB_PATH: Final[str] = DUCKDB_PATH

# Null handling per Background and Ingestion Scenario
NULLSTRINGS: Final[List[str]] = ["", "NA", "null"]

# Canonical type hints (structural; not bound to runtime enforcement)
# IDs may be BIGINT/HUGEINT, decimals DECIMAL(9,3), dates DATE.
IdLike = int  # BIGINT/HUGEINT alignment
Decimal9_3 = float  # Placeholder type; actual DECIMAL(9,3) enforced in SQL
DateLike = str  # ISO-8601 yyyy-mm-dd string representation for stubs

class CsvLoadPlan(TypedDict):
    """Plan for how a CSV should be loaded into staging.

    This mirrors the Gherkin scenario notes for read_csv_auto/COPY options.
    """
    source_file: str
    staging_table: str
    nullstrings: List[str]
    delimiter: NotRequired[str]
    header: bool
    types: NotRequired[Tuple[str, ...]]  # duckdb type strings if predeclared