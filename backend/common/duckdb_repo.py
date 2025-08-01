"""
DuckDB repository contract used by API views.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Section 3) API Expectations:
    * Players endpoint filters with pagination
    * Play-by-Play endpoint returns chronological events and normalizes IDs

Notes:
- This class contains method signatures only. No DuckDB logic is implemented.
- Designed for dependency injection: views should receive a repo instance externally.
"""

from typing import Any, Dict, Iterable, List, Mapping, Optional


class DuckDBRepo:
    """Repository contract for querying curated data in DuckDB."""

    def __init__(self, connection: Any) -> None:
        """Initialize with a DuckDB connection-like object (dependency-injected)."""
        self.connection = connection

    def query_players(self, filters: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        """Return player rows filtered by provided criteria.

        Expected filters
        ----------------
        - season: int or str
        - team: team code or alias (case-insensitive)

        Returns
        -------
        List[Mapping[str, Any]]
            Player entities aligned to curated schema. Pagination handled at view/DRF layer.

        Gherkin references:
        - "Players endpoint filters by season and team with pagination"
        """
        raise NotImplementedError("DuckDBRepo.query_players not implemented (scaffold)")

    def get_game_pbp(self, game_id: int) -> Iterable[Mapping[str, Any]]:
        """Return chronological play-by-play events for the given game.

        Returns
        -------
        Iterable[Mapping[str, Any]]
            Sequence of event mappings with required fields.

        Gherkin references:
        - "Play-by-Play endpoint returns PBP JSON for a game"
        """
        raise NotImplementedError("DuckDBRepo.get_game_pbp not implemented (scaffold)")