from statistics import median

from app.core.settings import settings
from app.operational_metrics.aggregator import OperationalMetricsAggregator
from app.operational_metrics.cost_engine import (
    KNOWLEDGE_ROUTES,
    LLM_ROUTES,
    is_knowledge_route,
    is_pipeline_route,
)
from app.operational_metrics.service import get_operational_metrics_service
from app.simulation_engine.schemas import RouteMix, SimulationBaseline


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((pct / 100.0) * (len(ordered) - 1)))))
    return round(ordered[index], 2)


def _map_route(handled_by: str) -> str:
    if handled_by == "business_pipeline":
        return "pipeline"
    if handled_by in KNOWLEDGE_ROUTES or handled_by == "business_knowledge":
        return "knowledge"
    if handled_by == "conversation_memory":
        return "memory"
    if handled_by == "executive_reasoning":
        return "executive"
    if handled_by == "legacy_chat":
        return "legacy"
    return "other"


class SimulationBaselineRepository:
    """Carga línea base exclusivamente desde Operational Metrics / FinOps."""

    def load_baseline(self) -> SimulationBaseline:
        service = get_operational_metrics_service()
        records = service._repository.list_records()
        if not records:
            return SimulationBaseline(
                source="settings_defaults",
                avg_input_tokens=settings.FINOPS_BASELINE_INPUT_TOKENS,
                avg_output_tokens=settings.FINOPS_BASELINE_OUTPUT_TOKENS,
                avg_latency_ms=850.0,
                latency_p50_ms=850.0,
                latency_p95_ms=1200.0,
                latency_p99_ms=1800.0,
                route_mix=RouteMix(
                    business_pipeline_pct=40.0,
                    knowledge_service_pct=25.0,
                    conversation_memory_pct=10.0,
                    executive_reasoning_pct=5.0,
                    legacy_chat_pct=10.0,
                    other_pct=10.0,
                ),
            )

        aggregator = OperationalMetricsAggregator(records)
        overview = aggregator.overview()
        providers = aggregator.providers()
        total = len(records)
        route_counts = {"pipeline": 0, "knowledge": 0, "memory": 0, "executive": 0, "legacy": 0, "other": 0}
        latencies = [r.response_time_ms for r in records]
        llm_records = [r for r in records if r.llm_used]
        avg_in = sum(r.input_tokens for r in llm_records) / len(llm_records) if llm_records else settings.FINOPS_BASELINE_INPUT_TOKENS
        avg_out = sum(r.output_tokens for r in llm_records) / len(llm_records) if llm_records else settings.FINOPS_BASELINE_OUTPUT_TOKENS
        for record in records:
            route_counts[_map_route(record.handled_by)] += 1

        def pct(count: int) -> float:
            return round((count / total) * 100, 2) if total else 0.0

        provider_latency = {
            item.provider: item.average_latency_ms for item in providers.providers if item.requests > 0
        }
        provider_cost_share = {
            item.provider: item.participation_pct for item in providers.providers if item.requests > 0
        }
        memory_count = sum(1 for r in records if r.handled_by == "conversation_memory")

        return SimulationBaseline(
            source="operational_metrics",
            total_historical_queries=total,
            route_mix=RouteMix(
                business_pipeline_pct=pct(route_counts["pipeline"]),
                knowledge_service_pct=pct(route_counts["knowledge"]),
                conversation_memory_pct=pct(route_counts["memory"]),
                executive_reasoning_pct=pct(route_counts["executive"]),
                legacy_chat_pct=pct(route_counts["legacy"]),
                other_pct=pct(route_counts["other"]),
            ),
            avg_input_tokens=round(avg_in, 2),
            avg_output_tokens=round(avg_out, 2),
            avg_latency_ms=round(sum(latencies) / total, 2),
            latency_p50_ms=_percentile(latencies, 50),
            latency_p95_ms=_percentile(latencies, 95),
            latency_p99_ms=_percentile(latencies, 99),
            avg_avoided_cost_usd=round(overview.total_avoided_cost_usd / total, 6) if total else 0.0,
            llm_avoidance_rate=overview.llm_avoidance_rate,
            knowledge_avoidance_rate=overview.knowledge_avoidance_rate,
            pipeline_avoidance_rate=overview.pipeline_avoidance_rate,
            memory_avoidance_rate=round(memory_count / total, 4) if total else 0.0,
            provider_latency=provider_latency,
            provider_cost_share=provider_cost_share,
        )
