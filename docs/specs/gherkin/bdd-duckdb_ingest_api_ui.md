# Feature: DuckDB ingestion, transformation, API, frontend, and CI/CD behavior

Background:
- Given curated CSV inputs exist in ./csv/*.csv
  And a DuckDB database file target at ./data/hoarchive.duckdb
  And Context Bank ERD v0.3 defines curated tables and grains
  And NULL strings are standardized as ['', 'NA', 'null']

## 1) Ingestion & Staging (DuckDB)

### Scenario: Ingest CSVs into staging with correct types and NULL handling
  Given the staging schema is empty in DuckDB
    And CSVs are available for players, teams, games, and box/pbp facts
  When ingestion runs to load via read_csv_auto or COPY from ./csv with NULLSTRINGS ['',', 'NA', 'null']
    And columns are cast per schema: IDs as BIGINT/HUGEINT, decimals as DECIMAL(9,3), dates as DATE, jersey as TEXT
  Then staging tables are populated for each source file
    And NULL-like tokens are stored as SQL NULL
    And jersey values keep leading zeros as TEXT
    And any float-like integers in ID columns are losslessly cast to integer keys

  ## Acceptance Criteria:
  * All staging tables exist and row counts > 0 for non-empty CSVs
  * Type assertions pass: ID columns are INTEGER-like, decimals are DECIMAL(9,3), dates parse as DATE
  * NULLSTRINGS are mapped to actual NULL
  * Jersey values with leading zeros remain preserved

  ## Edge Cases to Consider:
  * Empty CSVs result in empty staging tables without failure
  * Float-looking IDs like "123.0" cast to 123
  * Scientific notation in numeric fields rejected or coerced per schema
  * Extra columns in CSV ignored or mapped according to header

### Scenario: Deduplicate staging records using QUALIFY ROW_NUMBER
  Given duplicate candidate keys exist in a staging table
    And a business grain is defined per table (e.g., PlayerSeason by player_id, season)
  When a deduplication query runs using QUALIFY ROW_NUMBER() OVER (PARTITION BY grain ORDER BY source_priority, updated_at DESC)
  Then only one record per grain remains in the deduplicated staging view
    And a reproducible tie-breaker is applied to select the survivor

  ## Acceptance Criteria:
  * Row uniqueness is enforced at the deduped view per grain
  * RowNumber methodology is visible and testable in SQL
  * Deterministic ordering ensures stable survivors

  ## Edge Cases to Consider:
  * Perfect duplicates across all fields
  * Conflicting updates with identical timestamps
  * Multiple sources with priority ordering

### Scenario: Enforce “one TOT or many teams, but not both” per PlayerSeason
  Given PlayerSeason inputs include team-level splits and potential TOT rows for a player and season
  When validating team assignment for each (player_id, season)
  Then records must have either a single TOT row or one-or-more specific team rows, but not both
    And violations are flagged and excluded from promotion

  ## Acceptance Criteria:
  * Zero violations present after validation
  * A per-season per-player constraint check returns no rows

  ## Edge Cases to Consider:
  * Trades with multiple teams in one season
  * Missing team rows where TOT exists
  * Duplicate TOT rows for the same season and player

### Scenario: Referential integrity checks on staging for player_id, team_id, game_id
  Given staging facts reference players, teams, and games
  When integrity queries run to find FK orphans
  Then no orphan rows exist where child references a missing parent

  ## Acceptance Criteria:
  * Orphan check queries return zero rows for all relations
  * For known historical exceptions, explicit mappings or suppressions are documented

  ## Edge Cases to Consider:
  * Seasonal team alias mapping resolving renamed teams
  * Late-season team relocations with new abbreviations
  * Scrubbed or missing preseason/exhibition games

### Scenario: Sampling reconciliation with Basketball-Reference for PlayerSeason
  Given a random sample of 50 PlayerSeason rows selected from curated or deduped staging
  When the same rows are compared to Basketball-Reference calculated values
  Then each sampled metric matches within ±1 rounding unit for like-for-like stats

  ## Acceptance Criteria:
  * 50/50 rows meet the tolerance threshold
  * Any misses are logged with row identifiers and metric names

  ## Edge Cases to Consider:
  * Rounding differences due to rate denominators
  * Minutes rounding affecting per-36 or per-100 stats
  * Partial-season trades impacting totals vs rates

---

## 2) Transform & Promote (DuckDB)

### Scenario: Curated tables created to match ERD v0.3
  Given staging tables are ready and validated
    And ERD v0.3 defines curated tables: Player, Team, Game, Season, PlayerSeason, TeamSeason, GameBox, PlayByPlay, lookups
  When transformation SQL promotes cleaned data to curated tables
    And CHECK constraints are applied where applicable (e.g., 0 ≤ rate ≤ 1)
    And primary keys and unique constraints reflect curated grains
  Then all curated tables exist with expected columns, types, and constraints
    And team alias normalizations are applied consistently across seasons

  ## Acceptance Criteria:
  * Table existence and schema match ERD specification
  * CHECK constraints evaluate true for all rows
  * Unique constraints have no violations

  ## Edge Cases to Consider:
  * Jersey TEXT preserved through promotion
  * DECIMAL(9,3) maintained, no implicit float regressions
  * Historical team renames consistently normalized

### Scenario: League Averages stored and exposed via a union view
  Given season and league-average metrics are computed
  When League Averages are persisted in a dedicated curated table
    And a union view combines League Averages with team or player-level consumer views for simplicity
  Then clients can query a single view to access both entity and league rows

  ## Acceptance Criteria:
  * league_averages table exists with expected grain and types
  * union view returns league rows plus entity rows with disambiguating fields
  * Querying the view meets p90 < 1s on representative filters

  ## Edge Cases to Consider:
  * Missing league metrics for certain seasons default to NULL or are excluded
  * Versioning changes reflected via schema_version

---

## 3) API Expectations (Django + DRF via DuckDB repository)

### Scenario: Players endpoint filters by season and team with pagination
  Given the API endpoint GET /players?season=1996&team=BOS
    And DRF pagination is enabled with default page size
  When a client requests the endpoint
  Then the response status is 200 OK
    And results are filtered to players on BOS for the 1996 season
    And pagination metadata is included (count, next, previous)
    And fields align with curated Player/PlayerSeason schema

  ## Acceptance Criteria:
  * Filtering matches DuckDB query results exactly
  * Unknown filters produce empty result sets without error
  * Response time p90 < 1s on representative dataset

  ## Edge Cases to Consider:
  * Team alias mapping (historical variants) handled consistently
  * Case-insensitive filters
  * Missing season returns 400 with validation message

### Scenario: Play-by-Play endpoint returns PBP JSON for a game
  Given the API endpoint GET /games/<game_id>/pbp uses DuckDB PlayByPlay table
  When a client requests a valid game_id
  Then the response status is 200 OK
    And the response body contains chronological events with required fields
    And decimalized IDs in PBP are normalized to integer or canonical text keys

  ## Acceptance Criteria:
  * Event ordering strictly increasing by period and clock
  * No orphan player_id or team_id references
  * Response time p90 < 1s on representative PBP sizes

  ## Edge Cases to Consider:
  * Missing game_id returns 404
  * Mixed numeric formats for IDs in source mapped consistently
  * Large overtime games still return under performance target

### Scenario: Partial refresh rebuilds only impacted tables on CSV change
  Given metadata stores CSV mtime and/or content hash
  When a specific CSV’s mtime/hash changes
  Then only dependent staging and curated tables for that source are rebuilt or merged via MERGE
    And unaffected tables remain unchanged
    And metadata is updated to reflect the new hash and created_at

  ## Acceptance Criteria:
  * Dependency graph ensures minimal rebuild scope
  * MERGE-based upserts preserve surrogate keys and uniqueness
  * End-to-end refresh meets performance targets

  ## Edge Cases to Consider:
  * Multiple CSV changes cascade to correct dependents
  * Reverted CSV content (hash unchanged) triggers no rebuild
  * Interrupted refresh resumes idempotently

---

## 4) Frontend (React + Vite)

### Scenario: Deep links mirror Basketball-Reference and drive API queries
  Given a user navigates to a deep link pattern like /players/1996/BOS
  When the route loads
  Then the frontend issues API requests equivalent to /players?season=1996&team=BOS
    And the UI renders filtered player results with pagination controls
    And team alias mapping is reflected in displayed labels

  ## Acceptance Criteria:
  * URL changes update results without full reload
  * Back/forward navigation preserves filters and scroll position
  * 404 shown for invalid seasons or teams

  ## Edge Cases to Consider:
  * Bookmarked deep links after a deploy still function
  * Query param and path segment variants both supported

### Scenario: CSV export streams current table view with API field headers
  Given a results table is rendered from an API query
  When the user clicks “Export CSV”
  Then a streamed CSV download begins
    And the header row matches API field names and order
    And numeric formats match API outputs (DECIMAL(9,3), integers)

  ## Acceptance Criteria:
  * Export respects current filters and sorting
  * Large result sets stream without blocking UI
  * Leading zeros in jersey retained in CSV

  ## Edge Cases to Consider:
  * Empty result export yields a CSV with just headers
  * Network interruption resumes or shows a clear error toast
  * Locale does not alter decimal separators

---

## 5) CI/CD

### Scenario: Quality gates with pytest-cov and DuckDB smoke tests
  Given CI runs test suite with coverage
  When tests execute
  Then coverage is at least 90%
    And DuckDB smoke tests verify:
      | check                               |
      | no FK orphans                       |
      | no duplicate keys on curated grains |
      | TOT constraint enforcement          |

  ## Acceptance Criteria:
  * Failing any smoke test or coverage < 90% fails the build
  * Orphan and duplicate checks produce zero offending rows

  ## Edge Cases to Consider:
  * Flaky timing-dependent tests stabilized
  * Incremental schema changes adjust smoke queries correspondingly

### Scenario: Build artifact published with metadata and optional Parquet
  Given a successful CI build on main
  When the build completes
  Then hoarchive.duckdb is created at ./data/hoarchive.duckdb
    And a metadata table exists with schema_version, src_hash, created_at
    And optionally Parquet exports are produced for large immutable facts
    And Parquet row counts and samples match their DuckDB source tables

  ## Acceptance Criteria:
  * Artifact path and metadata rows verified in CI
  * Parquet schemas match DuckDB column types
  * Spot-sample equality checks pass within tolerance

  ## Edge Cases to Consider:
  * Missing Parquet optional step does not fail core build
  * Version bumps reflected in metadata and union views