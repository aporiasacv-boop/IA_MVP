COUNT_CLIENTES_TEMPLATE = "Actualmente existen {total} clientes registrados."

COUNT_PROVEEDORES_TEMPLATE = "Actualmente existen {total} proveedores registrados."

TOP_CLIENTES_HEADER = "Los principales clientes identificados son:"

TOP_PROVEEDORES_HEADER = "Los principales proveedores identificados son:"

MAX_PROVEEDOR_MES_TEMPLATE = (
    "El proveedor con mayor movimiento durante el mes consultado fue {proveedor} "
    "con un volumen total de {monto_total}."
)

UNSUPPORTED_TEMPLATE = (
    "Actualmente no existe una consulta empresarial configurada para esta solicitud."
)

SYSTEM_CAPABILITIES_HEADER = (
    "Actualmente puedo consultar información relacionada con:"
)

DATA_COVERAGE_TEMPLATE = (
    "Los datos disponibles abarcan desde el {fecha_min} hasta el {fecha_max}."
)

DATASET_INFO_HEADER = "Actualmente analizo:"

KPIS_TEMPLATE = (
    "El dataset contiene {movimientos:,} movimientos, "
    "{clientes:,} clientes, {proveedores:,} proveedores, "
    "{cuentas:,} cuentas y {divisas:,} divisas operativas."
)

CAPABILITY_LABELS: dict[str, str] = {
    "clientes": "Clientes",
    "proveedores": "Proveedores",
    "cuentas": "Cuentas",
    "kpis": "KPIs",
    "rankings": "Rankings",
    "actividad_mensual": "Actividad mensual",
    "insights": "Insights empresariales",
}

CAPABILITY_DISPLAY_ORDER: tuple[str, ...] = (
    "clientes",
    "proveedores",
    "cuentas",
    "kpis",
    "rankings",
    "actividad_mensual",
    "insights",
)

MES_NOMBRES: dict[int, str] = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}
