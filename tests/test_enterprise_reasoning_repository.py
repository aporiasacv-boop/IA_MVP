from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.enterprise_reasoning.repository import EnterpriseReasoningRepository


def test_count_objects() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = 5
    repo = EnterpriseReasoningRepository(session)
    assert repo.count_objects() == 5


def test_list_objects() -> None:
    session = MagicMock(spec=Session)
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = MagicMock()
    list_result.mappings.return_value.all.return_value = [
        {
            "reasoning_id": 1,
            "canonical_id": 10,
            "canonical_name": "WALMART",
            "average_confidence": Decimal("0.8"),
            "findings_count": 2,
            "alerts_count": 1,
            "recommendations_count": 1,
            "built_at": datetime(2026, 6, 24),
        }
    ]
    session.execute.side_effect = [count_result, list_result]
    repo = EnterpriseReasoningRepository(session)
    rows, total = repo.list_objects()
    assert total == 1
    assert len(rows) == 1


def test_repository_aggregates() -> None:
    session = MagicMock(spec=Session)
    count_result = MagicMock()
    count_result.scalar_one.return_value = 50
    session.execute.return_value = count_result
    repo = EnterpriseReasoningRepository(session)
    assert repo.count_knowledge_objects() == 50


def test_repository_averages() -> None:
    session = MagicMock(spec=Session)
    session.scalar.side_effect = [0.8, 1.5, datetime(2026, 6, 24)]
    repo = EnterpriseReasoningRepository(session)
    assert repo.average_confidence() == 0.8
    assert repo.average_findings() == 1.5
    assert repo.get_last_refresh() == datetime(2026, 6, 24)


def test_find_health_issues() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = []
    repo = EnterpriseReasoningRepository(session)
    issues = repo.find_health_issues()
    assert "missing_evidence" in issues


def test_get_object_by_canonical_id() -> None:
    session = MagicMock(spec=Session)
    obj = MagicMock()
    session.scalar.return_value = obj
    repo = EnterpriseReasoningRepository(session)
    assert repo.get_object_by_canonical_id(5) is obj

def test_upsert_creates() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = None
    repo = EnterpriseReasoningRepository(session)
    obj, is_new = repo.upsert_object(
        canonical_id=1,
        payload={"canonical_id": 1},
        average_confidence=Decimal("0.8"),
        findings_count=1,
        alerts_count=0,
        recommendations_count=0,
        built_at=datetime(2026, 6, 24),
    )
    assert is_new is True
    session.add.assert_called_once()
    assert obj.canonical_id == 1
