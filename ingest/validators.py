"""
Validation contract functions for DuckDB staging/curated data quality.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Sections:
    - Ingestion & Staging:
        * FK orphans check (players, teams, games)
        * Dedup grain uniqueness
        * TOT vs team-splits constraint
        * Sampling reconciliation with Basketball-Reference
    - Transform & Promote:
        * Unique constraints / CHECK constraints validation
    - CI/CD:
        * Smoke tests for orphans, duplicate keys, TOT constraint

Only function signatures and docstrings are provided. No data access or SQL is implemented.
"""

from typing import List, Dict, Any, Optional


def fk_orphans_check() -> List[Dict[str, Any]]:
    """Return offending rows for foreign key orphan checks.

    Returns
    -------
    List[Dict[str, Any]]
        Collection describing orphan findings (empty when none). Red phase will define shape.

    Gherkin reference:
    - "Referential integrity checks on staging for player_id, team_id, game_id"
    - Acceptance: orphan queries return zero rows.
    """
    return []


def uniq_check(entity: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return violations of uniqueness for curated grains or staging dedup views.

    Parameters
    ----------
    entity : Optional[str]
        Target entity/table name to scope the uniqueness check.

    Returns
    -------
    List[Dict[str, Any]]
        Collection describing duplicate key findings.

    Gherkin reference:
    - Deduplicate staging via QUALIFY ROW_NUMBER (staging uniqueness)
    - Transform acceptance: unique constraints have no violations.
    """
    return []


def tot_consistency_check() -> List[Dict[str, Any]]:
    """Return violations of the "one TOT or many teams, but not both" constraint.

    Returns
    -------
    List[Dict[str, Any]]
        Collection of violation descriptors keyed by (player_id, season) context.

    Gherkin reference:
    - Enforce "one TOT or many teams, but not both" per PlayerSeason.
    - Acceptance: zero violations present after validation.
    """
    return []


def sample_reconciliation_check(sample_size: int = 50) -> List[Dict[str, Any]]:
    """Compare a sample of curated or deduped staging rows against Basketball-Reference.

    Parameters
    ----------
    sample_size : int
        Number of rows to sample. Default aligns with scenario (50).

    Returns
    -------
    List[Dict[str, Any]]
        Collection of mismatch descriptors (row identifiers, metric names).

    Gherkin reference:
    - Sampling reconciliation scenario with ±1 tolerance.
    - Acceptance: 50/50 rows meet the tolerance threshold.
    """
    return []