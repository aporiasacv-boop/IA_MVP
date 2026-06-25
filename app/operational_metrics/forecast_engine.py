from app.core.settings import settings
from app.operational_metrics.cost_engine import benchmark_cost_usd
from app.operational_metrics.schemas import FinOpsForecastResponse, ForecastScenarioItem


class ForecastEngine:
    USER_TIERS = (100, 500, 1000, 5000, 10000)

    def __init__(
        self,
        *,
        avg_tokens_per_query: float | None = None,
        avg_latency_ms: float | None = None,
        queries_per_user_day: float | None = None,
    ) -> None:
        self._avg_tokens = avg_tokens_per_query or (
            settings.FINOPS_BASELINE_INPUT_TOKENS + settings.FINOPS_BASELINE_OUTPUT_TOKENS
        )
        self._avg_latency = avg_latency_ms or 850.0
        self._queries_per_user_day = queries_per_user_day or settings.FINOPS_QUERIES_PER_USER_DAY

    def build_forecast(self) -> FinOpsForecastResponse:
        scenarios: list[ForecastScenarioItem] = []
        input_tokens = int(settings.FINOPS_BASELINE_INPUT_TOKENS)
        output_tokens = int(settings.FINOPS_BASELINE_OUTPUT_TOKENS)
        for users in self.USER_TIERS:
            queries = int(users * self._queries_per_user_day * 30)
            tokens = int(queries * self._avg_tokens)
            scenarios.append(
                ForecastScenarioItem(
                    users=users,
                    estimated_queries=queries,
                    cost_openai_usd=round(benchmark_cost_usd("openai", input_tokens, output_tokens) * queries, 2),
                    cost_claude_usd=round(benchmark_cost_usd("claude", input_tokens, output_tokens) * queries, 2),
                    cost_ollama_usd=round(benchmark_cost_usd("ollama", input_tokens, output_tokens) * queries, 2),
                    estimated_cpu_cores=round(users * 0.02, 2),
                    estimated_ram_gb=round(users * 0.15, 2),
                    estimated_gpu_gb=round(users * 0.05, 2),
                    estimated_tokens=tokens,
                    estimated_latency_ms=round(self._avg_latency, 2),
                )
            )
        return FinOpsForecastResponse(
            scenarios=scenarios,
            assumptions={
                "queries_per_user_day": str(self._queries_per_user_day),
                "avg_tokens_per_query": str(self._avg_tokens),
                "avg_latency_ms": str(self._avg_latency),
                "horizon_days": "30",
                "cpu_per_user": "0.02 cores",
                "ram_per_user": "0.15 GB",
                "gpu_per_user": "0.05 GB VRAM",
            },
        )

    @classmethod
    def from_records(cls, records) -> "ForecastEngine":
        if not records:
            return cls()
        total = len(records)
        avg_tokens = sum(r.total_tokens or r.estimated_tokens for r in records) / total
        avg_latency = sum(r.response_time_ms for r in records) / total
        users = len({r.user_id for r in records if r.user_id}) or 1
        sessions = len({r.session_id for r in records if r.session_id}) or 1
        queries_per_user_day = max(total / users, 1.0)
        return cls(
            avg_tokens_per_query=max(avg_tokens, 100.0),
            avg_latency_ms=max(avg_latency, 100.0),
            queries_per_user_day=max(queries_per_user_day / max(sessions / users, 1.0), 1.0),
        )
