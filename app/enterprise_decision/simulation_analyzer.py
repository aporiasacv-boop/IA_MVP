from app.enterprise_decision.repository import DecisionContext
from app.enterprise_decision.schemas import RecommendationItem


class SimulationAnalyzer:
    def findings(self, context: DecisionContext) -> list[str]:
        findings: list[str] = []
        if context.simulation_comparison:
            findings.append(
                f"Proveedor más económico simulado: {context.simulation_comparison.get('cheapest_provider', 'N/D')}."
            )
            findings.append(
                f"Proveedor más rápido simulado: {context.simulation_comparison.get('fastest_provider', 'N/D')}."
            )
        if context.simulation_run:
            metrics = context.simulation_run.get("metrics", {})
            findings.append(
                f"Escenario {context.simulation_run.get('scenario_name')} proyecta "
                f"{metrics.get('queries_per_month', 0)} consultas/mes."
            )
            findings.append(
                f"Ahorro LLM simulado: {(metrics.get('llm_avoidance_rate', 0) * 100):.1f}%."
            )
        for rec in context.simulation_recommendations[:3]:
            findings.append(f"{rec.get('title')}: {rec.get('detail')}")
        return findings

    def infrastructure_recommendation(self, context: DecisionContext, evidence_ids: list[str]) -> RecommendationItem:
        metrics = context.simulation_run.get("metrics", {}) if context.simulation_run else {}
        cpu = metrics.get("estimated_cpu_cores", 0)
        ram = metrics.get("estimated_ram_gb", 0)
        gpu = metrics.get("estimated_gpu_gb", 0)
        return RecommendationItem(
            title="Infraestructura recomendada",
            detail=f"CPU {cpu} núcleos, RAM {ram} GB, GPU {gpu} GB según simulación operativa.",
            decision_type="infraestructura",
            evidence_ids=evidence_ids,
            confidence=0.8 if context.simulation_run else 0.5,
        )

    def provider_recommendation(self, context: DecisionContext, evidence_ids: list[str]) -> RecommendationItem:
        provider = context.simulation_comparison.get("cheapest_provider", "ollama")
        linked = evidence_ids[:3] if evidence_ids else []
        return RecommendationItem(
            title="Proveedor IA recomendado",
            detail=f"Según comparativa FinOps/Simulación, {provider} ofrece el menor costo proyectado.",
            decision_type="proveedor_ia",
            evidence_ids=linked,
            confidence=0.85 if context.operational_queries > 0 else 0.6,
        )

    def scenario_recommendation(self, context: DecisionContext, evidence_ids: list[str]) -> RecommendationItem:
        name = context.simulation_run.get("scenario_name", "Piloto") if context.simulation_run else "Piloto"
        return RecommendationItem(
            title="Escenario recomendado",
            detail=f"El escenario {name} equilibra costo, ahorro y latencia según histórico operativo.",
            decision_type="escenario",
            evidence_ids=evidence_ids,
            confidence=0.82,
        )
