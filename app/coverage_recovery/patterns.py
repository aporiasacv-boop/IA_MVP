"""Patrones y consultas canónicas de Coverage Recovery v1."""

from app.utils.text_normalizer import normalize_for_matching

# Consultas canónicas del requerimiento (auditoría y health checks).
DATA_COVERAGE_QUERIES: tuple[str, ...] = (
    "¿De qué fecha son tus datos?",
    "¿Qué fechas cubren los datos?",
    "¿Hasta qué fecha llegan los datos?",
    "¿Desde cuándo hay información?",
    "¿Cuál es la antigüedad de los datos?",
    "¿Cuál es el rango temporal?",
    "¿Qué periodo de información tienes?",
)

DATASET_INFO_QUERIES: tuple[str, ...] = (
    "¿Qué tipos de datos tienes?",
    "¿Qué datos tienes?",
    "¿Qué información tienes?",
    "¿Qué información contiene el sistema?",
    "¿Qué información puedo consultar?",
    "¿Qué datos analiza el asistente?",
)

CAPABILITY_DISCOVERY_QUERIES: tuple[str, ...] = (
    "¿Qué puedes hacer?",
    "¿Cómo puedes ayudarme?",
    "¿Qué consultas soportas?",
    "¿Qué puedo preguntarte?",
    "¿Qué sabes hacer?",
    "¿Para qué sirves?",
)

REGRESSION_BUSINESS_QUERIES: tuple[str, ...] = (
    "¿Cuántos clientes existen?",
    "¿Cuántos proveedores existen?",
    "¿Qué proveedor tuvo más movimiento?",
    "¿Cuál fue la transacción más alta?",
    "Muéstrame los principales clientes",
)

DATA_COVERAGE_PATTERNS: tuple[str, ...] = tuple(
    normalize_for_matching(query) for query in DATA_COVERAGE_QUERIES
) + (
    "de que fecha son tus datos",
    "de que fecha son los datos",
    "hasta que fecha llegan los datos",
    "desde cuando hay informacion",
    "antiguedad de los datos",
    "rango temporal",
    "periodo de informacion tienes",
    "fechas cubren los datos",
    "cobertura temporal",
    "rango de fechas",
)

DATASET_INFO_PATTERNS: tuple[str, ...] = tuple(
    normalize_for_matching(query) for query in DATASET_INFO_QUERIES
) + (
    "que tipos de datos",
    "que datos analiza el asistente",
    "que informacion contiene el sistema",
    "que informacion puedo consultar",
)

CAPABILITY_DISCOVERY_PATTERNS: tuple[str, ...] = tuple(
    normalize_for_matching(query) for query in CAPABILITY_DISCOVERY_QUERIES
)
