from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.canonical_business_entity.health import CanonicalEntityHealthError
from app.canonical_business_entity.metrics import CanonicalEntityMetrics
from app.canonical_business_entity.repository import CanonicalBusinessEntityRepository
from app.canonical_business_entity.service import CanonicalBusinessEntityService
from app.models.canonical_business_entity import CanonicalBusinessEntity


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    CanonicalEntityMetrics.reset_for_tests()


def test_service_list_canonical_maps_aliases() -> None:
    canonical = CanonicalBusinessEntity(
        canonical_id=1,
        canonical_name="WALMART",
        normalized_name="WALMART",
        primary_rfc="NWM9709244",
        alias_count=1,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    repo = MagicMock(spec=CanonicalBusinessEntityRepository)
    repo.list_canonical.return_value = ([canonical], 1)
    repo.list_aliases_for_canonical.return_value = [
        {
            "entity_id": 10,
            "entity_code": "C0027",
            "entity_name": "NUEVA WAL MART DE MEXICO",
            "source_column": "cuenta_cliente",
            "resolution_rule": "singleton_bootstrap",
            "resolution_score": Decimal("1.0000"),
        }
    ]
    service = CanonicalBusinessEntityService(repo)
    response = service.list_canonical()
    assert response.total == 1
    assert response.items[0].aliases[0].entity_code == "C0027"


def test_service_get_statistics_unresolved_pct() -> None:
    repo = MagicMock(spec=CanonicalBusinessEntityRepository)
    repo.count_commercial_entities.return_value = 100
    repo.count_resolved_commercial.return_value = 90
    repo.count_canonical.return_value = 90
    repo.count_canonical_matches.return_value = 2
    repo.count_pending_suggestions.return_value = 5
    repo.count_automatic_suggestions.return_value = 12
    repo.get_unresolved_commercial_entity_ids.return_value = [1, 2]
    service = CanonicalBusinessEntityService(repo)
    stats = service.get_statistics()
    assert stats.unresolved_entities == 10
    assert stats.unresolved_pct == 10.0
    assert stats.pending_matches == 5


def test_service_list_suggestions_maps_entities() -> None:
    repo = MagicMock(spec=CanonicalBusinessEntityRepository)
    repo.list_suggestions.return_value = (
        [
            {
                "suggestion_id": 1,
                "rule_used": "brand_token_match",
                "score": Decimal("0.8800"),
                "status": "pending",
                "created_at": datetime(2026, 1, 1),
                "source_entity_id": 1,
                "source_entity_code": "C0027",
                "source_entity_name": "WALMART",
                "source_source_column": "cuenta_cliente",
                "candidate_entity_id": 2,
                "candidate_entity_code": "NWM9709244",
                "candidate_entity_name": "NUEVA WALMART",
                "candidate_source_column": "cuenta_proveedor",
            }
        ],
        1,
    )
    service = CanonicalBusinessEntityService(repo)
    response = service.list_suggestions()
    assert response.total == 1
    assert response.items[0].rule_used == "brand_token_match"


def test_service_validate_health_raises_on_orphans() -> None:
    repo = MagicMock(spec=CanonicalBusinessEntityRepository)
    repo.find_health_issues.return_value = {
        "orphan_entities": [{"entity_id": 1}],
        "duplicate_resolutions": [],
        "invalid_suggestion_scores": [],
        "invalid_resolution_scores": [],
    }
    service = CanonicalBusinessEntityService(repo)
    with pytest.raises(CanonicalEntityHealthError):
        service.validate_health()


def test_service_validate_health_ok() -> None:
    repo = MagicMock(spec=CanonicalBusinessEntityRepository)
    repo.find_health_issues.return_value = {
        "orphan_entities": [],
        "duplicate_resolutions": [],
        "invalid_suggestion_scores": [],
        "invalid_resolution_scores": [],
    }
    service = CanonicalBusinessEntityService(repo)
    assert service.validate_health()["status"] == "healthy"


def test_service_get_health_issues() -> None:
    repo = MagicMock(spec=CanonicalBusinessEntityRepository)
    repo.find_health_issues.return_value = {"orphan_entities": []}
    service = CanonicalBusinessEntityService(repo)
    assert service.get_health_issues() == {"orphan_entities": []}
