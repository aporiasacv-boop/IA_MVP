from app.conversation_ux.classifier import ConversationCategory, classify_message, is_conversational
from app.reasoning_engine.constants import (
    INTENT_BUSINESS_QUERY,
    INTENT_CAPABILITIES,
    INTENT_CASUAL,
    INTENT_CLARIFICATION,
    INTENT_EXECUTIVE_ANALYSIS,
    INTENT_GREETING,
    INTENT_HELP,
    INTENT_IDENTITY,
    INTENT_INSTITUTIONAL,
    INTENT_LEGACY,
    INTENT_SOCIAL,
    INTENT_UNKNOWN,
    ROUTE_BUSINESS_PIPELINE,
    ROUTE_CLARIFICATION,
    ROUTE_CONVERSATION,
    ROUTE_EXECUTIVE_ANALYSIS,
    ROUTE_INSTITUTIONAL_KNOWLEDGE,
    ROUTE_LEGACY,
)
from app.reasoning_engine.schemas import ReasoningDecision
from app.utils.text_normalizer import normalize_for_matching

_CLARIFICATION_PATTERNS: tuple[str, ...] = (
    "no entiendo",
    "no comprendo",
    "que significa",
    "explicame de nuevo",
    "puedes aclarar",
    "no me quedo claro",
)

_EXECUTIVE_PATTERNS: tuple[str, ...] = (
    "resume",
    "resumen",
    "resumen de",
    "resumen ejecutivo",
    "panorama",
    "como ves el negocio",
    "analisis ejecutivo",
    "sintesis",
)

_BUSINESS_PATTERNS: tuple[str, ...] = (
    "cuantos",
    "cuantas",
    "top ",
    "principales",
    "proveedor",
    "cliente",
    "transaccion",
    "movimiento",
    "junio",
    "julio",
    "agosto",
    "periodo",
    "dataset",
    "registros",
)


def rule_based_decision(message: str) -> ReasoningDecision:
    normalized = normalize_for_matching(message)

    if any(pattern in normalized for pattern in _CLARIFICATION_PATTERNS):
        return _decision(
            INTENT_CLARIFICATION,
            ROUTE_CLARIFICATION,
            "El usuario expresa confusión o necesita aclaración.",
            confidence=0.82,
        )

    if any(pattern in normalized for pattern in _EXECUTIVE_PATTERNS):
        return _decision(
            INTENT_EXECUTIVE_ANALYSIS,
            ROUTE_EXECUTIVE_ANALYSIS,
            "El usuario solicita un análisis o resumen ejecutivo.",
            confidence=0.86,
        )

    if any(pattern in normalized for pattern in _BUSINESS_PATTERNS):
        return _decision(
            INTENT_BUSINESS_QUERY,
            ROUTE_BUSINESS_PIPELINE,
            "El usuario solicita información empresarial estructurada.",
            confidence=0.9,
        )

    category = classify_message(message)
    if is_conversational(category):
        return _decision_from_category(category)

    return _decision(
        INTENT_UNKNOWN,
        ROUTE_LEGACY,
        "No se detectó una intención clara; se recomienda flujo legacy.",
        confidence=0.55,
    )


def _decision_from_category(category: ConversationCategory) -> ReasoningDecision:
    mapping = {
        ConversationCategory.GREETING: (
            INTENT_GREETING,
            ROUTE_CONVERSATION,
            "Saludo inicial del usuario.",
            0.95,
        ),
        ConversationCategory.FAREWELL: (
            INTENT_SOCIAL,
            ROUTE_CONVERSATION,
            "Despedida o cierre conversacional.",
            0.93,
        ),
        ConversationCategory.CASUAL: (
            INTENT_CASUAL,
            ROUTE_CONVERSATION,
            "Conversación casual sin consulta empresarial.",
            0.9,
        ),
        ConversationCategory.SOCIAL: (
            INTENT_SOCIAL,
            ROUTE_CONVERSATION,
            "Interacción social sin consulta empresarial.",
            0.88,
        ),
        ConversationCategory.IDENTITY: (
            INTENT_IDENTITY,
            ROUTE_INSTITUTIONAL_KNOWLEDGE,
            "Consulta sobre identidad del asistente.",
            0.94,
        ),
        ConversationCategory.CAPABILITIES: (
            INTENT_CAPABILITIES,
            ROUTE_INSTITUTIONAL_KNOWLEDGE,
            "Consulta sobre capacidades del asistente.",
            0.94,
        ),
        ConversationCategory.INTRODUCTION: (
            INTENT_INSTITUTIONAL,
            ROUTE_INSTITUTIONAL_KNOWLEDGE,
            "Solicitud de presentación institucional.",
            0.92,
        ),
        ConversationCategory.HELP: (
            INTENT_HELP,
            ROUTE_CONVERSATION,
            "Solicitud de ayuda general sobre el asistente.",
            0.9,
        ),
        ConversationCategory.EXECUTIVE_GENERAL: (
            INTENT_EXECUTIVE_ANALYSIS,
            ROUTE_EXECUTIVE_ANALYSIS,
            "Consulta ejecutiva general sobre el negocio.",
            0.85,
        ),
    }
    intent, route, explanation, confidence = mapping[category]
    return _decision(intent, route, explanation, confidence)


def _decision(
    intent: str,
    route: str,
    explanation: str,
    confidence: float,
) -> ReasoningDecision:
    return ReasoningDecision(
        intent=intent,
        confidence=confidence,
        recommended_route=route,
        explanation=explanation,
        source="rules",
    )
