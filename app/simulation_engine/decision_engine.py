from app.simulation_engine.forecast_engine import PROVIDERS
from app.simulation_engine.schemas import (
    ProviderSimulationResult,
    SimulationBaseline,
    SimulationComparisonResponse,
    SimulationMetricsResult,
    SimulationRecommendation,
    SimulationRecommendationsResponse,
    SimulationScenarioInput,
)


class DecisionEngine:
    def __init__(self, baseline: SimulationBaseline) -> None:
        self._baseline = baseline

    def build_comparison(
        self,
        scenario_name: str,
        providers: list[ProviderSimulationResult],
    ) -> SimulationComparisonResponse:
        cheapest = min(providers, key=lambda item: item.cost_usd)
        fastest = min(providers, key=lambda item: item.avg_latency_ms)
        best_roi = max(providers, key=lambda item: item.roi_pct)
        return SimulationComparisonResponse(
            scenario_name=scenario_name,
            providers=providers,
            cheapest_provider=cheapest.provider,
            fastest_provider=fastest.provider,
            best_roi_provider=best_roi.provider,
        )

    def build_recommendations(
        self,
        *,
        scenario: SimulationScenarioInput,
        metrics: SimulationMetricsResult,
        providers: list[ProviderSimulationResult],
    ) -> SimulationRecommendationsResponse:
        comparison = self.build_comparison(scenario.name, providers)
        recommendations: list[SimulationRecommendation] = []

        recommendations.append(
            SimulationRecommendation(
                category="costo",
                title="Proveedor más económico",
                detail=f"{comparison.cheapest_provider.capitalize()} presenta el menor costo mensual proyectado.",
                metric_value=f"${min(p.cost_usd for p in providers):.4f}",
            )
        )
        recommendations.append(
            SimulationRecommendation(
                category="rendimiento",
                title="Proveedor más rápido",
                detail=f"{comparison.fastest_provider.capitalize()} ofrece la menor latencia promedio simulada.",
                metric_value=f"{min(p.avg_latency_ms for p in providers):.1f} ms",
            )
        )

        savings_channels = [
            ("Business Pipeline", metrics.pipeline_savings_usd),
            ("Enterprise Knowledge Service", metrics.knowledge_savings_usd),
            ("Conversation Memory", metrics.memory_savings_usd),
        ]
        best_channel = max(savings_channels, key=lambda item: item[1])
        recommendations.append(
            SimulationRecommendation(
                category="ahorro",
                title="Canal con mayor ahorro",
                detail=f"{best_channel[0]} concentra el mayor ahorro operativo simulado.",
                metric_value=f"${best_channel[1]:.4f}",
            )
        )

        most_used = max(
            [
                ("Business Pipeline", scenario.business_pipeline_pct or metrics.route_mix.business_pipeline_pct),
                ("Knowledge Service", scenario.knowledge_service_pct or metrics.route_mix.knowledge_service_pct),
                ("Conversation Memory", scenario.conversation_memory_pct or metrics.route_mix.conversation_memory_pct),
                ("Executive Reasoning", scenario.executive_reasoning_pct or metrics.route_mix.executive_reasoning_pct),
                ("Legacy Chat", scenario.legacy_chat_pct or metrics.route_mix.legacy_chat_pct),
            ],
            key=lambda item: item[1],
        )
        recommendations.append(
            SimulationRecommendation(
                category="adopcion",
                title="Canal más utilizado",
                detail=f"{most_used[0]} representa el mayor porcentaje del mix simulado.",
                metric_value=f"{most_used[1]:.1f}%",
            )
        )
        recommendations.append(
            SimulationRecommendation(
                category="finanzas",
                title="Costo evitado",
                detail="Ahorro acumulado por resolución determinística sin LLM.",
                metric_value=f"${metrics.avoided_cost_usd:.4f}",
            )
        )
        recommendations.append(
            SimulationRecommendation(
                category="infraestructura",
                title="Infraestructura recomendada",
                detail=(
                    f"CPU {metrics.estimated_cpu_cores} núcleos, "
                    f"RAM {metrics.estimated_ram_gb} GB, GPU {metrics.estimated_gpu_gb} GB."
                ),
                metric_value=f"Concurrencia {scenario.concurrency}",
            )
        )

        risks: list[str] = []
        if metrics.route_mix.legacy_chat_pct > 15:
            risks.append("Alta dependencia de Legacy Chat incrementa costo LLM.")
        if metrics.route_mix.executive_reasoning_pct > 20:
            risks.append("Executive Reasoning elevado puede aumentar latencia y GPU.")
        if self._baseline.total_historical_queries < 50:
            risks.append("Histórico limitado: la simulación usa supuestos parciales.")
        if scenario.concurrency > scenario.users:
            risks.append("Concurrencia superior a usuarios puede generar contención operativa.")
        recommendations.append(
            SimulationRecommendation(
                category="riesgo",
                title="Riesgos operativos",
                detail=" ".join(risks) if risks else "Sin riesgos críticos detectados en la simulación.",
                metric_value=f"LLM avoidance {(metrics.llm_avoidance_rate * 100):.1f}%",
            )
        )

        return SimulationRecommendationsResponse(
            recommendations=recommendations,
            based_on_queries=self._baseline.total_historical_queries,
            baseline_source=self._baseline.source,
        )
