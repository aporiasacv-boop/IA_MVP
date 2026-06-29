from app.query_engine.query_types import BusinessQueryType

INSIGHT_PROMPT_MARKER = "## EXECUTIVE_INSIGHT_V1"

INSIGHT_ELIGIBLE_HANDLED_BY = frozenset({
    "business_pipeline",
    "conversation_memory",
})

INSIGHT_ELIGIBLE_QUERY_TYPES = frozenset({
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
