#!/usr/bin/env python
"""
Minimal Django manage.py placeholder.

Traceability:
- See docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Sections: 3) API Expectations (Players endpoint, Play-by-Play endpoint)

This is a scaffolding file to allow Red phase tests to import Django entrypoint.
No Django setup or execution logic beyond placeholders.
"""

import os
import sys


def main() -> None:
    """Stub manage entrypoint. Intentionally non-functional."""
    # In scaffolding we do not invoke Django. Tests should fail until implemented.
    raise NotImplementedError("Django manage.py not implemented in scaffolding phase")


if __name__ == "__main__":
    main()