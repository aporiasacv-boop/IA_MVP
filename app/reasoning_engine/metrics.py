from dataclasses import dataclass


@dataclass
class ReasoningEngineMetrics:
    total_observations: int = 0
    route_matches: int = 0

    def record(self, *, route_match: bool) -> None:
        self.total_observations += 1
        if route_match:
            self.route_matches += 1

    @property
    def match_rate(self) -> float:
        if self.total_observations == 0:
            return 0.0
        return self.route_matches / self.total_observations

    def snapshot(self) -> dict:
        return {
            "reasoning_observations": self.total_observations,
            "reasoning_route_matches": self.route_matches,
            "reasoning_match_rate": round(self.match_rate, 4),
            **get_governance_metrics().snapshot(),
        }


@dataclass
class GovernanceMetrics:
    total_evaluations: int = 0
    governed_applied: int = 0
    pipeline_skipped: int = 0
    governance_fallbacks: int = 0
    total_governance_time_ms: float = 0.0

    def record_evaluation(
        self,
        *,
        governed: bool,
        pipeline_skipped: bool,
        rule: str,
        time_ms: float,
    ) -> None:
        self.total_evaluations += 1
        self.total_governance_time_ms += time_ms
        if governed:
            self.governed_applied += 1
        if pipeline_skipped:
            self.pipeline_skipped += 1
        if rule == "fallback":
            self.governance_fallbacks += 1

    @property
    def average_governance_time_ms(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        return self.total_governance_time_ms / self.total_evaluations

    @property
    def governance_rate(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        return self.governed_applied / self.total_evaluations

    def snapshot(self) -> dict:
        return {
            "governance_evaluations": self.total_evaluations,
            "governance_applied": self.governed_applied,
            "governance_pipeline_skipped": self.pipeline_skipped,
            "governance_fallbacks": self.governance_fallbacks,
            "governance_rate": round(self.governance_rate, 4),
            "governance_avg_time_ms": round(self.average_governance_time_ms, 2),
        }


_metrics = ReasoningEngineMetrics()
_governance_metrics = GovernanceMetrics()


def record_observation(*, route_match: bool) -> None:
    _metrics.record(route_match=route_match)


def record_governance(
    *,
    governed: bool,
    pipeline_skipped: bool,
    rule: str,
    time_ms: float,
) -> None:
    _governance_metrics.record_evaluation(
        governed=governed,
        pipeline_skipped=pipeline_skipped,
        rule=rule,
        time_ms=time_ms,
    )


def get_metrics() -> ReasoningEngineMetrics:
    return _metrics


def get_governance_metrics() -> GovernanceMetrics:
    return _governance_metrics


def reset_metrics() -> None:
    global _metrics, _governance_metrics
    _metrics = ReasoningEngineMetrics()
    _governance_metrics = GovernanceMetrics()
