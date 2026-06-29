from app.query_engine.query_types import BusinessQueryType
from app.repositories.query_executor.system_repository import SYSTEM_CAPABILITY_KEYS
from app.response_engine.response_templates import CAPABILITY_DISPLAY_ORDER, CAPABILITY_LABELS

EXECUTABLE_QUERY_TYPES: tuple[BusinessQueryType, ...] = tuple(
    query_type
    for query_type in BusinessQueryType
    if query_type != BusinessQueryType.UNSUPPORTED
    and query_type != BusinessQueryType.SYSTEM_CAPABILITIES
)

QUERY_TYPE_DESCRIPTIONS: dict[BusinessQueryType, str] = {
    BusinessQueryType.COUNT_CLIENTES: "Conteo de clientes registrados",
    BusinessQueryType.COUNT_PROVEEDORES: "Conteo de proveedores registrados",
    BusinessQueryType.TOP_CLIENTES: "Ranking de principales clientes",
    BusinessQueryType.TOP_PROVEEDORES: "Ranking de principales proveedores",
    BusinessQueryType.MAX_PROVEEDOR_MES: "Proveedor con mayor movimiento por mes",
    BusinessQueryType.MAX_TRANSACCION_CLIENTE: "Transacción máxima por cliente",
    BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA: "Relación cliente–cuenta",
    BusinessQueryType.DATA_COVERAGE: "Periodo y cobertura temporal de los datos",
    BusinessQueryType.DATASET_INFO: "Volumen del dataset (movimientos, clientes, proveedores)",
    BusinessQueryType.KPIS: "Indicadores clave del dataset",
}


def build_data_coverage_capabilities() -> list[str]:
    registered = set(SYSTEM_CAPABILITY_KEYS)
    capabilities: list[str] = []
    seen: set[str] = set()

    for key in CAPABILITY_DISPLAY_ORDER:
        if key == "rankings":
            if {"top_clientes", "top_proveedores"} <= registered:
                label = CAPABILITY_LABELS["rankings"]
                if label not in seen:
                    capabilities.append(label)
                    seen.add(label)
            continue

        if key in registered:
            label = CAPABILITY_LABELS[key]
            if label not in seen:
                capabilities.append(label)
                seen.add(label)

    return capabilities


def build_query_type_capabilities() -> list[str]:
    capabilities: list[str] = []
    seen: set[str] = set()

    for query_type in EXECUTABLE_QUERY_TYPES:
        description = QUERY_TYPE_DESCRIPTIONS.get(query_type)
        if description and description not in seen:
            capabilities.append(description)
            seen.add(description)

    return capabilities


def get_registered_capabilities() -> list[str]:
    coverage = build_data_coverage_capabilities()
    query_capabilities = build_query_type_capabilities()
    combined: list[str] = []
    seen: set[str] = set()

    for item in coverage + query_capabilities:
        if item not in seen:
            combined.append(item)
            seen.add(item)

    return combined


def get_supported_query_types() -> list[BusinessQueryType]:
    return list(EXECUTABLE_QUERY_TYPES)
