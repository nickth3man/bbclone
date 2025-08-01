"""
Transformation and promotion contracts from staging to curated in DuckDB.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Sections:
    - 1) Ingestion & Staging: dedup via QUALIFY ROW_NUMBER
    - 2) Transform & Promote: CTAS, CHECK constraints, PK/unique constraints,
      jersey TEXT preservation, DECIMAL(9,3), alias normalization, MERGE upsert
    - 3) API Expectations: downstream consumers rely on curated schemas

This module exposes only function signatures and docstrings to guide tests.
No SQL or transformation logic is implemented at this phase.
"""

import logging
from typing import Optional, Dict, Any

from .duckdb_client import connect

logger = logging.getLogger(__name__)


def promote_staging_to_curated(*, options: Optional[Dict[str, Any]] = None) -> None:
    """Promote validated and deduplicated staging data to curated tables.

    Implementation Notes
    --------------------
    - Create curated tables via CTAS with explicit types.
    - Apply business logic for player ID reconciliation and team alias mapping.
    - Handle TOT logic for player-season aggregates.
    - Preserve jersey TEXT semantics.
    - Normalize historical team aliases consistently.

    Parameters
    ----------
    options : Optional[Dict[str, Any]]
        Configuration flags (e.g., recreate, incremental).
    """
    if options is None:
        options = {}
    
    try:
        conn = connect()
        
        # Create curated tables in dependency order
        _create_curated_player(conn)
        _create_curated_team(conn)
        _create_curated_team_alias(conn)
        _create_curated_player_season(conn)
        _create_curated_play_by_play(conn)
        
        conn.close()
        logger.info("Successfully promoted staging data to curated tables")
        
    except Exception as e:
        logger.error(f"Failed to promote staging to curated: {e}")
        raise


def _create_curated_player(conn) -> None:
    """Create curated_player table with unified player registry."""
    query = """
        CREATE OR REPLACE TABLE curated_player AS
        WITH player_unified AS (
            -- Priority 1: NBA person_id from common_player_info
            SELECT 
                CAST(person_id AS BIGINT) as player_id,
                display_first_last as player_name,
                birthdate,
                height,
                weight,
                position,
                person_id as nba_person_id,
                NULL as legacy_player_id,
                'nba_common' as source_priority
            FROM staging_common_player_info
            WHERE person_id IS NOT NULL
            
            UNION ALL
            
            -- Priority 2: Legacy player_id from career info (only if not in NBA data)
            SELECT 
                CAST(pci.player_id AS BIGINT) as player_id,
                pci.player as player_name,
                TRY_CAST(pci.birth_year || '-01-01' AS DATE) as birthdate,
                NULL as height,
                NULL as weight,
                NULL as position,
                NULL as nba_person_id,
                pci.player_id as legacy_player_id,
                'legacy_career' as source_priority
            FROM staging_player_career_info pci
            WHERE pci.player_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM staging_common_player_info sci 
                WHERE sci.person_id = pci.player_id
            )
        ),
        player_dedupe AS (
            -- Deduplicate by player_id, preferring NBA data
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY player_id 
                    ORDER BY 
                        CASE source_priority 
                            WHEN 'nba_common' THEN 1 
                            WHEN 'legacy_career' THEN 2 
                            ELSE 3 
                        END
                ) as rn
            FROM player_unified
        )
        SELECT 
            player_id,
            player_name,
            birthdate,
            height,
            weight,
            position,
            nba_person_id,
            legacy_player_id
        FROM player_dedupe
        WHERE rn = 1
        ORDER BY player_id
    """
    
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_player").fetchone()[0]
    logger.info(f"Created curated_player with {count} players")


def _create_curated_team(conn) -> None:
    """Create curated_team table from modern team registry."""
    query = """
        CREATE OR REPLACE TABLE curated_team AS
        SELECT 
            CAST(id AS BIGINT) as team_id,
            full_name,
            abbreviation,
            nickname,
            city,
            state,
            CAST(year_founded AS INTEGER) as year_founded
        FROM staging_team
        WHERE id IS NOT NULL
        ORDER BY team_id
    """
    
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_team").fetchone()[0]
    logger.info(f"Created curated_team with {count} teams")


def _create_curated_team_alias(conn) -> None:
    """Create curated_team_alias for historical abbreviation mapping."""
    query = """
        CREATE OR REPLACE TABLE curated_team_alias AS
        WITH modern_aliases AS (
            -- Modern team abbreviations from Team Abbrev.csv
            SELECT 
                CAST(season AS INTEGER) as season,
                abbreviation as alias_abbreviation,
                team as alias_name,
                -- Try to map to modern team registry by abbreviation
                COALESCE(
                    (SELECT team_id FROM curated_team WHERE abbreviation = ta.abbreviation LIMIT 1),
                    -- Fallback mapping for known changes
                    CASE ta.abbreviation
                        WHEN 'PHO' THEN (SELECT team_id FROM curated_team WHERE abbreviation = 'PHX' LIMIT 1)
                        WHEN 'BRK' THEN (SELECT team_id FROM curated_team WHERE abbreviation = 'BKN' LIMIT 1)
                        WHEN 'CHO' THEN (SELECT team_id FROM curated_team WHERE abbreviation = 'CHA' LIMIT 1)
                        ELSE NULL
                    END
                ) as mapped_team_id
            FROM staging_team_abbrev ta
            WHERE season IS NOT NULL AND abbreviation IS NOT NULL
        ),
        historical_aliases AS (
            -- Historical team data from team_history.csv  
            SELECT DISTINCT
                2000 as season,  -- Default season for historical mapping
                'HIST_' || CAST(team_id AS VARCHAR) as alias_abbreviation,
                COALESCE(city || ' ' || nickname, 'Historical Team') as alias_name,
                CAST(team_id AS BIGINT) as mapped_team_id
            FROM staging_team_history
            WHERE team_id IS NOT NULL
        )
        SELECT DISTINCT
            season,
            alias_abbreviation,
            alias_name,
            mapped_team_id
        FROM (
            SELECT * FROM modern_aliases WHERE mapped_team_id IS NOT NULL
            UNION ALL
            SELECT * FROM historical_aliases
        ) combined
        ORDER BY season, alias_abbreviation
    """
    
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_team_alias").fetchone()[0]
    logger.info(f"Created curated_team_alias with {count} aliases")


def _create_curated_player_season(conn) -> None:
    """Create curated_player_season with TOT logic and team resolution."""
    query = """
        CREATE OR REPLACE TABLE curated_player_season AS
        WITH player_season_base AS (
            -- Combine totals and per-game data
            SELECT 
                CAST(pt.player_id AS BIGINT) as player_id,
                CAST(pt.season AS INTEGER) as season,
                pt.tm,
                CASE WHEN pt.tm = 'TOT' THEN 1 ELSE 0 END as is_tot,
                CAST(pt.g AS INTEGER) as games_played,
                CAST(pt.pts AS DOUBLE) as points,
                CAST(pt.ast AS DOUBLE) as assists,
                CAST(pt.trb AS DOUBLE) as rebounds
            FROM staging_player_totals pt
            WHERE pt.player_id IS NOT NULL 
            AND pt.season IS NOT NULL
            AND pt.tm IS NOT NULL
        ),
        player_season_resolved AS (
            -- Apply TOT logic: prefer TOT if present, else choose team with max games
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY player_id, season 
                    ORDER BY 
                        is_tot DESC,  -- TOT first
                        games_played DESC NULLS LAST,  -- Most games second
                        tm ASC  -- Alphabetical tie-breaker
                ) as team_priority
            FROM player_season_base
        )
        SELECT 
            psr.player_id,
            psr.season,
            psr.tm as team_abbreviation,
            -- Try to resolve to team_id via alias mapping
            ta.mapped_team_id as team_id,
            psr.games_played,
            psr.points,
            psr.assists,
            psr.rebounds,
            -- Compute jersey using LEFT JOINs after team priority resolution
            sci.jersey as jersey
        FROM player_season_resolved psr
        LEFT JOIN curated_team_alias ta ON (
            ta.season = psr.season 
            AND ta.alias_abbreviation = psr.tm
        )
        LEFT JOIN staging_common_player_info sci ON (
            sci.person_id = psr.player_id
        )
        LEFT JOIN staging_player_season_info psi ON (
            psi.player_id = psr.player_id 
            AND psi.season = psr.season 
            AND psi.tm = psr.tm
        )
        WHERE psr.team_priority = 1  -- Only keep the chosen team per player-season
        ORDER BY psr.player_id, psr.season
    """
    
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_player_season").fetchone()[0]
    logger.info(f"Created curated_player_season with {count} player-seasons")


def _create_curated_play_by_play(conn) -> None:
    """Create curated_play_by_play for future PBP features."""
    query = """
        CREATE OR REPLACE TABLE curated_play_by_play AS
        SELECT 
            CAST(season AS INTEGER) as season,
            CAST(player_id AS BIGINT) as player_id,
            tm as team_abbreviation,
            CAST(g AS INTEGER) as games_played,
            -- Role percentages (keep as proportions 0-1)
            CAST(pg_percent AS DOUBLE) as point_guard_pct,
            CAST(sg_percent AS DOUBLE) as shooting_guard_pct,
            CAST(sf_percent AS DOUBLE) as small_forward_pct,
            CAST(pf_percent AS DOUBLE) as power_forward_pct,
            CAST(c_percent AS DOUBLE) as center_pct
        FROM staging_player_pbp
        WHERE player_id IS NOT NULL 
        AND season IS NOT NULL
        ORDER BY season, player_id
    """
    
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_play_by_play").fetchone()[0]
    logger.info(f"Created curated_play_by_play with {count} player position allocations")