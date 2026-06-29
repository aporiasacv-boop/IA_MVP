from dataclasses import dataclass, field


@dataclass
class ExecutiveInsightMetricsStore:
    total_requests: int = 0
    insights_generated: int = 0
    fallbacks_used: int = 0
    total_generation_ms: float = 0.0

    def record(self, *, generated: bool, fallback: bool, generation_ms: float) -> None:
        self.total_requests += 1
        self.total_generation_ms += generation_ms
        if generated:
            self.insights_generated += 1
        if fallback:
            self.fallbacks_used += 1

    def snapshot(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "insights_generated": self.insights_generated,
            "fallbacks_used": self.fallbacks_used,
            "avg_generation_ms": round(
                self.total_generation_ms / self.total_requests,
                2,
            )
            if self.total_requests
            else 0.0,
        }


_STORE = ExecutiveInsightMetricsStore()


def record_insight_metrics(*, generated: bool, fallback: bool, generation_ms: float) -> None:
    _STORE.record(generated=generated, fallback=fallback, generation_ms=generation_ms)


def insight_metrics_snapshot() -> dict:
    return _STORE.snapshot()


def reset_insight_metrics_for_tests() -> None:
    global _STORE
    _STORE = ExecutiveInsightMetricsStore()
