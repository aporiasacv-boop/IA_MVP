from dataclasses import dataclass


@dataclass
class ExecutiveAdvisorMetricsStore:
    total_requests: int = 0
    agendas_generated: int = 0
    fallbacks_used: int = 0
    total_generation_ms: float = 0.0
    total_items: int = 0

    def record(
        self,
        *,
        generated: bool,
        fallback: bool,
        generation_ms: float,
        items: int,
    ) -> None:
        self.total_requests += 1
        self.total_generation_ms += generation_ms
        self.total_items += items
        if generated:
            self.agendas_generated += 1
        if fallback:
            self.fallbacks_used += 1

    def snapshot(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "agendas_generated": self.agendas_generated,
            "fallbacks_used": self.fallbacks_used,
            "avg_generation_ms": round(
                self.total_generation_ms / self.total_requests,
                2,
            )
            if self.total_requests
            else 0.0,
            "avg_items": round(self.total_items / self.total_requests, 2)
            if self.total_requests
            else 0.0,
        }


_STORE = ExecutiveAdvisorMetricsStore()


def record_advisor_metrics(
    *,
    generated: bool,
    fallback: bool,
    generation_ms: float,
    items: int,
) -> None:
    _STORE.record(
        generated=generated,
        fallback=fallback,
        generation_ms=generation_ms,
        items=items,
    )


def advisor_metrics_snapshot() -> dict:
    return _STORE.snapshot()


def reset_advisor_metrics_for_tests() -> None:
    global _STORE
    _STORE = ExecutiveAdvisorMetricsStore()
