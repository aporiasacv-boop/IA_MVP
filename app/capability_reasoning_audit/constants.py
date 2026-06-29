from app.query_engine.query_types import BusinessQueryType

AUDIT_CLASSIFICATION_CORRECT = "Correcto"
AUDIT_CLASSIFICATION_PARTIAL = "Parcial"
AUDIT_CLASSIFICATION_INCORRECT = "Incorrecto"

COMPATIBILITY_COMPATIBLE = "compatible"
COMPATIBILITY_PARTIAL = "partially_compatible"
COMPATIBILITY_NONE = "not_compatible"

AUDITABLE_QUERY_TYPES: tuple[BusinessQueryType, ...] = (
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

REGISTRY_CAPABILITY_IDS: tuple[str, ...] = (
    "INSTITUTIONAL_KNOWLEDGE",
    "BUSINESS_PIPELINE",
    "CONVERSATIONAL_ENRICHMENT",
)
