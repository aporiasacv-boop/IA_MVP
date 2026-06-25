from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.enterprise_knowledge.repository import EnterpriseKnowledgeRepository


def _empty_mappings():
    mock = MagicMock()
    mock.all.return_value = []
    return mock


def test_count_objects() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = 10
    repo = EnterpriseKnowledgeRepository(session)
    assert repo.count_objects() == 10


def test_list_objects() -> None:
    session = MagicMock(spec=Session)
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = MagicMock()
    list_result.mappings.return_value.all.return_value = [
        {
            "knowledge_id": 1,
            "canonical_id": 10,
            "canonical_name": "WALMART",
            "completeness": Decimal("0.8"),
            "average_confidence": Decimal("0.75"),
            "built_at": datetime(2026, 6, 24),
        }
    ]
    session.execute.side_effect = [count_result, list_result]
    repo = EnterpriseKnowledgeRepository(session)
    rows, total = repo.list_objects()
    assert total == 1
    assert len(rows) == 1


def test_fetch_methods() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = []
    session.execute.return_value.mappings.return_value.first.return_value = None
    repo = EnterpriseKnowledgeRepository(session)
    repo.fetch_build_contexts()
    repo.fetch_aliases(10)
    repo.fetch_profile(10)
    repo.fetch_ontology_assignments(10)


def test_find_health_issues() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = []
    repo = EnterpriseKnowledgeRepository(session)
    issues = repo.find_health_issues()
    assert "incomplete_objects" in issues


def test_upsert_object_updates() -> None:
    session = MagicMock(spec=Session)
    existing = MagicMock()
    existing.canonical_id = 1
    session.scalar.return_value = existing
    repo = EnterpriseKnowledgeRepository(session)
    obj, is_new = repo.upsert_object(
        canonical_id=1,
        payload={"canonical_id": 1},
        completeness=Decimal("0.9"),
        average_confidence=Decimal("0.85"),
        built_at=datetime(2026, 6, 24),
    )
    assert is_new is False
    session.add.assert_not_called()
    assert obj is existing


def test_get_object_by_canonical_id() -> None:
    session = MagicMock(spec=Session)
    obj = MagicMock()
    session.scalar.return_value = obj
    repo = EnterpriseKnowledgeRepository(session)
    assert repo.get_object_by_canonical_id(5) is obj


def test_upsert_object_creates() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = None
    repo = EnterpriseKnowledgeRepository(session)
    obj, is_new = repo.upsert_object(
        canonical_id=1,
        payload={"canonical_id": 1},
        completeness=Decimal("0.8"),
        average_confidence=Decimal("0.75"),
        built_at=datetime(2026, 6, 24),
    )
    assert is_new is True
    session.add.assert_called_once()
    assert obj.canonical_id == 1


def test_aggregate_methods() -> None:
    session = MagicMock(spec=Session)
    count_result = MagicMock()
    count_result.scalar_one.return_value = 100
    session.execute.return_value = count_result
    session.scalar.side_effect = [2, 0.75, 0.8, datetime(2026, 6, 24)]
    repo = EnterpriseKnowledgeRepository(session)
    assert repo.count_canonical() == 100
    assert repo.count_incomplete() == 2
    assert repo.average_completeness() == 0.75
    assert repo.average_confidence() == 0.8
    assert repo.get_last_refresh() == datetime(2026, 6, 24)
