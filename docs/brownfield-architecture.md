# HoopsArchive Brownfield Enhancement Architecture

**Document Version**: 1.0  
**Generated**: 2024  
**Project**: HoopsArchive Basketball Analytics Platform  
**Enhancement Type**: Brownfield Feature Addition & Performance Optimization  

## 1. Introduction & Project Context

### Current Project State

HoopsArchive is a basketball analytics platform currently in **Red Phase** scaffolding with foundational components established:

- **Backend**: Django REST Framework with DuckDB analytics database
- **Frontend**: React with TypeScript and Vite build system
- **Data Layer**: CSV-based historical basketball data (1M+ records)
- **Testing**: BDD framework with Gherkin specifications
- **Deployment**: Fly.io cloud platform configuration

### Enhancement Scope

This brownfield enhancement focuses on:

1. **Complete CSV Data Ingestion Pipeline** - Automated processing of 30+ CSV files
2. **High-Performance API Layer** - Sub-200ms response times for analytics queries
3. **Interactive Basketball Visualizations** - React-based charts and analytics dashboards
4. **Scalable Data Architecture** - Support for 1M+ historical records with room for growth

### Business Context

**Primary Goal**: Transform existing scaffolding into a production-ready basketball analytics platform
**Target Users**: Basketball analysts, coaches, sports journalists, and enthusiasts
**Success Metrics**: 
- API response times < 200ms
- 99.9% uptime
- Complete historical data coverage (1946-present)
- Interactive visualization performance

## 2. Existing Project Analysis

### Current Codebase Assessment

**Strengths**:
- Clean separation of concerns (backend/frontend)
- Modern tech stack (Django, React, TypeScript)
- DuckDB chosen for analytics workloads
- BDD testing framework established
- Fly.io deployment configuration

**Technical Debt & Gaps**:
- Incomplete CSV ingestion pipeline
- Missing API endpoints for core basketball entities
- No data validation or transformation logic
- Frontend components not implemented
- Performance optimization not addressed
- Security layer incomplete

### Existing Architecture Patterns

**Current Patterns**:
- **Repository Pattern**: DuckDB repository abstraction
- **REST API**: Django REST Framework endpoints
- **Component Architecture**: React functional components
- **Monorepo Structure**: Backend and frontend in single repository

**Architectural Decisions to Maintain**:
- DuckDB for analytics (excellent for read-heavy workloads)
- Django REST Framework (mature, well-documented)
- React with TypeScript (type safety, modern development)
- Fly.io deployment (cost-effective, good performance)

## 3. Enhancement Architecture Design

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Data Layer    │
│   (React)       │◄──►│   (Django)      │◄──►│   (DuckDB)      │
│                 │    │                 │    │                 │
│ • Visualizations│    │ • REST Endpoints│    │ • Analytics DB  │
│ • Player Stats  │    │ • Data Transform│    │ • CSV Ingestion │
│ • Team Analytics│    │ • Performance   │    │ • Indexes       │
│ • Game Analysis │    │ • Caching       │    │ • Views         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Deployment    │
                    │   (Fly.io)      │
                    │                 │
                    │ • Load Balancer │
                    │ • Auto-scaling  │
                    │ • Monitoring    │
                    └─────────────────┘
```

### Technology Stack Alignment

**Backend Stack**:
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: DuckDB for analytics, SQLite for Django metadata
- **Caching**: Redis for API response caching
- **Data Processing**: Pandas for CSV transformation
- **Validation**: Pydantic for data models

**Frontend Stack**:
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite for fast development and builds
- **Routing**: React Router for SPA navigation
- **State Management**: React Query for server state, Zustand for client state
- **Visualization**: D3.js and Chart.js for basketball-specific charts
- **Styling**: Tailwind CSS for responsive design

**Infrastructure Stack**:
- **Deployment**: Fly.io with Docker containers
- **Monitoring**: Fly.io metrics + custom application logging
- **CI/CD**: GitHub Actions for automated testing and deployment

## 4. Data Models & Database Design

### Core Entity Models

**Players**:
```sql
CREATE TABLE players (
    player_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    birth_date DATE,
    height_inches INTEGER,
    weight_lbs INTEGER,
    position VARCHAR(10),
    college VARCHAR(100),
    draft_year INTEGER,
    draft_round INTEGER,
    draft_pick INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Teams**:
```sql
CREATE TABLE teams (
    team_id VARCHAR PRIMARY KEY,
    team_name VARCHAR NOT NULL,
    abbreviation VARCHAR(3) NOT NULL,
    city VARCHAR(50),
    conference VARCHAR(10),
    division VARCHAR(20),
    founded_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Games**:
```sql
CREATE TABLE games (
    game_id VARCHAR PRIMARY KEY,
    game_date DATE NOT NULL,
    season INTEGER NOT NULL,
    home_team_id VARCHAR REFERENCES teams(team_id),
    away_team_id VARCHAR REFERENCES teams(team_id),
    home_score INTEGER,
    away_score INTEGER,
    overtime_periods INTEGER DEFAULT 0,
    attendance INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Player Game Stats**:
```sql
CREATE TABLE player_game_stats (
    stat_id VARCHAR PRIMARY KEY,
    game_id VARCHAR REFERENCES games(game_id),
    player_id VARCHAR REFERENCES players(player_id),
    team_id VARCHAR REFERENCES teams(team_id),
    minutes_played DECIMAL(4,1),
    points INTEGER,
    rebounds INTEGER,
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    field_goals_made INTEGER,
    field_goals_attempted INTEGER,
    three_pointers_made INTEGER,
    three_pointers_attempted INTEGER,
    free_throws_made INTEGER,
    free_throws_attempted INTEGER,
    plus_minus INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Performance Indexes

```sql
-- Player lookups
CREATE INDEX idx_players_name ON players(name);
CREATE INDEX idx_players_position ON players(position);

-- Game queries
CREATE INDEX idx_games_date ON games(game_date);
CREATE INDEX idx_games_season ON games(season);
CREATE INDEX idx_games_teams ON games(home_team_id, away_team_id);

-- Stats queries (critical for performance)
CREATE INDEX idx_player_stats_player_season ON player_game_stats(player_id, game_id);
CREATE INDEX idx_player_stats_team_season ON player_game_stats(team_id, game_id);
CREATE INDEX idx_player_stats_game ON player_game_stats(game_id);
```

### Analytical Views

**Player Season Averages**:
```sql
CREATE VIEW player_season_averages AS
SELECT 
    pgs.player_id,
    p.name,
    EXTRACT(YEAR FROM g.game_date) as season,
    COUNT(*) as games_played,
    AVG(pgs.minutes_played) as avg_minutes,
    AVG(pgs.points) as avg_points,
    AVG(pgs.rebounds) as avg_rebounds,
    AVG(pgs.assists) as avg_assists,
    AVG(pgs.field_goals_made::FLOAT / NULLIF(pgs.field_goals_attempted, 0)) as fg_percentage,
    AVG(pgs.three_pointers_made::FLOAT / NULLIF(pgs.three_pointers_attempted, 0)) as three_pt_percentage
FROM player_game_stats pgs
JOIN games g ON pgs.game_id = g.game_id
JOIN players p ON pgs.player_id = p.player_id
GROUP BY pgs.player_id, p.name, EXTRACT(YEAR FROM g.game_date);
```

## 5. API Design & Integration

### REST API Endpoints

**Player Endpoints**:
```
GET    /api/players/                    # List players with pagination
GET    /api/players/{id}/               # Player details
GET    /api/players/{id}/stats/         # Player career stats
GET    /api/players/{id}/games/         # Player game log
GET    /api/players/search/?q={query}   # Search players by name
```

**Team Endpoints**:
```
GET    /api/teams/                      # List all teams
GET    /api/teams/{id}/                 # Team details
GET    /api/teams/{id}/roster/          # Current roster
GET    /api/teams/{id}/stats/           # Team season stats
GET    /api/teams/{id}/schedule/        # Team schedule
```

**Game Endpoints**:
```
GET    /api/games/                      # List games with filters
GET    /api/games/{id}/                 # Game details
GET    /api/games/{id}/boxscore/        # Complete box score
GET    /api/games/today/                # Today's games
GET    /api/games/schedule/             # Upcoming games
```

**Analytics Endpoints**:
```
GET    /api/analytics/leaders/          # Statistical leaders
GET    /api/analytics/standings/        # Team standings
GET    /api/analytics/player-comparison/ # Compare players
GET    /api/analytics/team-comparison/  # Compare teams
```

### Response Schemas

**Player Response**:
```json
{
  "player_id": "player_123",
  "name": "LeBron James",
  "position": "SF",
  "height_inches": 81,
  "weight_lbs": 250,
  "birth_date": "1984-12-30",
  "college": "None",
  "draft_info": {
    "year": 2003,
    "round": 1,
    "pick": 1
  },
  "career_stats": {
    "games_played": 1421,
    "points_per_game": 27.2,
    "rebounds_per_game": 7.5,
    "assists_per_game": 7.3
  }
}
```

### Performance Optimization

**Caching Strategy**:
- **Redis Cache**: 5-minute TTL for frequently accessed endpoints
- **Database Query Optimization**: Proper indexing and query planning
- **Response Compression**: Gzip compression for large responses
- **Pagination**: Limit responses to 50 items per page

**Query Optimization**:
```python
# Optimized player stats query
def get_player_season_stats(player_id, season):
    return (
        PlayerGameStats.objects
        .select_related('game', 'player', 'team')
        .filter(player_id=player_id, game__season=season)
        .aggregate(
            games_played=Count('game_id'),
            avg_points=Avg('points'),
            avg_rebounds=Avg('rebounds'),
            avg_assists=Avg('assists')
        )
    )
```

## 6. Frontend Component Architecture

### Component Hierarchy

```
App
├── Layout
│   ├── Header
│   ├── Navigation
│   └── Footer
├── Pages
│   ├── HomePage
│   ├── PlayersPage
│   │   ├── PlayerList
│   │   ├── PlayerDetail
│   │   └── PlayerComparison
│   ├── TeamsPage
│   │   ├── TeamList
│   │   ├── TeamDetail
│   │   └── TeamStandings
│   ├── GamesPage
│   │   ├── GameList
│   │   ├── GameDetail
│   │   └── LiveScores
│   └── AnalyticsPage
│       ├── StatLeaders
│       ├── TrendAnalysis
│       └── CustomCharts
└── Shared Components
    ├── Charts
    │   ├── BarChart
    │   ├── LineChart
    │   ├── RadarChart
    │   └── HexbinChart
    ├── DataTable
    ├── SearchBox
    ├── Pagination
    └── LoadingSpinner
```

### Basketball-Specific Visualizations

**Shot Chart Component**:
```typescript
interface ShotChartProps {
  playerId: string;
  season: number;
  gameType?: 'regular' | 'playoffs';
}

const ShotChart: React.FC<ShotChartProps> = ({ playerId, season, gameType = 'regular' }) => {
  const { data: shotData, isLoading } = usePlayerShots(playerId, season, gameType);
  
  return (
    <div className="shot-chart-container">
      <svg width={600} height={400}>
        <CourtBackground />
        {shotData?.map(shot => (
          <ShotMarker 
            key={shot.id}
            x={shot.x}
            y={shot.y}
            made={shot.made}
            shotType={shot.shotType}
          />
        ))}
      </svg>
    </div>
  );
};
```

**Player Comparison Radar**:
```typescript
const PlayerRadarChart: React.FC<{ playerIds: string[] }> = ({ playerIds }) => {
  const { data: comparisonData } = usePlayerComparison(playerIds);
  
  const radarData = {
    labels: ['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', 'FG%'],
    datasets: comparisonData?.map((player, index) => ({
      label: player.name,
      data: [
        player.stats.points,
        player.stats.rebounds,
        player.stats.assists,
        player.stats.steals,
        player.stats.blocks,
        player.stats.fieldGoalPercentage * 100
      ],
      borderColor: PLAYER_COLORS[index],
      backgroundColor: `${PLAYER_COLORS[index]}20`
    }))
  };
  
  return <Radar data={radarData} options={radarOptions} />;
};
```

### State Management

**React Query for Server State**:
```typescript
// Custom hooks for data fetching
export const usePlayer = (playerId: string) => {
  return useQuery({
    queryKey: ['player', playerId],
    queryFn: () => api.getPlayer(playerId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const usePlayerStats = (playerId: string, season: number) => {
  return useQuery({
    queryKey: ['playerStats', playerId, season],
    queryFn: () => api.getPlayerStats(playerId, season),
    enabled: !!playerId && !!season,
  });
};
```

**Zustand for Client State**:
```typescript
interface AppState {
  selectedSeason: number;
  comparisonPlayers: string[];
  chartType: 'bar' | 'line' | 'radar';
  setSelectedSeason: (season: number) => void;
  addComparisonPlayer: (playerId: string) => void;
  removeComparisonPlayer: (playerId: string) => void;
  setChartType: (type: 'bar' | 'line' | 'radar') => void;
}

const useAppStore = create<AppState>((set) => ({
  selectedSeason: new Date().getFullYear(),
  comparisonPlayers: [],
  chartType: 'bar',
  setSelectedSeason: (season) => set({ selectedSeason: season }),
  addComparisonPlayer: (playerId) => 
    set((state) => ({ 
      comparisonPlayers: [...state.comparisonPlayers, playerId].slice(0, 4) 
    })),
  removeComparisonPlayer: (playerId) => 
    set((state) => ({ 
      comparisonPlayers: state.comparisonPlayers.filter(id => id !== playerId) 
    })),
  setChartType: (type) => set({ chartType: type }),
}));
```

## 7. Data Ingestion Pipeline

### CSV Processing Architecture

**Ingestion Flow**:
```
CSV Files → Validation → Transformation → DuckDB Loading → Index Creation
```

**Pipeline Components**:

1. **CSV Validator**:
```python
class CSVValidator:
    def __init__(self, schema_config):
        self.schema = schema_config
    
    def validate_file(self, file_path: str) -> ValidationResult:
        df = pd.read_csv(file_path)
        errors = []
        
        # Check required columns
        missing_cols = set(self.schema.required_columns) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Validate data types
        for col, expected_type in self.schema.column_types.items():
            if col in df.columns:
                if not self._validate_column_type(df[col], expected_type):
                    errors.append(f"Invalid type for column {col}")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

2. **Data Transformer**:
```python
class BasketballDataTransformer:
    def transform_player_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Standardize player names
        df['name'] = df['name'].str.title().str.strip()
        
        # Convert height to inches
        if 'height' in df.columns:
            df['height_inches'] = df['height'].apply(self._parse_height)
        
        # Handle missing values
        df['college'] = df['college'].fillna('Unknown')
        
        # Generate consistent IDs
        df['player_id'] = df.apply(self._generate_player_id, axis=1)
        
        return df
    
    def _parse_height(self, height_str: str) -> int:
        """Convert '6-8' format to inches"""
        if pd.isna(height_str):
            return None
        feet, inches = height_str.split('-')
        return int(feet) * 12 + int(inches)
```

3. **DuckDB Loader**:
```python
class DuckDBLoader:
    def __init__(self, db_path: str):
        self.conn = duckdb.connect(db_path)
    
    def load_dataframe(self, df: pd.DataFrame, table_name: str, mode: str = 'append'):
        # Use DuckDB's efficient pandas integration
        if mode == 'replace':
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        self.conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} AS 
            SELECT * FROM df
        """)
        
        if mode == 'append':
            self.conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
```

### Batch Processing Strategy

**Processing Order**:
1. **Reference Data**: Teams, Players (static entities)
2. **Game Data**: Games, Schedules
3. **Statistics**: Player/Team game stats
4. **Derived Data**: Season averages, advanced metrics

**Error Handling**:
```python
class IngestionOrchestrator:
    def process_all_files(self, csv_directory: str):
        results = []
        
        for file_path in self._get_processing_order(csv_directory):
            try:
                result = self._process_single_file(file_path)
                results.append(result)
                
                if not result.success:
                    self.logger.error(f"Failed to process {file_path}: {result.errors}")
                    
            except Exception as e:
                self.logger.error(f"Unexpected error processing {file_path}: {e}")
                results.append(ProcessingResult(
                    file_path=file_path,
                    success=False,
                    errors=[str(e)]
                ))
        
        return IngestionSummary(results)
```

## 8. Testing Strategy

### Backend Testing

**API Contract Tests**:
```python
class TestPlayerAPI(APITestCase):
    def setUp(self):
        self.player = Player.objects.create(
            player_id="test_player_1",
            name="Test Player",
            position="PG"
        )
    
    def test_get_player_detail(self):
        url = f"/api/players/{self.player.player_id}/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Test Player")
        self.assertEqual(response.data['position'], "PG")
    
    def test_player_stats_performance(self):
        # Create test game stats
        for i in range(100):
            PlayerGameStats.objects.create(
                player=self.player,
                game=self._create_test_game(),
                points=random.randint(10, 40)
            )
        
        start_time = time.time()
        response = self.client.get(f"/api/players/{self.player.player_id}/stats/")
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 0.2)  # Sub-200ms requirement
```

**Data Ingestion Tests**:
```python
class TestCSVIngestion(TestCase):
    def test_player_csv_validation(self):
        validator = CSVValidator(PLAYER_SCHEMA)
        result = validator.validate_file("test_data/valid_players.csv")
        self.assertTrue(result.is_valid)
    
    def test_malformed_csv_handling(self):
        validator = CSVValidator(PLAYER_SCHEMA)
        result = validator.validate_file("test_data/malformed_players.csv")
        self.assertFalse(result.is_valid)
        self.assertIn("Missing columns", str(result.errors))
```

### Frontend Testing

**Component Tests**:
```typescript
// PlayerCard.test.tsx
import { render, screen } from '@testing-library/react';
import { PlayerCard } from './PlayerCard';

const mockPlayer = {
  player_id: 'test_1',
  name: 'Test Player',
  position: 'PG',
  career_stats: {
    points_per_game: 25.5,
    rebounds_per_game: 7.2,
    assists_per_game: 8.1
  }
};

test('renders player information correctly', () => {
  render(<PlayerCard player={mockPlayer} />);
  
  expect(screen.getByText('Test Player')).toBeInTheDocument();
  expect(screen.getByText('PG')).toBeInTheDocument();
  expect(screen.getByText('25.5 PPG')).toBeInTheDocument();
});

test('handles missing stats gracefully', () => {
  const playerWithoutStats = { ...mockPlayer, career_stats: null };
  render(<PlayerCard player={playerWithoutStats} />);
  
  expect(screen.getByText('No stats available')).toBeInTheDocument();
});
```

**Integration Tests**:
```typescript
// PlayerPage.integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PlayerPage } from './PlayerPage';
import { server } from '../mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('loads and displays player data', async () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  
  render(
    <QueryClientProvider client={queryClient}>
      <PlayerPage playerId="test_player_1" />
    </QueryClientProvider>
  );
  
  expect(screen.getByText('Loading...')).toBeInTheDocument();
  
  await waitFor(() => {
    expect(screen.getByText('LeBron James')).toBeInTheDocument();
  });
  
  expect(screen.getByText('27.2 PPG')).toBeInTheDocument();
});
```

### Performance Testing

**Load Testing**:
```python
# locustfile.py
from locust import HttpUser, task, between

class BasketballAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_player_list(self):
        self.client.get("/api/players/")
    
    @task(2)
    def get_player_detail(self):
        player_id = random.choice(self.player_ids)
        self.client.get(f"/api/players/{player_id}/")
    
    @task(1)
    def get_player_stats(self):
        player_id = random.choice(self.player_ids)
        self.client.get(f"/api/players/{player_id}/stats/")
    
    def on_start(self):
        # Load test player IDs
        response = self.client.get("/api/players/?limit=100")
        self.player_ids = [p['player_id'] for p in response.json()['results']]
```

## 9. Security Integration

### API Security

**Rate Limiting**:
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# Custom throttling for analytics endpoints
class AnalyticsRateThrottle(UserRateThrottle):
    scope = 'analytics'
    rate = '500/hour'
```

**Input Validation**:
```python
from rest_framework import serializers

class PlayerStatsQuerySerializer(serializers.Serializer):
    season = serializers.IntegerField(min_value=1946, max_value=2030)
    game_type = serializers.ChoiceField(choices=['regular', 'playoffs'], default='regular')
    limit = serializers.IntegerField(min_value=1, max_value=100, default=20)
    
    def validate_season(self, value):
        if value > datetime.now().year + 1:
            raise serializers.ValidationError("Season cannot be in the future")
        return value
```

**CORS Configuration**:
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Development
    "https://hoopsarchive.fly.dev",  # Production
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

### Data Security

**Database Security**:
```python
# Secure database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# DuckDB connection with security
class SecureDuckDBRepository:
    def __init__(self, db_path: str):
        # Ensure database file permissions
        os.chmod(db_path, 0o600)
        self.conn = duckdb.connect(db_path, read_only=True)
    
    def execute_query(self, query: str, params: dict = None):
        # Validate query to prevent injection
        if not self._is_safe_query(query):
            raise SecurityError("Potentially unsafe query detected")
        
        return self.conn.execute(query, params or {})
```

**Environment Security**:
```python
# settings.py
import os
from pathlib import Path

# Security settings
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Secure headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

## 10. Deployment & Infrastructure

### Fly.io Configuration

**fly.toml**:
```toml
app = "hoopsarchive"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  DJANGO_SETTINGS_MODULE = "hoopsarchive.settings.production"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  path = "/health/"
  timeout = "5s"

[resources]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 1024

[[mounts]]
  source = "hoopsarchive_data"
  destination = "/app/data"
```

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "hoopsarchive.wsgi:application"]
```

### CI/CD Pipeline

**GitHub Actions**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to Fly.io

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          python manage.py test
          pytest tests/
      
      - name: Run linting
        run: |
          flake8 .
          black --check .
          mypy .
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - uses: superfly/flyctl-actions/setup-flyctl@master
      
      - name: Deploy to Fly.io
        run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### Monitoring & Observability

**Health Check Endpoint**:
```python
# views.py
from django.http import JsonResponse
from django.db import connection
import duckdb

def health_check(request):
    try:
        # Check Django database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check DuckDB
        duck_conn = duckdb.connect('data/hoarchive.duckdb')
        duck_conn.execute("SELECT COUNT(*) FROM players")
        duck_conn.close()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
```

**Application Logging**:
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'hoopsarchive': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## 11. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Backend Setup**:
- [ ] Complete Django project configuration
- [ ] Implement DuckDB repository pattern
- [ ] Create core data models (Player, Team, Game)
- [ ] Set up basic API endpoints
- [ ] Implement CSV validation framework

**Frontend Setup**:
- [ ] Initialize React project with TypeScript
- [ ] Set up routing and basic layout
- [ ] Implement API client with React Query
- [ ] Create basic component structure

**Infrastructure**:
- [ ] Configure Fly.io deployment
- [ ] Set up CI/CD pipeline
- [ ] Implement health checks

### Phase 2: Data Pipeline (Weeks 3-4)

**Data Ingestion**:
- [ ] Implement CSV processing pipeline
- [ ] Create data transformation logic
- [ ] Build batch loading system
- [ ] Add data validation and error handling
- [ ] Process all historical CSV files

**Database Optimization**:
- [ ] Create performance indexes
- [ ] Implement analytical views
- [ ] Optimize query patterns
- [ ] Add caching layer

### Phase 3: API Development (Weeks 5-6)

**Core Endpoints**:
- [ ] Player CRUD and search endpoints
- [ ] Team information and roster endpoints
- [ ] Game data and box score endpoints
- [ ] Analytics and statistics endpoints

**Performance Optimization**:
- [ ] Implement response caching
- [ ] Add pagination and filtering
- [ ] Optimize database queries
- [ ] Add rate limiting

### Phase 4: Frontend Implementation (Weeks 7-8)

**Core Pages**:
- [ ] Player listing and detail pages
- [ ] Team pages with rosters and stats
- [ ] Game schedules and box scores
- [ ] Analytics dashboard

**Visualizations**:
- [ ] Player statistics charts
- [ ] Team comparison tools
- [ ] Shot charts and heat maps
- [ ] Trend analysis graphs

### Phase 5: Testing & Polish (Weeks 9-10)

**Testing**:
- [ ] Comprehensive API testing
- [ ] Frontend component testing
- [ ] Integration testing
- [ ] Performance testing
- [ ] Load testing

**Security & Monitoring**:
- [ ] Security audit and hardening
- [ ] Monitoring and alerting setup
- [ ] Error tracking implementation
- [ ] Performance monitoring

**Documentation**:
- [ ] API documentation
- [ ] User guide
- [ ] Deployment documentation
- [ ] Maintenance procedures

## 12. Risk Assessment & Mitigation

### Technical Risks

**Risk**: DuckDB Performance with Large Datasets
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: 
  - Implement proper indexing strategy
  - Use DuckDB's columnar storage efficiently
  - Add query optimization monitoring
  - Plan migration path to ClickHouse if needed

**Risk**: API Response Time Requirements
- **Probability**: Medium
- **Impact**: High
- **Mitigation**:
  - Implement aggressive caching strategy
  - Optimize database queries early
  - Use database connection pooling
  - Add performance monitoring from day one

**Risk**: CSV Data Quality Issues
- **Probability**: High
- **Impact**: Medium
- **Mitigation**:
  - Implement comprehensive validation
  - Create data quality reports
  - Build manual override capabilities
  - Maintain data lineage tracking

### Operational Risks

**Risk**: Fly.io Resource Limitations
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**:
  - Monitor resource usage closely
  - Implement auto-scaling policies
  - Plan migration to dedicated infrastructure
  - Use efficient resource allocation

**Risk**: Data Loss During Migration
- **Probability**: Low
- **Impact**: High
- **Mitigation**:
  - Implement comprehensive backup strategy
  - Test restore procedures regularly
  - Use database transactions for critical operations
  - Maintain data versioning

### Business Risks

**Risk**: Scope Creep
- **Probability**: High
- **Impact**: Medium
- **Mitigation**:
  - Maintain strict MVP focus
  - Document all feature requests for future phases
  - Regular stakeholder communication
  - Time-boxed development cycles

## 13. Success Metrics

### Performance Metrics
- **API Response Time**: < 200ms for 95th percentile
- **Database Query Performance**: < 100ms for complex analytics queries
- **Frontend Load Time**: < 3 seconds for initial page load
- **Data Processing Speed**: Complete CSV ingestion in < 30 minutes

### Quality Metrics
- **Test Coverage**: > 90% for backend code
- **API Uptime**: > 99.9%
- **Data Accuracy**: 100% for core statistics
- **Error Rate**: < 0.1% for API requests

### User Experience Metrics
- **Page Load Speed**: < 2 seconds for subsequent navigation
- **Chart Rendering**: < 1 second for complex visualizations
- **Search Response**: < 500ms for player/team search
- **Mobile Responsiveness**: Full functionality on mobile devices

---

**Document Status**: Ready for Implementation  
**Next Steps**: Begin Phase 1 development with backend foundation setup  
**Review Date**: Weekly during implementation phases