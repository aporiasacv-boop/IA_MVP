from app.business_copilot.constants import (
    COPILOT_MAX_PROPOSALS,
    PROPOSAL_TYPE_COMPARAR,
    PROPOSAL_TYPE_CONTINUAR,
    PROPOSAL_TYPE_DEPENDENCIA,
    PROPOSAL_TYPE_EXPLICAR,
    PROPOSAL_TYPE_PROFUNDIZAR,
)
from app.business_copilot.schemas import CopilotPayload, CopilotProposal
from app.query_engine.query_types import BusinessQueryType
from app.utils.text_normalizer import normalize_for_matching


def build_rule_based_proposals(
    *,
    query_type: str,
    handled_by: str,
    prior_questions: list[str],
) -> CopilotPayload:
    normalized_prior = {normalize_for_matching(question) for question in prior_questions}
    candidates = _candidates_for_context(query_type=query_type, handled_by=handled_by)
    proposals: list[CopilotProposal] = []
    for candidate in candidates:
        if normalize_for_matching(candidate.query) in normalized_prior:
            continue
        proposals.append(candidate)
        if len(proposals) >= COPILOT_MAX_PROPOSALS:
            break
    return CopilotPayload(proposals=proposals)


def _candidates_for_context(*, query_type: str, handled_by: str) -> list[CopilotProposal]:
    if handled_by == "executive_reasoning":
        return [
            CopilotProposal(
                title="Profundizar en clientes clave",
                rationale="Después de un resumen ejecutivo conviene revisar la concentración comercial.",
                action_label="Profundizar",
                query="Muéstrame los principales clientes",
                proposal_type=PROPOSAL_TYPE_CONTINUAR,
            ),
            CopilotProposal(
                title="Revisar indicadores operativos",
                rationale="Los KPIs permiten validar la magnitud del periodo analizado.",
                action_label="Explicar",
                query="KPIs",
                proposal_type=PROPOSAL_TYPE_EXPLICAR,
            ),
        ]

    mapping: dict[str, list[CopilotProposal]] = {
        BusinessQueryType.TOP_CLIENTES.value: [
            CopilotProposal(
                title="Analizar concentración comercial",
                rationale="Los primeros clientes pueden concentrar una parte importante de la actividad.",
                action_label="Analizar",
                query="¿Qué porcentaje representan los primeros cinco clientes?",
                proposal_type=PROPOSAL_TYPE_PROFUNDIZAR,
            ),
            CopilotProposal(
                title="Comparar con proveedores principales",
                rationale="Contrastar clientes y proveedores ayuda a detectar dependencias cruzadas.",
                action_label="Comparar",
                query="Muéstrame los principales proveedores",
                proposal_type=PROPOSAL_TYPE_COMPARAR,
            ),
        ],
        BusinessQueryType.TOP_PROVEEDORES.value: [
            CopilotProposal(
                title="Analizar dependencia de proveedores",
                rationale="Un ranking elevado puede indicar dependencia operativa.",
                action_label="Analizar",
                query="¿Qué porcentaje del volumen corresponde al proveedor principal?",
                proposal_type=PROPOSAL_TYPE_DEPENDENCIA,
            ),
            CopilotProposal(
                title="Revisar proveedor con mayor movimiento",
                rationale="El máximo mensual complementa el análisis de concentración.",
                action_label="Comparar",
                query="¿Cuál fue el proveedor con mayor movimiento este mes?",
                proposal_type=PROPOSAL_TYPE_COMPARAR,
            ),
        ],
        BusinessQueryType.KPIS.value: [
            CopilotProposal(
                title="Explicar el indicador principal",
                rationale="Los movimientos suelen ser el indicador con mayor peso operativo.",
                action_label="Explicar",
                query="¿Qué porcentaje del volumen corresponde a los principales clientes?",
                proposal_type=PROPOSAL_TYPE_EXPLICAR,
            ),
            CopilotProposal(
                title="Profundizar en clientes clave",
                rationale="Los KPIs de volumen se entienden mejor con el ranking de clientes.",
                action_label="Profundizar",
                query="Muéstrame los principales clientes",
                proposal_type=PROPOSAL_TYPE_PROFUNDIZAR,
            ),
        ],
        BusinessQueryType.DATA_COVERAGE.value: [
            CopilotProposal(
                title="Consultar meses con menor cobertura",
                rationale="La cobertura temporal permite detectar vacíos de información.",
                action_label="Comparar",
                query="¿Qué meses tienen menor actividad registrada?",
                proposal_type=PROPOSAL_TYPE_COMPARAR,
            ),
            CopilotProposal(
                title="Validar magnitud del dataset",
                rationale="Los KPIs contextualizan el alcance temporal disponible.",
                action_label="Explicar",
                query="KPIs",
                proposal_type=PROPOSAL_TYPE_EXPLICAR,
            ),
        ],
        BusinessQueryType.MAX_PROVEEDOR_MES.value: [
            CopilotProposal(
                title="Analizar dependencia del proveedor líder",
                rationale="Un proveedor dominante puede representar riesgo de concentración.",
                action_label="Analizar",
                query="Muéstrame los principales proveedores",
                proposal_type=PROPOSAL_TYPE_DEPENDENCIA,
            ),
        ],
        BusinessQueryType.COUNT_CLIENTES.value: [
            CopilotProposal(
                title="Identificar clientes principales",
                rationale="Después del conteo conviene revisar quién concentra la actividad.",
                action_label="Profundizar",
                query="Muéstrame los principales clientes",
                proposal_type=PROPOSAL_TYPE_PROFUNDIZAR,
            ),
        ],
        BusinessQueryType.COUNT_PROVEEDORES.value: [
            CopilotProposal(
                title="Identificar proveedores principales",
                rationale="El conteo se complementa con el ranking de dependencia.",
                action_label="Profundizar",
                query="Muéstrame los principales proveedores",
                proposal_type=PROPOSAL_TYPE_PROFUNDIZAR,
            ),
        ],
        BusinessQueryType.DATASET_INFO.value: [
            CopilotProposal(
                title="Revisar cobertura temporal",
                rationale="El inventario del dataset debe validarse contra el periodo disponible.",
                action_label="Comparar",
                query="¿Cuál es la cobertura de datos disponible?",
                proposal_type=PROPOSAL_TYPE_COMPARAR,
            ),
        ],
    }
    return mapping.get(query_type.upper(), [])
