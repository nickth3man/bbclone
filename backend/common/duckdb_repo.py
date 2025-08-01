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
        conditions = []
        params = []
        
        if 'season' in filters:
            conditions.append("season = ?")
            params.append(filters['season'])
        
        if 'team' in filters:
            conditions.append("LOWER(team) = LOWER(?)")
            params.append(filters['team'])
        
        sql = "SELECT * FROM player_season"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        result = self.connection.execute(sql, params).fetchall()
        columns = [col[0] for col in self.connection.description]
        return [dict(zip(columns, row)) for row in result]

    def get_game_pbp(self, game_id: int) -> Iterable[Mapping[str, Any]]:
        """Return chronological play-by-play events for the given game.

        Returns
        -------
        Iterable[Mapping[str, Any]]
            Sequence of event mappings with required fields.

        Gherkin references:
        - "Play-by-Play endpoint returns PBP JSON for a game"
        """
        sql = """
        SELECT * FROM game_pbp 
        WHERE game_id = ? 
        ORDER BY period, clock ASC
        """
        result = self.connection.execute(sql, [game_id]).fetchall()
        columns = [col[0] for col in self.connection.description]
        return [dict(zip(columns, row)) for row in result]

    def get_team_season_stats(self, season: Optional[int] = None, team_abbreviation: Optional[str] = None) -> List[Mapping[str, Any]]:
        """Return team season stats filtered by provided criteria.

        Expected filters
        ----------------
        - season: int
        - team_abbreviation: str (case-insensitive)

        Returns
        -------
        List[Mapping[str, Any]]
            Team season stats entities aligned to curated schema.
        """
        conditions = []
        params = []

        sql = "SELECT * FROM curated_team_season_stats"

        if season is not None:
            conditions.append("season = ?")
            params.append(season)

        if team_abbreviation is not None:
            conditions.append("LOWER(team_abbreviation) = LOWER(?)")
            params.append(team_abbreviation)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY season DESC, team_abbreviation ASC"

        result = self.connection.execute(sql, params).fetchall()
        columns = [col[0] for col in self.connection.description]
        return [dict(zip(columns, row)) for row in result]

    def get_player_game_log(self, player_id: int, season: Optional[int] = None) -> List[Mapping[str, Any]]:
        """Return chronological player game log for the given player.

        Expected filters
        ----------------
        - player_id: int (required)
        - season: int (optional)

        Returns
        -------
        List[Mapping[str, Any]]
            Sequence of player game log entries.
        """
        conditions = ["player_id = ?"]
        params = [player_id]

        sql = "SELECT * FROM curated_player_game_log"

        if season is not None:
            conditions.append("season = ?")
            params.append(season)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY game_date DESC"

        result = self.connection.execute(sql, params).fetchall()
        columns = [col[0] for col in self.connection.description]
        return [dict(zip(columns, row)) for row in result]