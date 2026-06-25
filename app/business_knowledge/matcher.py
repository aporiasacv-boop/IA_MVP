from app.enterprise_knowledge_service.runtime.matcher import (
    IDENTITY_FAQ_KEYS,
    get_institutional_matcher,
)

_matcher = get_institutional_matcher()

is_identity_institutional_question = _matcher.is_identity_institutional_question
resolve_institutional_question = _matcher.resolve_institutional_question

__all__ = [
    "IDENTITY_FAQ_KEYS",
    "is_identity_institutional_question",
    "resolve_institutional_question",
]
