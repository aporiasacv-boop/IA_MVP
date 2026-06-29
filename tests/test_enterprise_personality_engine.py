from unittest.mock import MagicMock

import pytest

from app.conversation_ux.classifier import ConversationCategory
from app.conversation_ux.presenter import ConversationPresenter
from app.core import settings as settings_module
from app.enterprise_knowledge_service.schemas import CapabilitiesPayload
from app.enterprise_personality.constants import (
    ADAPTATION_CLOSURE,
    ADAPTATION_CONSULTANT_MODE,
    ADAPTATION_EXPLORATION,
    ADAPTATION_GUIDED_RECOVERY,
    ADAPTATION_INSTITUTIONAL_INTRO,
    FORBIDDEN_PHRASES,
    PROFILE_ENTERPRISE_INTELLIGENCE_DIRECTOR,
    PROTECTED_HANDLED_BY,
)
from app.enterprise_personality.engine import EnterprisePersonalityEngine
from app.enterprise_personality.metrics import get_metrics, reset_metrics
from app.schemas.hybrid_chat import HybridChatResult


@pytest.fixture
def engine() -> EnterprisePersonalityEngine:
    return EnterprisePersonalityEngine()


@pytest.fixture
def presenter() -> ConversationPresenter:
    return ConversationPresenter(
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
            "registros": 12500,
            "clientes": 48,
            "proveedores": 32,
            "fecha_minima": "2024-01-01",
            "fecha_maxima": "2024-06-30",
        },
    )


@pytest.fixture(autouse=True)
def enable_personality(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings_module.settings, "ENTERPRISE_PERSONALITY_ENABLED", True)


def _presented(presenter: ConversationPresenter, message: str) -> HybridChatResult:
    from app.conversation_ux.classifier import classify_message

    category = classify_message(message)
    return presenter.compose(message, category)


def test_personality_applies_director_voice_to_greeting(
    engine: EnterprisePersonalityEngine,
    presenter: ConversationPresenter,
) -> None:
    reset_metrics()
    base = _presented(presenter, "Hola")
    result = engine.apply("Hola", base)

    assert result.metadata["personality_applied"] is True
    assert result.metadata["personality_profile"] == PROFILE_ENTERPRISE_INTELLIGENCE_DIRECTOR
    assert result.metadata["adaptation_type"] == ADAPTATION_INSTITUTIONAL_INTRO
    assert "Director" in result.answer or "inteligencia empresarial" in result.answer.lower()
    assert "analista corporativo" not in result.answer.lower()
    assert "12.500 movimientos" in result.answer
    assert get_metrics().total_applications == 1


def test_personality_capabilities_use_exploration_adaptation(
    engine: EnterprisePersonalityEngine,
    presenter: ConversationPresenter,
) -> None:
    base = _presented(presenter, "¿Qué puedes hacer?")
    result = engine.apply("¿Qué puedes hacer?", base)

    assert result.metadata["adaptation_type"] == ADAPTATION_EXPLORATION
    assert "arrancar con impacto" in result.answer.lower()
    assert "Estas son algunas áreas" not in result.answer


def test_personality_help_uses_guided_recovery(
    engine: EnterprisePersonalityEngine,
    presenter: ConversationPresenter,
) -> None:
    base = _presented(presenter, "Ayuda")
    result = engine.apply("Ayuda", base)

    assert result.metadata["adaptation_type"] == ADAPTATION_GUIDED_RECOVERY
    assert "te oriento" in result.answer.lower()


def test_personality_executive_uses_consultant_mode(
    engine: EnterprisePersonalityEngine,
    presenter: ConversationPresenter,
) -> None:
    base = _presented(presenter, "¿Cómo ves el negocio?")
    result = engine.apply("¿Cómo ves el negocio?", base)

    assert result.metadata["adaptation_type"] == ADAPTATION_CONSULTANT_MODE
    assert "lectura ejecutiva" in result.answer.lower()


def test_personality_farewell_uses_closure(
    engine: EnterprisePersonalityEngine,
    presenter: ConversationPresenter,
) -> None:
    from app.conversation_ux.classifier import ConversationCategory

    base = presenter.compose("Adiós", ConversationCategory.FAREWELL)
    result = engine.apply("Adiós", base)

    assert result.metadata["adaptation_type"] == ADAPTATION_CLOSURE
    assert "acompañarte" in result.answer.lower()


def test_personality_skips_business_pipeline(engine: EnterprisePersonalityEngine) -> None:
    original = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        metadata={
            "query_type": "COUNT_CLIENTES",
            "conversation_ux_applied": True,
        },
    )

    result = engine.apply("¿Cuántos clientes existen?", original)

    assert result.metadata["personality_applied"] is False
    assert result.answer == original.answer


def test_personality_skips_without_conversation_ux(engine: EnterprisePersonalityEngine) -> None:
    original = HybridChatResult(
        handled_by="conversation_gateway",
        success=True,
        answer="Hola",
        metadata={},
    )

    result = engine.apply("Hola", original)

    assert result.metadata["personality_applied"] is False


@pytest.mark.parametrize("handled_by", sorted(PROTECTED_HANDLED_BY))
def test_personality_skips_protected_handlers(
    engine: EnterprisePersonalityEngine,
    handled_by: str,
) -> None:
    original = HybridChatResult(
        handled_by=handled_by,
        success=True,
        answer="Respuesta protegida.",
        metadata={
            "conversation_ux_applied": True,
            "conversation_category": ConversationCategory.GREETING.value,
        },
    )

    result = engine.apply("Hola", original)
    assert result.metadata["personality_applied"] is False
    assert result.answer == "Respuesta protegida."


def test_personality_disabled_returns_original(
    engine: EnterprisePersonalityEngine,
    presenter: ConversationPresenter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings_module.settings, "ENTERPRISE_PERSONALITY_ENABLED", False)
    base = _presented(presenter, "Hola")
    result = engine.apply("Hola", base)

    assert result.metadata["personality_applied"] is False
    assert result.answer == base.answer


def test_personality_does_not_use_forbidden_phrases(
    engine: EnterprisePersonalityEngine,
    presenter: ConversationPresenter,
) -> None:
    base = _presented(presenter, "¿Quién eres?")
    result = engine.apply("¿Quién eres?", base)
    lowered = result.answer.lower()

    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in lowered
