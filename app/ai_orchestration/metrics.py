from datetime import datetime, timezone


class LLMOrchestrationMetrics:
    llm_requests: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    estimated_cost: float = 0.0
    total_latency: float = 0.0
    hallucination_guard_triggered: int = 0
    llm_fallbacks: int = 0

    provider_distribution: dict[str, int] = {}
    provider_tokens_input: dict[str, int] = {}
    provider_tokens_output: dict[str, int] = {}
    provider_cost: dict[str, float] = {}
    provider_latency: dict[str, float] = {}
    provider_requests: dict[str, int] = {}

    daily_cost: dict[str, float] = {}
    monthly_cost: float = 0.0
    user_cost: dict[str, float] = {}
    query_costs: list[float] = []

    provider_down_events: list[dict] = []
    timeout_events: list[dict] = []
    empty_response_events: list[dict] = []
    no_evidence_events: list[dict] = []
    negative_cost_events: list[dict] = []
    unknown_model_events: list[dict] = []

    @classmethod
    def record_request(
        cls,
        *,
        provider: str,
        model: str,
        tokens_input: int,
        tokens_output: int,
        estimated_cost: float,
        response_time: float,
        hallucination_guard: bool,
        user_id: str | None = None,
    ) -> None:
        cls.llm_requests += 1
        cls.tokens_input += tokens_input
        cls.tokens_output += tokens_output
        cls.estimated_cost = round(cls.estimated_cost + estimated_cost, 6)
        cls.total_latency += response_time
        cls.monthly_cost = round(cls.monthly_cost + estimated_cost, 6)
        cls.query_costs.append(estimated_cost)
        if len(cls.query_costs) > 10000:
            cls.query_costs = cls.query_costs[-10000:]

        if hallucination_guard:
            cls.hallucination_guard_triggered += 1

        cls.provider_distribution[provider] = cls.provider_distribution.get(provider, 0) + 1
        cls.provider_tokens_input[provider] = cls.provider_tokens_input.get(provider, 0) + tokens_input
        cls.provider_tokens_output[provider] = cls.provider_tokens_output.get(provider, 0) + tokens_output
        cls.provider_cost[provider] = round(cls.provider_cost.get(provider, 0.0) + estimated_cost, 6)
        cls.provider_latency[provider] = round(
            cls.provider_latency.get(provider, 0.0) + response_time, 4
        )
        cls.provider_requests[provider] = cls.provider_requests.get(provider, 0) + 1

        day_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        cls.daily_cost[day_key] = round(cls.daily_cost.get(day_key, 0.0) + estimated_cost, 6)

        if user_id:
            cls.user_cost[user_id] = round(cls.user_cost.get(user_id, 0.0) + estimated_cost, 6)

        if estimated_cost < 0:
            cls.negative_cost_events.append({"provider": provider, "cost": estimated_cost})

    @classmethod
    def record_fallback(cls, *, from_provider: str, to_provider: str) -> None:
        cls.llm_fallbacks += 1
        cls.provider_down_events.append(
            {"from_provider": from_provider, "to_provider": to_provider}
        )

    @classmethod
    def record_timeout(cls, provider: str) -> None:
        cls.timeout_events.append({"provider": provider})

    @classmethod
    def record_empty_response(cls, provider: str) -> None:
        cls.empty_response_events.append({"provider": provider})

    @classmethod
    def record_no_evidence(cls, package_id: str) -> None:
        cls.no_evidence_events.append({"package_id": package_id})

    @classmethod
    def record_unknown_model(cls, model: str) -> None:
        cls.unknown_model_events.append({"model": model})

    @classmethod
    def average_latency(cls) -> float:
        if cls.llm_requests <= 0:
            return 0.0
        return round(cls.total_latency / cls.llm_requests, 4)

    @classmethod
    def average_cost_per_question(cls) -> float:
        if cls.llm_requests <= 0:
            return 0.0
        return round(cls.estimated_cost / cls.llm_requests, 6)

    @classmethod
    def cost_per_query(cls) -> float:
        if not cls.query_costs:
            return 0.0
        return round(sum(cls.query_costs) / len(cls.query_costs), 6)

    @classmethod
    def snapshot(cls) -> dict:
        return {
            "llm_requests": cls.llm_requests,
            "provider_distribution": dict(cls.provider_distribution),
            "tokens_input": cls.tokens_input,
            "tokens_output": cls.tokens_output,
            "estimated_cost": round(cls.estimated_cost, 6),
            "average_latency": cls.average_latency(),
            "average_cost_per_question": cls.average_cost_per_question(),
            "hallucination_guard_triggered": cls.hallucination_guard_triggered,
            "llm_fallbacks": cls.llm_fallbacks,
        }

    @classmethod
    def cost_snapshot(cls) -> dict:
        cost_by_provider = []
        for provider, count in cls.provider_distribution.items():
            requests = cls.provider_requests.get(provider, count)
            avg_lat = 0.0
            if requests > 0:
                avg_lat = round(cls.provider_latency.get(provider, 0.0) / requests, 4)
            cost_by_provider.append(
                {
                    "provider": provider,
                    "requests": requests,
                    "tokens_input": cls.provider_tokens_input.get(provider, 0),
                    "tokens_output": cls.provider_tokens_output.get(provider, 0),
                    "estimated_cost": cls.provider_cost.get(provider, 0.0),
                    "average_latency": avg_lat,
                }
            )
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return {
            **cls.snapshot(),
            "cost_by_provider": cost_by_provider,
            "daily_cost": cls.daily_cost.get(today, 0.0),
            "monthly_cost": round(cls.monthly_cost, 6),
            "cost_per_user": dict(cls.user_cost),
            "cost_per_query": cls.cost_per_query(),
            "provider_comparison": cost_by_provider,
        }

    @classmethod
    def health_issues(cls) -> dict:
        return {
            "provider_down": cls.provider_down_events[-100:],
            "timeout": cls.timeout_events[-100:],
            "empty_response": cls.empty_response_events[-100:],
            "no_evidence": cls.no_evidence_events[-100:],
            "negative_cost": cls.negative_cost_events[-100:],
            "unknown_model": cls.unknown_model_events[-100:],
        }

    @classmethod
    def reset_for_tests(cls) -> None:
        cls.llm_requests = 0
        cls.tokens_input = 0
        cls.tokens_output = 0
        cls.estimated_cost = 0.0
        cls.total_latency = 0.0
        cls.hallucination_guard_triggered = 0
        cls.llm_fallbacks = 0
        cls.provider_distribution = {}
        cls.provider_tokens_input = {}
        cls.provider_tokens_output = {}
        cls.provider_cost = {}
        cls.provider_latency = {}
        cls.provider_requests = {}
        cls.daily_cost = {}
        cls.monthly_cost = 0.0
        cls.user_cost = {}
        cls.query_costs = []
        cls.provider_down_events = []
        cls.timeout_events = []
        cls.empty_response_events = []
        cls.no_evidence_events = []
        cls.negative_cost_events = []
        cls.unknown_model_events = []
