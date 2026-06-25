from dataclasses import dataclass, field


@dataclass
class EnterpriseDecisionMetrics:
    decision_requests: int = 0
    recommendation_types: dict[str, int] = field(default_factory=dict)
    confidence_total: float = 0.0
    financial_impact_total: float = 0.0
    decision_sources: set[str] = field(default_factory=set)

    def record(
        self,
        *,
        decision_type: str,
        confidence: float,
        financial_impact: float,
        sources: list[str],
    ) -> None:
        self.decision_requests += 1
        self.recommendation_types[decision_type] = self.recommendation_types.get(decision_type, 0) + 1
        self.confidence_total += confidence
        self.financial_impact_total += financial_impact
        self.decision_sources.update(sources)

    @property
    def average_confidence(self) -> float:
        if self.decision_requests <= 0:
            return 0.0
        return round(self.confidence_total / self.decision_requests, 4)

    @property
    def average_financial_impact(self) -> float:
        if self.decision_requests <= 0:
            return 0.0
        return round(self.financial_impact_total / self.decision_requests, 4)

    def snapshot(self) -> dict:
        return {
            "decision_requests": self.decision_requests,
            "recommendation_types": dict(self.recommendation_types),
            "average_confidence": self.average_confidence,
            "average_financial_impact": self.average_financial_impact,
            "decision_sources": sorted(self.decision_sources),
        }


_metrics: EnterpriseDecisionMetrics | None = None


def get_enterprise_decision_metrics() -> EnterpriseDecisionMetrics:
    global _metrics
    if _metrics is None:
        _metrics = EnterpriseDecisionMetrics()
    return _metrics


def reset_enterprise_decision_metrics() -> None:
    global _metrics
    _metrics = None
