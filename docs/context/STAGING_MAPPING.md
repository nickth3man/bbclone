# STAGING MAPPING (Placeholder)

Traceability:
- See docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Section 1) Ingestion & Staging: CSV -> staging tables, NULLSTRINGS, type casts

## TODO: CSV to Staging Table Mapping
- csv/player.csv -> staging_player (ids BIGINT, jersey TEXT, dates DATE)
- csv/team.csv -> staging_team
- csv/game.csv -> staging_game
- csv/play_by_play.csv -> staging_pbp
- csv/game_box.csv -> staging_game_box
- csv/team_history.csv -> staging_team_history
- csv/common_player_info.csv -> staging_player_info
- csv/Player Season Info.csv -> staging_player_season
- csv/Team Stats Per Game.csv -> staging_team_stats_pg
- csv/Player Per Game.csv -> staging_player_stats_pg
- ...

Notes:
- Apply NULLSTRINGS: ['', 'NA', 'null'].
- Consider read_csv_auto or COPY options: delimiter, header, types.
- Edge cases: empty CSVs (empty tables), float-looking IDs cast to integers, jersey leading zeros preserved as TEXT.