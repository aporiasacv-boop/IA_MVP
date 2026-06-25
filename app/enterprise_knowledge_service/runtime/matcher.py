import re
import unicodedata

from app.capability_discovery.detector import CAPABILITY_DISCOVERY_PATTERNS
from app.enterprise_knowledge_service.metrics import get_enterprise_knowledge_metrics
from app.enterprise_knowledge_service.schemas import CapabilitiesPayload, InstitutionalAnswer, KnowledgeDocument
from app.enterprise_knowledge_service.service import get_enterprise_knowledge_platform_service
from app.utils.text_normalizer import normalize_for_matching

IDENTITY_FAQ_KEYS: tuple[str, ...] = (
    "como te llamas",
    "cual es tu nombre",
    "quien eres",
    "que eres",
    "quien te creo",
    "quien te desarrollo",
    "que haces",
    "que puedes hacer",
    "para que sirves",
    "como me ayudas",
    "como obtienes la informacion",
    "de donde obtienes la informacion",
    "como obtienes los datos",
    "de donde sale la informacion",
)

DEFINITION_PATTERNS: tuple[str, ...] = (
    "que es un ",
    "que es una ",
    "que significa ",
    "que son los ",
    "que son las ",
    "define ",
    "explicame que es ",
)


def _normalize_question(text: str) -> str:
    lowered = text.lower().strip()
    decomposed = unicodedata.normalize("NFD", lowered)
    without_accents = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    cleaned = re.sub(r"[^\w\s]", " ", without_accents)
    return re.sub(r"\s+", " ", cleaned).strip()


def _strip_question_mark(text: str) -> str:
    return text.strip().rstrip("?").strip()


class InstitutionalMatcher:
    """Componente interno BKR: resolución institucional sobre EKS."""

    def __init__(self, service=None) -> None:
        self._service = service or get_enterprise_knowledge_platform_service()

    def _faq_lookup(self, question: str) -> InstitutionalAnswer | None:
        answer = self._service.get_faq(question)
        if answer is None:
            answer = self._service.get_faq(_strip_question_mark(question))
        if answer is None:
            return None
        return InstitutionalAnswer(
            answer=answer,
            source="knowledge_pack/faq",
            category="faq",
            match_type="faq_exact",
        )

    def _definition_lookup(self, question: str) -> InstitutionalAnswer | None:
        normalized = _normalize_question(question)
        if not any(normalized.startswith(pattern) for pattern in DEFINITION_PATTERNS):
            return None
        answer = self._faq_lookup(question)
        if answer is not None:
            answer.match_type = "faq_definition"
            return answer
        results = self._service.search(question, limit=3).items
        for doc in results:
            if doc.category in {"concepts", "glossary", "faq"}:
                for section_title, body in doc.sections.items():
                    if (
                        normalize_for_matching(section_title) in normalized
                        or normalized in normalize_for_matching(section_title)
                    ):
                        return InstitutionalAnswer(
                            answer=body.strip(),
                            source=doc.path,
                            category=doc.category,
                            match_type="knowledge_search",
                            confidence=0.9,
                        )
        return None

    def _capability_lookup(self, question: str) -> InstitutionalAnswer | None:
        normalized = _normalize_question(question)
        if not any(
            normalized == pattern or normalized.startswith(f"{pattern} ")
            for pattern in CAPABILITY_DISCOVERY_PATTERNS
        ):
            return None
        payload = self._service.get_capabilities()
        return InstitutionalAnswer(
            answer=payload.answer,
            source="knowledge_pack/executive/capacidades-asistente.md",
            category="executive",
            match_type="capabilities",
        )

    def is_identity_institutional_question(self, question: str) -> bool:
        normalized = _normalize_question(question)
        return any(
            normalized == key or normalized.startswith(f"{key} ")
            for key in IDENTITY_FAQ_KEYS
        )

    def resolve_institutional_question(self, question: str) -> InstitutionalAnswer | None:
        metrics = get_enterprise_knowledge_metrics()
        if not question.strip():
            metrics.record_miss()
            return None

        if self.is_identity_institutional_question(question):
            result = self._faq_lookup(question)
            if result is not None:
                result.match_type = "identity_faq"
                metrics.record_hit()
                return result

        result = self._faq_lookup(question)
        if result is not None:
            metrics.record_hit()
            return result

        result = self._capability_lookup(question)
        if result is not None:
            metrics.record_hit()
            return result

        result = self._definition_lookup(question)
        if result is not None:
            metrics.record_hit()
            return result

        metrics.record_miss()
        return None


_matcher: InstitutionalMatcher | None = None


def get_institutional_matcher() -> InstitutionalMatcher:
    global _matcher
    if _matcher is None:
        _matcher = InstitutionalMatcher()
    return _matcher


def is_identity_institutional_question(question: str) -> bool:
    return get_institutional_matcher().is_identity_institutional_question(question)


def resolve_institutional_question(question: str) -> InstitutionalAnswer | None:
    return get_institutional_matcher().resolve_institutional_question(question)


__all__ = [
    "IDENTITY_FAQ_KEYS",
    "get_institutional_matcher",
    "is_identity_institutional_question",
    "resolve_institutional_question",
]
