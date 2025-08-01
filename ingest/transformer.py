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
        _create_curated_game(conn) # New game table
        _create_curated_player_awards(conn) # New player awards table
        _create_curated_team_season_stats(conn) # New team season stats table
        _create_curated_draft_data(conn) # New draft data table
        _create_curated_player_game_log(conn) # New player game log table
        _create_curated_player_season(conn)
        _create_curated_play_by_play(conn) # Player PBP (summary)
        _create_curated_game_play_by_play(conn) # Game PBP (detailed events)
        
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


def _create_curated_game(conn) -> None:
    """Create curated_game table by joining game, game_info, line_score, and game_summary."""
    query = """
        CREATE OR REPLACE TABLE curated_game AS
        SELECT
            g.game_id,
            g.season_id,
            CAST(g.game_date AS DATE) as game_date,
            g.team_id_home AS home_team_id,
            th.abbreviation AS home_team_abbreviation,
            g.team_name_home AS home_team_name,
            g.wl_home AS home_team_win_loss,
            g.pts_home AS home_team_points,
            g.team_id_away AS visitor_team_id,
            tv.abbreviation AS visitor_team_abbreviation,
            g.team_name_away AS visitor_team_name,
            g.wl_away AS visitor_team_win_loss,
            g.pts_away AS visitor_team_points,
            g.season_type,
            COALESCE(gi.attendance, 0) AS attendance,
            ls.pts_qtr1_home,
            ls.pts_qtr2_home,
            ls.pts_qtr3_home,
            ls.pts_qtr4_home,
            ls.pts_ot1_home,
            ls.pts_ot2_home,
            ls.pts_ot3_home,
            ls.pts_ot4_home,
            ls.pts_ot5_home,
            ls.pts_ot6_home,
            ls.pts_ot7_home,
            ls.pts_ot8_home,
            ls.pts_ot9_home,
            ls.pts_ot10_home,
            ls.pts_qtr1_away,
            ls.pts_qtr2_away,
            ls.pts_qtr3_away,
            ls.pts_qtr4_away,
            ls.pts_ot1_away,
            ls.pts_ot2_away,
            ls.pts_ot3_away,
            ls.pts_ot4_away,
            ls.pts_ot5_away,
            ls.pts_ot6_away,
            ls.pts_ot7_away,
            ls.pts_ot8_away,
            ls.pts_ot9_away,
            ls.pts_ot10_away,
            osu.pts_paint_home,
            osu.pts_2nd_chance_home,
            osu.pts_fb_home,
            osu.largest_lead_home,
            osu.lead_changes,
            osu.times_tied,
            osu.total_turnovers_home,
            osu.pts_off_to_home,
            osu.pts_paint_away,
            osu.pts_2nd_chance_away,
            osu.pts_fb_away,
            osu.largest_lead_away,
            osu.total_turnovers_away,
            osu.pts_off_to_away
        FROM staging_game g
        LEFT JOIN staging_game_info gi ON g.game_id = gi.game_id
        LEFT JOIN staging_line_score ls ON g.game_id = ls.game_id
        LEFT JOIN staging_other_stats osu ON g.game_id = osu.game_id
        LEFT JOIN curated_team th ON g.team_id_home = th.team_id 
        LEFT JOIN curated_team tv ON g.team_id_away = tv.team_id 
        WHERE g.game_id IS NOT NULL AND g.game_date IS NOT NULL
        ORDER BY g.game_date DESC
    """
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_game").fetchone()[0]
    logger.info(f"Created curated_game with {count} games")


def _create_curated_player_awards(conn) -> None:
    """Create curated_player_awards table by combining data from player award shares and all-star selections."""
    query = """
        CREATE OR REPLACE TABLE curated_player_awards AS
        WITH all_awards AS (
            SELECT
                CAST(season AS INTEGER) as season,
                player_id,
                player AS player_name,
                award AS award_name,
                CAST(share AS DOUBLE) as share,
                winner AS is_winner,
                'award_share' AS award_type
            FROM staging_player_award_shares
            WHERE player_id IS NOT NULL AND season IS NOT NULL

            UNION ALL

            SELECT
                CAST(season AS INTEGER) as season,
                cp.player_id,
                sel.player AS player_name,
                'All-Star Selection' AS award_name,
                NULL AS share,
                TRUE AS is_winner,
                'all_star' AS award_type
            FROM staging_all_star_selections sel
            LEFT JOIN curated_player cp ON sel.player = cp.player_name 
            WHERE sel.season IS NOT NULL
        )
        SELECT
            aa.season,
            aa.player_id,
            aa.player_name,
            aa.award_name,
            aa.share,
            aa.is_winner,
            aa.award_type
        FROM all_awards aa
        WHERE aa.player_id IS NOT NULL 
        ORDER BY aa.season DESC, aa.player_name, aa.award_name
    """
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_player_awards").fetchone()[0]
    logger.info(f"Created curated_player_awards with {count} player awards")


def _create_curated_draft_data(conn) -> None:
    """Create curated_draft_data by combining draft history and combine stats."""
    query = """
        CREATE OR REPLACE TABLE curated_draft_data AS
        SELECT
            dh.season AS draft_season,
            dh.person_id AS player_id,
            dh.player_name,
            dh.round_number AS draft_round,
            dh.overall_pick AS draft_overall_pick,
            dh.team_name AS drafted_by_team_name,
            dh.team_abbreviation AS drafted_by_team_abbreviation,
            dcs.position AS combine_position,
            dcs.height_wo_shoes AS combine_height_wo_shoes,
            dcs.weight AS combine_weight,
            dcs.wingspan AS combine_wingspan,
            dcs.standing_reach AS combine_standing_reach,
            dcs.standing_vertical_leap AS combine_standing_vertical_leap,
            dcs.max_vertical_leap AS combine_max_vertical_leap,
            dcs.three_quarter_sprint AS combine_three_quarter_sprint
        FROM staging_draft_history dh
        LEFT JOIN staging_draft_combine_stats dcs ON dh.person_id = dcs.player_id AND dh.season = dcs.season
        WHERE dh.person_id IS NOT NULL AND dh.season IS NOT NULL
        ORDER BY dh.season DESC, dh.overall_pick ASC
    """
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_draft_data").fetchone()[0]
    logger.info(f"Created curated_draft_data with {count} draft entries")


def _create_curated_game_play_by_play(conn) -> None:
    """Create curated_game_play_by_play for detailed game events."""
    query = """
        CREATE OR REPLACE TABLE curated_game_play_by_play AS
        SELECT
            CAST(game_id AS VARCHAR) as game_id,
            CAST(eventnum AS BIGINT) as event_number,
            CAST(eventmsgtype AS INTEGER) as event_message_type,
            CAST(eventmsgactiontype AS INTEGER) as event_message_action_type,
            CAST(period AS INTEGER) as period,
            wctimestring AS wc_time_string,
            pctimestring AS pc_time_string,
            homedescription AS home_description,
            neutraldescription AS neutral_description,
            visitordescription AS visitor_description,
            score,
            scoremargin AS score_margin,
            CAST(player1_id AS BIGINT) as player1_id,
            player1_name,
            CAST(player1_team_id AS BIGINT) as player1_team_id,
            player1_team_abbreviation,
            CAST(player2_id AS BIGINT) as player2_id,
            player2_name,
            CAST(player2_team_id AS BIGINT) as player2_team_id,
            player2_team_abbreviation,
            CAST(player3_id AS BIGINT) as player3_id,
            player3_name,
            CAST(player3_team_id AS BIGINT) as player3_team_id,
            player3_team_abbreviation,
            CAST(video_available_flag AS BOOLEAN) as video_available
        FROM staging_play_by_play
        WHERE game_id IS NOT NULL AND eventnum IS NOT NULL
        ORDER BY game_id, eventnum ASC
    """
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_game_play_by_play").fetchone()[0]
    logger.info(f"Created curated_game_play_by_play with {count} game events")


def _create_curated_team_season_stats(conn) -> None:
    """Create curated_team_season_stats by combining various team statistics."""
    query = """
        CREATE OR REPLACE TABLE curated_team_season_stats AS
        SELECT
            tts.season AS season,
            cta.mapped_team_id AS team_id,
            tts.tm AS team_abbreviation,
            tts.lg AS league_abbreviation,
            tsm.w AS wins,
            tsm.l AS losses,
            tts.g AS games_played,
            tts.mp_per_g AS minutes_played_per_game,
            tts.fg AS field_goals,
            tts.fga AS field_goal_attempts,
            CAST(tts.fg_percent AS DOUBLE) AS field_goal_percentage,
            tts.fg3 AS field_goals_3pt,
            tts.fg3a AS field_goal_attempts_3pt,
            CAST(tts.fg3_percent AS DOUBLE) AS field_goal_percentage_3pt,
            tts.fg2 AS field_goals_2pt,
            tts.fg2a AS field_goal_attempts_2pt,
            CAST(tts.fg2_percent AS DOUBLE) AS field_goal_percentage_2pt,
            CAST(tts.efg_percent AS DOUBLE) AS effective_field_goal_percentage,
            tts.ft AS free_throws,
            tts.fta AS free_throw_attempts,
            CAST(tts.ft_percent AS DOUBLE) AS free_throw_percentage,
            tts.orb AS offensive_rebounds,
            tts.drb AS defensive_rebounds,
            tts.trb AS total_rebounds,
            tts.ast AS assists,
            tts.stl AS steals,
            tts.blk AS blocks,
            tts.tov AS turnovers,
            tts.pf AS personal_fouls,
            tts.pts AS points,
            tsi.age AS team_age,
            tsi.w_perc AS winning_percentage,
            tsi.l_perc AS losing_percentage,
            tsi.mov AS margin_of_victory,
            tsi.sos AS strength_of_schedule,
            tsi.srs AS simple_rating_system,
            tsi.pace AS pace,
            tsi.ortg AS offensive_rating,
            tsi.drtg AS defensive_rating,
            tsi.n_rtg AS net_rating,
            tsi.fta_per_fga_perc AS free_throw_attempt_rate,
            tsi.fg3a_per_fga_perc AS fg3_attempt_rate,
            tsi.ts_perc AS true_shooting_percentage,
            tsi.e_fg_perc AS team_effective_field_goal_percentage,
            tsi.tov_perc AS team_turnover_percentage,
            tsi.orb_perc AS team_offensive_rebound_percentage,
            tsi.ft_rate AS team_free_throw_rate,
            tsi.opp_e_fg_perc AS opponent_effective_field_goal_percentage,
            tsi.opp_tov_perc AS opponent_turnover_percentage,
            tsi.opp_drb_perc AS opponent_defensive_rebound_percentage,
            tsi.opp_ft_rate AS opponent_free_throw_rate
        FROM staging_team_totals tts
        LEFT JOIN staging_team_summaries tsm ON tts.season = tsm.season AND tts.tm = tsm.team_abbreviation
        LEFT JOIN staging_team_stats_per_game tspg ON tts.season = tspg.season AND tts.tm = tspg.tm
        LEFT JOIN staging_team_stats_per_100_poss tspc ON tts.season = tspc.season AND tts.tm = tspc.tm
        LEFT JOIN staging_team_info_common tsi ON tts.season = tsi.season AND tts.tm = tsi.abbreviation
        LEFT JOIN curated_team_alias cta ON tts.season = cta.season AND tts.tm = cta.alias_abbreviation
        WHERE tts.season IS NOT NULL AND tts.tm IS NOT NULL
        ORDER BY tts.season DESC, tts.tm ASC
    """
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_team_season_stats").fetchone()[0]
    logger.info(f"Created curated_team_season_stats with {count} team season stats entries")

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

def _create_curated_player_game_log(conn) -> None:
    """Create curated_player_game_log with daily player stats."""
    query = """
        CREATE OR REPLACE TABLE curated_player_game_log AS
        SELECT
            ppg.game_id,
            ppg.season AS season,
            ppg.player_id,
            cp.player_name,
            cg.game_date,
            ppg.tm AS team_abbreviation,
            cta.mapped_team_id AS team_id,
            ppg.opp AS opponent_team_abbreviation,
            opp_cta.mapped_team_id AS opponent_team_id,
            ppg.gs AS games_started,
            CAST(REPLACE(ppg.mp, ':', '.') AS DOUBLE) AS minutes_played, -- Convert MM:SS to decimal minutes
            ppg.fg AS field_goals,
            ppg.fga AS field_goal_attempts,
            CAST(ppg.fg_percent AS DOUBLE) AS field_goal_percentage,
            ppg.fg3 AS field_goals_3pt,
            ppg.fg3a AS field_goal_attempts_3pt,
            CAST(ppg.fg3_percent AS DOUBLE) AS field_goal_percentage_3pt,
            ppg.fg2 AS field_goals_2pt,
            ppg.fg2a AS field_goal_attempts_2pt,
            CAST(ppg.fg2_percent AS DOUBLE) AS field_goal_percentage_2pt,
            CAST(ppg.efg_percent AS DOUBLE) AS effective_field_goal_percentage,
            ppg.ft AS free_throws,
            ppg.fta AS free_throw_attempts,
            CAST(ppg.ft_percent AS DOUBLE) AS free_throw_percentage,
            ppg.orb AS offensive_rebounds,
            ppg.drb AS defensive_rebounds,
            ppg.trb AS total_rebounds,
            ppg.ast AS assists,
            ppg.stl AS steals,
            ppg.blk AS blocks,
            ppg.tov AS turnovers,
            ppg.pf AS personal_fouls,
            ppg.pts AS points,
            CAST(ppg.plus_minus AS DOUBLE) AS plus_minus_per_game,
            ppg.g_code AS game_code
        FROM staging_player_per_game ppg
        LEFT JOIN curated_game cg ON ppg.game_id = cg.game_id
        LEFT JOIN curated_player cp ON ppg.player_id = cp.player_id
        LEFT JOIN curated_team_alias cta ON ppg.season = cta.season AND ppg.tm = cta.alias_abbreviation
        LEFT JOIN curated_team_alias opp_cta ON ppg.season = opp_cta.season AND ppg.opp = opp_cta.alias_abbreviation
        WHERE ppg.game_id IS NOT NULL AND ppg.player_id IS NOT NULL
        ORDER BY cg.game_date DESC, ppg.player_id ASC
    """
    conn.execute(query)
    count = conn.execute("SELECT COUNT(*) FROM curated_player_game_log").fetchone()[0]
    logger.info(f"Created curated_player_game_log with {count} player game log entries")