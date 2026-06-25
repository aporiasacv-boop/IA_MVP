import pytest
from unittest.mock import MagicMock

from app.operational_audit.formulas import coverage_gap_score, coverage_score, pct
from app.operational_audit.health import OperationalAuditHealthError, validate_overview_health
from app.operational_audit.repository import OperationalAuditRepository
from app.operational_audit.schemas import AuditOverviewResponse
from app.operational_audit.service import OperationalAuditService


@pytest.fixture
def overview_counts() -> dict:
    return {
        "total_requests": 1000,
        "total_successes": 920,
        "total_failures": 80,
        "business_pipeline": 500,
        "conversation_memory": 80,
        "slot_clarification": 100,
        "capability_discovery": 70,
        "guided_fallback": 150,
        "legacy_chat": 100,
        "success_rate": 0.92,
    }


@pytest.fixture
def repository(overview_counts: dict) -> MagicMock:
    repo = MagicMock(spec=OperationalAuditRepository)
    repo.get_overview_counts.return_value = overview_counts
    repo.get_coverage_gaps.return_value = [
        {"question": "¿Qué es un proveedor?", "route": "legacy_chat", "count": 20},
        {"question": "¿Cómo va el negocio?", "route": "guided_fallback", "count": 15},
    ]
    repo.get_top_routes.return_value = [
        {"route": "business_pipeline", "count": 500},
        {"route": "guided_fallback", "count": 150},
    ]
    repo.get_top_failures.return_value = [
        {"question": "fallo", "route": "legacy_chat", "frequency": 5},
    ]
    repo.get_adoption_counts.return_value = {
        "suggested_questions_usage": 600,
        "conversation_memory_usage": 80,
        "slot_clarification_usage": 100,
        "capability_discovery_usage": 70,
    }
    return repo


@pytest.fixture
def service(repository: MagicMock) -> OperationalAuditService:
    return OperationalAuditService(repository)


def test_pct_helper() -> None:
    assert pct(25, 100) == 25.0
    assert pct(0, 0) == 0.0


def test_coverage_gap_score_formula() -> None:
    score = coverage_gap_score(legacy_count=100, fallback_count=150, total=1000)
    assert score == 25.0


def test_coverage_score_formula() -> None:
    score = coverage_score(deterministic_count=900, total=1000, success_rate=0.92)
    assert score == 82.8


def test_get_overview(service: OperationalAuditService) -> None:
    overview = service.get_overview()

    assert overview.total_requests == 1000
    assert overview.total_successes == 920
    assert overview.total_failures == 80
    assert overview.business_pipeline_pct == 50.0
    assert overview.fallback_pct == 15.0
    assert overview.legacy_pct == 10.0
    assert overview.coverage_gap_score == 25.0
    assert overview.coverage_score == 82.8


def test_get_coverage_gaps(service: OperationalAuditService) -> None:
    gaps = service.get_coverage_gaps()
    assert len(gaps) == 2
    assert gaps[0].route in {"legacy_chat", "guided_fallback"}


def test_get_top_routes(service: OperationalAuditService) -> None:
    routes = service.get_top_routes()
    assert routes[0].route == "business_pipeline"
    assert routes[0].percentage == 50.0


def test_get_top_failures(service: OperationalAuditService) -> None:
    failures = service.get_top_failures()
    assert failures[0].frequency == 5


def test_get_adoption(service: OperationalAuditService) -> None:
    adoption = service.get_adoption()
    assert adoption.suggested_questions_usage == 600
    assert adoption.conversation_memory_usage == 80


def test_export_coverage_gaps_json(service: OperationalAuditService) -> None:
    exported = service.export_coverage_gaps_json()
    assert len(exported.items) == 2
    assert exported.coverage_gap_score == 25.0


def test_export_coverage_gaps_csv(service: OperationalAuditService) -> None:
    csv_text = service.export_coverage_gaps_csv()
    assert "question,count,route" in csv_text.replace(" ", "")
    assert "legacy_chat" in csv_text


def test_validate_health_passes(service: OperationalAuditService) -> None:
    result = service.validate_health()
    assert result["coverage_gap_score"] == 25.0


def test_validate_health_rejects_bad_coverage_score() -> None:
    overview = AuditOverviewResponse(
        total_requests=10,
        total_successes=10,
        total_failures=0,
        business_pipeline_pct=100.0,
        memory_pct=0.0,
        clarification_pct=0.0,
        capability_pct=0.0,
        fallback_pct=0.0,
        legacy_pct=0.0,
        coverage_score=150.0,
        coverage_gap_score=0.0,
    )
    with pytest.raises(OperationalAuditHealthError, match="coverage_score"):
        validate_overview_health(overview)


def test_coverage_score_clamped() -> None:
    score = coverage_score(deterministic_count=2000, total=1000, success_rate=1.0)
    assert score == 100.0


def test_export_coverage_gaps_json_text(service: OperationalAuditService) -> None:
    text = service.export_coverage_gaps_json_text()
    assert '"coverage_gap_score"' in text
    assert 'legacy_chat' in text


def test_overview_zero_requests(repository: MagicMock) -> None:
    repository.get_overview_counts.return_value = {
        "total_requests": 0,
        "total_successes": 0,
        "total_failures": 0,
        "business_pipeline": 0,
        "conversation_memory": 0,
        "slot_clarification": 0,
        "capability_discovery": 0,
        "guided_fallback": 0,
        "legacy_chat": 0,
        "success_rate": 0.0,
    }
    service = OperationalAuditService(repository)
    overview = service.get_overview()
    assert overview.coverage_gap_score == 0.0
    assert overview.coverage_score == 0.0

