from unittest.mock import MagicMock

import pytest

from app.conversation_ux.constants import (
    GATEWAY_DECISION_BUSINESS,
    GATEWAY_DECISION_CONVERSATION,
    HANDLED_BY_CONVERSATION_GATEWAY,
)
from app.conversation_ux.gateway import ConversationIntelligenceGateway
from app.conversation_ux.presenter import ConversationPresenter
from app.enterprise_knowledge_service.schemas import CapabilitiesPayload


@pytest.fixture
def gateway() -> ConversationIntelligenceGateway:
    presenter = ConversationPresenter(
        knowledge_service=MagicMock(
            get_capabilities=MagicMock(
                return_value=CapabilitiesPayload(
                    answer="",
                    capabilities=["Clientes", "Proveedores"],
                    examples=["¿Cuántos clientes existen?"],
                )
            ),
            get_faq=MagicMock(return_value=None),
        ),
        dataset_summary_provider=lambda: {
            "registros": 1000,
            "clientes": 10,
            "proveedores": 5,
        },
    )
    return ConversationIntelligenceGateway(presenter)


@pytest.mark.parametrize(
    "message",
    [
        "Hola",
        "¿Cómo estás?",
        "¿Quién eres?",
        "¿Qué puedes hacer?",
        "¿Cómo ves el negocio?",
        "Gracias",
        "Adiós",
    ],
)
def test_gateway_routes_conversational_without_business_pipeline(
    gateway: ConversationIntelligenceGateway,
    message: str,
) -> None:
    outcome = gateway.route(message)

    assert outcome.decision == GATEWAY_DECISION_CONVERSATION
    assert outcome.result is not None
    assert outcome.result.handled_by == HANDLED_BY_CONVERSATION_GATEWAY
    assert outcome.result.metadata["conversation_ux_applied"] is True
    assert outcome.metadata()["gateway_decision"] == GATEWAY_DECISION_CONVERSATION
    assert outcome.metadata()["gateway_reason"] != "business_query"


@pytest.mark.parametrize(
    "message",
    [
        "¿Cuántos clientes existen?",
        "Resumen de junio",
        "Proveedor con más compras",
        "Muéstrame los top clientes",
        "¿Qué proveedor tuvo más movimiento en junio?",
    ],
)
def test_gateway_routes_business_queries_to_pipeline(
    gateway: ConversationIntelligenceGateway,
    message: str,
) -> None:
    outcome = gateway.route(message)

    assert outcome.decision == GATEWAY_DECISION_BUSINESS
    assert outcome.result is None
    assert outcome.metadata()["gateway_reason"] == "business_query"


def test_gateway_records_timing_metadata(gateway: ConversationIntelligenceGateway) -> None:
    outcome = gateway.route("Hola")
    metadata = outcome.metadata()

    assert metadata["gateway_time_ms"] >= 0
    assert "gateway_decision" in metadata
    assert "gateway_reason" in metadata
