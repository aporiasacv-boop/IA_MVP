from collections import Counter
from dataclasses import dataclass, field

from app.guided_fallback.v2.domains import BusinessDomain


@dataclass
class GuidedFallbackV2MetricsState:
    domain_fallback_hits: int = 0
    domain_fallback_misses: int = 0
    last_domain_detected: str | None = None
    domain_counts: Counter[str] = field(default_factory=Counter)


v2_metrics = GuidedFallbackV2MetricsState()


class GuidedFallbackV2Metrics:
    @staticmethod
    def record_hit(domain: BusinessDomain) -> None:
        v2_metrics.domain_fallback_hits += 1
        v2_metrics.last_domain_detected = domain.value
        v2_metrics.domain_counts[domain.value] += 1

    @staticmethod
    def record_miss() -> None:
        v2_metrics.domain_fallback_misses += 1

    @staticmethod
    def get_top_domains(*, limit: int = 7) -> list[dict[str, int | str]]:
        return [
            {"domain": domain, "count": count}
            for domain, count in v2_metrics.domain_counts.most_common(limit)
        ]

    @staticmethod
    def snapshot() -> dict:
        return {
            "domain_detected": v2_metrics.last_domain_detected,
            "domain_fallback_hits": v2_metrics.domain_fallback_hits,
            "domain_fallback_misses": v2_metrics.domain_fallback_misses,
            "top_domains": GuidedFallbackV2Metrics.get_top_domains(),
        }

    @staticmethod
    def reset() -> None:
        v2_metrics.domain_fallback_hits = 0
        v2_metrics.domain_fallback_misses = 0
        v2_metrics.last_domain_detected = None
        v2_metrics.domain_counts.clear()
