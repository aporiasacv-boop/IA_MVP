from unittest.mock import MagicMock, patch

from app.capabilities.executive_reasoning_capability import ExecutiveReasoningCapability
from app.schemas.hybrid_chat import HybridChatResult


def test_try_reason_returns_none_when_disabled() -> None:
    handler = MagicMock()
    capability = ExecutiveReasoningCapability(handler=handler)

    with patch("app.capabilities.executive_reasoning_capability.settings") as settings:
        settings.EXECUTIVE_REASONING_ENABLED = False
        result = capability.try_reason("Evaluar riesgos del cliente principal")

    assert result is None
    handler.assert_not_called()


def test_try_reason_returns_none_for_non_candidate() -> None:
    handler = MagicMock()
    capability = ExecutiveReasoningCapability(handler=handler)

    with patch(
        "app.capabilities.executive_reasoning_capability.is_executive_reasoning_candidate",
        return_value=False,
    ):
        result = capability.try_reason("Listar clientes")

    assert result is None
    handler.assert_not_called()


def test_try_reason_invokes_handler_for_candidate() -> None:
    expected = HybridChatResult(
        handled_by="executive_reasoning",
        success=True,
        answer="Análisis ejecutivo.",
        metadata={"handled_by": "executive_reasoning"},
    )
    handler = MagicMock(return_value=expected)
    capability = ExecutiveReasoningCapability(handler=handler)

    with patch(
        "app.capabilities.executive_reasoning_capability.is_executive_reasoning_candidate",
        return_value=True,
    ), patch(
        "app.capabilities.executive_reasoning_capability.settings"
    ) as settings:
        settings.EXECUTIVE_REASONING_ENABLED = True
        stage = capability.try_reason("Evaluar riesgos del cliente principal")

    assert stage is not None
    assert stage.result is expected
    assert stage.stage_ms >= 0
    handler.assert_called_once_with("Evaluar riesgos del cliente principal")
