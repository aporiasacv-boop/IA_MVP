from app.enterprise_knowledge_service.runtime.matcher import get_institutional_matcher
from app.schemas.hybrid_chat import HybridChatResult

HANDLED_BY_BUSINESS_KNOWLEDGE = "business_knowledge"
HANDLED_BY_PRODUCT_IDENTITY = "product_identity"


def try_business_knowledge_response(message: str) -> HybridChatResult | None:
    matcher = get_institutional_matcher()
    if matcher.is_identity_institutional_question(message):
        return None
    resolved = matcher.resolve_institutional_question(message)
    if resolved is None:
        return None
    return HybridChatResult(
        handled_by=HANDLED_BY_BUSINESS_KNOWLEDGE,
        success=True,
        answer=resolved.answer,
        metadata={
            "handled_by": HANDLED_BY_BUSINESS_KNOWLEDGE,
            "confidence": resolved.confidence,
            "query_type": "BUSINESS_KNOWLEDGE",
            "knowledge_source": resolved.source,
            "knowledge_category": resolved.category,
            "knowledge_match_type": resolved.match_type,
        },
    )


def try_product_identity_from_runtime(message: str) -> HybridChatResult | None:
    matcher = get_institutional_matcher()
    if not matcher.is_identity_institutional_question(message):
        return None
    resolved = matcher.resolve_institutional_question(message)
    if resolved is None:
        return None
    return HybridChatResult(
        handled_by=HANDLED_BY_PRODUCT_IDENTITY,
        success=True,
        answer=resolved.answer,
        metadata={
            "handled_by": HANDLED_BY_PRODUCT_IDENTITY,
            "confidence": 1.0,
            "query_type": "PRODUCT_IDENTITY",
            "knowledge_source": resolved.source,
            "knowledge_category": resolved.category,
            "knowledge_match_type": resolved.match_type,
        },
    )


__all__ = [
    "HANDLED_BY_BUSINESS_KNOWLEDGE",
    "HANDLED_BY_PRODUCT_IDENTITY",
    "try_business_knowledge_response",
    "try_product_identity_from_runtime",
]
