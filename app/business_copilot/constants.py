from app.query_engine.query_types import BusinessQueryType

COPILOT_PROMPT_MARKER = "## BUSINESS_COPILOT_V1"

COPILOT_MAX_PROPOSALS = 3

COPILOT_ELIGIBLE_HANDLED_BY = frozenset({
    "business_pipeline",
    "conversation_memory",
    "executive_reasoning",
})

COPILOT_ELIGIBLE_QUERY_TYPES = frozenset({
    BusinessQueryType.COUNT_CLIENTES.value,
    BusinessQueryType.COUNT_PROVEEDORES.value,
    BusinessQueryType.TOP_CLIENTES.value,
    BusinessQueryType.TOP_PROVEEDORES.value,
    BusinessQueryType.MAX_PROVEEDOR_MES.value,
    BusinessQueryType.MAX_TRANSACCION_CLIENTE.value,
    BusinessQueryType.KPIS.value,
    BusinessQueryType.DATA_COVERAGE.value,
    BusinessQueryType.DATASET_INFO.value,
})

PROPOSAL_TYPE_PROFUNDIZAR = "profundizar"
PROPOSAL_TYPE_COMPARAR = "comparar"
PROPOSAL_TYPE_EXPLICAR = "explicar"
PROPOSAL_TYPE_DEPENDENCIA = "detectar_dependencia"
PROPOSAL_TYPE_CONTINUAR = "continuar_conversacion"
