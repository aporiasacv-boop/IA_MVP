from unittest.mock import MagicMock

from app.capability_executor.executor import CapabilityExecutor
from app.capability_registry.constants import (
    BUSINESS_PIPELINE,
    CONVERSATIONAL_ENRICHMENT,
    INSTITUTIONAL_KNOWLEDGE,
)
from app.capability_registry.registry import CapabilityRegistry
from app.execution_plan.step import ExecutionStep
from app.schemas.hybrid_chat import HybridChatResult


def _registry(*, institutional=None, business_pipeline=None, conversational_enrichment=None) -> CapabilityRegistry:
    return CapabilityRegistry(
        institutional_knowledge=institutional,
        business_pipeline=business_pipeline or MagicMock(),
        conversational_enrichment=conversational_enrichment,
    )


def test_registry_lists_registered_steps_in_catalog():
    registry = _registry()

    assert INSTITUTIONAL_KNOWLEDGE in registry.registered_names()
    assert BUSINESS_PIPELINE in registry.registered_names()
    assert CONVERSATIONAL_ENRICHMENT in registry.registered_names()


def test_registry_exposes_institutional_knowledge_capability():
    capability = MagicMock()
    registry = _registry(institutional=capability)

    assert registry.institutional_knowledge() is capability


def test_registry_exposes_business_pipeline_capability():
    capability = MagicMock()
    registry = _registry(business_pipeline=capability)

    assert registry.business_pipeline() is capability


def test_registry_exposes_conversational_enrichment_capability():
    capability = MagicMock()
    registry = _registry(conversational_enrichment=capability)

    assert registry.conversational_enrichment() is capability


def test_registry_get_returns_registered_capability():
    institutional = MagicMock()
    business = MagicMock()
    registry = _registry(institutional=institutional, business_pipeline=business)

    assert registry.get(INSTITUTIONAL_KNOWLEDGE) is institutional
    assert registry.get(BUSINESS_PIPELINE) is business


def test_executor_delegates_institutional_step_to_capability():
    institutional = MagicMock()
    expected = HybridChatResult(
        handled_by="product_identity",
        success=True,
        answer="Soy Olnatura Intelligence.",
        metadata={},
    )
    institutional.execute.return_value = expected
    registry = _registry(institutional=institutional)
    executor = CapabilityExecutor(registry)

    result = executor.execute(
        ExecutionStep(step_id=INSTITUTIONAL_KNOWLEDGE),
        "como te llamas",
        session_id="sess-1",
    )

    institutional.execute.assert_called_once_with("como te llamas", session_id="sess-1")
    assert result is expected
