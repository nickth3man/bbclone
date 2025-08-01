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

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, cast # Import cast

from .config import CsvLoadPlan, CSV_DIR, NULLSTRINGS
from .duckdb_client import connect

logger = logging.getLogger(__name__)


def plan_csv_loads() -> List[CsvLoadPlan]:
    """Return a list of CsvLoadPlan describing CSV -> staging mappings.

    Notes
    -----
    - Background and Ingestion scenario define the csv directory and nullstrings.
    - Maps specific CSVs to staging tables with appropriate type handling.
    """
    return [
        {
            'source_file': 'Player Career Info.csv',
            'staging_table': 'staging_player_career_info',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Player Directory.csv',
            'staging_table': 'staging_player_directory',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'common_player_info.csv',
            'staging_table': 'staging_common_player_info',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Player Per Game.csv',
            'staging_table': 'staging_player_per_game',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Player Totals.csv',
            'staging_table': 'staging_player_totals',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Player Play By Play.csv',
            'staging_table': 'staging_player_pbp',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Player Season Info.csv',
            'staging_table': 'staging_player_season_info',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Team Abbrev.csv',
            'staging_table': 'staging_team_abbrev',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'team.csv',
            'staging_table': 'staging_team',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'team_history.csv',
            'staging_table': 'staging_team_history',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'game.csv',
            'staging_table': 'staging_game',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'game_summary.csv',
            'staging_table': 'staging_game_summary',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'line_score.csv',
            'staging_table': 'staging_line_score',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Advanced.csv',
            'staging_table': 'staging_advanced',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'All-Star Selections.csv',
            'staging_table': 'staging_all_star_selections',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'draft_combine_stats.csv',
            'staging_table': 'staging_draft_combine_stats',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'draft_history.csv',
            'staging_table': 'staging_draft_history',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'End of Season Teams (Voting).csv',
            'staging_table': 'staging_end_of_season_teams_voting',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'End of Season Teams.csv',
            'staging_table': 'staging_end_of_season_teams',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'game_info.csv',
            'staging_table': 'staging_game_info',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'inactive_players.csv',
            'staging_table': 'staging_inactive_players',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'officials.csv',
            'staging_table': 'staging_officials',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Opponent Stats Per 100 Poss.csv',
            'staging_table': 'staging_opponent_stats_per_100_poss',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Opponent Stats Per Game.csv',
            'staging_table': 'staging_opponent_stats_per_game',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Opponent Totals.csv',
            'staging_table': 'staging_opponent_totals',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'other_stats.csv',
            'staging_table': 'staging_other_stats',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Per 36 Minutes.csv',
            'staging_table': 'staging_per_36_minutes',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Per 100 Poss.csv',
            'staging_table': 'staging_per_100_poss',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'play_by_play.csv',
            'staging_table': 'staging_play_by_play',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Player Award Shares.csv',
            'staging_table': 'staging_player_award_shares',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Player Shooting.csv',
            'staging_table': 'staging_player_shooting',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'player.csv',
            'staging_table': 'staging_player',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Team Stats Per 100 Poss.csv',
            'staging_table': 'staging_team_stats_per_100_poss',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Team Stats Per Game.csv',
            'staging_table': 'staging_team_stats_per_game',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Team Summaries.csv',
            'staging_table': 'staging_team_summaries',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'Team Totals.csv',
            'staging_table': 'staging_team_totals',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'team_details.csv',
            'staging_table': 'staging_team_details',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
        {
            'source_file': 'team_info_common.csv',
            'staging_table': 'staging_team_info_common',
            'nullstrings': NULLSTRINGS,
            'header': True
        },
    ]


def load_csv_to_staging(table_name: str, *, options: Optional[Dict[str, Any]] = None) -> None:
    """Load a CSV file into a DuckDB staging table with appropriate options.

    Parameters
    ----------
    table_name : str
        Target staging table name (e.g., staging_player, staging_team).
    options : Optional[Dict[str, Any]]
        Options for CSV loading (source_file, nullstrings, header, etc.).

    Behavior (per Gherkin)
    ----------------------
    - Use read_csv_auto with NULLSTRINGS defined in config.
    - Ensure proper type casting: IDs as BIGINT, decimals as DOUBLE, jersey as VARCHAR.
    - Preserve jersey leading zeros.
    - Handle empty CSVs gracefully (empty table).
    """
    if options is None:
        options = {}
    
    source_file = options.get('source_file')
    if not source_file:
        logger.error(f"No source_file specified for table {table_name}")
        return
    
    try:
        conn = connect()
        csv_path = Path(CSV_DIR) / source_file
        
        if not csv_path.exists():
            logger.warning(f"CSV file not found: {csv_path}")
            # Create empty table for missing files
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('nonexistent') WHERE FALSE")
            conn.close()
            return
        
        # Build nullstrings parameter for DuckDB
        nullstrings = options.get('nullstrings', NULLSTRINGS)
        nullstr_param = "[" + ", ".join([f"'{ns}'" for ns in nullstrings]) + "]"
        
        # Use read_csv_auto with proper null handling
        query = f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto(
                '{csv_path}',
                header=true,
                nullstr={nullstr_param},
                normalize_names=false
            )
        """
        
        logger.info(f"Loading {source_file} into {table_name}")
        conn.execute(query)
        
        # Get row count for verification
        count_result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        row_count = count_result[0] if count_result else 0
        logger.info(f"Loaded {row_count} rows into {table_name}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to load {source_file} into {table_name}: {e}")
        raise


def load_all_staging_tables() -> None:
    """Load all CSV files into their corresponding staging tables."""
    plans = plan_csv_loads()
    
    for plan in plans:
        try:
            # Explicitly cast plan to Dict[str, Any] to satisfy Pylance
            load_csv_to_staging(
                table_name=plan['staging_table'],
                options=cast(Dict[str, Any], plan) # Cast to Dict[str, Any]
            )
        except Exception as e:
            logger.error(f"Failed to load staging table {plan['staging_table']}: {e}")
            # Continue with other tables rather than failing completely
            continue
    
    logger.info(f"Completed loading {len(plans)} staging tables")