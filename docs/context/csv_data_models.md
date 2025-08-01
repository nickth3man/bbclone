# BBClone CSV Data Models

This document outlines the conceptual data models derived from the provided CSV files, illustrating the relationships between various entities for the Basketball-Reference clone. The diagrams are presented using Mermaid syntax for clarity.

## 1. Player-centric Data Model

This diagram focuses on the `PLAYER` entity and its relationships with various data points, including biographical information, career and season statistics, awards, and draft details.

```mermaid
erDiagram
    PLAYER ||--o{ PLAYER_CAREER_INFO : "has career stats"
    PLAYER ||--o{ PLAYER_SEASON_INFO : "has season stats"
    PLAYER ||--o{ ALL_STAR_SELECTIONS : "participated in"
    PLAYER ||--o{ PLAYER_AWARD_SHARES : "received awards"
    PLAYER ||--o{ DRAFT_COMBINE_STATS : "has combine stats from"
    PLAYER ||--o{ DRAFT_HISTORY : "was drafted in"
    PLAYER ||--o{ INACTIVE_PLAYERS : "was inactive in"

    PLAYER {
        INT id PK "Player ID"
        VARCHAR full_name
        VARCHAR first_name
        VARCHAR last_name
        BOOLEAN is_active
    }

    COMMON_PLAYER_INFO {
        INT person_id PK "Player ID (same as PLAYER.id)"
        VARCHAR display_first_last
        DATE birthdate
        VARCHAR school
        VARCHAR country
        VARCHAR height
        VARCHAR weight
        FLOAT season_exp
        VARCHAR position
        VARCHAR draft_year
        VARCHAR draft_round
        VARCHAR draft_number
    }

    PLAYER_CAREER_INFO {
        INT player_id FK "Player ID"
        VARCHAR player
        INT birth_year
        BOOLEAN hof
        INT num_seasons
        INT first_seas
        INT last_seas
    }

    PLAYER_SEASON_INFO {
        INT seas_id PK,FK "Season ID"
        INT season FK "Season Year"
        INT player_id PK,FK "Player ID"
        VARCHAR player
        VARCHAR pos
        INT age
        VARCHAR lg
        VARCHAR tm FK "Team abbreviation"
        INT experience
    }

    ALL_STAR_SELECTIONS {
        VARCHAR player FK "Player Name"
        VARCHAR team FK "Team Name"
        VARCHAR lg
        INT season FK "Season Year"
        BOOLEAN replaced
    }

    PLAYER_AWARD_SHARES {
        INT season FK "Season Year"
        VARCHAR award
        VARCHAR player FK "Player Name"
        INT player_id FK "Player ID"
        INT seas_id FK "Season ID"
        FLOAT share
        BOOLEAN winner
    }

    DRAFT_COMBINE_STATS {
        INT season FK "Season Year"
        INT player_id PK,FK "Player ID"
        VARCHAR player_name
        VARCHAR position
        FLOAT height_wo_shoes
        FLOAT weight
        FLOAT wingspan
        FLOAT standing_reach
        FLOAT max_vertical_leap
        FLOAT three_quarter_sprint
    }

    DRAFT_HISTORY {
        INT person_id PK,FK "Player ID"
        VARCHAR player_name
        INT season FK "Season Year"
        INT round_number
        INT overall_pick
        VARCHAR draft_type
        INT team_id FK "Team ID"
    }

    INACTIVE_PLAYERS {
        INT game_id FK "Game ID"
        INT player_id PK,FK "Player ID"
        INT team_id FK "Team ID"
        VARCHAR first_name
        VARCHAR last_name
        VARCHAR jersey_num
    }

    PLAYER_SEASON_INFO ||--o{ PLAYER_PER_GAME : "has per game stats for"
    PLAYER_SEASON_INFO ||--o{ PLAYER_TOTALS : "has total stats for"
    PLAYER_SEASON_INFO ||--o{ PER_36_MINUTES : "has per 36 min stats for"
    PLAYER_SEASON_INFO ||--o{ PER_100_POSS : "has per 100 poss stats for"
    PLAYER_SEASON_INFO ||--o{ ADVANCED : "has advanced stats for"
    PLAYER_SEASON_INFO ||--o{ PLAYER_PLAY_BY_PLAY : "has play by play stats for"
    PLAYER_SEASON_INFO ||--o{ PLAYER_SHOOTING : "has shooting stats for"
```

**Explanation:**
The central entity is `PLAYER` (from `player.csv`), identified by `id`. `COMMON_PLAYER_INFO` provides extended biographical data, linked via `person_id` (assumed equivalent to `player.id`). Statistical data is organized around `PLAYER_SEASON_INFO` (linking `seas_id` and `player_id`), acting as a bridge to detailed season-level performance tables like `PLAYER_PER_GAME`, `PLAYER_TOTALS`, and `ADVANCED`. Draft and award information (`DRAFT_HISTORY`, `ALL_STAR_SELECTIONS`, `PLAYER_AWARD_SHARES`, `DRAFT_COMBINE_STATS`) are linked directly or indirectly to the `PLAYER` and `SEASON` entities. `INACTIVE_PLAYERS` connects players to specific games where they were inactive.

## 2. Team-centric Data Model

This diagram illustrates the relationships around the `TEAM` entity, including detailed information, historical data, and various team and opponent statistics.

```mermaid
erDiagram
    TEAM ||--o{ TEAM_DETAILS : "has details"
    TEAM ||--o{ TEAM_HISTORY : "has history"
    TEAM ||--o{ TEAM_INFO_COMMON : "has season info"
    TEAM_INFO_COMMON ||--o{ TEAM_ABBREV : "has abbreviation for"

    TEAM_INFO_COMMON ||--o{ TEAM_STATS_PER_GAME : "has per game stats for"
    TEAM_INFO_COMMON ||--o{ TEAM_TOTALS : "has total stats for"
    TEAM_INFO_COMMON ||--o{ TEAM_STATS_PER_100_POSS : "has per 100 possession stats for"
    TEAM_INFO_COMMON ||--o{ TEAM_SUMMARIES : "has summary stats for"

    TEAM_INFO_COMMON ||--o{ OPPONENT_STATS_PER_GAME : "has opponent per game stats for"
    TEAM_INFO_COMMON ||--o{ OPPONENT_TOTALS : "has opponent total stats for"
    TEAM_INFO_COMMON ||--o{ OPPONENT_STATS_PER_100_POSS : "has opponent per 100 possession stats for"

    TEAM {
        INT id PK "Team ID"
        VARCHAR full_name
        VARCHAR abbreviation
        VARCHAR nickname
        VARCHAR city
        VARCHAR state
        FLOAT year_founded
    }

    TEAM_DETAILS {
        INT team_id PK,FK "Team ID"
        VARCHAR abbreviation
        VARCHAR nickname
        FLOAT yearfounded
        VARCHAR city
        VARCHAR arena
        FLOAT arenacapacity
        VARCHAR owner
        VARCHAR generalmanager
        VARCHAR headcoach
        VARCHAR facebook
        VARCHAR instagram
        VARCHAR twitter
    }

    TEAM_HISTORY {
        INT team_id PK,FK "Team ID"
        VARCHAR city
        VARCHAR nickname
        INT year_founded
        INT year_active_till
    }

    TEAM_INFO_COMMON {
        INT team_id PK,FK "Team ID"
        INT season_year PK,FK "Season Year"
        VARCHAR team_city
        VARCHAR team_name
        VARCHAR team_abbreviation PK,FK "Team abbreviation"
        VARCHAR team_conference
        VARCHAR team_division
        INT w "Wins"
        INT l "Losses"
        FLOAT pct "Winning Percentage"
    }

    TEAM_ABBREV {
        INT season PK,FK "Season Year"
        VARCHAR lg
        VARCHAR team
        BOOLEAN playoffs
        VARCHAR abbreviation PK,FK "Team abbreviation"
    }
```

**Explanation:**
The `TEAM` entity (`team.csv`) is the primary focus, identified by `id`. `TEAM_DETAILS` and `TEAM_HISTORY` enrich this with current and historical information. `TEAM_INFO_COMMON` is a critical junction, associating `TEAM` data with specific `SEASON`s and providing high-level performance metrics. This table acts as a hub for various statistical views (`TEAM_STATS_PER_GAME`, `TEAM_TOTALS`, `OPPONENT_STATS_PER_GAME`, etc.), allowing for detailed seasonal analysis of both a team's performance and its opponents'.

## 3. Game-centric Data Model

This diagram outlines the structure of game-related information, showing how different CSVs contribute to a complete picture of an individual game.

```mermaid
erDiagram
    GAME ||--o{ GAME_INFO : "has info"
    GAME ||--o{ LINE_SCORE : "has line score"
    GAME ||--o{ GAME_SUMMARY : "has summary"
    GAME ||--o{ OFFICIALS : "has officials"
    GAME ||--o{ OTHER_STATS : "has other stats"
    GAME ||--o{ INACTIVE_PLAYERS : "includes inactive players"

    GAME {
        VARCHAR game_id PK "Game ID"
        INT season_id
        INT team_id_home FK "Home Team ID"
        INT team_id_away FK "Away Team ID"
        DATE game_date
        VARCHAR matchup_home
        VARCHAR wl_home "Win/Loss Home"
        INT pts_home "Points Home"
        INT pts_away "Points Away"
        VARCHAR season_type
    }

    GAME_INFO {
        VARCHAR game_id PK,FK "Game ID"
        DATE game_date
        INT attendance
        VARCHAR game_time
    }

    LINE_SCORE {
        DATE game_date_est PK "Game Date (EST)"
        VARCHAR game_id PK,FK "Game ID"
        INT team_id_home FK "Home Team ID"
        INT team_id_away FK "Away Team ID"
        INT pts_qtr1_home
        INT pts_qtr4_home
        INT pts_home
        INT pts_qtr1_away
        INT pts_qtr4_away
        INT pts_away
    }

    GAME_SUMMARY {
        DATE game_date_est PK "Game Date (EST)"
        VARCHAR game_id PK,FK "Game ID"
        INT home_team_id FK "Home Team ID"
        INT visitor_team_id FK "Visitor Team ID"
        INT season FK "Season Year"
        VARCHAR gamecode
    }

    OFFICIALS {
        VARCHAR game_id PK,FK "Game ID"
        INT official_id PK "Official ID"
        VARCHAR first_name
        VARCHAR last_name
        INT jersey_num
    }

    OTHER_STATS {
        VARCHAR game_id PK,FK "Game ID"
        INT team_id_home FK "Home Team ID"
        INT team_id_away FK "Away Team ID"
        INT pts_paint_home
        INT pts_2nd_chance_home
        INT largest_lead_home
        INT lead_changes
        INT times_tied
        INT total_turnovers_home
        INT pts_off_to_home
        INT pts_paint_away
        INT pts_2nd_chance_away
        INT largest_lead_away
        INT total_turnovers_away
        INT pts_off_to_away
    }
```

**Explanation:**
The `GAME` entity (`game.csv`) serves as the central point for all game-related data, uniquely identified by `game_id`. It includes core details like participating teams and final scores, with foreign keys linking to the `TEAM` entity. Auxiliary tables such as `GAME_INFO`, `LINE_SCORE`, `GAME_SUMMARY`, `OFFICIALS`, and `OTHER_STATS` provide additional context and granular details for each game, all connected through the `game_id`. `INACTIVE_PLAYERS` also bridges to the `GAME` entity.

## 4. Overall Conceptual Data Model

This unified diagram provides a high-level overview of how the primary entities—`PLAYER`, `TEAM`, and `GAME`—interact within the BBClone data structure.

```mermaid
erDiagram
    PLAYER ||--o{ PLAYER_SEASON_INFO : "participates in"
    PLAYER ||--o{ DRAFT_HISTORY : "is drafted in"
    PLAYER ||--o{ INACTIVE_PLAYERS : "is inactive in"

    TEAM ||--o{ TEAM_INFO_COMMON : "has season data"

    GAME ||--o{ TEAM : "played by (home)"
    GAME ||--o{ TEAM : "played by (away)"
    GAME ||--o{ INACTIVE_PLAYERS : "has inactive players"

    PLAYER_SEASON_INFO ||--o{ GAME_PARTICIPATION : "stats in game"
    TEAM_INFO_COMMON ||--o{ GAME_PARTICIPATION : "teams participate in games"

    PLAYER {
        INT id PK "Player ID"
        VARCHAR full_name
    }

    TEAM {
        INT id PK "Team ID"
        VARCHAR full_name
        VARCHAR abbreviation
    }

    GAME {
        VARCHAR game_id PK "Game ID"
        DATE game_date
        INT team_id_home FK "Home Team ID"
        INT team_id_away FK "Away Team ID"
        INT pts_home
        INT pts_away
    }

    PLAYER_SEASON_INFO {
        INT seas_id PK,FK
        INT player_id PK,FK
        INT season
        VARCHAR tm
    }

    TEAM_INFO_COMMON {
        INT team_id PK,FK
        INT season_year PK,FK
    }

    DRAFT_HISTORY {
        INT person_id FK
        INT season FK
        INT team_id FK
    }

    INACTIVE_PLAYERS {
        INT game_id FK
        INT player_id FK
        INT team_id FK
    }

    GAME_PARTICIPATION {
        VARCHAR game_id FK
        INT player_id FK
        INT team_id FK
        INT seas_id FK
        INT pts
        INT reb
        INT ast
    }
```

**Explanation:**
This diagram demonstrates the core relationships:
*   **Players and Seasons:** Players are linked to their seasonal statistics through `PLAYER_SEASON_INFO`.
*   **Players and Draft/Inactivity:** Players have direct relationships to their draft history (`DRAFT_HISTORY`) and to game where they were inactive (`INACTIVE_PLAYERS`).
*   **Teams and Seasons:** Teams are linked to their seasonal information and statistics via `TEAM_INFO_COMMON`.
*   **Games, Players, and Teams:** Games are central, connecting to two teams (home and away). The conceptual `GAME_PARTICIPATION` links player and team seasonal data to individual game events.