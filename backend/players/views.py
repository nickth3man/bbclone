"""
DRF API view stubs for Players and Play-by-Play endpoints.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Scenarios:
    * Players endpoint filters by season and team with pagination (p90 < 1s)
    * Play-by-Play endpoint returns PBP JSON for a game (ordering, integrity)

Notes:
- These views intentionally raise NotImplementedError to ensure Red phase tests fail
  until repository and serialization are implemented.
- Docstrings reference pagination, CSV export, and performance acceptance criteria.
"""

from typing import Any


# Provide local minimal stubs to avoid requiring DRF at scaffold time
class _BaseView(object):
    """New-style base to satisfy type checker."""

    @classmethod
    def as_view(cls, *args: Any, **kwargs: Any):  # pragma: no cover
        def _view(*_a: Any, **_k: Any):
            raise NotImplementedError("APIView.as_view stub invoked")
        return _view


class APIView(_BaseView):  # type: ignore
    pass


class Request(object):  # type: ignore
    pass


class Response(object):  # type: ignore
    pass


class PlayersView(APIView):
    """GET /players?season=YYYY&team=ABC

    Expected behavior per BDD (to be implemented later):
    - Filters: season, team (case-insensitive; alias mapping handled downstream).
    - Pagination: include count, next, previous metadata.
    - Fields: align with curated Player/PlayerSeason schema.
    - Performance: p90 < 1s for representative dataset.
    - CSV Export: triggered client-side; server provides consistent headers.

    In scaffolding, this endpoint is not implemented and should raise.
    """

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        raise NotImplementedError("PlayersView.get not implemented (scaffold)")


class GamePbpView(APIView):
    """GET /games/<game_id>/pbp

    Expected behavior per BDD (to be implemented later):
    - Returns chronological play-by-play events with required fields.
    - Ensures event ordering by period and clock.
    - Normalizes decimalized IDs to canonical keys.
    - Performance: p90 < 1s on large OT games.
    - 404 for missing game_id.

    In scaffolding, this endpoint is not implemented and should raise.
    """

    def get(self, request: Request, game_id: int, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        raise NotImplementedError("GamePbpView.get not implemented (scaffold)")