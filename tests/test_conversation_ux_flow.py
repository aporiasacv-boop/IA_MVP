from unittest.mock import MagicMock

from app.conversation_ux.presenter import ConversationPresenter
from app.conversation_ux.response_generator import ConversationResponseGenerator
from app.enterprise_personality.engine import EnterprisePersonalityEngine
from app.enterprise_knowledge_service.schemas import CapabilitiesPayload
from app.schemas.hybrid_chat import HybridChatResult


def test_presenter_then_generator_flow() -> None:
    presenter = ConversationPresenter(
        knowledge_service=MagicMock(
            get_capabilities=MagicMock(
                return_value=CapabilitiesPayload(
                    answer="",
                    capabilities=["Clientes", "Proveedores"],
                    examples=["¿Cuántos clientes existen?"],
                )
            )
        ),
        dataset_summary_provider=lambda: {
            "registros": 1000,
            "clientes": 10,
            "proveedores": 5,
        },
    )
    provider = MagicMock()
    provider.generate_response.return_value = MagicMock(
        text="¡Hola! Estoy aquí para ayudarte con clientes y proveedores.",
        provider="mock",
        model="mock-v1",
    )
    provider.provider_name.return_value = "mock"
    provider.model_name = "mock-v1"

    generator = ConversationResponseGenerator(provider, enabled=True)
    pipeline_result = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Puedo ayudarte con:",
        metadata={"fallback_type": "AMBIGUOUS"},
    )

    presented = presenter.enhance("Hola", pipeline_result)
    personalized = EnterprisePersonalityEngine().apply("Hola", presented)
    final = generator.generate("Hola", personalized)

    assert presented.metadata["conversation_ux_applied"] is True
    assert personalized.metadata["personality_applied"] is True
    assert final.metadata["conversation_llm_applied"] is True
    assert "clientes" in final.answer.lower()
    provider.generate_response.assert_called_once()
