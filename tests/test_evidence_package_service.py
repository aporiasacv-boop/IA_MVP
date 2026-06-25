from unittest.mock import MagicMock

import pytest

from app.evidence_package.metrics import EvidencePackageMetrics
from app.evidence_package.repository import EvidencePackageRepository
from app.evidence_package.schemas import EvidenceBuildRequest
from app.evidence_package.service import EvidencePackageService


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    EvidencePackageMetrics.reset_for_tests()


def test_service_get_schema() -> None:
    service = EvidencePackageService(MagicMock())
    schema = service.get_schema()
    assert schema.schema_id == "enterprise_evidence_package_v1"


def test_service_get_example() -> None:
    repo = MagicMock(spec=EvidencePackageRepository)
    repo.fetch_first_available_entity.return_value = None
    service = EvidencePackageService(repo)
    pkg = service.get_example()
    assert pkg.question


def test_service_build_without_db() -> None:
    repo = MagicMock(spec=EvidencePackageRepository)
    repo.resolve_canonical_id.return_value = None
    repo.fetch_first_available_entity.return_value = None
    repo.fetch_eko.return_value = None
    repo.fetch_ero.return_value = None
    service = EvidencePackageService(repo)
    pkg = service.build(EvidenceBuildRequest(question="Listar clientes"))
    assert pkg.execution_plan.detected_verb == "listar"


def test_service_build_with_entity() -> None:
    from tests.test_evidence_package_builder import _minimal_eko

    repo = MagicMock(spec=EvidencePackageRepository)
    repo.resolve_canonical_id.return_value = 1
    repo.fetch_first_available_entity.return_value = 1
    repo.fetch_eko.return_value = _minimal_eko()
    repo.fetch_ero.return_value = None
    service = EvidencePackageService(repo)
    pkg = service.build(EvidenceBuildRequest(question="Evaluar cliente WALMART", canonical_id=1))
    assert pkg.metadata["canonical_id"] == 1


def test_service_get_example_with_db() -> None:
    from tests.test_evidence_package_builder import _minimal_eko

    repo = MagicMock(spec=EvidencePackageRepository)
    repo.fetch_first_available_entity.return_value = 1
    repo.fetch_eko.return_value = _minimal_eko()
    repo.fetch_ero.return_value = None
    service = EvidencePackageService(repo)
    pkg = service.get_example()
    assert pkg.metadata["canonical_id"] == 1

    service = EvidencePackageService(MagicMock())
    service.build(EvidenceBuildRequest(question="Listar clientes"))
    stats = service.get_statistics()
    assert stats.evidence_packages_total >= 1


def test_service_validate_health() -> None:
    service = EvidencePackageService(MagicMock())
    assert service.validate_health()["status"] == "healthy"
    assert service.get_health_issues() is not None
