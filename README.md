# BBClone

[![CI](https://img.shields.io/badge/ci-pytest-blue.svg)](#) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

BBClone is a monorepo scaffold for a basketball data clone project. It ingests CSV datasets into DuckDB, exposes a Django + DRF API, and serves a React + Vite frontend. Development is driven by BDD specs, and the repository is currently in the scaffolding/Red phase: many components are intentionally stubbed and raise NotImplementedError while contracts and tests are defined. See the context summary for scope and stack details in [docs/context/CONTEXT_SUMMARY.md](docs/context/CONTEXT_SUMMARY.md:1-12).

Status: Red phase scaffolding. Known intentional stubs include:
- Players API and Game PBP API handlers raising NotImplementedError in [backend/players/views.py](backend/players/views.py:55-57) and [backend/players/views.py](backend/players/views.py:72-73)
- Ingest CLI subcommands (ingest|transform|validate) raising NotImplementedError in [ingest/cli.py](ingest/cli.py:20-36) and [ingest/cli.py](ingest/cli.py:58-77)
- DuckDB repository contract methods present but unimplemented in [backend/common/duckdb_repo.py](backend/common/duckdb_repo.py:18-54)
- Serializers present but unimplemented in [backend/players/serializers.py](backend/players/serializers.py:18-46)

## Monorepo layout

- backend/ — Django scaffolding, settings and URL routes:
  - Settings scaffold: [backend/hoopsarchive/settings.py](backend/hoopsarchive/settings.py:1-76)
  - URL routes: [backend/hoopsarchive/urls.py](backend/hoopsarchive/urls.py:1-22) mapping:
    - GET /players
    - GET /games/<int:game_id>/pbp
  - Views stubs: [backend/players/views.py](backend/players/views.py:42-73)
  - DuckDB repo contract: [backend/common/duckdb_repo.py](backend/common/duckdb_repo.py:18-54)
  - Serializers stubs: [backend/players/serializers.py](backend/players/serializers.py:18-46)
  - manage.py scaffold: [backend/manage.py](backend/manage.py:17-24)
- ingest/ — CLI, config, and ingest/transform/validate scaffolds:
  - CLI entry and subcommands: [ingest/cli.py](ingest/cli.py:38-77)
  - Config constants: [ingest/config.py](ingest/config.py:16-39)
  - Validators placeholder: [ingest/validators.py](ingest/validators.py:1)
- frontend/ — React + Vite + TypeScript scaffolding:
  - Vite config: [frontend/vite.config.ts](frontend/vite.config.ts:11-17)
  - Entry and routes: [frontend/src/main.tsx](frontend/src/main.tsx:8-30)
  - Players page stub: [frontend/src/routes/PlayersPage.tsx](frontend/src/routes/PlayersPage.tsx:17-63)
  - Game PBP page stub: [frontend/src/routes/GamePbpPage.tsx](frontend/src/routes/GamePbpPage.tsx:18-39)
  - Index HTML: [frontend/index.html](frontend/index.html:9-15)
  - tsconfig: [frontend/tsconfig.json](frontend/tsconfig.json:1-19)
- csv/ — CSV datasets inventory used by ingest ([docs/context/CONTEXT_SUMMARY.md](docs/context/CONTEXT_SUMMARY.md:32-279))
- docs/ — Context, ERD draft, staging mapping, and BDD specs:
  - Context summary: [docs/context/CONTEXT_SUMMARY.md](docs/context/CONTEXT_SUMMARY.md:1-12)
  - ERD placeholder v0.3: [docs/context/ERD_v0.3.md](docs/context/ERD_v0.3.md:1-33)
  - Staging mapping placeholder: [docs/context/STAGING_MAPPING.md](docs/context/STAGING_MAPPING.md:1-23)
  - Gherkin specs (ingest, transform, API, frontend, CI/CD): [docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md](docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md:1-262)
- tests/ — Pytest scaffolding for validations and API contracts:
  - API contracts placeholders: [tests/test_api_contracts.py](tests/test_api_contracts.py:12-21)
  - Ingest validations scaffolding: [tests/test_ingest_validations.py](tests/test_ingest_validations.py:1-133)
- ci/ — Pytest config: [ci/pytest.ini](ci/pytest.ini:1)

## Quickstart

This project targets Python 3.11+, Node.js (with npm/pnpm/yarn), and Windows PowerShell 7 workflows. The current phase is scaffolding, so most commands will surface NotImplementedError as contracts are finalized.

### Requirements

- Python 3.11 or newer
- Node.js 18+ and one of:
  - npm (preferred), pnpm, or Yarn Classic (v1.x)
- PowerShell 7 on Windows (commands below are pwsh-friendly)

### Setup

Python environment:
1. Create and activate a virtual environment:
   - pwsh:
     - python -m venv .venv
     - .\.venv\Scripts\Activate.ps1
2. Install backend dependencies:
   - Note: requirements files are not yet present; Django/DRF will be added during Green phase.
   - For future state, expect to run:
     - python -m pip install --upgrade pip
     - python -m pip install django djangorestframework

Node dependencies (frontend):
1. Change to frontend/ and install:
   - npm install
     - or pnpm install
     - or yarn
2. Start Vite dev server:
   - npm run dev
     - or pnpm run dev
     - or yarn dev

Data location:
- CSV datasets live under ./csv; config defaults point to this directory in [ingest/config.py](ingest/config.py:18-22).

### Ingest CLI

The ingest CLI is currently scaffolded and raises NotImplementedError while interfaces are defined by BDD specs.

- Entry point:
  - python -m ingest.cli --help
- Subcommands (all stubbed):
  - python -m ingest.cli ingest — see [ingest/cli.py](ingest/cli.py:20-36)
  - python -m ingest.cli transform — see [ingest/cli.py](ingest/cli.py:58-63)
  - python -m ingest.cli validate — see [ingest/cli.py](ingest/cli.py:64-77)

Config defaults:
- DB_PATH="data/hoarchive.duckdb", CSV_DIR="csv", NULLSTRINGS=["", "NA", "null"] as defined in [ingest/config.py](ingest/config.py:16-27).

Expected current behavior:
- Running any subcommand will raise NotImplementedError until implementations move to Green phase.

### Running the backend

Django project scaffold:
- Settings: [backend/hoopsarchive/settings.py](backend/hoopsarchive/settings.py:1-76)
- URLs: [backend/hoopsarchive/urls.py](backend/hoopsarchive/urls.py:1-22)

Note: Views and repository are stubs that raise NotImplementedError. Invoking manage.py will surface stub behavior depending on hit codepaths:
- manage.py scaffold: [backend/manage.py](backend/manage.py:17-24)

Typical Django commands (future state once deps are added):
- python backend/manage.py runserver
- python backend/manage.py migrate

### Running the frontend

From frontend/:
- npm run dev
  - or pnpm run dev
  - or yarn dev

Routes wired in [frontend/src/main.tsx](frontend/src/main.tsx:8-30):
- /players → PlayersPage ([frontend/src/routes/PlayersPage.tsx](frontend/src/routes/PlayersPage.tsx:17-63))
- /games/:gameId/pbp → GamePbpPage ([frontend/src/routes/GamePbpPage.tsx](frontend/src/routes/GamePbpPage.tsx:18-39))

Both page components are stubs; UI will render basic placeholders until APIs are implemented.

## Data sources

- CSV inventory is stored under ./csv and referenced in the context summary [docs/context/CONTEXT_SUMMARY.md](docs/context/CONTEXT_SUMMARY.md:32-279).
- Ingest configuration uses CSV_DIR="csv" as default in [ingest/config.py](ingest/config.py:18-22).

## API

Django URL routes:
- GET /players
- GET /games/<int:game_id>/pbp
Defined at [backend/hoopsarchive/urls.py](backend/hoopsarchive/urls.py:19-22).

Views are stubbed:
- PlayersView.get raises NotImplementedError: [backend/players/views.py](backend/players/views.py:55-57)
- GamePbpView.get raises NotImplementedError: [backend/players/views.py](backend/players/views.py:72-73)

Expected parameters and behavior (as per stubs/specs):
- GET /players
  - Query params: season, team suggested by stubs/specs; see [backend/players/views.py](backend/players/views.py:42-57) and BDD scenarios in [docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md](docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md:133-153)
  - Response: Will serialize curated player fields; exact schema pending ERD finalization ([docs/context/ERD_v0.3.md](docs/context/ERD_v0.3.md:10-33)) and serializers in [backend/players/serializers.py](backend/players/serializers.py:18-46).
- GET /games/<game_id>/pbp
  - Path param: game_id
  - Response: Play-by-play events per game; DuckDBRepo.get_game_pbp() contract at [backend/common/duckdb_repo.py](backend/common/duckdb_repo.py:41-54).

Repository contracts to support endpoints:
- DuckDBRepo.query_players() and DuckDBRepo.get_game_pbp() in [backend/common/duckdb_repo.py](backend/common/duckdb_repo.py:18-54)

Performance targets and pagination:
- REST_FRAMEWORK pagination defaults placeholder noted in settings for future tuning at [backend/hoopsarchive/settings.py](backend/hoopsarchive/settings.py:62-66).

## Configuration

Ingest configuration defaults:
- DB_PATH="data/hoarchive.duckdb"
- CSV_DIR="csv"
- NULLSTRINGS=["", "NA", "null"]
See [ingest/config.py](ingest/config.py:16-27). CsvLoadPlan type is also defined there ([ingest/config.py](ingest/config.py:28-39)).

Django REST framework (future placeholder):
- Pagination/REST settings section reserved in settings: [backend/hoopsarchive/settings.py](backend/hoopsarchive/settings.py:62-66).

## Usage examples

Current phase examples (showing expected stubs/NotImplementedError):

CLI:
- python -m ingest.cli ingest
- python -m ingest.cli transform
- python -m ingest.cli validate
Each subcommand currently raises NotImplementedError ([ingest/cli.py](ingest/cli.py:20-36), [ingest/cli.py](ingest/cli.py:58-77)).

API:
- GET /players — routes wired, view stubbed ([backend/hoopsarchive/urls.py](backend/hoopsarchive/urls.py:19-22), [backend/players/views.py](backend/players/views.py:55-57))
- GET /games/0022200001/pbp — routes wired, view stubbed ([backend/hoopsarchive/urls.py](backend/hoopsarchive/urls.py:21-22), [backend/players/views.py](backend/players/views.py:72-73))

Frontend:
- Navigate to /players or /games/0022200001/pbp to reach stub components ([frontend/src/main.tsx](frontend/src/main.tsx:8-30)).

For eventual behaviors and acceptance criteria, see the BDD Gherkin specs in [docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md](docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md:1-262).

## Architecture and ERD

- High-level scope and stack: [docs/context/CONTEXT_SUMMARY.md](docs/context/CONTEXT_SUMMARY.md:1-12)
- ERD draft v0.3 (pending finalization): [docs/context/ERD_v0.3.md](docs/context/ERD_v0.3.md:1-33)
- Staging mapping placeholder for ingest: [docs/context/STAGING_MAPPING.md](docs/context/STAGING_MAPPING.md:1-23)

## BDD / Acceptance Criteria

System behavior is defined via Gherkin specs covering ingestion, transform, API, frontend, and CI/CD. These specifications drive Red/Green development and test coverage. See [docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md](docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md:1-262). The players endpoint parameters and filtering scenarios are highlighted at [docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md](docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md:133-153).

## Testing

Pytest scaffolding is present:
- Ingest validations: [tests/test_ingest_validations.py](tests/test_ingest_validations.py:32-101) includes checks for FK orphans, dedup row_number, TOT constraint, and sampling reconciliation.
- API contracts placeholders: [tests/test_api_contracts.py](tests/test_api_contracts.py:12-21)

Run tests (once implementations are added and dependencies installed):
- python -m pytest

Note: In Red phase, several tests may intentionally fail until corresponding features are implemented.

## Contributing

Workflow (driven by BDD):
1. Open an issue describing the change and link to relevant Gherkin specs in [docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md](docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md:9-262).
2. Create a feature branch.
3. Add or update tests under tests/. Start from Red with failing tests to codify acceptance criteria.
4. Implement changes in ingest/ and backend/ (and frontend/ for UI routes), ensuring:
   - Ingest pipeline honors [ingest/config.py](ingest/config.py:16-27) defaults.
   - API endpoints adhere to routes in [backend/hoopsarchive/urls.py](backend/hoopsarchive/urls.py:19-22) and serializers in [backend/players/serializers.py](backend/players/serializers.py:18-46).
   - Frontend routes match deep links defined in [frontend/src/main.tsx](frontend/src/main.tsx:8-30).
5. Run pytest locally and ensure Green phase for touched specs.
6. Submit a PR referencing the issue and specs.

Coding notes:
- Keep repository contracts stable: [backend/common/duckdb_repo.py](backend/common/duckdb_repo.py:18-54).
- Align data shapes with evolving ERD: [docs/context/ERD_v0.3.md](docs/context/ERD_v0.3.md:10-33).

## License

BBClone — MIT License. If a LICENSE file is not present in the repository, contributors should add one in a follow-up change. Standard MIT terms apply.
