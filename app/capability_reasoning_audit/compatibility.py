from dataclasses import dataclass

from app.capability_discovery.registry import QUERY_TYPE_DESCRIPTIONS
from app.capability_reasoning_audit.constants import (
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_NONE,
    COMPATIBILITY_PARTIAL,
)
from app.query_engine.query_types import BusinessQueryType
from app.reasoning_engine.constants import (
    INTENT_BUSINESS_QUERY,
    INTENT_CAPABILITIES,
    INTENT_EXECUTIVE_ANALYSIS,
    INTENT_INSTITUTIONAL,
)
from app.utils.text_normalizer import normalize_for_matching


@dataclass(frozen=True)
class CapabilityRule:
    query_type: BusinessQueryType
    strong_patterns: tuple[str, ...]
    partial_patterns: tuple[str, ...]
    entity_tokens: tuple[str, ...]
    intents: tuple[str, ...]


_CAPABILITY_RULES: tuple[CapabilityRule, ...] = (
    CapabilityRule(
        BusinessQueryType.COUNT_CLIENTES,
        ("cuantos clientes", "numero de clientes", "total de clientes", "conteo de clientes"),
        ("universo de clientes", "clientes registrados", "cuantos hay de clientes"),
        ("cliente", "clientes"),
        (INTENT_BUSINESS_QUERY,),
    ),
    CapabilityRule(
        BusinessQueryType.COUNT_PROVEEDORES,
        ("cuantos proveedores", "numero de proveedores", "total de proveedores"),
        ("proveedores registrados", "universo de proveedores"),
        ("proveedor", "proveedores"),
        (INTENT_BUSINESS_QUERY,),
    ),
    CapabilityRule(
        BusinessQueryType.TOP_CLIENTES,
        ("top clientes", "principales clientes", "ranking de clientes", "mejores clientes"),
        ("analiza clientes", "universo de clientes", "concentracion de clientes", "clientes principales"),
        ("cliente", "clientes", "ranking"),
        (INTENT_BUSINESS_QUERY, INTENT_EXECUTIVE_ANALYSIS),
    ),
    CapabilityRule(
        BusinessQueryType.TOP_PROVEEDORES,
        ("top proveedores", "principales proveedores", "ranking de proveedores"),
        ("proveedores principales", "concentracion de proveedores"),
        ("proveedor", "proveedores", "ranking"),
        (INTENT_BUSINESS_QUERY,),
    ),
    CapabilityRule(
        BusinessQueryType.MAX_PROVEEDOR_MES,
        ("proveedor con mas movimiento", "mayor movimiento del proveedor", "proveedor mas activo"),
        ("movimiento por mes", "proveedor destacado"),
        ("proveedor", "movimiento", "mes"),
        (INTENT_BUSINESS_QUERY,),
    ),
    CapabilityRule(
        BusinessQueryType.MAX_TRANSACCION_CLIENTE,
        ("transaccion mas alta", "mayor transaccion", "transaccion maxima"),
        ("monto maximo", "operacion mas grande"),
        ("transaccion", "cliente", "monto"),
        (INTENT_BUSINESS_QUERY,),
    ),
    CapabilityRule(
        BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA,
        ("a que cliente pertenece la cuenta", "cliente de la cuenta", "cuenta c0"),
        ("relacion cliente cuenta", "buscar por cuenta"),
        ("cuenta", "cliente"),
        (INTENT_BUSINESS_QUERY,),
    ),
    CapabilityRule(
        BusinessQueryType.DATA_COVERAGE,
        ("periodo de los datos", "cobertura temporal", "desde cuando hay datos", "hasta que fecha"),
        ("antiguedad de los datos", "fechas cubren", "rango temporal"),
        ("fecha", "periodo", "cobertura", "datos"),
        (INTENT_BUSINESS_QUERY,),
    ),
    CapabilityRule(
        BusinessQueryType.DATASET_INFO,
        ("cuantos registros", "volumen del dataset", "informacion del dataset"),
        ("que datos tienes", "que informacion tienes", "tamano del dataset"),
        ("registros", "dataset", "informacion", "datos"),
        (INTENT_BUSINESS_QUERY, INTENT_CAPABILITIES),
    ),
    CapabilityRule(
        BusinessQueryType.KPIS,
        ("kpis", "indicadores clave", "indicadores del negocio"),
        ("metricas del negocio", "panorama general", "resumen de indicadores", "analiza el universo"),
        ("kpi", "indicador", "metrica", "resumen"),
        (INTENT_BUSINESS_QUERY, INTENT_EXECUTIVE_ANALYSIS),
    ),
)


def assess_query_type_compatibility(
    question: str,
    query_type: BusinessQueryType,
    *,
    intent: str | None,
) -> tuple[str, str]:
    normalized = normalize_for_matching(question)
    rule = _rule_for(query_type)
    if rule is None:
        return COMPATIBILITY_NONE, "Capability no evaluable en catálogo de auditoría."

    if any(pattern in normalized for pattern in rule.strong_patterns):
        return COMPATIBILITY_COMPATIBLE, "La pregunta coincide con patrones fuertes de esta capability."

    intent_match = intent in rule.intents if intent else False
    entity_match = any(token in normalized for token in rule.entity_tokens)

    if intent_match and entity_match:
        return COMPATIBILITY_COMPATIBLE, "La intención y las entidades alinean con esta capability."

    if any(pattern in normalized for pattern in rule.partial_patterns):
        return COMPATIBILITY_PARTIAL, "La pregunta es parcialmente cubierta por esta capability."

    if entity_match and intent in {INTENT_BUSINESS_QUERY, INTENT_EXECUTIVE_ANALYSIS}:
        return COMPATIBILITY_PARTIAL, "Comparte entidades de negocio relevantes para esta capability."

    if intent == INTENT_CAPABILITIES and query_type == BusinessQueryType.DATASET_INFO:
        return COMPATIBILITY_PARTIAL, "Consulta de capacidades relacionada con inventario de datos."

    if intent in {INTENT_INSTITUTIONAL, INTENT_CAPABILITIES} and query_type == BusinessQueryType.KPIS:
        return COMPATIBILITY_PARTIAL, "Consulta exploratoria que podría complementarse con indicadores."

    return COMPATIBILITY_NONE, "No se detectó afinidad suficiente con la pregunta."


def capability_label(query_type: BusinessQueryType) -> str:
    return QUERY_TYPE_DESCRIPTIONS.get(query_type, query_type.value)


def _rule_for(query_type: BusinessQueryType) -> CapabilityRule | None:
    for rule in _CAPABILITY_RULES:
        if rule.query_type == query_type:
            return rule
    return None
