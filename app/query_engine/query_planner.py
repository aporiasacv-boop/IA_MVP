from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.schemas.semantic_intent import BusinessFilters, BusinessSemanticIntent


class BusinessQueryPlanner:
    def plan(self, intent: BusinessSemanticIntent) -> BusinessQuery:
        operation = intent.operation
        target_entity = intent.target_entity
        source_entity = intent.source_entity
        filters = intent.filters

        if operation == BusinessOperation.COUNT and target_entity == BusinessEntity.CLIENTE:
            return BusinessQuery(
                query_type=BusinessQueryType.COUNT_CLIENTES,
                filters=self._serialize_filters(filters),
            )

        if operation == BusinessOperation.COUNT and target_entity == BusinessEntity.PROVEEDOR:
            return BusinessQuery(
                query_type=BusinessQueryType.COUNT_PROVEEDORES,
                filters=self._serialize_filters(filters),
            )

        if operation == BusinessOperation.TOP and target_entity == BusinessEntity.CLIENTE:
            return BusinessQuery(
                query_type=BusinessQueryType.TOP_CLIENTES,
                filters=self._serialize_filters(filters),
            )

        if operation == BusinessOperation.TOP and target_entity == BusinessEntity.PROVEEDOR:
            return BusinessQuery(
                query_type=BusinessQueryType.TOP_PROVEEDORES,
                filters=self._serialize_filters(filters),
            )

        if (
            operation == BusinessOperation.MAX
            and target_entity == BusinessEntity.PROVEEDOR
        ):
            return BusinessQuery(
                query_type=BusinessQueryType.MAX_PROVEEDOR_MES,
                filters=self._serialize_filters(filters),
            )

        if (
            operation == BusinessOperation.MAX
            and target_entity == BusinessEntity.TRANSACCION
        ):
            return BusinessQuery(
                query_type=BusinessQueryType.MAX_TRANSACCION_CLIENTE,
                filters=self._serialize_filters(filters),
            )

        if (
            operation == BusinessOperation.LOOKUP
            and target_entity == BusinessEntity.CLIENTE
            and source_entity == BusinessEntity.CUENTA
        ):
            return BusinessQuery(
                query_type=BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA,
                filters=self._serialize_filters(filters),
            )

        if operation == BusinessOperation.SYSTEM_INFO:
            return BusinessQuery(
                query_type=BusinessQueryType.SYSTEM_CAPABILITIES,
                filters=self._serialize_filters(filters),
            )

        if operation == BusinessOperation.DATA_COVERAGE:
            return BusinessQuery(
                query_type=BusinessQueryType.DATA_COVERAGE,
                filters=self._serialize_filters(filters),
            )

        if operation == BusinessOperation.DATASET_INFO:
            return BusinessQuery(
                query_type=BusinessQueryType.DATASET_INFO,
                filters=self._serialize_filters(filters),
            )

        if operation == BusinessOperation.KPIS:
            return BusinessQuery(
                query_type=BusinessQueryType.KPIS,
                filters=self._serialize_filters(filters),
            )

        return BusinessQuery(
            query_type=BusinessQueryType.UNSUPPORTED,
            filters=self._serialize_filters(filters),
        )

    @staticmethod
    def _serialize_filters(filters: BusinessFilters) -> dict:
        return filters.model_dump(exclude_none=True)
