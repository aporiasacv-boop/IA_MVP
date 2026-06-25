from app.capability_discovery.detector import is_capability_discovery
from app.coverage_recovery.patterns import (
    CAPABILITY_DISCOVERY_QUERIES,
    DATA_COVERAGE_QUERIES,
    DATASET_INFO_QUERIES,
    REGRESSION_BUSINESS_QUERIES,
)
from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_engine.query_types import BusinessQueryType
from app.services.semantic_intent_builder import SemanticIntentBuilder


class CoverageRecoveryHealthError(Exception):
    pass


_REGRESSION_EXPECTATIONS: dict[str, BusinessQueryType] = {
    "¿Cuántos clientes existen?": BusinessQueryType.COUNT_CLIENTES,
    "¿Cuántos proveedores existen?": BusinessQueryType.COUNT_PROVEEDORES,
    "¿Qué proveedor tuvo más movimiento?": BusinessQueryType.MAX_PROVEEDOR_MES,
    "¿Cuál fue la transacción más alta?": BusinessQueryType.MAX_TRANSACCION_CLIENTE,
    "Muéstrame los principales clientes": BusinessQueryType.TOP_CLIENTES,
}


def validate_coverage_recovery_health(
    *,
    builder: SemanticIntentBuilder | None = None,
    planner: BusinessQueryPlanner | None = None,
) -> dict:
    builder = builder or SemanticIntentBuilder()
    planner = planner or BusinessQueryPlanner()
    errors: list[str] = []

    for question in DATA_COVERAGE_QUERIES:
        if is_capability_discovery(question):
            errors.append(f"cobertura interceptada por discovery: {question}")
        query = planner.plan(builder.build(question))
        if query.query_type != BusinessQueryType.DATA_COVERAGE:
            errors.append(
                f"cobertura no planificada como DATA_COVERAGE: {question} -> {query.query_type.value}"
            )

    for question in DATASET_INFO_QUERIES:
        if is_capability_discovery(question):
            errors.append(f"dataset interceptado por discovery: {question}")
        query = planner.plan(builder.build(question))
        if query.query_type != BusinessQueryType.DATASET_INFO:
            errors.append(
                f"dataset no planificado como DATASET_INFO: {question} -> {query.query_type.value}"
            )

    for question in CAPABILITY_DISCOVERY_QUERIES:
        if not is_capability_discovery(question):
            errors.append(f"capability no detectada: {question}")

    for question in REGRESSION_BUSINESS_QUERIES:
        expected = _REGRESSION_EXPECTATIONS[question]
        query = planner.plan(builder.build(question))
        if query.query_type != expected:
            errors.append(
                f"regresión empresarial: {question} -> {query.query_type.value}, esperado {expected.value}"
            )

    if errors:
        raise CoverageRecoveryHealthError("; ".join(errors))

    return {
        "data_coverage_queries": len(DATA_COVERAGE_QUERIES),
        "dataset_info_queries": len(DATASET_INFO_QUERIES),
        "capability_discovery_queries": len(CAPABILITY_DISCOVERY_QUERIES),
        "regression_queries": len(REGRESSION_BUSINESS_QUERIES),
        "status": "ok",
    }
