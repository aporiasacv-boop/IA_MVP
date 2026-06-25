from app.enterprise_knowledge_service.integration.consumers import knowledge_for_product_identity
from app.enterprise_knowledge_service.runtime.responder import (
    HANDLED_BY_PRODUCT_IDENTITY,
    try_product_identity_from_runtime,
)
from app.schemas.hybrid_chat import HybridChatResult

__all__ = [
    "HANDLED_BY_PRODUCT_IDENTITY",
    "build_identity_answer",
    "is_identity_question",
    "try_product_identity_response",
]


def build_identity_answer(question: str) -> str | None:
    return knowledge_for_product_identity(question)


def is_identity_question(question: str) -> bool:
    from app.enterprise_knowledge_service.runtime.matcher import get_institutional_matcher

    return get_institutional_matcher().is_identity_institutional_question(question)


def try_product_identity_response(message: str) -> HybridChatResult | None:
    return try_product_identity_from_runtime(message)
