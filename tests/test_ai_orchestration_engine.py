from unittest.mock import MagicMock

import pytest

from app.ai_orchestration.executive_response_engine import ExecutiveResponseEngine, _parse_sections
from app.ai_orchestration.metrics import LLMOrchestrationMetrics
from app.ai_orchestration.providers.mock_provider import MockProvider
from app.ai_orchestration.schemas import LLMGenerateResult
from app.evidence_package.example_data import build_example_package
from app.evidence_package.schemas import EvidenceLimitation


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    LLMOrchestrationMetrics.reset_for_tests()


def test_executive_engine_generates_response() -> None:
    engine = ExecutiveResponseEngine(MockProvider())
    package = build_example_package()
    response = engine.generate(package)
    assert response.executive_summary
    assert response.provider == "mock"
    assert response.tokens_input > 0
    assert LLMOrchestrationMetrics.llm_requests == 1


def test_executive_engine_insufficient_evidence() -> None:
    engine = ExecutiveResponseEngine(MockProvider())
    package = build_example_package()
    package.evidence = []
    package.knowledge = []
    package.reasoning = []
    package.facts = []
    package.limitations = [
        EvidenceLimitation(
            code="missing_eko",
            description="Sin EKO",
            severity="critical",
            source="eko",
        )
    ]
    response = engine.generate(package)
    assert response.hallucination_guard_triggered is True
    assert "evidencia" in response.executive_summary.lower()
    assert response.tokens_input == 0


def test_engine_hallucination_post_guard() -> None:
    provider = MagicMock()
    provider.provider_name.return_value = "mock"
    provider.model_name = "m"
    provider.generate_response.return_value = LLMGenerateResult(
        text="Texto genérico sin claves",
        tokens_input=10,
        tokens_output=5,
        model="m",
        provider="mock",
    )
    provider.estimated_cost.return_value = 0.0
    engine = ExecutiveResponseEngine(provider)
    package = build_example_package()
    response = engine.generate(package)
    assert response.hallucination_guard_triggered is True


def test_parse_sections_single_paragraph() -> None:
    summary, analysis = _parse_sections("Un solo bloque de texto.")
    assert summary == analysis
