from app.query_engine.query_types import BusinessQueryType

REGISTERED_QUERY_CAPABILITIES: tuple[BusinessQueryType, ...] = (
    BusinessQueryType.COUNT_CLIENTES,
    BusinessQueryType.COUNT_PROVEEDORES,
    BusinessQueryType.TOP_CLIENTES,
    BusinessQueryType.TOP_PROVEEDORES,
    BusinessQueryType.MAX_PROVEEDOR_MES,
    BusinessQueryType.MAX_TRANSACCION_CLIENTE,
    BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA,
    BusinessQueryType.DATA_COVERAGE,
    BusinessQueryType.DATASET_INFO,
    BusinessQueryType.KPIS,
)

MIN_CANDIDATE_SCORE = 0.45
MIN_PRIMARY_SCORE = 0.55
COMBINATION_GAP = 0.18
FALLBACK_COVERAGE_THRESHOLD = 0.50

SCORE_COMPATIBLE_BASE = 0.82
SCORE_PARTIAL_BASE = 0.64
SCORE_NONE_BASE = 0.18
