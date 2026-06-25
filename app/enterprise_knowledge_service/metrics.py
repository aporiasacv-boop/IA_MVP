from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class EnterpriseKnowledgeMetrics:
    knowledge_requests: int = 0
    hits: int = 0
    misses: int = 0
    cache_hits: int = 0
    reload_time_ms: float = 0.0
    last_refresh: datetime | None = None
    cache_size: int = 0
    search_time_total_ms: float = 0.0
    search_count: int = 0
    provider_distribution: dict[str, int] = field(default_factory=dict)

    def record_request(self) -> None:
        self.knowledge_requests += 1

    def record_hit(self) -> None:
        self.hits += 1

    def record_miss(self) -> None:
        self.misses += 1

    def record_cache_hit(self) -> None:
        self.cache_hits += 1

    def record_reload(self, elapsed_ms: float) -> None:
        self.reload_time_ms = round(elapsed_ms, 2)
        self.last_refresh = datetime.now(timezone.utc)

    def record_search(self, elapsed_ms: float) -> None:
        self.search_time_total_ms += elapsed_ms
        self.search_count += 1

    def set_cache_size(self, size: int) -> None:
        self.cache_size = size

    def set_provider_distribution(self, distribution: dict[str, int]) -> None:
        self.provider_distribution = dict(distribution)

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + max(self.knowledge_requests, 1)
        return round(self.cache_hits / total, 4)

    @property
    def average_search_time_ms(self) -> float:
        if self.search_count == 0:
            return 0.0
        return round(self.search_time_total_ms / self.search_count, 2)

    def snapshot(self) -> dict:
        return {
            "knowledge_requests": self.knowledge_requests,
            "knowledge_runtime_hits": self.hits,
            "knowledge_runtime_misses": self.misses,
            "knowledge_runtime_cache_hits": self.cache_hits,
            "knowledge_runtime_reload_time": self.reload_time_ms,
            "knowledge_runtime_last_refresh": self.last_refresh,
            "provider_distribution": self.provider_distribution,
            "cache_hit_rate": self.cache_hit_rate,
            "cache_size": self.cache_size,
            "average_search_time_ms": self.average_search_time_ms,
            "knowledge_sources": list(self.provider_distribution.keys()),
        }


_metrics = EnterpriseKnowledgeMetrics()


def get_enterprise_knowledge_metrics() -> EnterpriseKnowledgeMetrics:
    return _metrics


def reset_enterprise_knowledge_metrics() -> None:
    global _metrics
    _metrics = EnterpriseKnowledgeMetrics()
