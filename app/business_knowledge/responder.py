from app.enterprise_knowledge_service.runtime.matcher import get_institutional_matcher
from app.enterprise_knowledge_service.runtime.responder import (
    HANDLED_BY_BUSINESS_KNOWLEDGE,
    HANDLED_BY_PRODUCT_IDENTITY,
    try_business_knowledge_response,
    try_product_identity_from_runtime,
)

__all__ = [
    "HANDLED_BY_BUSINESS_KNOWLEDGE",
    "HANDLED_BY_PRODUCT_IDENTITY",
    "try_business_knowledge_response",
    "try_product_identity_from_runtime",
    "is_identity_institutional_question",
]

from app.enterprise_knowledge_service.runtime.matcher import (  # noqa: E402
    is_identity_institutional_question,
)
