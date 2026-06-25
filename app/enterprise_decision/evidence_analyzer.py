import uuid

from app.enterprise_decision.repository import DecisionContext
from app.enterprise_decision.schemas import EvidenceItem


class EvidenceAnalyzer:
    def analyze(self, context: DecisionContext) -> list[EvidenceItem]:
        items: list[EvidenceItem] = []
        counter = 0

        def add(source: str, category: str, metric: str, value: str, confidence: float, rule: str) -> None:
            nonlocal counter
            counter += 1
            items.append(
                EvidenceItem(
                    evidence_id=f"ev-{counter:03d}",
                    source=source,
                    category=category,
                    metric=metric,
                    value=value,
                    confidence=confidence,
                    rule=rule,
                )
            )

        if context.eks_documents > 0:
            add(
                "enterprise_knowledge_service",
                "conocimiento",
                "documentos_cargados",
                str(context.eks_documents),
                1.0,
                "eks_document_count",
            )
        if context.eko_objects > 0:
            add(
                "eko",
                "objetos",
                "objetos_conocimiento",
                str(context.eko_objects),
                min(context.eko_confidence, 1.0),
                "eko_statistics",
            )
            add(
                "eko",
                "calidad",
                "completitud_promedio",
                f"{context.eko_completeness:.2f}",
                min(context.eko_completeness, 1.0),
                "eko_completeness",
            )
        if context.ero_objects > 0:
            add(
                "ero",
                "razonamiento",
                "objetos_razonamiento",
                str(context.ero_objects),
                min(context.ero_confidence, 1.0),
                "ero_statistics",
            )
        if context.eep_packages > 0:
            add(
                "eep",
                "evidencia",
                "paquetes_evidencia",
                str(context.eep_packages),
                min(context.eep_confidence, 1.0),
                "eep_statistics",
            )
        if context.operational_queries > 0:
            overview = context.finops_overview
            add(
                "operational_metrics",
                "operacion",
                "consultas_registradas",
                str(context.operational_queries),
                1.0,
                "operational_query_count",
            )
            add(
                "finops",
                "ahorro",
                "llm_avoidance_rate",
                f"{overview.get('llm_avoidance_rate', 0):.4f}",
                0.95,
                "finops_llm_avoidance",
            )
            add(
                "finops",
                "costo",
                "costo_acumulado_usd",
                f"{overview.get('total_cost_usd', 0):.4f}",
                0.9 if overview.get("real_cost_share", 0) > 0 else 0.7,
                "finops_total_cost",
            )
        if context.simulation_comparison:
            comp = context.simulation_comparison
            add(
                "simulation_engine",
                "proveedor",
                "proveedor_mas_economico",
                comp.get("cheapest_provider", ""),
                0.85,
                "simulation_provider_comparison",
            )
            add(
                "simulation_engine",
                "proveedor",
                "proveedor_mas_rapido",
                comp.get("fastest_provider", ""),
                0.85,
                "simulation_latency_comparison",
            )
        if context.simulation_run:
            metrics = context.simulation_run.get("metrics", {})
            add(
                "simulation_engine",
                "escenario",
                "costo_mensual_proyectado_usd",
                f"{metrics.get('cost_usd', 0):.4f}",
                0.8,
                "simulation_forecast_cost",
            )
            add(
                "simulation_engine",
                "escenario",
                "ahorro_proyectado_usd",
                f"{metrics.get('avoided_cost_usd', 0):.4f}",
                0.8,
                "simulation_forecast_savings",
            )
        return items
