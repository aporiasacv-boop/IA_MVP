UNKNOWN_HEADER = "Actualmente puedo ayudarte con:"

UNKNOWN_CAPABILITIES: tuple[str, ...] = (
    "Clientes",
    "Proveedores",
    "KPIs",
    "Actividad mensual",
    "Rankings",
)

AMBIGUOUS_HEADER = "Puedo ayudarte con:"

AMBIGUOUS_OPTIONS: tuple[str, ...] = (
    "KPIs ejecutivos",
    "Principales clientes",
    "Principales proveedores",
)

AMBIGUOUS_FOOTER = "¿Cuál te interesa?"

OUT_OF_DOMAIN_ANSWER = (
    "Estoy especializado en información empresarial de Olnatura."
)

LOW_CONFIDENCE_HEADER = (
    "No logré identificar con claridad tu consulta, pero puedo orientarte con:"
)

UNSUPPORTED_CAPABILITY_HEADER = (
    "Esa consulta aún no está disponible de forma directa. Puedes probar con:"
)
