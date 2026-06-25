from app.enterprise_knowledge_service.integration.consumers import knowledge_for_product_identity
from app.enterprise_knowledge_service.runtime.matcher import get_institutional_matcher


def build_identity_answer(question: str) -> str | None:
    return knowledge_for_product_identity(question)


def is_identity_question(question: str) -> bool:
    return get_institutional_matcher().is_identity_institutional_question(question)
