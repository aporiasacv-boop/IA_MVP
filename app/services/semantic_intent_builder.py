import time

from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation
from app.observability.performance_metrics import elapsed_ms, get_active_collector
from app.schemas.entity import EntityResolution
from app.schemas.operation import OperationResolution
from app.schemas.semantic_intent import BusinessFilters, BusinessSemanticIntent
from app.services.entity_resolver import EntityResolver
from app.services.operation_resolver import OperationResolver
from app.services.target_entity_resolver import TargetEntityResolver
from app.utils.text_normalizer import normalize_text

MONTH_TO_INT: dict[str, int] = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


class SemanticIntentBuilder:
    def __init__(
        self,
        operation_resolver: OperationResolver | None = None,
        entity_resolver: EntityResolver | None = None,
        target_entity_resolver: TargetEntityResolver | None = None,
    ) -> None:
        self._operation_resolver = operation_resolver or OperationResolver()
        self._entity_resolver = entity_resolver or EntityResolver()
        self._target_entity_resolver = target_entity_resolver or TargetEntityResolver()

    def build(self, question: str) -> BusinessSemanticIntent:
        collector = get_active_collector()

        operation_started = time.perf_counter()
        operation_resolution = self._operation_resolver.resolve(question)
        if collector is not None:
            collector.record_stage("operation", elapsed_ms(operation_started))

        entity_started = time.perf_counter()
        entity_resolution = self._entity_resolver.resolve(question)
        if collector is not None:
            collector.record_stage("entity", elapsed_ms(entity_started))

        operation = self._reconcile_operation(
            operation_resolution.operation,
            entity_resolution,
        )
        target_entity, source_entity = self._target_entity_resolver.resolve(
            operation,
            entity_resolution.entities,
        )
        filters = self._build_filters(entity_resolution)
        confidence = self._calculate_confidence(operation_resolution, entity_resolution)

        return BusinessSemanticIntent(
            operation=operation,
            target_entity=target_entity,
            source_entity=source_entity,
            filters=filters,
            confidence=confidence,
            source_question=question,
        )

    @staticmethod
    def _reconcile_operation(
        operation: BusinessOperation | None,
        entity_resolution: EntityResolution,
    ) -> BusinessOperation | None:
        """Reglas v1 de reconciliacion operacion-entidad cuando el resolver es ambiguo."""
        entity_set = set(entity_resolution.entities)
        codigo = entity_resolution.parameters.get("codigo")

        if (
            BusinessEntity.CLIENTE in entity_set
            and BusinessEntity.CUENTA in entity_set
        ):
            return BusinessOperation.LOOKUP

        if operation is not None:
            return operation

        if (
            BusinessEntity.TRANSACCION in entity_set
            and BusinessEntity.CLIENTE in entity_set
        ):
            return BusinessOperation.MAX

        if BusinessEntity.TRANSACCION in entity_set:
            return BusinessOperation.MAX

        if (
            BusinessEntity.PROVEEDOR in entity_set
            and BusinessEntity.MOVIMIENTO in entity_set
        ):
            return BusinessOperation.MAX

        return operation

    def _build_filters(self, entity_resolution: EntityResolution) -> BusinessFilters:
        filters = BusinessFilters()
        entity_set = set(entity_resolution.entities)
        parameters = entity_resolution.parameters

        codigo = parameters.get("codigo")
        if codigo:
            if BusinessEntity.CUENTA in entity_set:
                filters.cuenta_codigo = codigo
            elif BusinessEntity.CLIENTE in entity_set:
                filters.cliente_codigo = codigo
            elif BusinessEntity.PROVEEDOR in entity_set:
                filters.proveedor_codigo = codigo

        mes = parameters.get("mes")
        if mes:
            filters.mes = MONTH_TO_INT.get(normalize_text(mes))

        anio = parameters.get("anio")
        if anio is not None:
            filters.anio = anio

        return filters

    @staticmethod
    def _calculate_confidence(
        operation_resolution: OperationResolution,
        entity_resolution: EntityResolution,
    ) -> float:
        return round(
            (operation_resolution.confidence + entity_resolution.confidence) / 2,
            4,
        )
