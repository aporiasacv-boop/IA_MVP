from app.query_engine.query_types import BusinessQueryType

# Evidencias disponibles y capability que las materializa (sin SQL nuevo).
EVIDENCE_DEFINITIONS: dict[str, dict[str, object]] = {
    "principales_clientes": {
        "label": "Principales clientes",
        "capability": BusinessQueryType.TOP_CLIENTES.value,
        "priority": 10,
    },
    "conteo_clientes": {
        "label": "Conteo de clientes",
        "capability": BusinessQueryType.COUNT_CLIENTES.value,
        "priority": 20,
    },
    "kpis_negocio": {
        "label": "Indicadores clave del negocio",
        "capability": BusinessQueryType.KPIS.value,
        "priority": 30,
    },
    "cobertura_temporal": {
        "label": "Cobertura temporal de datos",
        "capability": BusinessQueryType.DATA_COVERAGE.value,
        "priority": 40,
    },
    "volumen_dataset": {
        "label": "Volumen del dataset",
        "capability": BusinessQueryType.DATASET_INFO.value,
        "priority": 50,
    },
    "principales_proveedores": {
        "label": "Principales proveedores",
        "capability": BusinessQueryType.TOP_PROVEEDORES.value,
        "priority": 10,
    },
    "conteo_proveedores": {
        "label": "Conteo de proveedores",
        "capability": BusinessQueryType.COUNT_PROVEEDORES.value,
        "priority": 20,
    },
    "movimiento_proveedor": {
        "label": "Movimiento destacado de proveedores",
        "capability": BusinessQueryType.MAX_PROVEEDOR_MES.value,
        "priority": 30,
    },
    "concentracion_comercial": {
        "label": "Concentración comercial",
        "capability": BusinessQueryType.TOP_CLIENTES.value,
        "priority": 15,
    },
}

EXECUTION_ORDER_WEIGHT: dict[str, int] = {
    BusinessQueryType.DATA_COVERAGE.value: 10,
    BusinessQueryType.DATASET_INFO.value: 15,
    BusinessQueryType.COUNT_CLIENTES.value: 20,
    BusinessQueryType.COUNT_PROVEEDORES.value: 20,
    BusinessQueryType.TOP_CLIENTES.value: 30,
    BusinessQueryType.TOP_PROVEEDORES.value: 30,
    BusinessQueryType.MAX_PROVEEDOR_MES.value: 35,
    BusinessQueryType.KPIS.value: 40,
}

SIMPLE_QUERY_EVIDENCE: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (("cuantos clientes", "numero de clientes", "total de clientes"), "conteo_clientes", "Contar clientes registrados"),
    (("cuantos proveedores", "numero de proveedores"), "conteo_proveedores", "Contar proveedores registrados"),
    (("principales clientes", "top clientes", "ranking de clientes"), "principales_clientes", "Ranking de clientes"),
    (("principales proveedores", "top proveedores"), "principales_proveedores", "Ranking de proveedores"),
    (("periodo de los datos", "cobertura temporal", "fechas cubren"), "cobertura_temporal", "Periodo disponible"),
    (("cuantos registros", "volumen del dataset"), "volumen_dataset", "Volumen del dataset"),
    (("kpis", "indicadores clave"), "kpis_negocio", "Indicadores clave"),
)

OPEN_QUERY_PROFILES: tuple[dict[str, object], ...] = (
    {
        "patterns": ("cartera", "salud comercial", "como ves nuestra"),
        "business_goal": "Analizar salud comercial",
        "evidence_keys": ("principales_clientes", "kpis_negocio", "cobertura_temporal"),
    },
    {
        "patterns": ("universo de clientes", "analiza el universo", "analiza clientes"),
        "business_goal": "Evaluar universo de clientes",
        "evidence_keys": ("principales_clientes", "conteo_clientes", "kpis_negocio"),
    },
    {
        "patterns": ("riesgo", "riesgos comerciales"),
        "business_goal": "Identificar riesgos comerciales",
        "evidence_keys": ("principales_clientes", "kpis_negocio", "concentracion_comercial"),
    },
    {
        "patterns": ("como esta el negocio", "panorama del negocio", "desempeno del negocio"),
        "business_goal": "Evaluar desempeño del negocio",
        "evidence_keys": ("kpis_negocio", "principales_clientes", "cobertura_temporal"),
    },
    {
        "patterns": ("concentracion", "concentracion de clientes"),
        "business_goal": "Evaluar concentración de clientes",
        "evidence_keys": ("principales_clientes", "concentracion_comercial", "kpis_negocio"),
    },
    {
        "patterns": ("proveedores", "base de proveedores", "analiza nuestros proveedores"),
        "business_goal": "Analizar base de proveedores",
        "evidence_keys": ("principales_proveedores", "conteo_proveedores", "movimiento_proveedor"),
    },
)
