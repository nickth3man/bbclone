"""
URL routing scaffold for API endpoints.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Section 3) API Expectations:
    * GET /players?season=1996&team=BOS (pagination, filters)
    * GET /games/<game_id>/pbp (chronological events)

Routes are wired to stub views that raise NotImplementedError.
"""

from typing import List
from django.urls import path  # type: ignore

from players.views import PlayersView, GamePbpView, TeamSeasonStatsView, player_game_logs  # type: ignore


urlpatterns: List = [
    path("players", PlayersView.as_view(), name="players"),
    path("games/<int:game_id>/pbp", GamePbpView.as_view(), name="game-pbp"),
    path("teams/stats", TeamSeasonStatsView.as_view(), name="team-season-stats"),
    path("players/<int:player_id>/gamelog", player_game_logs, name="player-game-log"),
]