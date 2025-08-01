# BBClone Implementation Guide

## Phase 1: Foundation Setup (Week 1)

### 1. Install Dependencies

**Backend:**
```bash
cd backend/
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend/
npm install
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Generate a proper SECRET_KEY for production
```

### 3. Database Setup

```bash
# Create data directory
mkdir -p data/

# Initialize DuckDB (will be created on first connection)
python -c "import duckdb; duckdb.connect('data/hoarchive.duckdb').close()"
```

### 4. Django Setup

```bash
cd backend/
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Development Servers

**Terminal 1 - Django Backend:**
```bash
cd backend/
python manage.py runserver
```

**Terminal 2 - Vite Frontend:**
```bash
cd frontend/
npm run dev
```

## Phase 2: Core Implementation (Weeks 2-4)

### Priority Order:

1. **DuckDB Connection & Basic Queries**
   - Implement `ingest/duckdb_client.py`
   - Create minimal curated tables
   - Test repository health check

2. **API Endpoints** 
   - Implement `PlayersView.get()` method
   - Add proper serializers
   - Test with pagination

3. **Frontend Integration**
   - Add API fetch logic
   - Implement deep-link routing (`/players/:season/:team`)
   - Add error handling

4. **Data Pipeline MVP**
   - Implement basic CSV loading
   - Create staging-to-curated transforms
   - Add validation functions

## Phase 3: Feature Completion (Weeks 5-8)

1. **Complete API Implementation**
   - Game PBP endpoint
   - CSV export functionality
   - Advanced filtering

2. **Frontend Polish**
   - Complete UI components
   - Add loading states
   - Implement CSV export

3. **Data Quality**
   - Complete validation suite
   - Add data quality monitoring
   - Implement error recovery

## Phase 4: Production Readiness (Weeks 9-12)

1. **Performance Optimization**
   - Add caching layer
   - Optimize queries
   - Load testing

2. **Security Hardening**
   - Production configuration
   - Security audit
   - Rate limiting

3. **CI/CD & Monitoring**
   - GitHub Actions
   - Health checks
   - Logging/monitoring

## Key Implementation Notes

### Database Schema Priority

Start with these core tables:
1. `curated_player` 
2. `curated_team`
3. `curated_player_season`
4. `curated_team_alias`
5. `curated_play_by_play`

### API Contract Adherence

Ensure all implementations match the BDD specifications:
- Response time p90 < 1s
- Proper pagination metadata
- Error handling with meaningful messages
- Consistent field naming

### Frontend-Backend Integration

Use the Vite proxy configuration for development:
- Frontend calls `/api/players` → proxied to `localhost:8000/players`
- No CORS issues during development
- Production deployment will need proper CORS configuration

## Testing Strategy

1. **Unit Tests**: Repository methods, data transformations
2. **Integration Tests**: API endpoints, data pipeline
3. **E2E Tests**: Critical user journeys
4. **Contract Tests**: API response schemas

Run tests frequently:
```bash
# Backend tests
cd backend/
pytest

# Frontend tests (after adding test dependencies)
cd frontend/
npm test
```

## Success Metrics

- [ ] All API endpoints return 200 responses
- [ ] Frontend displays player data correctly
- [ ] Performance targets met (p90 < 1s)
- [ ] Test coverage > 90%
- [ ] Data validation passes
- [ ] Security scan passes

## Common Pitfalls to Avoid

1. **Don't skip the dependency installations** - many errors stem from missing packages
2. **Environment variables are crucial** - improper configuration causes runtime errors
3. **Database schema must match repository queries** - alignment is critical
4. **CORS issues will block frontend development** - use proxy or enable CORS
5. **Test the data pipeline early** - CSV parsing can be tricky with real data

## Resources

- **Django REST Framework**: https://www.django-rest-framework.org/
- **DuckDB Python**: https://duckdb.org/docs/api/python/overview
- **React Router**: https://reactrouter.com/en/main
- **Vite Proxy**: https://vitejs.dev/config/server-options.html#server-proxy