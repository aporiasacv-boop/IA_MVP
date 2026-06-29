from unittest.mock import MagicMock

import pytest

from app.capabilities.conversational_enrichment_capability import ConversationalEnrichmentCapability
from app.conversation_memory.schemas import ConversationContext
from app.schemas.hybrid_chat import HybridChatResult
from app.suggested_questions.schemas import SuggestedQuestionsResult


@pytest.fixture
def enrichment_engine() -> MagicMock:
    engine = MagicMock()
    engine.generate.return_value = SuggestedQuestionsResult(
        questions=[
            "¿Cuántos proveedores existen?",
            "¿Qué proveedor tuvo más movimiento?",
            "¿Cuál es el periodo de los datos?",
        ],
        source="type_rules",
        confidence=0.9,
    )
    return engine


@pytest.fixture
def capability(enrichment_engine: MagicMock) -> ConversationalEnrichmentCapability:
    return ConversationalEnrichmentCapability(
        suggested_questions_engine=enrichment_engine,
    )


def test_enrich_capability_discovery_skips_suggestions(
    capability: ConversationalEnrichmentCapability,
    enrichment_engine: MagicMock,
) -> None:
    context = ConversationContext(session_id="sess-1")
    result = HybridChatResult(
        handled_by="capability_discovery",
        success=True,
        answer="Puedo ayudarte con consultas de negocio.",
        metadata={"query_type": "UNSUPPORTED"},
    )

    enriched = capability.enrich(result, context=context)

    enrichment_engine.generate.assert_not_called()
    assert enriched.suggestions is None
    assert enriched.metadata["suggested_questions"] == []
    assert enriched.metadata["suggested_questions_count"] == 0
    assert enriched.metadata["suggested_questions_source"] == "none"
    assert enriched.metadata["suggested_questions_generated"] is False
    assert "coverage_recovery_hits" in enriched.metadata
    assert "coverage_recovery_misses" in enriched.metadata


def test_enrich_attaches_suggested_questions(
    capability: ConversationalEnrichmentCapability,
    enrichment_engine: MagicMock,
) -> None:
    context = ConversationContext(
        session_id="sess-2",
        last_operation="count",
        last_target_entity="clientes",
    )
    result = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Existen 50 clientes.",
        metadata={"query_type": "COUNT_CLIENTES", "confidence": 0.95},
    )

    enriched = capability.enrich(result, context=context)

    enrichment_engine.generate.assert_called_once_with(
        current_query_type="COUNT_CLIENTES",
        current_operation="count",
        current_entity="clientes",
        conversation_context=context,
        handled_by="business_pipeline",
        confidence=0.95,
    )
    assert enriched.suggestions is not None
    assert len(enriched.metadata["suggested_questions"]) == 3
    assert enriched.metadata["suggested_questions_count"] == 3
    assert enriched.metadata["suggested_questions_source"] == "type_rules"
    assert enriched.metadata["suggested_questions_generated"] is True
    assert enriched.metadata["suggested_questions_clicked"] == 0


def test_enrich_uses_pending_query_type_when_query_type_missing(
    capability: ConversationalEnrichmentCapability,
    enrichment_engine: MagicMock,
) -> None:
    context = ConversationContext(session_id="sess-3")
    result = HybridChatResult(
        handled_by="slot_clarification",
        success=True,
        answer="¿De qué cliente?",
        metadata={"pending_query_type": "MAX_TRANSACCION_CLIENTE"},
    )

    capability.enrich(result, context=context)

    enrichment_engine.generate.assert_called_once()
    call_kwargs = enrichment_engine.generate.call_args.kwargs
    assert call_kwargs["current_query_type"] == "MAX_TRANSACCION_CLIENTE"
