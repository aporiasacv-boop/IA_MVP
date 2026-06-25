import time

from app.enterprise_knowledge_service.metrics import get_enterprise_knowledge_metrics
from app.enterprise_knowledge_service.repository.repository import KnowledgeRepository
from app.enterprise_knowledge_service.schemas import KnowledgeDocument, KnowledgeSearchResult
from app.utils.text_normalizer import normalize_for_matching


class KnowledgeSearchEngine:
    def __init__(self, repository: KnowledgeRepository | None = None) -> None:
        self._repository = repository or KnowledgeRepository()

    def search(self, query: str, limit: int = 20) -> KnowledgeSearchResult:
        metrics = get_enterprise_knowledge_metrics()
        metrics.record_request()
        started = time.perf_counter()
        normalized = normalize_for_matching(query)
        scored: list[tuple[int, KnowledgeDocument]] = []
        if normalized:
            for doc in self._repository.all_documents():
                haystack = normalize_for_matching(f"{doc.title}\n{doc.content}")
                if normalized in haystack:
                    scored.append((haystack.count(normalized), doc))
            scored.sort(key=lambda pair: (-pair[0], pair[1].title))
            items = [doc for _, doc in scored[:limit]]
        else:
            items = []
        elapsed = (time.perf_counter() - started) * 1000
        metrics.record_search(elapsed)
        if items:
            metrics.record_hit()
        else:
            metrics.record_miss()
        return KnowledgeSearchResult(
            query=query,
            total=len(items),
            items=items,
            average_search_time_ms=elapsed,
        )
