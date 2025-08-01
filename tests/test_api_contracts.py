"""
Placeholders for API contract tests (Red phase).

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  API Expectations:
    * GET /players?season=1996&team=BOS with pagination
    * GET /games/<game_id>/pbp returns chronological events
"""


def test_players_endpoint_contract_placeholder():
    # TODO: Implement in Red phase: ensure 200, pagination metadata, fields shape
    # Target backend.players.views.PlayersView.get and repo layer contracts.
    pass


def test_game_pbp_endpoint_contract_placeholder():
    # TODO: Implement in Red phase: ensure 200, chronological ordering, IDs normalized
    # Target backend.players.views.GamePbpView.get and DuckDBRepo.get_game_pbp.
    pass