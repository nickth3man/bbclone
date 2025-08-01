# AGENTS Guidelines (Project-Specific + Reusable Patterns)

This file codifies high-level, reusable guidance derived from the BBClone analysis conversation. It complements existing rules under [.roo/rules/00-core-prompt.md](.roo/rules/00-core-prompt.md) and focuses on actionable, non-redundant practices.

## 1) Tooling Discipline and Sequencing

- New exploration protocol:
  - Always begin any new code area with [codebase_search.query()](.): use semantic search before using other file tools.
  - Use one tool per message. After each tool, wait for explicit confirmation of success before proceeding.
  - Use [read_file.path()](.) efficiently: max 4 files per call, minimal line ranges with enough context. Combine adjacent ranges (<=10 lines apart).

- Evidence-first communication:
  - Cite evidence with clickable references:
    - Files: [relative/path.ext](relative/path.ext)
    - Syntax/constructs: [function_name()](relative/path.ext:line), [ClassName.method()](relative/path.ext:line)
  - Summaries must map back to code references; avoid claims without links.

- Attempt completion protocol:
  - Use [attempt_completion.result()](.) only after the user confirms prior tool outcomes succeeded.
  - The result must be final (no trailing questions).

## 2) Orchestration Patterns

- Delegation:
  - Use [new_task.mode()](.) to delegate focused work to specialized modes with:
    - Clear scope and acceptance criteria
    - Explicit “only do this” constraint
    - Completion signal using attempt_completion
  - Use [switch_mode.mode_slug()](.) when a different mode is required, with a concise reason.

- Progress tracking:
  - For multi-step work, maintain a checklist with [update_todo_list.todos()](.) using:
    - [ ] pending
    - [-] in progress
    - [x] completed

## 3) Security and Configuration Defaults

- Never place secrets in code or chat; use environment variables.
- Treat CORS as environment policy:
  - Prefer same-origin or local dev proxy.
  - If enabling CORS, scope to explicit dev origins and avoid broad wildcards in production.
- Validate and sanitize all user inputs; never trust external input.

## 4) Performance and Testing Posture

- Treat pagination, sorting, and filtering defaults as API contracts; document and test them.
- Define latency targets (e.g., p90) per endpoint and treat them as acceptance criteria where feasible.
- Red → Green development:
  - Assert behavior (schemas, shapes, ordering) first.
  - Implement to satisfy those assertions.
  - Favor behavior tests over implementation details.

## 5) Workspace Hygiene

- Do not create files unless explicitly required; prefer editing existing files.
- Avoid helper scripts for simple steps; provide direct commands/instructions in chat.
- Keep the repository clean of temporary or analysis artifacts.

---

# Project-Specific Guidance (BBClone)

High-level structure and roles:
- Backend (Django/DRF scaffolding):
  - URLs in [backend/hoopsarchive/urls.py](backend/hoopsarchive/urls.py)
  - Views and serializers in [backend/players/](backend/players/)
  - Settings in [backend/hoopsarchive/settings.py](backend/hoopsarchive/settings.py)
- Ingest (DuckDB pipeline):
  - Config and types in [ingest/config.py](ingest/config.py)
  - Connection in [ingest/duckdb_client.py](ingest/duckdb_client.py)
  - CSV loading in [ingest/staging_loader.py](ingest/staging_loader.py)
  - Transforms in [ingest/transformer.py](ingest/transformer.py)
  - Validators in [ingest/validators.py](ingest/validators.py)
  - CSV sources under [csv/](csv/)
- Frontend (Vite + React + TS):
  - App bootstrap in [frontend/src/main.tsx](frontend/src/main.tsx), [frontend/src/App.tsx](frontend/src/App.tsx)
  - Routes in [frontend/src/routes/](frontend/src/routes/)
  - Vite config in [frontend/vite.config.ts](frontend/vite.config.ts)
- Documentation:
  - Context/ERD/staging in [docs/context/](docs/context/)
  - BDD specs in [docs/specs/gherkin/](docs/specs/gherkin/)
- Tests:
  - API and ingest validations in [tests/](tests/)

Development workflow patterns:
- Backend enablement (scaffold → functional baseline):
  - Ensure DRF is enabled in settings and essential middleware is configured in [backend/hoopsarchive/settings.py](backend/hoopsarchive/settings.py)
  - Implement repository access in [backend/common/duckdb_repo.py](backend/common/duckdb_repo.py) and inject into views in [backend/players/views.py](backend/players/views.py)
  - Implement serializers in [backend/players/serializers.py](backend/players/serializers.py) to match API contract shapes

- Ingest pipeline MVP:
  - Implement connect() in [ingest/duckdb_client.py](ingest/duckdb_client.py)
  - Define minimal CSV load plans and stage using [ingest/staging_loader.py](ingest/staging_loader.py)
  - Promote curated tables via [ingest/transformer.py](ingest/transformer.py)
  - Implement validators in [ingest/validators.py](ingest/validators.py) returning structured issues as asserted by tests

- Frontend integration:
  - Prefer Vite dev proxy configured in [frontend/vite.config.ts](frontend/vite.config.ts) for backend API paths during local development
  - If not proxying, configure minimal CORS on the backend for dev origins

Testing posture:
- Red-phase validators in [tests/test_ingest_validations.py](tests/test_ingest_validations.py) assert shapes and expect initial issues; move to Green by implementing loader/transform/validators
- API contract tests in [tests/test_api_contracts.py](tests/test_api_contracts.py) should cover status, pagination metadata, filtering, and response fields

Efficiency shortcuts (non-binding patterns):
- Frequent touchpoints:
  - URLs and views: [backend/hoopsarchive/urls.py](backend/hoopsarchive/urls.py), [backend/players/views.py](backend/players/views.py)
  - Ingest connection and checks: [ingest/duckdb_client.py](ingest/duckdb_client.py), [ingest/validators.py](ingest/validators.py)
  - Frontend routes: [frontend/src/routes/](frontend/src/routes/), [frontend/src/App.tsx](frontend/src/App.tsx)

Debugging heuristics:
- Backend routing failures: verify patterns in [backend/hoopsarchive/urls.py](backend/hoopsarchive/urls.py) and method implementations in [backend/players/views.py](backend/players/views.py); ensure serializer fields in [backend/players/serializers.py](backend/players/serializers.py) match the contract
- Frontend deep links vs query params: ensure routes in [frontend/src/main.tsx](frontend/src/main.tsx) align with the desired URL shape and fetch logic
- Ingest deduplication: use DuckDB window functions with deterministic ordering in [ingest/transformer.py](ingest/transformer.py) to qualify a single winning row per business key

---

## Change Control

- Keep this file high-level and reusable. Do not add secrets, environment values, or implementation specifics.
- When adding guidance:
  - Ensure it applies broadly and does not duplicate existing [.roo/rules/00-core-prompt.md](.roo/rules/00-core-prompt.md)
  - Provide examples only when they are reusable patterns.