from app.query_engine.query_types import BusinessQueryType

QUERY_TYPE_EXAMPLE_QUESTIONS: dict[BusinessQueryType, str] = {
    BusinessQueryType.COUNT_CLIENTES: "¿Cuántos clientes existen?",
    BusinessQueryType.COUNT_PROVEEDORES: "¿Cuántos proveedores existen?",
    BusinessQueryType.TOP_CLIENTES: "Muéstrame los principales clientes",
    BusinessQueryType.TOP_PROVEEDORES: "Muéstrame los principales proveedores",
    BusinessQueryType.MAX_PROVEEDOR_MES: "¿Qué proveedor tuvo más movimiento en junio?",
    BusinessQueryType.MAX_TRANSACCION_CLIENTE: "¿Cuál fue la transacción más alta?",
    BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA: "¿A qué cliente pertenece la cuenta C001?",
    BusinessQueryType.DATA_COVERAGE: "¿Cuál es el periodo de los datos?",
    BusinessQueryType.DATASET_INFO: "¿Cuántos registros tienes?",
    BusinessQueryType.SYSTEM_CAPABILITIES: "¿Qué puedo preguntarte?",
}

RELATED_QUERY_TYPES: dict[BusinessQueryType, tuple[BusinessQueryType, ...]] = {
    BusinessQueryType.COUNT_CLIENTES: (
        BusinessQueryType.TOP_CLIENTES,
        BusinessQueryType.COUNT_PROVEEDORES,
        BusinessQueryType.DATA_COVERAGE,
    ),
    BusinessQueryType.TOP_CLIENTES: (
        BusinessQueryType.MAX_PROVEEDOR_MES,
        BusinessQueryType.TOP_PROVEEDORES,
        BusinessQueryType.COUNT_CLIENTES,
    ),
    BusinessQueryType.MAX_PROVEEDOR_MES: (
        BusinessQueryType.TOP_PROVEEDORES,
        BusinessQueryType.TOP_CLIENTES,
        BusinessQueryType.DATA_COVERAGE,
    ),
    BusinessQueryType.COUNT_PROVEEDORES: (
        BusinessQueryType.MAX_PROVEEDOR_MES,
        BusinessQueryType.TOP_PROVEEDORES,
        BusinessQueryType.DATA_COVERAGE,
    ),
    BusinessQueryType.TOP_PROVEEDORES: (
        BusinessQueryType.MAX_PROVEEDOR_MES,
        BusinessQueryType.TOP_CLIENTES,
        BusinessQueryType.COUNT_PROVEEDORES,
    ),
}

DISCOVERY_QUESTIONS: tuple[str, ...] = (
    "¿Qué puedes hacer?",
    "¿Qué puedo preguntarte?",
    "¿Qué información manejas?",
)

DEFAULT_TOP_QUESTIONS: tuple[str, ...] = (
    "¿Cuántos clientes existen?",
    "¿Cuántos proveedores existen?",
    "¿Qué proveedor tuvo más movimiento en junio?",
    "Muéstrame los principales clientes",
    "¿Cuál es el periodo de los datos?",
)
