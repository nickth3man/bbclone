"""
DRF API views for Players and Play-by-Play endpoints.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Scenarios:
    * Players endpoint filters by season and team with pagination (p90 < 1s)
    * Play-by-Play endpoint returns PBP JSON for a game (ordering, integrity)

Notes:
- Uses Django REST Framework for API endpoints
- Implements repository pattern with DuckDBRepo
- Handles pagination, filtering, and error responses
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from players.serializers import TeamSeasonStatsSerializer, PlayerGameLogSerializer

from common.duckdb_repo import DuckDBRepo
from ingest.duckdb_client import connect

class PlayersPagination(PageNumberPagination):
    """Custom pagination for players endpoint."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

class PlayersView(APIView):
    """GET /players?season=YYYY&team=ABC
    
    Filters players by season and team with pagination.
    
    Expected behavior per BDD:
    - Filters: season, team (case-insensitive; alias mapping handled downstream).
    - Pagination: include count, next, previous metadata.
    - Fields: align with curated Player/PlayerSeason schema.
    - Performance: p90 < 1s for representative dataset.
    """
    pagination_class = PlayersPagination

    def get(self, request):
        """Handle GET request for filtered player data."""
        filters = {}
        if 'season' in request.GET:
            filters['season'] = request.GET['season']
        if 'team' in request.GET:
            filters['team'] = request.GET['team']
        
        try:
            repo = DuckDBRepo(connect())
            data = repo.query_players(filters)
            
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(data, request)
            return paginator.get_paginated_response(page)
        except Exception as e:
            return Response(
                {"error": f"Database error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GamePbpView(APIView):
    """GET /games/<game_id>/pbp
    
    Returns chronological play-by-play events for the given game.
    
    Expected behavior per BDD:
    - Returns chronological play-by-play events with required fields.
    - Ensures event ordering by period and clock.
    - Normalizes decimalized IDs to canonical keys.
    - Performance: p90 < 1s on large OT games.
    - 404 for missing game_id.
    """
    def get(self, request, game_id):
        """Handle GET request for game play-by-play data."""
        try:
            repo = DuckDBRepo(connect())
            data = repo.get_game_pbp(int(game_id))
            
            if not data:
                return Response(
                    {"error": "Game not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            return Response(data)
        except ValueError:
            return Response(
                {"error": "Invalid game ID format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Database error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TeamSeasonStatsPagination(PageNumberPagination):
    """Custom pagination for team season stats endpoint."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class TeamSeasonStatsView(APIView):
    """GET /teams/stats/?season=YYYY&team=ABC
    
    Filters team season statistics by season and team with pagination.
    """
    pagination_class = TeamSeasonStatsPagination

    def get(self, request):
        """Handle GET request for filtered team season data."""
        filters = {}
        if 'season' in request.GET:
            try:
                filters['season'] = int(request.GET['season'])
            except ValueError:
                return Response(
                    {"error": "Invalid season format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if 'team' in request.GET:
            filters['team_abbreviation'] = request.GET['team']
        
        try:
            repo = DuckDBRepo(connect())
            data = repo.get_team_season_stats(**filters)
            
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(data, request)
            serializer = TeamSeasonStatsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Database error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PlayerGameLogView(APIView):
    """GET /players/<player_id>/gamelog/?season=YYYY
    
    Returns chronological game log events for the given player.
    """
    def get(self, request, player_id):
        """Handle GET request for player game log data."""
        season = request.GET.get('season')
        if season:
            try:
                season = int(season)
            except ValueError:
                return Response(
                    {"error": "Invalid season format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            repo = DuckDBRepo(connect())
            data = repo.get_player_game_log(int(player_id), season)
            
            if not data:
                return Response(
                    {"error": "Player game log not found for the given criteria"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = PlayerGameLogSerializer(data, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid player ID format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Database error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )