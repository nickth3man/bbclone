"""
Argparse CLI skeleton for ingestion workflow.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Sections:
    - 1) Ingestion & Staging (ingest command)
    - 2) Transform & Promote (transform command)
    - 1/2) Validation checks (validate command)
    - 5) CI/CD (to be used by pipelines)

This module wires command names to placeholder functions only.
No business logic is implemented; handlers are stubs.
"""

import argparse
from typing import List


def _cmd_ingest(args: argparse.Namespace) -> None:
    """Placeholder for ingestion step: load CSVs to staging."""
    # Intentionally not implemented
    raise NotImplementedError("ingest command not implemented in scaffolding phase")


def _cmd_transform(args: argparse.Namespace) -> None:
    """Placeholder for transform step: promote staging to curated."""
    # Intentionally not implemented
    raise NotImplementedError("transform command not implemented in scaffolding phase")


def _cmd_validate(args: argparse.Namespace) -> None:
    """Placeholder for validation suite across staging/curated."""
    # Intentionally not implemented
    raise NotImplementedError("validate command not implemented in scaffolding phase")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="hoops-ingest",
        description="DuckDB ingestion/transform/validate CLI (scaffold).",
    )
    subparsers = parser.add_subparsers(dest="command")

    p_ingest = subparsers.add_parser("ingest", help="Load CSVs into staging (stub)")
    p_ingest.set_defaults(func=_cmd_ingest)

    p_transform = subparsers.add_parser("transform", help="Promote staging to curated (stub)")
    p_transform.set_defaults(func=_cmd_transform)

    p_validate = subparsers.add_parser("validate", help="Run validation checks (stub)")
    p_validate.set_defaults(func=_cmd_validate)

    return parser


def main(argv: List[str] | None = None) -> int:
    """Entry point for command-line execution.

    Returns
    -------
    int
        Zero on success. In scaffolding this will raise NotImplementedError.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    # All handlers are stubs raising NotImplementedError
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())