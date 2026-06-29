from app.conversation_memory.schemas import ConversationContext
from app.capabilities.guided_fallback_capability import GuidedFallbackCapability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.conversation_ux.classifier import (
    ConversationCategory,
    classify_message,
    is_conversational,
)
from app.conversation_ux.presenter import ConversationPresenter
from app.guided_fallback.engine import GuidedFallbackEngine
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.reasoning_engine.constants import (
    INTENT_CAPABILITIES,
    INTENT_CASUAL,
    INTENT_CLARIFICATION,
    INTENT_GREETING,
    INTENT_HELP,
    INTENT_IDENTITY,
    INTENT_INSTITUTIONAL,
    INTENT_SOCIAL,
    ROUTE_CLARIFICATION,
    ROUTE_CONVERSATION,
    ROUTE_INSTITUTIONAL_KNOWLEDGE,
)
from app.reasoning_engine.schemas import ReasoningDecision
from app.schemas.hybrid_chat import HybridChatResult
from app.schemas.semantic_intent import BusinessSemanticIntent


_INTENT_TO_CATEGORY: dict[str, ConversationCategory] = {
    INTENT_GREETING: ConversationCategory.GREETING,
    INTENT_CASUAL: ConversationCategory.CASUAL,
    INTENT_SOCIAL: ConversationCategory.SOCIAL,
    INTENT_IDENTITY: ConversationCategory.IDENTITY,
    INTENT_CAPABILITIES: ConversationCategory.CAPABILITIES,
    INTENT_HELP: ConversationCategory.HELP,
    INTENT_INSTITUTIONAL: ConversationCategory.INTRODUCTION,
    INTENT_CLARIFICATION: ConversationCategory.HELP,
}


class GovernedRouteExecutor:
    """Ejecuta rutas gobernadas sin invocar Enterprise Runtime."""

    def __init__(
        self,
        *,
        conversation_presenter: ConversationPresenter,
        institutional_knowledge: InstitutionalKnowledgeCapability | None = None,
        guided_fallback_engine: GuidedFallbackEngine | None = None,
    ) -> None:
        self._conversation_presenter = conversation_presenter
        self._institutional_knowledge = (
            institutional_knowledge or InstitutionalKnowledgeCapability()
        )
        self._guided_fallback_engine = guided_fallback_engine or GuidedFallbackEngine()
        self._guided_fallback_capability = GuidedFallbackCapability(self._guided_fallback_engine)

    def execute(
        self,
        route: str,
        message: str,
        *,
        session_id: str | None = None,
        decision: ReasoningDecision | None = None,
    ) -> HybridChatResult:
        if route == ROUTE_CONVERSATION:
            return self._execute_conversation(message, session_id=session_id, decision=decision)
        if route == ROUTE_INSTITUTIONAL_KNOWLEDGE:
            return self._execute_institutional(message, session_id=session_id)
        if route == ROUTE_CLARIFICATION:
            return self._execute_clarification(message, session_id=session_id)
        raise ValueError(f"Ruta gobernada no soportada: {route}")

    def _execute_conversation(
        self,
        message: str,
        *,
        session_id: str | None,
        decision: ReasoningDecision | None,
    ) -> HybridChatResult:
        category = classify_message(message)
        if not is_conversational(category):
            if decision is not None:
                category = _INTENT_TO_CATEGORY.get(decision.intent, ConversationCategory.HELP)
            else:
                category = ConversationCategory.HELP

        result = self._conversation_presenter.compose(message, category, session_id=session_id)
        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={
                **result.metadata,
                "governance_route": ROUTE_CONVERSATION,
                "governance_executor": "conversation_gateway",
            },
        )

    def _execute_institutional(
        self,
        message: str,
        *,
        session_id: str | None,
    ) -> HybridChatResult:
        result = self._institutional_knowledge.execute(message, session_id=session_id)
        if result is None:
            result = self._institutional_knowledge.resolve_system_capabilities(message)
        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={
                **result.metadata,
                "governance_route": ROUTE_INSTITUTIONAL_KNOWLEDGE,
                "governance_executor": "institutional_knowledge",
            },
        )

    def _execute_clarification(
        self,
        message: str,
        *,
        session_id: str | None,
    ) -> HybridChatResult:
        semantic_intent = BusinessSemanticIntent(
            source_question=message,
            confidence=0.35,
        )
        business_query = BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED)
        context = ConversationContext(session_id=session_id or "governance-clarification")
        stage = self._guided_fallback_capability.try_fallback(
            message,
            semantic_intent,
            business_query,
            context,
            session_id=session_id or "governance-clarification",
        )
        if stage is None:
            raise ValueError("Clarification engine no produjo resultado")

        return HybridChatResult(
            handled_by=stage.result.handled_by,
            success=stage.result.success,
            answer=stage.result.answer,
            suggestions=stage.result.suggestions,
            metadata={
                **stage.result.metadata,
                "governance_route": ROUTE_CLARIFICATION,
                "governance_executor": "guided_fallback",
            },
        )
