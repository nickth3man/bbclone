"""DuckDB repository implementation for querying basketball data.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Section 3) API Expectations:
    * Players endpoint filters with pagination
    * Play-by-Play endpoint returns chronological events and normalizes IDs

Implementation:
- Uses staging tables from DuckDB for data retrieval
- Supports filtering, pagination, and error handling
- Designed for dependency injection: views should receive a repo instance externally.
"""

import logging
from typing import Any, Dict, List, Optional
import duckdb

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
            # Default to the project database
            self.connection = duckdb.connect('data/hoarchive.duckdb')

    def query_players(
        self,
        season: Optional[int] = None,
        team: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Query players with optional filters and pagination.

        Parameters
        ----------
        season : Optional[int]
            Filter by season year (e.g., 2023)
        team : Optional[str]
            Filter by team abbreviation (e.g., 'LAL')
        limit : int
            Maximum number of results to return
        offset : int
            Number of results to skip for pagination

        Returns
        -------
        Dict[str, Any]
            Dictionary with 'data' (list of player records) and 'total' (count)
        """
        try:
            # Build WHERE clause conditions
            where_conditions = []
            params = []
            
            if season is not None:
                where_conditions.append("season = ?")
                params.append(season)
            
            if team is not None:
                where_conditions.append("tm = ?")
                params.append(team)
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Count query for total
            count_sql = f"""
                SELECT COUNT(*) as total
                FROM staging_player_per_game
                {where_clause}
            """
            
            total_result = self.connection.execute(count_sql, params).fetchone()
            total = total_result[0] if total_result else 0
            
            # Data query with pagination
            data_sql = f"""
                SELECT 
                    player_id,
                    player,
                    season,
                    tm as team,
                    pos as position,
                    age,
                    g as games,
                    gs as games_started,
                    mp_per_game as minutes_per_game,
                    pts_per_game as points_per_game,
                    trb_per_game as rebounds_per_game,
                    ast_per_game as assists_per_game,
                    fg_percent as field_goal_percentage,
                    x3p_percent as three_point_percentage,
                    ft_percent as free_throw_percentage
                FROM staging_player_per_game
                {where_clause}
                ORDER BY pts_per_game DESC, player
                LIMIT ? OFFSET ?
            """
            
            data_params = params + [limit, offset]
            data_result = self.connection.execute(data_sql, data_params).fetchall()
            
            # Convert to list of dictionaries
            columns = [
                'player_id', 'player', 'season', 'team', 'position', 'age',
                'games', 'games_started', 'minutes_per_game', 'points_per_game',
                'rebounds_per_game', 'assists_per_game', 'field_goal_percentage',
                'three_point_percentage', 'free_throw_percentage'
            ]
            
            data = [
                dict(zip(columns, row)) for row in data_result
            ]
            
            return {"data": data, "total": total}
            
        except Exception as e:
            logger.error(f"Error querying players: {e}")
            return {"data": [], "total": 0}

    def query_play_by_play(
        self,
        game_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Query play-by-play data for a specific game.

        Parameters
        ----------
        game_id : str
            Unique game identifier
        limit : int
            Maximum number of events to return
        offset : int
            Number of events to skip for pagination

        Returns
        -------
        Dict[str, Any]
            Dictionary with 'data' (list of play events) and 'total' (count)
        """
        try:
            # Count query for total
            count_sql = """
                SELECT COUNT(*) as total
                FROM staging_player_play_by_play
                WHERE game_id = ?
            """
            
            total_result = self.connection.execute(count_sql, [game_id]).fetchone()
            total = total_result[0] if total_result else 0
            
            # Data query with pagination
            data_sql = """
                SELECT 
                    game_id,
                    player_id,
                    player,
                    mp as minutes_played,
                    fg as field_goals_made,
                    fga as field_goals_attempted,
                    fg_percent as field_goal_percentage,
                    x3p as three_pointers_made,
                    x3pa as three_pointers_attempted,
                    x3p_percent as three_point_percentage,
                    ft as free_throws_made,
                    fta as free_throws_attempted,
                    ft_percent as free_throw_percentage,
                    orb as offensive_rebounds,
                    drb as defensive_rebounds,
                    trb as total_rebounds,
                    ast as assists,
                    stl as steals,
                    blk as blocks,
                    tov as turnovers,
                    pf as personal_fouls,
                    pts as points,
                    plus_minus
                FROM staging_player_play_by_play
                WHERE game_id = ?
                ORDER BY pts DESC, player
                LIMIT ? OFFSET ?
            """
            
            data_result = self.connection.execute(data_sql, [game_id, limit, offset]).fetchall()
            
            # Convert to list of dictionaries
            columns = [
                'game_id', 'player_id', 'player', 'minutes_played',
                'field_goals_made', 'field_goals_attempted', 'field_goal_percentage',
                'three_pointers_made', 'three_pointers_attempted', 'three_point_percentage',
                'free_throws_made', 'free_throws_attempted', 'free_throw_percentage',
                'offensive_rebounds', 'defensive_rebounds', 'total_rebounds',
                'assists', 'steals', 'blocks', 'turnovers', 'personal_fouls',
                'points', 'plus_minus'
            ]
            
            data = [
                dict(zip(columns, row)) for row in data_result
            ]
            
            return {"data": data, "total": total}
            
        except Exception as e:
            logger.error(f"Error querying play-by-play for game {game_id}: {e}")
            return {"data": [], "total": 0}

    def query_team_season_stats(
        self,
        season: Optional[int] = None,
        team: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Query team season statistics.

        Parameters
        ----------
        season : Optional[int]
            Filter by season year
        team : Optional[str]
            Filter by team abbreviation
        limit : int
            Maximum number of results to return
        offset : int
            Number of results to skip for pagination

        Returns
        -------
        Dict[str, Any]
            Dictionary with 'data' (list of team stats) and 'total' (count)
        """
        try:
            # Build WHERE clause conditions
            where_conditions = []
            params = []
            
            if season is not None:
                where_conditions.append("season = ?")
                params.append(season)
            
            if team is not None:
                where_conditions.append("team = ?")
                params.append(team)
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Count query for total
            count_sql = f"""
                SELECT COUNT(*) as total
                FROM staging_team_abbrev
                {where_clause}
            """
            
            total_result = self.connection.execute(count_sql, params).fetchone()
            total = total_result[0] if total_result else 0
            
            # Data query with pagination
            data_sql = f"""
                SELECT 
                    season,
                    team,
                    abbreviation,
                    lg as league,
                    playoffs
                FROM staging_team_abbrev
                {where_clause}
                ORDER BY season DESC, team
                LIMIT ? OFFSET ?
            """
            
            data_params = params + [limit, offset]
            data_result = self.connection.execute(data_sql, data_params).fetchall()
            
            # Convert to list of dictionaries
            columns = ['season', 'team', 'abbreviation', 'league', 'playoffs']
            
            data = [
                dict(zip(columns, row)) for row in data_result
            ]
            
            return {"data": data, "total": total}
            
        except Exception as e:
            logger.error(f"Error querying team season stats: {e}")
            return {"data": [], "total": 0}

    def query_player_game_logs(
        self,
        player_id: Optional[int] = None,
        season: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Query player game logs.

        Parameters
        ----------
        player_id : Optional[int]
            Filter by player ID
        season : Optional[int]
            Filter by season year
        limit : int
            Maximum number of results to return
        offset : int
            Number of results to skip for pagination

        Returns
        -------
        Dict[str, Any]
            Dictionary with 'data' (list of game logs) and 'total' (count)
        """
        try:
            # Build WHERE clause conditions
            where_conditions = []
            params = []
            
            if player_id is not None:
                where_conditions.append("player_id = ?")
                params.append(player_id)
            
            if season is not None:
                where_conditions.append("season = ?")
                params.append(season)
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Count query for total
            count_sql = f"""
                SELECT COUNT(*) as total
                FROM staging_player_totals
                {where_clause}
            """
            
            total_result = self.connection.execute(count_sql, params).fetchone()
            total = total_result[0] if total_result else 0
            
            # Data query with pagination
            data_sql = f"""
                SELECT 
                    player_id,
                    player,
                    season,
                    tm as team,
                    pos as position,
                    age,
                    g as games,
                    gs as games_started,
                    mp as minutes_played,
                    fg as field_goals_made,
                    fga as field_goals_attempted,
                    fg_percent as field_goal_percentage,
                    x3p as three_pointers_made,
                    x3pa as three_pointers_attempted,
                    x3p_percent as three_point_percentage,
                    ft as free_throws_made,
                    fta as free_throws_attempted,
                    ft_percent as free_throw_percentage,
                    orb as offensive_rebounds,
                    drb as defensive_rebounds,
                    trb as total_rebounds,
                    ast as assists,
                    stl as steals,
                    blk as blocks,
                    tov as turnovers,
                    pf as personal_fouls,
                    pts as points
                FROM staging_player_totals
                {where_clause}
                ORDER BY season DESC, pts DESC, player
                LIMIT ? OFFSET ?
            """
            
            data_params = params + [limit, offset]
            data_result = self.connection.execute(data_sql, data_params).fetchall()
            
            # Convert to list of dictionaries
            columns = [
                'player_id', 'player', 'season', 'team', 'position', 'age',
                'games', 'games_started', 'minutes_played',
                'field_goals_made', 'field_goals_attempted', 'field_goal_percentage',
                'three_pointers_made', 'three_pointers_attempted', 'three_point_percentage',
                'free_throws_made', 'free_throws_attempted', 'free_throw_percentage',
                'offensive_rebounds', 'defensive_rebounds', 'total_rebounds',
                'assists', 'steals', 'blocks', 'turnovers', 'personal_fouls', 'points'
            ]
            
            data = [
                dict(zip(columns, row)) for row in data_result
            ]
            
            return {"data": data, "total": total}
            
        except Exception as e:
            logger.error(f"Error querying player game logs: {e}")
            return {"data": [], "total": 0}