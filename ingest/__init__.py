"""
Ingestion package scaffolding for DuckDB-centered pipeline.

Traceability:
- See Gherkin spec at docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Sections: 1) Ingestion & Staging, 2) Transform & Promote, 5) CI/CD

This package provides only contracts, type hints, and placeholders for the Red phase.
NO business logic is implemented here.
"""

__all__ = [
    "config",
    "duckdb_client",
    "staging_loader",
    "transformer",
    "validators",
    "cli",
]