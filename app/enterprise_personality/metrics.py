from dataclasses import dataclass


@dataclass
class PersonalityMetrics:
    total_applications: int = 0
    total_time_ms: float = 0.0

    def record(self, *, time_ms: float) -> None:
        self.total_applications += 1
        self.total_time_ms += time_ms

    @property
    def average_time_ms(self) -> float:
        if self.total_applications == 0:
            return 0.0
        return self.total_time_ms / self.total_applications

    def snapshot(self) -> dict:
        return {
            "personality_applications": self.total_applications,
            "personality_avg_time_ms": round(self.average_time_ms, 2),
        }


_metrics = PersonalityMetrics()


def record_personality(*, time_ms: float) -> None:
    _metrics.record(time_ms=time_ms)


def get_metrics() -> PersonalityMetrics:
    return _metrics


def reset_metrics() -> None:
    global _metrics
    _metrics = PersonalityMetrics()
