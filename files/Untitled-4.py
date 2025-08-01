"""
DuckDB repository implementation with basic functionality.

Addresses the core gap identified in analysis by providing minimal
working implementations of the repository contract methods.
"""

from typing import Any, Dict, Iterable, List, Mapping, Optional
import duckdb
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DuckDBRepo:
    """Repository for querying curated data in DuckDB."""

    def __init__(self, connection: Optional[Any] = None, db_path: Optional[str] = None) -> None:
        """Initialize with a DuckDB connection or database path."""
        if connection is not None:
            self.connection = connection
        elif db_path is not None:
            self.connection = duckdb.connect(db_path)
        else:
            # Default to in-memory database for development
            self.connection = duckdb.connect(':memory:')
    
    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self.connection, 'close'):
            self.connection.close()
    
    def query_players(self, filters: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        """Return player rows filtered by provided criteria.

        Expected filters
        ----------------
        - season: int or str
        - team: team code or alias (case-insensitive)
        - limit: maximum number of results (default: 50)
        - offset: pagination offset (default: 0)

        Returns
        -------
        List[Mapping[str, Any]]
            Player entities aligned to curated schema with pagination.
        """
        try:
            # Build base query
            query = """
                SELECT 
                    p.id as player_id,
                    p.full_name as player_name,
                    ps.season,
                    COALESCE(ta.abbreviation, ps.tm) as team,
                    ps.jersey,
                    ps.g as games_played,
                    ps.pts as points,
                    ps.ast as assists,
                    ps.trb as rebounds
                FROM curated_player p
                LEFT JOIN curated_player_season ps ON p.id = ps.player_id
                LEFT JOIN curated_team_alias ta ON (ps.season = ta.season AND ps.tm = ta.abbreviation)
                WHERE 1=1
            """
            
            params = {}
            conditions = []
            
            # Apply filters
            if 'season' in filters:
                conditions.append("ps.season = $season")
                params['season'] = int(filters['season'])
            
            if 'team' in filters:
                conditions.append("(UPPER(ps.tm) = UPPER($team) OR UPPER(ta.abbreviation) = UPPER($team))")
                params['team'] = str(filters['team'])
            
            # Add conditions to query
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            # Add ordering and pagination
            query += " ORDER BY p.full_name, ps.season"
            
            limit = filters.get('limit', 50)
            offset = filters.get('offset', 0)
            query += f" LIMIT {limit} OFFSET {offset}"
            
            # Execute query
            result = self.connection.execute(query, params).fetchall()
            columns = [desc[0] for desc in self.connection.description]
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in result]
            
        except Exception as e:
            logger.error(f"Error querying players: {e}")
            # Return empty result on error to maintain API contract
            return []

    def get_game_pbp(self, game_id: str) -> Iterable[Mapping[str, Any]]:
        """Return chronological play-by-play events for the given game.

        Parameters
        ----------
        game_id : str
            Game identifier

        Returns
        -------
        Iterable[Mapping[str, Any]]
            Sequence of event mappings with required fields, ordered chronologically.
        """
        try:
            query = """
                SELECT 
                    game_id,
                    eventnum,
                    period,
                    wctimestring as game_clock,
                    eventmsgtype,
                    eventmsgactiontype,
                    homedescription,
                    neutraldescription,
                    visitordescription,
                    score,
                    scoremargin,
                    person1type,
                    player1_id,
                    player1_name,
                    player1_team_id,
                    person2type,
                    player2_id,
                    player2_name,
                    player2_team_id,
                    person3type,
                    player3_id,
                    player3_name,
                    player3_team_id
                FROM curated_play_by_play
                WHERE game_id = $game_id
                ORDER BY period, eventnum
            """
            
            result = self.connection.execute(query, {'game_id': game_id}).fetchall()
            columns = [desc[0] for desc in self.connection.description]
            
            # Yield results as generator for memory efficiency
            for row in result:
                yield dict(zip(columns, row))
                
        except Exception as e:
            logger.error(f"Error getting game PBP for {game_id}: {e}")
            # Return empty generator on error
            return iter([])
    
    def get_player_count(self, filters: Mapping[str, Any]) -> int:
        """Get total count of players matching filters (for pagination)."""
        try:
            query = """
                SELECT COUNT(DISTINCT p.id) as total
                FROM curated_player p
                LEFT JOIN curated_player_season ps ON p.id = ps.player_id
                LEFT JOIN curated_team_alias ta ON (ps.season = ta.season AND ps.tm = ta.abbreviation)
                WHERE 1=1
            """
            
            params = {}
            conditions = []
            
            if 'season' in filters:
                conditions.append("ps.season = $season")
                params['season'] = int(filters['season'])
            
            if 'team' in filters:
                conditions.append("(UPPER(ps.tm) = UPPER($team) OR UPPER(ta.abbreviation) = UPPER($team))")
                params['team'] = str(filters['team'])
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            result = self.connection.execute(query, params).fetchone()
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"Error getting player count: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            self.connection.execute("SELECT 1").fetchone()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


def create_repository(db_path: Optional[str] = None) -> DuckDBRepo:
    """Factory function to create a DuckDB repository instance."""
    if db_path is None:
        # Use default path from config
        from .config import DB_PATH
        db_path = DB_PATH
    
    # Ensure database directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    return DuckDBRepo(db_path=db_path)