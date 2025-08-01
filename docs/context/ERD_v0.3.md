# ERD v0.3 (Placeholder)

Traceability:
- See docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Sections:
    - Background (ERD v0.3 defines curated tables and grains)
    - 2) Transform & Promote (curated tables, constraints, grains)
    - 3) API Expectations (fields align with curated schemas)

## TODO: Entities
- Player
- Team
- Game
- Season
- PlayerSeason
- TeamSeason
- GameBox
- PlayByPlay
- Lookups (aliases, seasons, etc.)
- LeagueAverages

## TODO: Relationships
- PlayerSeason (player_id) -> Player(id)
- TeamSeason (team_id) -> Team(id)
- GameBox (game_id) -> Game(id)
- PlayByPlay (game_id, player_id?, team_id?) -> Game/Player/Team
- LeagueAverages (season) -> Season(id or season)

## TODO: Constraints
- Primary keys and unique grains per table
- CHECK constraints (e.g., 0 ≤ rate ≤ 1)
- Jersey as TEXT (leading zeros preserved)
- DECIMAL(9,3) for numeric rates