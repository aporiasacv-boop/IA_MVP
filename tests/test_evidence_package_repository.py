from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.evidence_package.repository import EvidencePackageRepository


def test_resolve_canonical_exact() -> None:
    session = MagicMock(spec=Session)
    result = MagicMock()
    result.mappings.return_value.first.return_value = {"canonical_id": 42}
    session.execute.return_value = result
    repo = EvidencePackageRepository(session)
    assert repo.resolve_canonical_id(["WALMART"]) == 42


def test_resolve_canonical_ilike() -> None:
    session = MagicMock(spec=Session)
    miss = MagicMock()
    miss.mappings.return_value.first.return_value = None
    hit = MagicMock()
    hit.mappings.return_value.first.return_value = {"canonical_id": 7}
    session.execute.side_effect = [miss, hit]
    repo = EvidencePackageRepository(session)
    assert repo.resolve_canonical_id(["WALMART"]) == 7


def test_resolve_skips_short_hints() -> None:
    session = MagicMock(spec=Session)
    repo = EvidencePackageRepository(session)
    assert repo.resolve_canonical_id(["ab", ""]) is None
    session.execute.assert_not_called()


def test_fetch_eko_and_ero() -> None:
    session = MagicMock(spec=Session)
    now = datetime(2026, 6, 24)
    eko_row = MagicMock()
    eko_row.mappings.return_value.first.return_value = {
        "knowledge_payload": {
            "schema_version": "1.0.0",
            "canonical_id": 1,
            "identity": {
                "canonical_id": 1,
                "canonical_name": "X",
                "normalized_name": "X",
                "alias_count": 1,
                "items": [
                    {
                        "key": "canonical_name",
                        "value": "X",
                        "source": "canonical_business_entity",
                        "evidence": {},
                        "confidence": "1.0",
                        "computed_at": now.isoformat(),
                    }
                ],
            },
            "quality": {
                "completeness": "0.8",
                "average_confidence": "0.8",
                "has_profile": True,
                "has_ontology": True,
                "ontology_assignment_count": 1,
            },
            "evidence": [{"rule_code": "test"}],
        }
    }
    session.execute.return_value = eko_row
    repo = EvidencePackageRepository(session)
    eko = repo.fetch_eko(1)
    assert eko is not None
    assert eko.canonical_id == 1


def test_fetch_ero() -> None:
    session = MagicMock(spec=Session)
    now = datetime(2026, 6, 24)
    ero_row = MagicMock()
    ero_row.mappings.return_value.first.return_value = {
        "reasoning_payload": {
            "schema_version": "1.0.0",
            "canonical_id": 1,
            "confidence": {
                "average_confidence": "0.8",
                "conclusions_count": 0,
                "rules_executed": 1,
            },
            "evidence": [],
        }
    }
    session.execute.return_value = ero_row
    repo = EvidencePackageRepository(session)
    ero = repo.fetch_ero(1)
    assert ero is not None
    assert ero.canonical_id == 1


def test_fetch_missing_returns_none() -> None:
    session = MagicMock(spec=Session)
    result = MagicMock()
    result.mappings.return_value.first.return_value = None
    session.execute.return_value = result
    repo = EvidencePackageRepository(session)
    assert repo.fetch_eko(99) is None
    assert repo.fetch_ero(99) is None


def test_fetch_first_available() -> None:
    session = MagicMock(spec=Session)
    result = MagicMock()
    result.mappings.return_value.first.return_value = {"canonical_id": 5}
    session.execute.return_value = result
    repo = EvidencePackageRepository(session)
    assert repo.fetch_first_available_entity() == 5


def test_fetch_first_available_none() -> None:
    session = MagicMock(spec=Session)
    result = MagicMock()
    result.mappings.return_value.first.return_value = None
    session.execute.return_value = result
    repo = EvidencePackageRepository(session)
    assert repo.fetch_first_available_entity() is None
