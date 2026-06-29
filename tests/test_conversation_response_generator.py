from unittest.mock import MagicMock

import pytest

from app.ai_orchestration.schemas import LLMGenerateResult
from app.conversation_ux.prompt import CONVERSATION_PROMPT_MARKER, build_conversation_response_prompt
from app.conversation_ux.response_generator import ConversationResponseGenerator
from app.conversation_ux.schemas import ConversationGenerationContext
from app.conversation_ux.classifier import ConversationCategory
from app.schemas.hybrid_chat import HybridChatResult
from app.suggested_questions.schemas import SuggestedQuestionsResult


@pytest.fixture
def conversational_result() -> HybridChatResult:
    return HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Hola. Soy Olnatura Intelligence, tu analista corporativo.",
        suggestions=SuggestedQuestionsResult(
            questions=["¿Qué pasó en junio?", "¿Cuántos clientes existen?"],
            source="conversation_ux",
            confidence=1.0,
            metadata={},
        ),
        metadata={
            "conversation_ux_applied": True,
            "conversation_category": "greeting",
            "conversation_pipeline_answer": "Puedo ayudarte con:",
            "conversation_template_answer": "Hola. Soy Olnatura Intelligence, tu analista corporativo.",
            "conversation_dataset_snapshot": {
                "registros": 12500,
                "clientes": 48,
                "proveedores": 32,
            },
            "conversation_capabilities": ["Clientes", "Proveedores"],
            "conversation_capability_examples": ["¿Cuántos clientes existen?"],
        },
    )


def test_generate_rewrites_with_llm(conversational_result: HybridChatResult) -> None:
    provider = MagicMock()
    provider.generate_response.return_value = LLMGenerateResult(
        text="Hola, encantado de ayudarte. Tengo acceso a 48 clientes y 32 proveedores.",
        provider="mock",
        model="mock-v1",
    )
    provider.provider_name.return_value = "mock"
    provider.model_name = "mock-v1"

    generator = ConversationResponseGenerator(provider, enabled=True)
    result = generator.generate("Hola", conversational_result)

    assert result.answer.startswith("Hola, encantado")
    assert result.metadata["conversation_llm_applied"] is True
    assert result.metadata["conversation_llm_fallback_used"] is False
    assert result.metadata["conversation_llm_provider"] == "mock"
    assert result.metadata["conversation_ux_layer"] == "llm_v1"


def test_generate_falls_back_to_template_on_failure(
    conversational_result: HybridChatResult,
) -> None:
    provider = MagicMock()
    provider.generate_response.side_effect = TimeoutError("timeout")
    provider.provider_name.return_value = "ollama"
    provider.model_name = "qwen3:8b"

    generator = ConversationResponseGenerator(provider, enabled=True)
    result = generator.generate("Hola", conversational_result)

    assert result.answer == conversational_result.answer
    assert result.metadata["conversation_llm_fallback_used"] is True
    assert result.metadata["conversation_llm_applied"] is False
    assert result.metadata["conversation_ux_layer"] == "presenter_v1"


def test_generate_skips_without_conversation_ux() -> None:
    provider = MagicMock()
    original = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        metadata={"query_type": "COUNT_CLIENTES"},
    )

    generator = ConversationResponseGenerator(provider, enabled=True)
    result = generator.generate("¿Cuántos clientes existen?", original)

    assert result is original
    provider.generate_response.assert_not_called()


def test_generate_respects_disabled_flag(conversational_result: HybridChatResult) -> None:
    provider = MagicMock()
    generator = ConversationResponseGenerator(provider, enabled=False)
    result = generator.generate("Hola", conversational_result)

    assert result.answer == conversational_result.answer
    assert result.metadata["conversation_llm_fallback_used"] is True
    provider.generate_response.assert_not_called()


def test_prompt_contains_guardrails_and_marker() -> None:
    prompt = build_conversation_response_prompt(
        ConversationGenerationContext(
            user_message="Hola",
            conversation_category=ConversationCategory.GREETING,
            pipeline_answer="Puedo ayudarte con:",
            template_answer="Hola. Soy Olnatura Intelligence.",
            dataset_snapshot={"clientes": 48},
            capabilities=("Clientes",),
            capability_examples=("¿Cuántos clientes existen?",),
            suggested_questions=("¿Qué pasó en junio?",),
            pipeline_metadata={"handled_by": "guided_fallback"},
        )
    )

    assert CONVERSATION_PROMPT_MARKER in prompt
    assert "Nunca inventes datos" in prompt
    assert "48" in prompt
    assert "PREGUNTA DEL USUARIO" in prompt
