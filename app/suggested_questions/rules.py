from app.query_engine.query_types import BusinessQueryType

TYPE_SPECIFIC_RULES: dict[BusinessQueryType, tuple[str, ...]] = {
    BusinessQueryType.COUNT_CLIENTES: (
        "Muéstrame los principales clientes",
        "¿Cuántos proveedores existen?",
        "¿Cuál es el periodo de los datos?",
    ),
    BusinessQueryType.TOP_CLIENTES: (
        "Muéstrame los principales proveedores",
        "¿Qué proveedor tuvo más movimiento en junio?",
        "¿Cuántos clientes existen?",
    ),
    BusinessQueryType.MAX_PROVEEDOR_MES: (
        "¿Qué proveedor tuvo más movimiento en julio?",
        "Muéstrame los principales proveedores",
        "Muéstrame los principales clientes",
    ),
}

CAPABILITY_DISCOVERY_RULES: tuple[str, ...] = (
    "¿Cuántos clientes existen?",
    "¿Qué proveedor tuvo más movimiento en junio?",
    "¿Cuál es el periodo de los datos?",
    "Muéstrame los principales clientes",
    "¿Cuántos proveedores existen?",
)

GUIDED_FALLBACK_RULES: tuple[str, ...] = (
    "¿Qué puedes hacer?",
    "¿Cuántos clientes existen?",
    "¿Cuál es el periodo de los datos?",
    "Muéstrame los principales clientes",
)
