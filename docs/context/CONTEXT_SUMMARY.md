# HoopsArchive Context Summary – Consolidated v0.3

Scope
- Repository provides NBA/ABA/BAA-like CSV datasets for players, teams, games, play-by-play, awards, and seasonal aggregates.
- Target platform: Postgres 16 (pgvector-ready), Django + DRF, React + Vite, Fly.io.
- Objectives in v0.3:
  1) Complete CSV inventory with schemas and grain
  2) Identify PK/FK candidates and join keys
  3) Catalog data quality risks and normalization rules
  4) Propose ERD v0.3 entities and relationships
  5) Define staging conventions to feed curated models

Method
- Sampled first ~50 lines per CSV to infer columns, types, and edge cases.
- Cross-referenced across files to identify join keys and normalization needs.
- Normalization principles: use numeric IDs where possible; otherwise resolve to TeamAlias(season, abbreviation). Treat NA/empty as NULL. Coerce float-like integers to integer domains.

High-Level Data Model Concepts
- Dimensions
  - Player: Numeric primary key from player.csv; unified across other sources via mapping tables for alternate IDs and slugs.
  - Team: Numeric primary key from team.csv; historical aliases per season via TeamAlias to handle code/name drift and defunct teams.
  - Season: Canonical season (e.g., 1947, 2025) and optional season_id mapping from source files.
  - SeasonType: Encodes Regular vs Playoffs vs All-Star when applicable.
- Facts
  - Game family keyed by game_id (TEXT) with game_summary, game_info, line_score (per team), other_stats (per team), play_by_play (events).
  - Player-season aggregates (Totals, Per Game, Per 36, Per 100, Advanced, Play By Play allocations).
  - Team-season aggregates (Totals, Per Game, Per 100, Opponent Per Game, Summaries).
  - Awards and end-of-season teams; All-Star selections; Draft and Combine.
- Core joins
  - game_id across game tables; player_id across player facts; team_id or TeamAlias(season, abbreviation) across team facts.

CSV Inventory and Inferred Schemas

Players and Identifiers
1) player.csv
- Columns: id, full_name, first_name, last_name, is_active
- PK: id (BIGINT)
- Notes: Boolean normalization for is_active; names for display only.

2) Player Directory.csv
- Columns: player, from, to, pos, ht_in_in, wt, birth_date, colleges, hof, slug
- Keys: slug unique-ish per player; use PlayerSlug mapping to Player.id.
- Quality: hof TRUE/FALSE; ht_in_in integer inches; colleges multi-text; dates YYYY-MM-DD.

3) common_player_info.csv
- Columns: person_id, names, slug, birthdate, position, jersey, team fields, flags, draft metadata
- Keys: person_id numeric; maps to Player.id via PlayerIdentifier mapping.
- Quality: height "6-10" string; weight numeric; birthdate timestamp; flags Y/N; many optional.

4) Player Career Info.csv
- Columns: player_id, player, birth_year, hof, num_seasons, first_seas, last_seas
- Keys: player_id aligns to player.csv.id
- Quality: birth_year often NA; hof boolean-like; seasons as INT.

Teams, Aliases, and History
1) team.csv
- Columns: id, full_name, abbreviation, nickname, city, state, year_founded
- PK: id (BIGINT)
- Quality: year_founded observed as float-like (e.g., 1949.0) → cast to INT.

2) Team Abbrev.csv
- Columns: season, lg, team, playoffs, abbreviation
- Grain: team-season with seasonal alias; includes legacy abbreviations (PHO/PHX, BRK/BKN, CHO/CHA).
- Keys: (season, abbreviation) as alias key; maps to Team via TeamAlias table.
- Quality: playoffs boolean-like; team free-text historic names; lg=NBA/ABA/BAA.

3) team_history.csv (sampled earlier)
- Tracks relocations/renames (team_id, city, nickname, year_founded, year_active_till)
- Use to build franchise lineage; may not cover all defunct ids.

4) team_details.csv (sampled earlier)
- Team metadata (arena, capacity, ownership, socials); some numeric fields float-like.

5) team_info_common.csv (header-only in sample)
- Intended for team-season metadata/rankings; confirm availability before modeling.

Games, Box, PBP
1) game.csv
- Grain: one row per game; includes team-level stats for both sides, matchup, W/L, season_type, and plenty of splits.
- Keys: game_id (TEXT) primary join key across game family.
- Fields: season_id (int), season type, game_date, home/visitor team IDs and names, splits, totals.
- Quality: treat game_id as canonical; prefer numeric team_id where available.

2) game_summary.csv
- Columns: game_date_est, game_id, status fields, home_team_id, visitor_team_id, season.
- Use for authoritative home/visitor assignment; join via game_id.

3) game_info.csv
- Columns: game_id, game_date, attendance, game_time.
- Quality: game_time often blank; attendance int.

4) line_score.csv
- Grain: per-team per-game scoring by quarter and OTs.
- Normalize into two rows per game (home/away) as GameLineScore; PK (game_id, team_id) or (game_id, is_home).

5) other_stats.csv
- Grain: per-team per-game paint points, second chance, fast break, turnovers, rebounds, leads, ties, points off turnovers.
- Normalize into two rows like line_score.

6) play_by_play.csv
- Grain: event-level with event types, descriptions, clock, score, player ids and team ids.
- Keys: (game_id, eventnum)
- Quality: Some numeric ids appear with decimal renderings (e.g., 1610612747.0) → cast to BIGINT; person1type/player roles vary by event type.

Officiating and Inactives
1) officials.csv
- Grain: game_id with official assignments; includes official_id, name, jersey_num (leading zeros).
- Model: Official dimension + GameOfficial association.

2) inactive_players.csv
- Grain: game_id; per-team per-game inactive lists, player and team metadata.
- Model: GameInactive association keyed by game_id and player_id.

Player Season Aggregates
1) Player Totals.csv
- Grain: player-season-team with TOT rows present (tm='TOT').
- Keys: candidate natural keys (seas_id) or composite (player_id, season, tm, is_tot).
- Fields: g, gs, mp, fg, fga, fg_percent, x3p, x3pa, x3p_percent, x2p, x2pa, x2p_percent, ft, fta, ft_percent, orb, drb, trb, ast, stl, blk, tov, pf, pts.
- Quality: NA in percentages; ages/experience as ints; ensure boolean-like flags normalized where present.

2) Player Per Game.csv
- Grain: mirrors Totals with per-game rates; same keys and TOT patterns.
- Fields: *_per_game NUMERIC plus mp_per_game.

3) Per 36 Minutes.csv
- Grain: player-season-team; rate metrics per 36; includes g, gs, mp context; TOT rows present.
- Keys: (seas_id) or (player_id, season, tm, is_tot).
- Quality: NA in 3P% and FT%; ensure NUMERIC(6,3) rates; maintain is_tot.

4) Per 100 Poss.csv
- Grain: same as Per 36 with o_rtg and d_rtg ratings appended.
- Keys: same as above.
- Quality: Extreme outliers for tiny mp; keep INT or SMALLINT ratings (prefer INT).

5) Advanced.csv
- Grain: player-season-team; PER, TS%, usage, BPM, OBPM, DBPM, WS, VORP, etc.
- Keys: aligns with other player season tables.
- Quality: NA and division-by-zero edge cases; store as NUMERIC with NULLs.

6) Player Play By Play.csv
- Grain: player-season-team; position allocations (pg/sg/sf/pf/c %) and on/off metrics.
- Keys: aligns with player season tables.
- Quality: percentages 0..1; event counts included.

7) Player Season Info.csv
- Columns: season, seas_id, player_id, player, birth_year, pos, age, lg, tm, experience.
- Use as master of player-season-team roster context (including TOT markers).
- Quality: BAA/ABA era codes; legacy tm abbreviations.

Team Season Aggregates
1) Team Totals.csv
- Grain: team-season, includes playoffs flag; League Average row included.
- Keys: natural composite (season, abbreviation, playoffs); prefer surrogate team_season_id via TeamAlias(season, abbreviation) + playoffs + lg.
- Fields: totals and percentages.

2) Team Stats Per Game.csv
- Grain: team-season; per-game rates including mp_per_game.
- Keys: (season, abbreviation, playoffs).
- Quality: league average present.

3) Team Stats Per 100 Poss.csv
- Grain: team-season; per-100 possession metrics and total mp.
- Keys: (season, abbreviation, playoffs).

4) Opponent Stats Per Game.csv
- Grain: team-season opponent per-game allowed.
- Keys: (season, abbreviation, playoffs).

5) Team Summaries.csv
- Grain: team-season summary with advanced ratings and context: age, w/l, pw/pl, mov, sos, srs, o_rtg, d_rtg, n_rtg, pace, f_tr, x3p_ar, ts_percent, e_fg_percent, tov_percent, orb_percent, ft_fga, opp_* mirrored rates, arena, attend, attend_g.
- Keys: (season, abbreviation, playoffs).
- Quality: Some rates in fraction form (0..1). League Average row contains NA in certain fields.

Awards, All-Star, Draft, Combine
1) All-Star Selections.csv
- Grain: player-season with team label being conference/captain/team depending on era.
- Model: AllStarTeam (season-specific label) and AllStarSelection linking Player to AllStarTeam.

2) Player Award Shares.csv
- Grain: player-season-award; includes votes points/share, first-place count, winner flag.
- Model: AwardType dimension and AwardVote fact keyed by (season, award_code, player_id).

3) End of Season Teams.csv and End of Season Teams (Voting).csv
- Grain: season, lg, team number (1st/2nd/3rd), player, position; voting includes pts_won, share and 1st/2nd/3rd counts.
- Model: EndSeasonTeam and EndSeasonVote; link to Player and Season.

4) draft_history.csv
- Grain: pick-level; person_id, player name, season, round, overall, team_id/abbreviation, school info.
- Model: DraftPick; reconcile person_id→Player.id via mapping.

5) draft_combine_stats.csv
- Grain: player-season; measurements and drills; many nulls; some player_id = -1 placeholders.
- Model: CombineMeasurement with nullable FKs and data quality whitelist for -1 as unknown.

Game Officiating and Inactives
- officials.csv: Official dimension (official_id, name, jersey_num TEXT) and GameOfficial association (game_id, official_id).
- inactive_players.csv: GameInactive (game_id, team_id/abbreviation, player_id, jersey_num TEXT).

Keys and Relationships

Player identifiers
- Primary: Player.id from player.csv (BIGINT).
- Alternate: common_player_info.person_id (BIGINT), directory.slug (TEXT). Use PlayerIdentifier mapping and PlayerSlug linkage.

Teams and aliases
- Primary: Team.id (BIGINT) from team.csv.
- Aliasing: TeamAlias(team_id, season, abbreviation, team_name, lg, playoffs?) with UNIQUE(season, abbreviation).
- Historical/defunct teams: ensure all referenced numeric team_ids exist; if not, add HistoricalTeam or expand Team to include defunct entries.

Seasons and types
- Season(season SMALLINT) with optional season_key mapping from season_id fields.
- SeasonType: Regular, Playoffs; derived from playoffs column in team-season aggregates; store season_type in game as provided.

Game family
- Game(game_id TEXT PK) is the universal join key across game, summary, info, line_score, other_stats, play_by_play.
- PlayByPlay PK: (game_id, eventnum).

Player season facts
- Natural grain: (player_id, season, team alias or team_id) with is_tot boolean for TOT lines.
- Use PlayerSeasonInfo as the master roster fact per player-season-team; all derived rate and advanced tables share its grain.

Team season facts
- Natural grain: (season, team alias or team_id, playoffs). Prefer a surrogate team_season_id to unify joins and allow strict FKs.

Data Quality and Normalization Rules

Nulls and NA
- Map NA, empty strings, and out-of-range sentinel values to NULL.
- For boolean-like: map TRUE/FALSE, true/false, 1/0, Y/N as needed; jersey numbers stored as TEXT to preserve leading zeros.

Numeric casting
- IDs: BIGINT; game_id: TEXT.
- Small bounded ints: SMALLINT for ages, periods, quarter points; INTEGER for counts (g, mp, fga).
- Percentages/ratios: NUMERIC(6,3) standard; some columns may fit NUMERIC(5,3). Values are fractions (0..1), not 0..100.
- Ratings/pace: store as NUMERIC(6,1) or INT where appropriate; offensive/defensive ratings in player per-100 as INT.

Team abbreviations
- Resolve tm/abbreviation with TeamAlias(season, abbreviation). Retain raw values in staging for lineage.

TOT rows
- Keep both TOT and per-team rows in staging with is_tot derived as (tm='TOT').
- Curated rule: for a player-season, either one TOT record or aggregated team splits; define a unique curated output per (player_id, season).

Historical IDs
- Some files use numeric team_id for defunct teams (e.g., 1610610035). Include these in Team dimension or maintain a HistoricalTeam dimension mapped to Team franchise when needed.

Play-by-play decimals
- Some IDs appear with decimals; parse to BIGINT safely. Validate that player/team IDs exist; if not, stage as NULL and audit.

League Average rows (team season aggregates)
- Present in Team Totals, Team Per Game, Team Per 100, Opponent Per Game, Team Summaries. Strategy decision is deferred to ERD/STAGING docs; both approaches are viable:
  1) Separate league_average_* tables to avoid null team FKs
  2) Single tables with is_league_average flag and nullable team FK

Staging Conventions (pre-curation)
- One staging table per CSV preserving source column names and types closely (after safe casting).
- Enforce PK or uniqueness where naturally present:
  - game_id unique in game family
  - (player_id, season, tm, is_tot) unique per player-season stat table
  - (season, abbreviation, playoffs) unique per team-season aggregate
- Derive helper columns:
  - is_tot from tm
  - season_type from playoffs where relevant
  - team_alias_id from TeamAlias(season, abbreviation)
- Apply robust casting:
  - Trim whitespace; normalize booleans; convert float-like ints to INT; NA/""→NULL
  - Bounds checks for rates 0..1; if out of range, NULL and log

ERD v0.3 Summary (to be detailed in ERD_v0.3.md)
- Dimensions
  - Player, PlayerIdentifier, PlayerSlug
  - Team, TeamAlias, optional HistoricalTeam/Franchise
  - Season, SeasonType, League (NBA/ABA/BAA)
  - Official, AllStarTeam, AwardType, Draft metadata
- Facts
  - Game, GameLineScore, GameOtherStats, GameOfficial, GameInactive, PlayByPlay
  - PlayerSeasonInfo (roster), PlayerTotals, PlayerPerGame, PlayerPer36, PlayerPer100, PlayerAdvanced, PlayerPlayByPlayAllocation
  - TeamSeasonTotals, TeamSeasonPerGame, TeamSeasonPer100, TeamOpponentPerGame, TeamSeasonSummaries
  - AllStarSelection, AwardVote, EndSeasonTeam, EndSeasonVote, DraftPick, CombineMeasurement
- Joins
  - game_id across game facts; player_id across player facts; team_id via Team or via TeamAlias(season, abbreviation) where only codes exist; officials through GameOfficial.

What Changes From Earlier Drafts
- Completed sampling of remaining CSV families:
  - Player Per 36 and Per 100 Poss (with o_rtg/d_rtg)
  - Team Totals, Team Stats Per Game, Team Stats Per 100 Poss, Opponent Stats Per Game, Team Summaries
  - Player Career Info
- Clarified handling of League Average rows in team-season aggregates
- Standardized numeric types for rates and ratings; jersey_num as TEXT
- Confirmed TOT handling and PlayerSeason master grain
- Affirmed PlayByPlay PK and decimal ID normalization

Next Steps
- Write docs/context/ERD_v0.3.md with concrete entity lists and relationship diagrams.
- Write docs/context/STAGING_MAPPING.md enumerating each CSV’s staging schema, PK/FK, and cleaning rules.
- Decide League Average storage pattern and codify in both ERD and STAGING docs.
- Implement loaders and validations aligned to the staging mappings.
