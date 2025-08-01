"""
Serializer stubs for Players and Play-by-Play payloads.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Scenarios:
    * Players endpoint fields align with curated Player/PlayerSeason schema
    * Play-by-Play endpoint returns chronological events with required fields

Notes:
- No DRF dependency is required at scaffolding time. Types are placeholders.
- Red phase will replace these with actual DRF Serializers and field definitions.
"""

from typing import Any, Dict, List, Optional


class PlayerSerializerStub:
    """Placeholder serializer for player list items (structure only)."""

    def __init__(self, instance: Any, many: bool = False) -> None:
        self.instance = instance
        self.many = many

    @property
    def data(self) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Return placeholder serialized data.

        Red phase will implement actual schema and serialization rules.
        """
        # Intentionally non-functional
        raise NotImplementedError("PlayerSerializerStub.data not implemented (scaffold)")


class PlayByPlaySerializerStub:
    """Placeholder serializer for PBP events list."""

    def __init__(self, instance: Any, many: bool = False) -> None:
        self.instance = instance
        self.many = many

    @property
    def data(self) -> List[Dict[str, Any]] | Dict[str, Any]:
        """Return placeholder serialized data for PBP events."""
        # Intentionally non-functional
        raise NotImplementedError("PlayByPlaySerializerStub.data not implemented (scaffold)")