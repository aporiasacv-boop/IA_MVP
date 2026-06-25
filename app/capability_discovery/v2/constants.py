"""Constantes UX de Capability Discovery v2."""

MAX_CAPABILITIES = 5
MAX_EXAMPLES = 3
MAX_RESPONSE_LINES = 12

V2_CAPABILITIES: tuple[str, ...] = (
    "Clientes",
    "Proveedores",
    "KPIs",
    "Actividad mensual",
    "Insights empresariales",
)

V2_EXAMPLES: tuple[str, ...] = (
    "¿Cuántos clientes existen?",
    "¿Quién es el principal cliente?",
    "¿Qué proveedor tuvo más movimiento en junio?",
)

FORBIDDEN_EXAMPLE_PATTERNS: tuple[str, ...] = (
    "hola",
    "quien eres",
    "que es un proveedor",
    "que sabes hacer",
)

FORBIDDEN_VISIBLE_TERMS: tuple[str, ...] = (
    "query type",
    "query types",
    "capacidades soportadas",
    "cobertura del dataset",
    "cobertura de datos",
    "consultas empresariales soportadas",
    "ejemplos que puedes hacer",
    "dataset",
    "rankings",
    "cuentas",
    "conteo de",
    "ranking de",
    "relacion cliente",
)

INTRO_LINE = "Puedo ayudarte con información sobre:"
EXAMPLES_LINE = "Por ejemplo:"
