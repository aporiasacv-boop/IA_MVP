from app.core.settings import settings
from app.operational_metrics.cost_engine import avoided_llm_cost_usd, provider_token_cost_usd, usd_to_mxn
from app.simulation_engine.schemas import (
    ProviderSimulationResult,
    RouteMix,
    SimulationBaseline,
    SimulationMetricsResult,
    SimulationScenarioInput,
)

PROVIDERS = ("openai", "claude", "ollama", "mock")

PROVIDER_LATENCY_FACTOR = {
    "openai": 1.0,
    "claude": 1.05,
    "ollama": 1.35,
    "mock": 0.2,
}


class SimulationForecastEngine:
    def __init__(self, baseline: SimulationBaseline) -> None:
        self._baseline = baseline

    def _token_rates(self, scenario: SimulationScenarioInput, provider: str) -> tuple[float, float]:
        if scenario.cost_per_1k_input_tokens is not None and scenario.cost_per_1k_output_tokens is not None:
            return scenario.cost_per_1k_input_tokens, scenario.cost_per_1k_output_tokens
        from app.operational_metrics.cost_engine import PROVIDER_INPUT_RATES, PROVIDER_OUTPUT_RATES

        key = provider.lower()
        return (
            PROVIDER_INPUT_RATES.get(key, settings.GPT_COST_PER_1K_INPUT_TOKENS),
            PROVIDER_OUTPUT_RATES.get(key, settings.GPT_COST_PER_1K_OUTPUT_TOKENS),
        )

    def _cost_for_provider(
        self,
        *,
        provider: str,
        llm_queries: int,
        input_tokens: int,
        output_tokens: int,
        scenario: SimulationScenarioInput,
    ) -> float:
        if provider == "mock":
            return 0.0
        in_rate, out_rate = self._token_rates(scenario, provider)
        return round(
            llm_queries * ((input_tokens / 1000.0) * in_rate + (output_tokens / 1000.0) * out_rate),
            4,
        )

    def _latency_for_provider(self, provider: str) -> float:
        historical = self._baseline.provider_latency.get(provider)
        base = historical if historical else self._baseline.avg_latency_ms
        return round(base * PROVIDER_LATENCY_FACTOR.get(provider, 1.0), 2)

    def simulate(
        self,
        scenario: SimulationScenarioInput,
        route_mix: RouteMix,
        *,
        provider: str | None = None,
    ) -> SimulationMetricsResult:
        selected_provider = (provider or scenario.llm_provider).lower()
        queries_per_day = int(scenario.users * scenario.queries_per_user_day)
        queries_per_month = int(queries_per_day * scenario.working_days)

        llm_pct = route_mix.executive_reasoning_pct + route_mix.legacy_chat_pct
        llm_queries = int(queries_per_month * (llm_pct / 100.0))
        deterministic_queries = queries_per_month - llm_queries

        input_tokens = int(self._baseline.avg_input_tokens)
        output_tokens = int(self._baseline.avg_output_tokens)
        total_tokens = llm_queries * (input_tokens + output_tokens)

        cost_usd = self._cost_for_provider(
            provider=selected_provider,
            llm_queries=llm_queries,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            scenario=scenario,
        )
        avoided_per_query = (
            self._baseline.avg_avoided_cost_usd
            if self._baseline.avg_avoided_cost_usd > 0
            else avoided_llm_cost_usd(input_tokens=input_tokens, output_tokens=output_tokens)
        )
        avoided_cost_usd = round(deterministic_queries * avoided_per_query, 4)

        knowledge_queries = int(queries_per_month * (route_mix.knowledge_service_pct / 100.0))
        pipeline_queries = int(queries_per_month * (route_mix.business_pipeline_pct / 100.0))
        memory_queries = int(queries_per_month * (route_mix.conversation_memory_pct / 100.0))

        knowledge_savings = round(knowledge_queries * avoided_per_query, 4)
        pipeline_savings = round(pipeline_queries * avoided_per_query, 4)
        memory_savings = round(memory_queries * avoided_per_query, 4)

        llm_avoidance = round(deterministic_queries / queries_per_month, 4) if queries_per_month else 0.0
        roi_pct = round((avoided_cost_usd / cost_usd) * 100, 2) if cost_usd > 0 else 0.0

        concurrency_factor = max(scenario.concurrency / max(scenario.users, 1), 0.1)
        peak_factor = scenario.peak_hours / 8.0
        cpu = round(scenario.users * 0.02 * concurrency_factor * peak_factor, 2)
        ram = round(scenario.users * 0.15 * concurrency_factor, 2)
        gpu = round(scenario.users * 0.05 * (route_mix.executive_reasoning_pct / 100.0) * peak_factor, 2)

        provider_latency = self._latency_for_provider(selected_provider)
        deterministic_latency = self._baseline.latency_p50_ms * 0.6
        weighted_latency = round(
            (deterministic_queries * deterministic_latency + llm_queries * provider_latency) / max(queries_per_month, 1),
            2,
        )

        return SimulationMetricsResult(
            queries_per_day=queries_per_day,
            queries_per_month=queries_per_month,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            cost_mxn=usd_to_mxn(cost_usd),
            avoided_cost_usd=avoided_cost_usd,
            llm_avoidance_rate=llm_avoidance,
            knowledge_savings_usd=knowledge_savings,
            pipeline_savings_usd=pipeline_savings,
            memory_savings_usd=memory_savings,
            avg_latency_ms=weighted_latency,
            latency_p50_ms=self._baseline.latency_p50_ms,
            latency_p95_ms=round(self._baseline.latency_p95_ms * peak_factor, 2),
            latency_p99_ms=round(self._baseline.latency_p99_ms * peak_factor, 2),
            estimated_cpu_cores=cpu,
            estimated_ram_gb=ram,
            estimated_gpu_gb=gpu,
            route_mix=route_mix,
            roi_pct=roi_pct,
        )

    def compare_providers(
        self,
        scenario: SimulationScenarioInput,
        route_mix: RouteMix,
    ) -> list[ProviderSimulationResult]:
        results: list[ProviderSimulationResult] = []
        costs: list[tuple[str, float]] = []
        for provider in PROVIDERS:
            metrics = self.simulate(scenario, route_mix, provider=provider)
            costs.append((provider, metrics.cost_usd))
            results.append(
                ProviderSimulationResult(
                    provider=provider,
                    cost_usd=metrics.cost_usd,
                    cost_mxn=metrics.cost_mxn,
                    avg_latency_ms=metrics.avg_latency_ms,
                    avoided_cost_usd=metrics.avoided_cost_usd,
                    roi_pct=metrics.roi_pct,
                    participation_pct=0.0,
                )
            )
        total_cost = sum(cost for _, cost in costs) or 1.0
        for item in results:
            item.participation_pct = round((item.cost_usd / total_cost) * 100, 2)
        return results
