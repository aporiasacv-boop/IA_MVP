from app.enterprise_decision.repository import DecisionContext
from app.enterprise_decision.schemas import DecisionType, EvidenceItem, RecommendationItem
from app.enterprise_decision.simulation_analyzer import SimulationAnalyzer


class RecommendationEngine:
    def __init__(self) -> None:
        self._simulation = SimulationAnalyzer()

    def build(
        self,
        decision_type: DecisionType,
        context: DecisionContext,
        evidence: list[EvidenceItem],
    ) -> tuple[RecommendationItem, list[RecommendationItem], list[str], list[str]]:
        evidence_ids = [item.evidence_id for item in evidence]
        provider_ids = [item.evidence_id for item in evidence if "proveedor" in item.metric or item.rule == "simulation_provider_comparison"]
        scenario_ids = [item.evidence_id for item in evidence if item.category in {"escenario", "operacion"}]
        finops_ids = [item.evidence_id for item in evidence if item.source in {"finops", "operational_metrics"}]

        if decision_type == DecisionType.PROVEEDOR_IA:
            main = self._simulation.provider_recommendation(context, provider_ids or evidence_ids)
            alternatives = self._provider_alternatives(context, evidence_ids)
        elif decision_type == DecisionType.ESCENARIO:
            main = self._simulation.scenario_recommendation(context, scenario_ids or evidence_ids)
            alternatives = self._scenario_alternatives(context, evidence_ids)
        elif decision_type == DecisionType.INFRAESTRUCTURA:
            main = self._simulation.infrastructure_recommendation(context, evidence_ids)
            alternatives = [
                RecommendationItem(
                    title="Escalar gradualmente",
                    detail="Incrementar recursos solo si la concurrencia supera el umbral simulado.",
                    decision_type=decision_type.value,
                    evidence_ids=evidence_ids[:2],
                    confidence=0.7,
                )
            ]
        elif decision_type == DecisionType.ESTRATEGIA_DESPLIEGUE:
            main = self._deployment_strategy(context, evidence_ids)
            alternatives = self._deployment_alternatives(context, evidence_ids)
        elif decision_type == DecisionType.OPTIMIZACION_COSTOS:
            main = self._cost_optimization(context, finops_ids or evidence_ids)
            alternatives = self._cost_alternatives(context, evidence_ids)
        elif decision_type == DecisionType.OPTIMIZACION_IA:
            main = self._ai_optimization(context, finops_ids or evidence_ids)
            alternatives = self._ai_alternatives(context, evidence_ids)
        elif decision_type == DecisionType.OPTIMIZACION_PIPELINE:
            main = self._pipeline_optimization(context, evidence_ids)
            alternatives = self._pipeline_alternatives(context, evidence_ids)
        else:
            main = self._simulation.provider_recommendation(context, evidence_ids)
            alternatives = []

        risks = self._risks(context, evidence)
        opportunities = self._opportunities(context, evidence)
        return main, alternatives, risks, opportunities

    def _provider_alternatives(self, context: DecisionContext, evidence_ids: list[str]) -> list[RecommendationItem]:
        items: list[RecommendationItem] = []
        comparison = context.simulation_comparison
        if comparison:
            fastest = comparison.get("fastest_provider", "")
            best_roi = comparison.get("best_roi_provider", "")
            if fastest:
                items.append(
                    RecommendationItem(
                        title="Proveedor con menor latencia",
                        detail=f"{fastest} ofrece la menor latencia media en la comparativa simulada.",
                        decision_type=DecisionType.PROVEEDOR_IA.value,
                        evidence_ids=evidence_ids[:2],
                        confidence=0.8,
                    )
                )
            if best_roi and best_roi != fastest:
                items.append(
                    RecommendationItem(
                        title="Proveedor con mejor ROI",
                        detail=f"{best_roi} maximiza el retorno según proyección FinOps.",
                        decision_type=DecisionType.PROVEEDOR_IA.value,
                        evidence_ids=evidence_ids[:2],
                        confidence=0.78,
                    )
                )
        for provider in context.finops_providers[:2]:
            items.append(
                RecommendationItem(
                    title=f"Proveedor histórico: {provider.get('provider', 'N/D')}",
                    detail=f"Participación {provider.get('share_pct', 0):.1f}% con costo acumulado ${provider.get('cost_usd', 0):.4f}.",
                    decision_type=DecisionType.PROVEEDOR_IA.value,
                    evidence_ids=evidence_ids[:1],
                    confidence=0.75,
                )
            )
        return items[:3]

    def _scenario_alternatives(self, context: DecisionContext, evidence_ids: list[str]) -> list[RecommendationItem]:
        predefined = ["demo", "produccion", "enterprise"]
        current = context.simulation_run.get("scenario_id", "piloto") if context.simulation_run else "piloto"
        items: list[RecommendationItem] = []
        for scenario_id in predefined:
            if scenario_id == current:
                continue
            items.append(
                RecommendationItem(
                    title=f"Evaluar escenario {scenario_id}",
                    detail="Comparar costo y ahorro proyectado antes de ampliar despliegue.",
                    decision_type=DecisionType.ESCENARIO.value,
                    evidence_ids=evidence_ids[:1],
                    confidence=0.65,
                )
            )
        return items[:2]

    def _deployment_strategy(self, context: DecisionContext, evidence_ids: list[str]) -> RecommendationItem:
        mix = context.historical_route_mix
        pipeline = mix.get("business_pipeline", 0.0)
        knowledge = mix.get("business_knowledge", 0.0)
        detail = (
            f"Desplegar priorizando rutas determinísticas: Pipeline {pipeline:.1f}%, "
            f"Conocimiento {knowledge:.1f}% según histórico operativo."
        )
        return RecommendationItem(
            title="Estrategia de despliegue por capas",
            detail=detail,
            decision_type=DecisionType.ESTRATEGIA_DESPLIEGUE.value,
            evidence_ids=evidence_ids,
            confidence=0.82 if context.operational_queries > 0 else 0.55,
        )

    def _deployment_alternatives(self, context: DecisionContext, evidence_ids: list[str]) -> list[RecommendationItem]:
        return [
            RecommendationItem(
                title="Piloto controlado",
                detail="Iniciar con escenario Piloto y ampliar según métricas de ahorro real.",
                decision_type=DecisionType.ESTRATEGIA_DESPLIEGUE.value,
                evidence_ids=evidence_ids[:1],
                confidence=0.7,
            ),
            RecommendationItem(
                title="Despliegue enterprise",
                detail="Adoptar escenario Enterprise solo si el ahorro LLM supera el 60%.",
                decision_type=DecisionType.ESTRATEGIA_DESPLIEGUE.value,
                evidence_ids=evidence_ids[:1],
                confidence=0.68,
            ),
        ]

    def _cost_optimization(self, context: DecisionContext, evidence_ids: list[str]) -> RecommendationItem:
        savings = context.finops_savings
        total = savings.get("total_avoided_cost_usd", 0.0)
        rate = context.finops_overview.get("llm_avoidance_rate", 0.0)
        return RecommendationItem(
            title="Optimización de costos",
            detail=(
                f"Mantener rutas sin LLM para preservar ${total:.4f} USD evitados "
                f"y ampliar el {rate * 100:.1f}% de ahorro actual."
            ),
            decision_type=DecisionType.OPTIMIZACION_COSTOS.value,
            evidence_ids=evidence_ids,
            confidence=0.88 if context.operational_queries >= 5 else 0.6,
        )

    def _cost_alternatives(self, context: DecisionContext, evidence_ids: list[str]) -> list[RecommendationItem]:
        cheapest = context.simulation_comparison.get("cheapest_provider", "ollama")
        return [
            RecommendationItem(
                title="Migrar proveedor LLM",
                detail=f"Evaluar {cheapest} para reducir costo marginal por consulta.",
                decision_type=DecisionType.OPTIMIZACION_COSTOS.value,
                evidence_ids=evidence_ids[:2],
                confidence=0.75,
            )
        ]

    def _ai_optimization(self, context: DecisionContext, evidence_ids: list[str]) -> RecommendationItem:
        rate = context.finops_overview.get("llm_avoidance_rate", 0.0)
        return RecommendationItem(
            title="Optimización del uso de IA",
            detail=(
                f"Incrementar enrutamiento a Pipeline, Conocimiento y Memoria para superar "
                f"el {rate * 100:.1f}% de consultas sin LLM."
            ),
            decision_type=DecisionType.OPTIMIZACION_IA.value,
            evidence_ids=evidence_ids,
            confidence=0.86,
        )

    def _ai_alternatives(self, context: DecisionContext, evidence_ids: list[str]) -> list[RecommendationItem]:
        return [
            RecommendationItem(
                title="Ampliar Knowledge Service",
                detail="Derivar FAQs y capacidades al servicio de conocimiento antes del LLM.",
                decision_type=DecisionType.OPTIMIZACION_IA.value,
                evidence_ids=evidence_ids[:1],
                confidence=0.72,
            )
        ]

    def _pipeline_optimization(self, context: DecisionContext, evidence_ids: list[str]) -> RecommendationItem:
        pipeline = context.historical_route_mix.get("business_pipeline", 0.0)
        return RecommendationItem(
            title="Optimización del Pipeline",
            detail=f"Elevar participación del Business Pipeline desde {pipeline:.1f}% hacia consultas estructuradas.",
            decision_type=DecisionType.OPTIMIZACION_PIPELINE.value,
            evidence_ids=evidence_ids,
            confidence=0.84 if pipeline > 0 else 0.5,
        )

    def _pipeline_alternatives(self, context: DecisionContext, evidence_ids: list[str]) -> list[RecommendationItem]:
        return [
            RecommendationItem(
                title="Auditar consultas legacy",
                detail="Reclasificar consultas en legacy_chat hacia intents soportados por el pipeline.",
                decision_type=DecisionType.OPTIMIZACION_PIPELINE.value,
                evidence_ids=evidence_ids[:1],
                confidence=0.7,
            )
        ]

    def _risks(self, context: DecisionContext, evidence: list[EvidenceItem]) -> list[str]:
        risks: list[str] = []
        if context.operational_queries < 10:
            risks.append("Histórico operativo limitado; la confianza estadística es baja.")
        legacy = context.historical_route_mix.get("legacy_chat", 0.0)
        if legacy > 20:
            risks.append(f"Alta dependencia de conversación general ({legacy:.1f}%).")
        if context.eko_completeness and context.eko_completeness < 0.7:
            risks.append("Objetos EKO con completitud inferior al 70%.")
        if len({item.source for item in evidence}) < 2:
            risks.append("Evidencia concentrada en una sola fuente.")
        return risks

    def _opportunities(self, context: DecisionContext, evidence: list[EvidenceItem]) -> list[str]:
        opportunities: list[str] = []
        savings = context.finops_savings.get("total_avoided_cost_usd", 0.0)
        if savings > 0:
            opportunities.append(f"Capitalizar ${savings:.4f} USD ya evitados ampliando rutas determinísticas.")
        if context.eks_documents > 0:
            opportunities.append(f"Aprovechar {context.eks_documents} documentos del servicio de conocimiento.")
        cheapest = context.simulation_comparison.get("cheapest_provider")
        if cheapest:
            opportunities.append(f"Reducir costo marginal migrando hacia {cheapest}.")
        if context.eep_packages > 0:
            opportunities.append("Reutilizar paquetes EEP existentes para auditoría de decisiones.")
        return opportunities
