from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.enterprise_reasoning.metrics import EnterpriseReasoningMetrics
from app.enterprise_reasoning.repository import EnterpriseReasoningRepository
from app.enterprise_reasoning.schemas import EnterpriseReasoningObjectSchema, ReasoningConfidence
from app.enterprise_reasoning.service import EnterpriseReasoningService


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    EnterpriseReasoningMetrics.reset_for_tests()


def test_service_get_rules() -> None:
    service = EnterpriseReasoningService(MagicMock())
    rules = service.get_rules()
    assert rules.total_rules >= 10
    assert rules.enabled_rules >= 10


def test_service_list_entities() -> None:
    repo = MagicMock(spec=EnterpriseReasoningRepository)
    repo.list_objects.return_value = (
        [
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
        ],
        1,
    )
    service = EnterpriseReasoningService(repo)
    result = service.list_entities()
    assert result.total == 1


def test_service_get_entity() -> None:
    repo = MagicMock(spec=EnterpriseReasoningRepository)
    ero = EnterpriseReasoningObjectSchema(
        schema_version="1.0.0",
        canonical_id=1,
        confidence=ReasoningConfidence(
            average_confidence=Decimal("0.8"),
            conclusions_count=1,
            rules_executed=5,
        ),
    )
    obj = MagicMock()
    obj.reasoning_payload = ero.model_dump(mode="json")
    repo.get_object_by_canonical_id.return_value = obj
    service = EnterpriseReasoningService(repo)
    assert service.get_entity(1) is not None


def test_service_get_entity_not_found() -> None:
    repo = MagicMock(spec=EnterpriseReasoningRepository)
    repo.get_object_by_canonical_id.return_value = None
    service = EnterpriseReasoningService(repo)
    assert service.get_entity(999) is None


def test_service_get_statistics() -> None:
    repo = MagicMock(spec=EnterpriseReasoningRepository)
    repo.count_objects.return_value = 5
    repo.count_knowledge_objects.return_value = 10
    repo.average_confidence.return_value = 0.8
    repo.average_findings.return_value = 1.0
    repo.average_alerts.return_value = 0.5
    repo.average_recommendations.return_value = 0.7
    repo.get_last_refresh.return_value = datetime(2026, 6, 24)
    repo.count_incomplete.return_value = 1
    service = EnterpriseReasoningService(repo)
    stats = service.get_statistics()
    assert stats.reasoning_objects_total == 5


def test_service_validate_health() -> None:
    from app.enterprise_reasoning.health import validate_reasoning_health

    repo = MagicMock(spec=EnterpriseReasoningRepository)
    repo.find_health_issues.return_value = {
        "missing_evidence": [],
        "invalid_confidence": [],
        "incomplete_objects": [],
        "duplicate_findings": [],
        "contradictory_rules": [],
        "incompatible_recommendations": [],
    }
    service = EnterpriseReasoningService(repo)
    assert service.validate_health()["status"] == "healthy"
    assert service.get_health_issues() == repo.find_health_issues.return_value

    repo = MagicMock(spec=EnterpriseReasoningRepository)
    repo.count_objects.return_value = 2
    repo.average_confidence.return_value = 0.8
    repo.average_findings.return_value = 1.5
    repo.average_alerts.return_value = 0.5
    repo.average_recommendations.return_value = 1.0
    repo.get_last_refresh.return_value = datetime(2026, 6, 24)
    service = EnterpriseReasoningService(repo)
    service._engine.run_idempotent = MagicMock(
        return_value={
            "objects_upserted": 2,
            "objects_created": 1,
            "objects_updated": 1,
            "entities_processed": 2,
            "rules_executed": 30,
            "build_time_seconds": 1.2,
        }
    )
    result = service.run_build()
    assert result.rules_executed == 30
