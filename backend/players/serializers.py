"""
Serializers for Players and Play-by-Play API payloads.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Scenarios:
    * Players endpoint fields align with curated Player/PlayerSeason schema
    * Play-by-Play endpoint returns chronological events with required fields

Notes:
- Implements proper DRF serializers for API responses
- Fields match curated schema from DuckDB ingestion
- Handles data serialization for API endpoints
"""
from rest_framework import serializers

class PlayerSerializer(serializers.Serializer):
    """Serializer for player data."""
    player_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    season = serializers.CharField(max_length=10)
    team = serializers.CharField(max_length=10)
    games_played = serializers.IntegerField()
    minutes = serializers.FloatField()
    points = serializers.FloatField()
    rebounds = serializers.FloatField()
    assists = serializers.FloatField()
    steals = serializers.FloatField()
    blocks = serializers.FloatField()
    fg_pct = serializers.FloatField()
    ft_pct = serializers.FloatField()
    three_pt_pct = serializers.FloatField()

class PlayByPlaySerializer(serializers.Serializer):
    """Serializer for play-by-play events."""
    event_id = serializers.IntegerField()
    game_id = serializers.IntegerField()
    period = serializers.IntegerField()
    clock = serializers.CharField(max_length=10)
    event_type = serializers.CharField(max_length=50)
    description = serializers.CharField()
    player_id = serializers.IntegerField(allow_null=True)
    team_id = serializers.CharField(max_length=10, allow_null=True)
    points_scored = serializers.IntegerField(default=0)
    home_score = serializers.IntegerField()
    away_score = serializers.IntegerField()

class TeamSeasonStatsSerializer(serializers.Serializer):
    """Serializer for team season statistics."""
    season = serializers.IntegerField()
    team_id = serializers.IntegerField(allow_null=True)
    team_abbreviation = serializers.CharField(max_length=10)
    league_abbreviation = serializers.CharField(max_length=10)
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    games_played = serializers.IntegerField()
    minutes_played_per_game = serializers.FloatField()
    field_goals = serializers.IntegerField()
    field_goal_attempts = serializers.IntegerField()
    field_goal_percentage = serializers.FloatField()
    field_goals_3pt = serializers.IntegerField()
    field_goal_attempts_3pt = serializers.IntegerField()
    field_goal_percentage_3pt = serializers.FloatField()
    field_goals_2pt = serializers.IntegerField()
    field_goal_attempts_2pt = serializers.IntegerField()
    field_goal_percentage_2pt = serializers.FloatField()
    effective_field_goal_percentage = serializers.FloatField()
    free_throws = serializers.IntegerField()
    free_throw_attempts = serializers.IntegerField()
    free_throw_percentage = serializers.FloatField()
    offensive_rebounds = serializers.IntegerField()
    defensive_rebounds = serializers.IntegerField()
    total_rebounds = serializers.IntegerField()
    assists = serializers.IntegerField()
    steals = serializers.IntegerField()
    blocks = serializers.IntegerField()
    turnovers = serializers.IntegerField()
    personal_fouls = serializers.IntegerField()
    points = serializers.IntegerField()
    team_age = serializers.FloatField(allow_null=True)
    winning_percentage = serializers.FloatField(allow_null=True)
    losing_percentage = serializers.FloatField(allow_null=True)
    margin_of_victory = serializers.FloatField(allow_null=True)
    strength_of_schedule = serializers.FloatField(allow_null=True)
    simple_rating_system = serializers.FloatField(allow_null=True)
    pace = serializers.FloatField(allow_null=True)
    offensive_rating = serializers.FloatField(allow_null=True)
    defensive_rating = serializers.FloatField(allow_null=True)
    net_rating = serializers.FloatField(allow_null=True)
    free_throw_attempt_rate = serializers.FloatField(allow_null=True)
    fg3_attempt_rate = serializers.FloatField(allow_null=True)
    true_shooting_percentage = serializers.FloatField(allow_null=True)
    team_effective_field_goal_percentage = serializers.FloatField(allow_null=True)
    team_turnover_percentage = serializers.FloatField(allow_null=True)
    team_offensive_rebound_percentage = serializers.FloatField(allow_null=True)
    team_free_throw_rate = serializers.FloatField(allow_null=True)
    opponent_effective_field_goal_percentage = serializers.FloatField(allow_null=True)
    opponent_turnover_percentage = serializers.FloatField(allow_null=True)
    opponent_defensive_rebound_percentage = serializers.FloatField(allow_null=True)
    opponent_free_throw_rate = serializers.FloatField(allow_null=True)


class PlayerGameLogSerializer(serializers.Serializer):
    """Serializer for player game level statistics."""
    game_id = serializers.CharField(max_length=50)
    season = serializers.IntegerField()
    player_id = serializers.IntegerField()
    player_name = serializers.CharField(max_length=100)
    game_date = serializers.DateField()
    team_abbreviation = serializers.CharField(max_length=10)
    team_id = serializers.IntegerField(allow_null=True)
    opponent_team_abbreviation = serializers.CharField(max_length=10)
    opponent_team_id = serializers.IntegerField(allow_null=True)
    games_started = serializers.IntegerField()
    minutes_played = serializers.FloatField()
    field_goals = serializers.IntegerField()
    field_goal_attempts = serializers.IntegerField()
    field_goal_percentage = serializers.FloatField()
    field_goals_3pt = serializers.IntegerField()
    field_goal_attempts_3pt = serializers.IntegerField()
    field_goal_percentage_3pt = serializers.FloatField()
    field_goals_2pt = serializers.IntegerField()
    field_goal_attempts_2pt = serializers.IntegerField()
    field_goal_percentage_2pt = serializers.FloatField()
    effective_field_goal_percentage = serializers.FloatField()
    free_throws = serializers.IntegerField()
    free_throw_attempts = serializers.IntegerField()
    free_throw_percentage = serializers.FloatField()
    offensive_rebounds = serializers.IntegerField()
    defensive_rebounds = serializers.IntegerField()
    total_rebounds = serializers.IntegerField()
    assists = serializers.IntegerField()
    steals = serializers.IntegerField()
    blocks = serializers.IntegerField()
    turnovers = serializers.IntegerField()
    personal_fouls = serializers.IntegerField()
    points = serializers.IntegerField()
    plus_minus_per_game = serializers.FloatField(allow_null=True)
    game_code = serializers.CharField(max_length=50)
