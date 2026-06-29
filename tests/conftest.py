import pytest

from unittest.mock import MagicMock

from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.business_resolution_capability import BusinessResolutionCapability
from app.capabilities.business_understanding_capability import BusinessUnderstandingCapability
from app.capabilities.conversation_context_capability import ConversationContextCapability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.operational_metrics.metrics import reset_operational_finops_metrics
from app.operational_metrics.repository import reset_operational_memory_store
from app.operational_metrics.service import reset_operational_metrics_service
from app.simulation_engine.metrics import reset_simulation_engine_metrics
from app.simulation_engine.service import reset_simulation_engine_service
from app.enterprise_decision.metrics import reset_enterprise_decision_metrics
from app.enterprise_decision.service import reset_enterprise_decision_service


@pytest.fixture(autouse=True)
def reset_operational_metrics_state() -> None:
    reset_operational_memory_store()
    reset_operational_finops_metrics()
    reset_operational_metrics_service()
    reset_simulation_engine_metrics()
    reset_simulation_engine_service()
    reset_enterprise_decision_metrics()
    reset_enterprise_decision_service()


@pytest.fixture
def conversation_context() -> ConversationContextCapability:
    return ConversationContextCapability()


@pytest.fixture
def business_understanding() -> BusinessUnderstandingCapability:
    return BusinessUnderstandingCapability()


@pytest.fixture
def business_resolution() -> BusinessResolutionCapability:
    return BusinessResolutionCapability(MagicMock(), MagicMock())


@pytest.fixture
def institutional_knowledge() -> InstitutionalKnowledgeCapability:
    return InstitutionalKnowledgeCapability()


@pytest.fixture
def executive_reasoning() -> MagicMock:
    return MagicMock()


@pytest.fixture
def guided_fallback() -> MagicMock:
    return MagicMock()


@pytest.fixture
def pipeline_preparer(
    conversation_context: ConversationContextCapability,
    business_understanding: BusinessUnderstandingCapability,
    business_resolution: BusinessResolutionCapability,
    institutional_knowledge: InstitutionalKnowledgeCapability,
    executive_reasoning: MagicMock,
    guided_fallback: MagicMock,
) -> BusinessPipelineCapability:
    return BusinessPipelineCapability(
        MagicMock(),
        MagicMock(),
        conversation_context,
        business_understanding,
        business_resolution,
        institutional_knowledge,
        executive_reasoning,
        guided_fallback,
    )
