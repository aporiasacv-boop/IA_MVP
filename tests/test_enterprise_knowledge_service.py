from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from app.enterprise_knowledge.metrics import EnterpriseKnowledgeMetrics
from app.enterprise_knowledge.repository import EnterpriseKnowledgeRepository
from app.enterprise_knowledge.schemas import EnterpriseKnowledgeObjectSchema, KnowledgeIdentity, KnowledgeQuality
from app.enterprise_knowledge.service import EnterpriseKnowledgeService


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    EnterpriseKnowledgeMetrics.reset_for_tests()


def test_service_get_schema() -> None:
    service = EnterpriseKnowledgeService(MagicMock())
    schema = service.get_schema()
    assert schema.schema_id == "enterprise_knowledge_object_v1"
    assert "identity" in schema.required_sections


def test_service_get_entity() -> None:
    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    eko = EnterpriseKnowledgeObjectSchema(
        schema_version="1.0.0",
        canonical_id=1,
        identity=KnowledgeIdentity(
            canonical_id=1,
            canonical_name="X",
            normalized_name="X",
            alias_count=1,
        ),
        quality=KnowledgeQuality(
            completeness=Decimal("0.8"),
            average_confidence=Decimal("0.75"),
            has_profile=True,
            has_ontology=True,
            ontology_assignment_count=1,
        ),
    )
    obj = MagicMock()
    obj.knowledge_payload = eko.model_dump(mode="json")
    repo.get_object_by_canonical_id.return_value = obj
    service = EnterpriseKnowledgeService(repo)
    result = service.get_entity(1)
    assert result is not None
    assert result.canonical_id == 1


def test_service_list_entities() -> None:
    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    repo.list_objects.return_value = (
        [
            {
                "knowledge_id": 1,
                "canonical_id": 10,
                "canonical_name": "WALMART",
                "completeness": Decimal("0.8"),
                "average_confidence": Decimal("0.75"),
                "built_at": datetime(2026, 6, 24),
            }
        ],
        1,
    )
    service = EnterpriseKnowledgeService(repo)
    result = service.list_entities()
    assert result.total == 1
    assert result.items[0].canonical_name == "WALMART"


def test_service_get_statistics() -> None:
    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    repo.count_objects.return_value = 5
    repo.count_canonical.return_value = 10
    repo.average_completeness.return_value = 0.7
    repo.average_confidence.return_value = 0.8
    repo.get_last_refresh.return_value = datetime(2026, 6, 24)
    repo.count_incomplete.return_value = 1
    service = EnterpriseKnowledgeService(repo)
    stats = service.get_statistics()
    assert stats.knowledge_objects_total == 5


def test_service_get_entity_not_found() -> None:
    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    repo.get_object_by_canonical_id.return_value = None
    service = EnterpriseKnowledgeService(repo)
    assert service.get_entity(999) is None


def test_service_run_build() -> None:
    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    repo.count_objects.return_value = 3
    repo.average_completeness.return_value = 0.6
    repo.average_confidence.return_value = 0.7
    repo.get_last_refresh.return_value = datetime(2026, 6, 24)
    service = EnterpriseKnowledgeService(repo)
    service._engine.run_idempotent = MagicMock(
        return_value={
            "objects_upserted": 3,
            "objects_created": 1,
            "objects_updated": 2,
            "entities_processed": 3,
            "build_time_seconds": 1.5,
        }
    )
    result = service.run_build()
    assert result.entities_processed == 3


def test_service_get_health_issues() -> None:
    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    repo.find_health_issues.return_value = {"incomplete_objects": []}
    service = EnterpriseKnowledgeService(repo)
    assert service.get_health_issues() == {"incomplete_objects": []}


def test_service_validate_health_raises() -> None:
    from app.enterprise_knowledge.health import KnowledgeHealthError

    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    repo.find_health_issues.return_value = {
        "incomplete_objects": [],
        "invalid_confidence": [],
        "missing_evidence": [],
        "empty_sections": [],
        "broken_relationships": [],
        "contradictory_facts": [],
    }
    service = EnterpriseKnowledgeService(repo)
    assert service.validate_health()["status"] == "healthy"

    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    repo.find_health_issues.return_value = {
        "incomplete_objects": [],
        "invalid_confidence": [{"knowledge_id": 1}],
        "missing_evidence": [],
        "empty_sections": [],
        "broken_relationships": [],
        "contradictory_facts": [],
    }
    service = EnterpriseKnowledgeService(repo)
    with pytest.raises(KnowledgeHealthError):
        service.validate_health()
