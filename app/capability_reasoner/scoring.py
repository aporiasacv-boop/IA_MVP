from app.capability_reasoning_audit.compatibility import (
    assess_query_type_compatibility,
    capability_label,
)
from app.capability_reasoning_audit.constants import (
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_NONE,
    COMPATIBILITY_PARTIAL,
)
from app.capability_reasoner.constants import (
    REGISTERED_QUERY_CAPABILITIES,
    SCORE_COMPATIBLE_BASE,
    SCORE_NONE_BASE,
    SCORE_PARTIAL_BASE,
)
from app.capability_reasoner.schemas import CandidateCapability
from app.query_engine.query_types import BusinessQueryType
from app.reasoning_engine.constants import (
    INTENT_BUSINESS_QUERY,
    INTENT_CAPABILITIES,
    INTENT_EXECUTIVE_ANALYSIS,
    INTENT_INSTITUTIONAL,
)
from app.utils.text_normalizer import normalize_for_matching


def score_registered_capabilities(
    question: str,
    *,
    intent: str | None,
    explanation: str | None,
    reasoning_confidence: float | None,
) -> list[CandidateCapability]:
    confidence_factor = 0.85 + (0.15 * reasoning_confidence if reasoning_confidence else 0.1)
    candidates: list[CandidateCapability] = []

    for query_type in REGISTERED_QUERY_CAPABILITIES:
        compatibility, _ = assess_query_type_compatibility(question, query_type, intent=intent)
        base = _base_score(compatibility)
        adjusted = min(0.95, round(base * confidence_factor, 4))
        adjusted = _apply_intent_boost(
            adjusted,
            query_type=query_type,
            intent=intent,
            question=question,
            explanation=explanation,
        )
        adjusted = _apply_question_pattern_boost(adjusted, query_type=query_type, question=question)

        candidates.append(
            CandidateCapability(
                capability_id=query_type.value,
                label=capability_label(query_type),
                score=round(adjusted, 2),
            )
        )

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates


def infer_reasoning_goal(
    question: str,
    *,
    intent: str | None,
    explanation: str | None,
) -> str:
    normalized = normalize_for_matching(question)
    if intent in {INTENT_EXECUTIVE_ANALYSIS, "customer_analysis"} or "cliente" in normalized:
        if "proveedor" in normalized:
            return "Analizar clientes y proveedores"
        return "Analizar clientes"
    if "proveedor" in normalized:
        return "Analizar proveedores"
    if intent == INTENT_CAPABILITIES:
        return "Explorar capacidades del asistente"
    if intent == INTENT_INSTITUTIONAL:
        return "Consultar conocimiento institucional"
    if intent == INTENT_BUSINESS_QUERY:
        return "Responder consulta empresarial estructurada"
    if explanation:
        return explanation.rstrip(".")
    return "Atender la intención del usuario con capacidades existentes"


def _base_score(compatibility: str) -> float:
    if compatibility == COMPATIBILITY_COMPATIBLE:
        return SCORE_COMPATIBLE_BASE
    if compatibility == COMPATIBILITY_PARTIAL:
        return SCORE_PARTIAL_BASE
    return SCORE_NONE_BASE


def _apply_intent_boost(
    score: float,
    *,
    query_type: BusinessQueryType,
    intent: str | None,
    question: str,
    explanation: str | None,
) -> float:
    normalized = normalize_for_matching(question)
    boost = 0.0

    if intent in {INTENT_BUSINESS_QUERY, INTENT_EXECUTIVE_ANALYSIS, "customer_analysis"}:
        if query_type in {
            BusinessQueryType.TOP_CLIENTES,
            BusinessQueryType.COUNT_CLIENTES,
            BusinessQueryType.KPIS,
        } and "cliente" in normalized:
            boost = 0.06
        if query_type in {
            BusinessQueryType.TOP_PROVEEDORES,
            BusinessQueryType.COUNT_PROVEEDORES,
            BusinessQueryType.MAX_PROVEEDOR_MES,
        } and "proveedor" in normalized:
            boost = 0.06

    if explanation and query_type.value.lower() in normalize_for_matching(explanation):
        boost = max(boost, 0.04)

    return min(0.95, score + boost)


def _apply_question_pattern_boost(
    score: float,
    *,
    query_type: BusinessQueryType,
    question: str,
) -> float:
    normalized = normalize_for_matching(question)
    boost = 0.0

    ranking_tokens = ("principal", "principales", "top ", "ranking", "mejores", "analiza")
    count_tokens = ("cuantos", "cuantas", "numero", "total", "conteo", "existen")
    kpi_tokens = ("kpi", "indicador", "metrica", "panorama", "universo", "analiza")

    if query_type == BusinessQueryType.TOP_CLIENTES and any(t in normalized for t in ranking_tokens):
        boost = 0.12
    if query_type == BusinessQueryType.COUNT_CLIENTES and any(t in normalized for t in count_tokens):
        boost = 0.12
    if query_type == BusinessQueryType.KPIS and any(t in normalized for t in kpi_tokens):
        boost = 0.10
    if query_type == BusinessQueryType.TOP_PROVEEDORES and "proveedor" in normalized and any(
        t in normalized for t in ranking_tokens
    ):
        boost = 0.12

    adjusted = min(0.95, score + boost)
    if query_type == BusinessQueryType.COUNT_CLIENTES and any(
        token in normalized for token in ranking_tokens
    ) and not any(token in normalized for token in count_tokens):
        adjusted = max(0.18, adjusted - 0.20)

    return adjusted
