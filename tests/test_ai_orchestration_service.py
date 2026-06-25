from unittest.mock import MagicMock

import pytest

from app.ai_orchestration.metrics import LLMOrchestrationMetrics
from app.ai_orchestration.providers.mock_provider import MockProvider
from app.ai_orchestration.schemas import ExecutiveGenerateRequest
from app.ai_orchestration.service import AIOrchestrationService, is_executive_reasoning_candidate
from app.ai_orchestration.executive_response_engine import ExecutiveResponseEngine
from app.evidence_package.example_data import build_example_package


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    LLMOrchestrationMetrics.reset_for_tests()


def test_is_executive_candidate() -> None:
    assert is_executive_reasoning_candidate("Evaluar riesgos del cliente principal") is True
    assert is_executive_reasoning_candidate("Listar clientes") is False


def test_service_generate() -> None:
    evidence = MagicMock()
    package = build_example_package()
    evidence.build.return_value = package
    service = AIOrchestrationService(evidence, ExecutiveResponseEngine(MockProvider()))
    response = service.generate(ExecutiveGenerateRequest(question="Evaluar cliente"))
    assert response.executive_summary
    assert response.evidence_package_id == package.package_id


def test_service_schema() -> None:
    service = AIOrchestrationService(MagicMock(), ExecutiveResponseEngine(MockProvider()))
    schema = service.get_schema()
    assert schema.schema_id == "executive_response_v1"


def test_service_cost_summary() -> None:
    evidence = MagicMock()
    evidence.build.return_value = build_example_package()
    service = AIOrchestrationService(evidence, ExecutiveResponseEngine(MockProvider()))
    service.generate(ExecutiveGenerateRequest(question="Evaluar cliente"))
    summary = service.get_cost_summary()
    assert summary.llm_requests >= 1


def test_service_health() -> None:
    service = AIOrchestrationService(MagicMock(), ExecutiveResponseEngine(MockProvider()))
    health = service.validate_health()
    assert health.status in {"healthy", "unhealthy"}


def test_service_format_answer() -> None:
    from app.ai_orchestration.schemas import ExecutiveResponse
    from decimal import Decimal

    service = AIOrchestrationService(MagicMock(), ExecutiveResponseEngine(MockProvider()))
    answer = service.format_executive_answer(
        ExecutiveResponse(
            executive_summary="Resumen",
            detailed_analysis="Detalle",
            confidence=Decimal("0.8"),
            limitations=["Limite"],
            provider="mock",
            model="m",
            tokens_input=1,
            tokens_output=1,
            estimated_cost=0.0,
            response_time=0.1,
        )
    )
    assert "Resumen" in answer
    assert "Limite" in answer
