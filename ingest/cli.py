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
import logging
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def _cmd_ingest(args: argparse.Namespace) -> None:
    """Load CSVs into staging tables."""
    from .staging_loader import load_all_staging_tables
    from .duckdb_client import health_check
    
    print("🔄 Starting CSV ingestion...")
    
    if not health_check():
        print("❌ Database health check failed")
        return
    
    try:
        load_all_staging_tables()
        print("✅ CSV ingestion completed successfully")
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        raise


def _cmd_transform(args: argparse.Namespace) -> None:
    """Promote staging data to curated tables."""
    from .transformer import promote_staging_to_curated
    from .duckdb_client import health_check
    
    print("🔄 Starting data transformation...")
    
    if not health_check():
        print("❌ Database health check failed")
        return
    
    try:
        promote_staging_to_curated()
        print("✅ Data transformation completed successfully")
    except Exception as e:
        print(f"❌ Transformation failed: {e}")
        raise


def _cmd_validate(args: argparse.Namespace) -> None:
    """Run validation checks across staging and curated data."""
    from .validators import (
        table_existence_check,
        fk_orphans_check, 
        uniq_check,
        tot_consistency_check,
        sample_reconciliation_check
    )
    
    print("🔄 Running validation checks...")
    
    # Table existence check
    print("\n📋 Checking table existence...")
    table_issues = table_existence_check()
    if table_issues:
        print(f"⚠️  Found {len(table_issues)} table issues:")
        for issue in table_issues[:5]:  # Show first 5
            print(f"   - {issue['table']}: {issue['issue']}")
    else:
        print("✅ All required tables exist")
    
    # FK orphans check
    print("\n🔗 Checking foreign key integrity...")
    fk_issues = fk_orphans_check()
    if fk_issues:
        print(f"⚠️  Found {len(fk_issues)} FK orphan issues:")
        for issue in fk_issues[:5]:  # Show first 5
            print(f"   - {issue['child_table']}.{issue['child_fk']} -> {issue['parent_table']}: {issue['missing_key']}")
    else:
        print("✅ No foreign key violations found")
    
    # Uniqueness check
    print("\n🔑 Checking uniqueness constraints...")
    uniq_issues = uniq_check()
    if uniq_issues:
        print(f"⚠️  Found {len(uniq_issues)} uniqueness violations:")
        for issue in uniq_issues[:5]:  # Show first 5
            print(f"   - {issue['entity']}.{issue['grain']}: {issue['count']} duplicates")
    else:
        print("✅ No uniqueness violations found")
    
    # TOT consistency check  
    print("\n📊 Checking TOT consistency...")
    tot_issues = tot_consistency_check()
    if tot_issues:
        print(f"⚠️  Found {len(tot_issues)} TOT consistency issues:")
        for issue in tot_issues[:5]:  # Show first 5
            print(f"   - Player {issue['player_id']} Season {issue['season']}: {issue['violation']}")
    else:
        print("✅ No TOT consistency issues found")
    
    # Sample reconciliation (limited for MVP)
    print("\n🎯 Running sample reconciliation...")
    recon_issues = sample_reconciliation_check(sample_size=10)  # Small sample for MVP
    if recon_issues:
        print(f"⚠️  Found {len(recon_issues)} reconciliation mismatches:")
        for issue in recon_issues[:3]:  # Show first 3
            print(f"   - {issue['entity']} {issue['row_key']}: {issue['metric']} delta={issue['delta']}")
    else:
        print("✅ All sampled data reconciled successfully")
    
    # Summary
    total_issues = len(table_issues) + len(fk_issues) + len(uniq_issues) + len(tot_issues) + len(recon_issues)
    print(f"\n📈 Validation Summary: {total_issues} total issues found")
    
    if total_issues == 0:
        print("🎉 All validation checks passed!")
    else:
        print("⚠️  Some validation issues found - review above for details")


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