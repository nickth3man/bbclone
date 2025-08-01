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
from rest_framework.decorators import api_view
from django.http import Http404
import logging

from .serializers import (
    PlayerSerializer,
    PlayByPlaySerializer,
    TeamSeasonStatsSerializer,
    PlayerGameLogSerializer,
)
from common.duckdb_repo import DuckDBRepo

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


# Initialize repository with database path
repo = DuckDBRepo(db_path='../data/hoarchive.duckdb')


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
        try:
            # Extract query parameters
            season = request.GET.get('season')
            team = request.GET.get('team')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 50))
            
            # Calculate offset for pagination
            offset = (page - 1) * page_size
            
            # Convert season to int if provided
            season_int = int(season) if season else None
            
            result = repo.query_players(
                season=season_int,
                team=team,
                limit=page_size,
                offset=offset
            )
            
            # Calculate pagination info
            total_count = result['total']
            has_next = offset + page_size < total_count
            has_previous = page > 1
            
            # Build paginated response
            paginated_data = {
                'count': total_count,
                'next': f'?page={page + 1}&page_size={page_size}' if has_next else None,
                'previous': f'?page={page - 1}&page_size={page_size}' if has_previous else None,
                'results': result['data']
            }
            
            return Response(paginated_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
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
            result = repo.query_play_by_play(game_id=game_id)
            
            if not result['data']:
                return Response(
                    {"error": "Game not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            return Response({
                'game_id': game_id,
                'total_events': result['total'],
                'events': result['data']
            })
        except ValueError:
            return Response(
                {"error": "Invalid game ID format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Database query failed: {e}")
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
        try:
            # Extract query parameters
            season = request.GET.get('season')
            team = request.GET.get('team')
            
            # Convert season to int if provided
            season_int = int(season) if season else None
            
            result = repo.query_team_season_stats(
                season=season_int,
                team=team
            )
            
            if not result['data']:
                return Response(
                    {'message': 'No data found for the specified criteria'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            return Response({
                'total': result['total'],
                'results': result['data']
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {'error': f'Invalid parameter format: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return Response(
                {"error": f"Database error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def player_game_logs(request, player_id):
    """Handle GET request for player game logs."""
    try:
        season = request.GET.get('season')
        season_int = int(season) if season else None
        
        try:
            result = repo.query_player_game_logs(
                player_id=player_id,
                season=season_int
            )
            
            if not result['data']:
                return Response(
                    {'message': 'No game logs found for this player'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            return Response({
                'player_id': player_id,
                'season': season,
                'total_games': result['total'],
                'games': result['data']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return Response(
                {'error': f'Database query failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except ValueError:
        return Response(
            {'error': 'Invalid player ID format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Request processing failed: {e}")
        return Response(
            {'error': f'Request processing failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )