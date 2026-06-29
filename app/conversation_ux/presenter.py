from collections.abc import Callable

from app.conversation_ux.classifier import (
    ConversationCategory,
    classify_message,
    greeting_time_phrase,
)
from app.conversation_ux.constants import HANDLED_BY_CONVERSATION_GATEWAY
from app.conversation_ux.context import DatasetSnapshot, resolve_dataset_snapshot
from app.conversation_ux.response_generator import snapshot_to_dict
from app.conversation_ux.suggestions import build_conversational_suggestions
from app.conversation_ux.templates import (
    build_capabilities_answer,
    build_casual_answer,
    build_executive_general_answer,
    build_farewell_answer,
    build_greeting_answer,
    build_help_answer,
    build_identity_answer,
    build_introduction_answer,
    build_social_answer,
)
from app.enterprise_knowledge_service.service import EnterpriseKnowledgePlatformService
from app.schemas.hybrid_chat import HybridChatResult
from app.suggested_questions.schemas import SuggestedQuestionsResult

DatasetSummaryProvider = Callable[[], dict]

_PROTECTED_HANDLED_BY = frozenset({
    "business_pipeline",
    "slot_clarification",
    "conversation_memory",
})

_ENHANCEABLE_HANDLED_BY = frozenset({
    "product_identity",
    "business_knowledge",
    "guided_fallback",
    "executive_reasoning",
    "legacy_chat",
})


class ConversationPresenter:
    """Capa de experiencia conversacional post-pipeline.

    Transforma respuestas institucionales o de fallback en un tono de analista
    corporativo sin alterar la lógica del Business Pipeline.
    """

    def __init__(
        self,
        *,
        knowledge_service: EnterpriseKnowledgePlatformService | None = None,
        dataset_summary_provider: DatasetSummaryProvider | None = None,
    ) -> None:
        self._knowledge_service = knowledge_service
        self._dataset_summary_provider = dataset_summary_provider

    def compose(
        self,
        message: str,
        category: ConversationCategory,
        *,
        session_id: str | None = None,
    ) -> HybridChatResult:
        """Construye respuesta conversacional sin pasar por el Business Pipeline."""
        snapshot = resolve_dataset_snapshot(self._dataset_summary_provider)
        capabilities = self._load_capabilities()
        answer = self._build_answer(category, message, snapshot, capabilities)
        if answer is None:
            raise ValueError(f"Categoría conversacional sin plantilla: {category.value}")

        suggestions = build_conversational_suggestions(
            category,
            capability_examples=capabilities.examples,
        )
        institutional_reference = self._institutional_reference(message, category)
        metadata: dict = {
            "conversation_ux_applied": True,
            "conversation_category": category.value,
            "conversation_pipeline_answer": institutional_reference,
            "conversation_template_answer": answer,
            "conversation_dataset_snapshot": snapshot_to_dict(snapshot),
            "conversation_capabilities": list(capabilities.capabilities),
            "conversation_capability_examples": list(capabilities.examples),
            "conversation_ux_layer": "presenter_v1",
            "gateway_handled": True,
            "confidence": 1.0,
            "query_type": "CONVERSATION",
        }
        if session_id:
            metadata["session_id"] = session_id

        return HybridChatResult(
            handled_by=HANDLED_BY_CONVERSATION_GATEWAY,
            success=True,
            answer=answer,
            suggestions=SuggestedQuestionsResult(
                questions=suggestions,
                source="conversation_ux",
                confidence=1.0,
                metadata={
                    "suggested_questions_count": len(suggestions),
                    "conversation_category": category.value,
                    "suggested_questions_generated": True,
                    "suggested_questions_source": "conversation_ux",
                },
            ),
            metadata=metadata,
        )

    def enhance(self, message: str, result: HybridChatResult) -> HybridChatResult:
        category = classify_message(message)
        if category is ConversationCategory.NONE:
            return result
        if result.handled_by in _PROTECTED_HANDLED_BY:
            return result
        if result.handled_by not in _ENHANCEABLE_HANDLED_BY:
            return result

        snapshot = resolve_dataset_snapshot(self._dataset_summary_provider)
        capabilities = self._load_capabilities()
        answer = self._build_answer(category, message, snapshot, capabilities)
        if answer is None:
            return result

        suggestions = build_conversational_suggestions(
            category,
            capability_examples=capabilities.examples,
        )
        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=answer,
            suggestions=SuggestedQuestionsResult(
                questions=suggestions,
                source="conversation_ux",
                confidence=1.0,
                metadata={
                    "suggested_questions_count": len(suggestions),
                    "conversation_category": category.value,
                    "suggested_questions_generated": True,
                    "suggested_questions_source": "conversation_ux",
                },
            ),
            metadata={
                **result.metadata,
                "conversation_ux_applied": True,
                "conversation_category": category.value,
                "conversation_pipeline_answer": result.answer,
                "conversation_template_answer": answer,
                "conversation_dataset_snapshot": snapshot_to_dict(snapshot),
                "conversation_capabilities": list(capabilities.capabilities),
                "conversation_capability_examples": list(capabilities.examples),
                "conversation_ux_layer": "presenter_v1",
            },
        )

    def _load_capabilities(self):
        if self._knowledge_service is None:
            from app.enterprise_knowledge_service.service import (
                get_enterprise_knowledge_platform_service,
            )

            self._knowledge_service = get_enterprise_knowledge_platform_service()
        return self._knowledge_service.get_capabilities()

    def _build_answer(
        self,
        category: ConversationCategory,
        message: str,
        snapshot: DatasetSnapshot,
        capabilities,
    ) -> str | None:
        labels = list(capabilities.capabilities)
        examples = list(capabilities.examples)

        if category is ConversationCategory.GREETING:
            return build_greeting_answer(greeting_time_phrase(message), snapshot)
        if category is ConversationCategory.CASUAL:
            return build_casual_answer(snapshot)
        if category is ConversationCategory.IDENTITY:
            return build_identity_answer(snapshot)
        if category is ConversationCategory.CAPABILITIES:
            return build_capabilities_answer(snapshot, labels, examples)
        if category is ConversationCategory.EXECUTIVE_GENERAL:
            return build_executive_general_answer(snapshot)
        if category is ConversationCategory.HELP:
            return build_help_answer(snapshot)
        if category is ConversationCategory.FAREWELL:
            return build_farewell_answer(snapshot)
        if category is ConversationCategory.INTRODUCTION:
            return build_introduction_answer(snapshot)
        if category is ConversationCategory.SOCIAL:
            return build_social_answer(snapshot)
        return None

    def _institutional_reference(
        self,
        message: str,
        category: ConversationCategory,
    ) -> str:
        if category not in {
            ConversationCategory.IDENTITY,
            ConversationCategory.CAPABILITIES,
            ConversationCategory.INTRODUCTION,
        }:
            return ""
        if self._knowledge_service is None:
            from app.enterprise_knowledge_service.service import (
                get_enterprise_knowledge_platform_service,
            )

            self._knowledge_service = get_enterprise_knowledge_platform_service()
        faq = self._knowledge_service.get_faq(message)
        return faq or ""
