from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.business_ontology.health import OntologyHealthError
from app.business_ontology.metrics import BusinessOntologyMetrics
from app.business_ontology.repository import BusinessOntologyRepository
from app.business_ontology.service import BusinessOntologyService


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    BusinessOntologyMetrics.reset_for_tests()


def test_service_list_ontology() -> None:
    repo = MagicMock(spec=BusinessOntologyRepository)
    repo.list_ontology_entities.return_value = ([1], 1)
    repo.get_canonical_identity.return_value = {
        "canonical_id": 1,
        "canonical_name": "WALMART",
        "primary_rfc": None,
        "normalized_name": "WALMART",
        "alias_count": 1,
    }
    repo.get_profile_summary.return_value = {
        "total_movements": 100,
        "total_amount": Decimal("1000"),
        "debit_credit_ratio": Decimal("1.5"),
        "dimensions_used": ["cuenta_cliente"],
        "profile_completeness": Decimal("0.8"),
    }
    repo.fetch_assignments_for_canonical.return_value = [
        {
            "assignment_id": 1,
            "canonical_id": 1,
            "concept_category": "role",
            "type_code": "CLIENTE",
            "type_label": "Cliente",
            "rule_code": "role_client_dimension",
            "evidence_json": {},
            "score": Decimal("0.92"),
            "confidence": Decimal("0.85"),
            "status": "pending",
            "created_at": datetime(2026, 6, 24),
        }
    ]
    service = BusinessOntologyService(repo)
    response = service.list_ontology()
    assert response.total == 1
    assert response.items[0].identity.canonical_name == "WALMART"


def test_service_get_statistics() -> None:
    repo = MagicMock(spec=BusinessOntologyRepository)
    repo.count_entities_with_assignments.return_value = 50
    repo.count_assignments.side_effect = lambda status=None: {"pending": 40, "approved": 5, "rejected": 2}.get(status, 0)
    repo.count_rules.return_value = 25
    repo.count_types.return_value = 35
    repo.average_confidence.return_value = 0.82
    repo.count_entities_without_suggestions.return_value = 10
    service = BusinessOntologyService(repo)
    stats = service.get_statistics()
    assert stats.ontology_entities == 50
    assert stats.ontology_pending == 40


def test_service_list_types() -> None:
    repo = MagicMock(spec=BusinessOntologyRepository)
    row = MagicMock()
    row.type_id = 1
    row.concept_category = "role"
    row.type_code = "CLIENTE"
    row.type_label = "Cliente"
    row.description = None
    row.is_active = True
    row.sort_order = 10
    repo.list_types.return_value = [row]
    service = BusinessOntologyService(repo)
    response = service.list_types()
    assert response.total == 1


def test_service_list_assignments() -> None:
    repo = MagicMock(spec=BusinessOntologyRepository)
    repo.list_assignments.return_value = (
        [{
            "assignment_id": 1,
            "canonical_id": 1,
            "concept_category": "role",
            "type_code": "CLIENTE",
            "type_label": "Cliente",
            "rule_code": "role_client_dimension",
            "evidence_json": {},
            "score": Decimal("0.92"),
            "confidence": Decimal("0.85"),
            "status": "pending",
            "created_at": datetime(2026, 6, 24),
        }],
        1,
    )
    service = BusinessOntologyService(repo)
    assert service.list_assignments().total == 1


def test_service_validate_health_ok() -> None:
    repo = MagicMock(spec=BusinessOntologyRepository)
    repo.find_health_issues.return_value = {
        "entities_without_suggestions": [],
        "contradictory_rules": [],
        "incompatible_natures": [],
        "invalid_scores": [],
        "incomplete_relations": [],
    }
    service = BusinessOntologyService(repo)
    assert service.validate_health()["status"] == "healthy"


def test_service_get_health_issues() -> None:
    repo = MagicMock(spec=BusinessOntologyRepository)
    repo.find_health_issues.return_value = {"contradictory_rules": []}
    service = BusinessOntologyService(repo)
    assert service.get_health_issues() == {"contradictory_rules": []}


def test_service_validate_health_raises() -> None:
    repo = MagicMock(spec=BusinessOntologyRepository)
    repo.find_health_issues.return_value = {
        "entities_without_suggestions": [],
        "contradictory_rules": [{"canonical_id": 1}],
        "incompatible_natures": [],
        "invalid_scores": [],
        "incomplete_relations": [],
    }
    service = BusinessOntologyService(repo)
    with pytest.raises(OntologyHealthError):
        service.validate_health()
