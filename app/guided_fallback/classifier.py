from app.conversation_memory.schemas import ConversationContext
from app.guided_fallback.types import FallbackType
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.schemas.semantic_intent import BusinessSemanticIntent
from app.utils.text_normalizer import normalize_for_matching

LOW_CONFIDENCE_THRESHOLD = 0.45

OUT_OF_DOMAIN_TERMS: tuple[str, ...] = (
    "mundial",
    "futbol",
    "fútbol",
    "seleccion",
    "selección",
    "clima",
    "tiempo atmosferico",
    "receta",
    "pelicula",
    "película",
    "elecciones",
    "presidente de mexico",
)

AMBIGUOUS_PATTERNS: tuple[str, ...] = (
    "como va el negocio",
    "como estamos",
    "que tal el negocio",
    "como va todo",
    "como va la empresa",
)

UNKNOWN_DISCOVERY_PATTERNS: tuple[str, ...] = ()

LEGACY_DELEGATION_PATTERNS: tuple[str, ...] = (
    "explicame",
    "explícame",
    "que observas",
    "qué observas",
    "que es un ",
    "qué es un ",
    "que es una ",
    "qué es una ",
    "define ",
    "definicion de",
    "definición de",
)


def should_delegate_to_legacy(question: str) -> bool:
    normalized = normalize_for_matching(question)
    return any(pattern in normalized for pattern in LEGACY_DELEGATION_PATTERNS)


def classify_fallback_type(
    question: str,
    semantic_intent: BusinessSemanticIntent,
    business_query: BusinessQuery,
    conversation_context: ConversationContext | None,
) -> FallbackType | None:
    if business_query.query_type != BusinessQueryType.UNSUPPORTED:
        return None

    if should_delegate_to_legacy(question):
        return None

    normalized = normalize_for_matching(question)

    if any(term in normalized for term in OUT_OF_DOMAIN_TERMS):
        return FallbackType.OUT_OF_DOMAIN

    if any(pattern in normalized for pattern in AMBIGUOUS_PATTERNS):
        return FallbackType.AMBIGUOUS

    if any(pattern in normalized for pattern in UNKNOWN_DISCOVERY_PATTERNS):
        return FallbackType.UNKNOWN

    has_partial_intent = (
        semantic_intent.operation is not None or semantic_intent.target_entity is not None
    )

    if has_partial_intent and semantic_intent.confidence < LOW_CONFIDENCE_THRESHOLD:
        return FallbackType.LOW_CONFIDENCE

    if has_partial_intent:
        return FallbackType.UNSUPPORTED_CAPABILITY

    _ = conversation_context
    return FallbackType.UNKNOWN
