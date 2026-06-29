from unittest.mock import MagicMock

import pytest

from app.conversation_ux.presenter import ConversationPresenter
from app.enterprise_knowledge_service.schemas import CapabilitiesPayload
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture
def presenter() -> ConversationPresenter:
    return ConversationPresenter(
        knowledge_service=MagicMock(
            get_capabilities=MagicMock(
                return_value=CapabilitiesPayload(
                    answer="",
                    capabilities=["Clientes", "Proveedores", "Indicadores empresariales"],
                    examples=[
                        "¿Cuántos clientes existen?",
                        "¿Qué proveedor tuvo más movimiento en junio?",
                    ],
                )
            )
        ),
        dataset_summary_provider=lambda: {
            "registros": 12500,
            "clientes": 48,
            "proveedores": 32,
            "fecha_minima": "2024-01-01",
            "fecha_maxima": "2024-06-30",
        },
    )


def test_enhance_greeting_rewrites_guided_fallback(presenter: ConversationPresenter) -> None:
    original = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Puedo ayudarte con:\n\n• KPIs ejecutivos",
        metadata={"fallback_type": "AMBIGUOUS"},
    )

    enhanced = presenter.enhance("Hola", original)

    assert enhanced.metadata["conversation_ux_applied"] is True
    assert enhanced.metadata["conversation_category"] == "greeting"
    assert "Olnatura Intelligence" in enhanced.answer
    assert "12.500 movimientos" in enhanced.answer
    assert enhanced.suggestions is not None
    assert 3 <= len(enhanced.suggestions.questions) <= 5


def test_enhance_capabilities_keeps_product_identity_handler(
    presenter: ConversationPresenter,
) -> None:
    original = HybridChatResult(
        handled_by="product_identity",
        success=True,
        answer="Soy Olnatura Intelligence. Puedo ayudarte...",
        metadata={"query_type": "PRODUCT_IDENTITY"},
    )

    enhanced = presenter.enhance("¿Qué puedes hacer?", original)

    assert enhanced.handled_by == "product_identity"
    assert enhanced.metadata["conversation_ux_applied"] is True
    assert "48 clientes" in enhanced.answer
    assert enhanced.suggestions is not None


def test_enhance_skips_business_pipeline(presenter: ConversationPresenter) -> None:
    original = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        metadata={"query_type": "COUNT_CLIENTES"},
    )

    enhanced = presenter.enhance("¿Cuántos clientes existen?", original)

    assert enhanced is original


def test_enhance_executive_general_for_ambiguous_question(
    presenter: ConversationPresenter,
) -> None:
    original = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Puedo ayudarte con:",
        metadata={"fallback_type": "AMBIGUOUS"},
    )

    enhanced = presenter.enhance("¿Cómo ves el negocio?", original)

    assert enhanced.metadata["conversation_category"] == "executive_general"
    assert "lectura ejecutiva" in enhanced.answer.lower()


def test_enhance_without_dataset_provider_uses_generic_copy() -> None:
    presenter = ConversationPresenter(
        knowledge_service=MagicMock(
            get_capabilities=MagicMock(
                return_value=CapabilitiesPayload(
                    answer="",
                    capabilities=["Clientes"],
                    examples=["¿Cuántos clientes existen?"],
                )
            )
        ),
        dataset_summary_provider=None,
    )
    original = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="fallback",
        metadata={},
    )

    enhanced = presenter.enhance("Hola", original)

    assert "datos corporativos estructurados" in enhanced.answer
