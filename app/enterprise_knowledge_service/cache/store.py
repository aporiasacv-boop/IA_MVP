import time
from dataclasses import dataclass, field

from app.enterprise_knowledge_service.metrics import get_enterprise_knowledge_metrics
from app.enterprise_knowledge_service.providers.knowledge_pack import (
    CAPABILITIES_DOC_ID,
    KnowledgePackProvider,
    parse_list_section,
)
from app.enterprise_knowledge_service.schemas import KnowledgeDocument
from app.utils.text_normalizer import normalize_for_matching


@dataclass
class KnowledgeCacheSnapshot:
    signature: float = 0.0
    documents: tuple[KnowledgeDocument, ...] = field(default_factory=tuple)
    faq_answers: dict[str, str] = field(default_factory=dict)
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    examples: tuple[str, ...] = field(default_factory=tuple)
    intro_line: str = "Puedo ayudarte con información sobre:"
    examples_line: str = "Por ejemplo:"
    provider_distribution: dict[str, int] = field(default_factory=dict)


class KnowledgeCacheStore:
    """Cache centralizada compartida por todos los consumidores del EKS."""

    def __init__(self) -> None:
        self._snapshot = KnowledgeCacheSnapshot()
        self._pack_provider = KnowledgePackProvider()

    @property
    def snapshot(self) -> KnowledgeCacheSnapshot:
        return self._snapshot

    def ensure_loaded(self) -> KnowledgeCacheSnapshot:
        metrics = get_enterprise_knowledge_metrics()
        signature = self._pack_provider.pack_signature()
        if signature == self._snapshot.signature and self._snapshot.documents:
            metrics.record_cache_hit()
            return self._snapshot

        started = time.perf_counter()
        documents = self._pack_provider.load_documents()
        docs_tuple = tuple(documents)
        faq_answers = self._build_faq_index(docs_tuple)
        caps, examples, intro, examples_line = self._load_capabilities(docs_tuple)
        distribution: dict[str, int] = {}
        for doc in docs_tuple:
            key = doc.provider
            distribution[key] = distribution.get(key, 0) + 1

        self._snapshot = KnowledgeCacheSnapshot(
            signature=signature,
            documents=docs_tuple,
            faq_answers=faq_answers,
            capabilities=caps,
            examples=examples,
            intro_line=intro,
            examples_line=examples_line,
            provider_distribution=distribution,
        )
        metrics.record_reload((time.perf_counter() - started) * 1000)
        metrics.set_cache_size(len(docs_tuple))
        return self._snapshot

    def invalidate(self) -> None:
        self._snapshot = KnowledgeCacheSnapshot()
        self.ensure_loaded()

    @staticmethod
    def _build_faq_index(documents: tuple[KnowledgeDocument, ...]) -> dict[str, str]:
        answers: dict[str, str] = {}
        for doc in documents:
            if doc.category != "faq":
                continue
            for question, answer in doc.sections.items():
                answers[normalize_for_matching(question)] = answer.strip()
        return answers

    @staticmethod
    def _load_capabilities(
        documents: tuple[KnowledgeDocument, ...],
    ) -> tuple[tuple[str, ...], tuple[str, ...], str, str]:
        for doc in documents:
            if doc.id != CAPABILITIES_DOC_ID:
                continue
            caps = parse_list_section(doc.sections.get("Capacidades", ""))
            examples = parse_list_section(doc.sections.get("Ejemplos", ""))
            intro = doc.sections.get("Introducción", "Puedo ayudarte con información sobre:").strip()
            examples_line = doc.sections.get("Cierre de ejemplos", "Por ejemplo:").strip()
            return caps, examples, intro, examples_line
        return (), (), "Puedo ayudarte con información sobre:", "Por ejemplo:"


_cache_store: KnowledgeCacheStore | None = None


def get_knowledge_cache_store() -> KnowledgeCacheStore:
    global _cache_store
    if _cache_store is None:
        _cache_store = KnowledgeCacheStore()
    return _cache_store


def reset_knowledge_cache_store() -> None:
    global _cache_store
    _cache_store = None
