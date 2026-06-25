from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.query_result import BusinessQueryResult
from app.repositories.query_executor.cliente_repository import ClienteRepository
from app.repositories.query_executor.proveedor_repository import ProveedorRepository
from app.repositories.query_executor.system_repository import SystemRepository


class BusinessQueryExecutor:
    def __init__(
        self,
        cliente_repository: ClienteRepository,
        proveedor_repository: ProveedorRepository,
        system_repository: SystemRepository,
    ) -> None:
        self._cliente_repository = cliente_repository
        self._proveedor_repository = proveedor_repository
        self._system_repository = system_repository

    def execute(self, query: BusinessQuery) -> BusinessQueryResult:
        query_type = query.query_type
        filters = query.filters
        metadata = {"filters": filters}

        if query_type == BusinessQueryType.COUNT_CLIENTES:
            total = self._cliente_repository.count_clientes()
            return BusinessQueryResult(
                query_type=query_type.value,
                success=True,
                data={"total": total},
                metadata=metadata,
            )

        if query_type == BusinessQueryType.COUNT_PROVEEDORES:
            total = self._proveedor_repository.count_proveedores()
            return BusinessQueryResult(
                query_type=query_type.value,
                success=True,
                data={"total": total},
                metadata=metadata,
            )

        if query_type == BusinessQueryType.TOP_CLIENTES:
            limit = int(filters.get("limit", 10))
            items = self._cliente_repository.top_clientes(limit=limit)
            metadata["limit"] = limit
            return BusinessQueryResult(
                query_type=query_type.value,
                success=True,
                data={"items": items},
                metadata=metadata,
            )

        if query_type == BusinessQueryType.TOP_PROVEEDORES:
            limit = int(filters.get("limit", 10))
            items = self._proveedor_repository.top_proveedores(limit=limit)
            metadata["limit"] = limit
            return BusinessQueryResult(
                query_type=query_type.value,
                success=True,
                data={"items": items},
                metadata=metadata,
            )

        if query_type == BusinessQueryType.MAX_PROVEEDOR_MES:
            mes = filters.get("mes")
            if mes is None:
                return self._failure(
                    query_type,
                    metadata,
                    reason="missing_required_filter",
                    filter_name="mes",
                )

            proveedor = self._proveedor_repository.max_proveedor_mes(
                mes=int(mes),
                anio=filters.get("anio"),
            )
            if proveedor is None:
                return self._failure(
                    query_type,
                    metadata,
                    reason="no_data_for_period",
                )

            return BusinessQueryResult(
                query_type=query_type.value,
                success=True,
                data=proveedor,
                metadata=metadata,
            )

        if query_type == BusinessQueryType.SYSTEM_CAPABILITIES:
            capabilities = self._system_repository.get_system_capabilities()
            return BusinessQueryResult(
                query_type=query_type.value,
                success=True,
                data=capabilities,
                metadata=metadata,
            )

        if query_type == BusinessQueryType.DATA_COVERAGE:
            coverage = self._system_repository.get_data_coverage()
            return BusinessQueryResult(
                query_type=query_type.value,
                success=True,
                data=coverage,
                metadata=metadata,
            )

        if query_type == BusinessQueryType.DATASET_INFO:
            dataset = self._system_repository.get_dataset_info()
            return BusinessQueryResult(
                query_type=query_type.value,
                success=True,
                data=dataset,
                metadata=metadata,
            )

        return self._failure(
            query_type,
            metadata,
            reason="unsupported_query_type",
        )

    @staticmethod
    def _failure(
        query_type: BusinessQueryType,
        metadata: dict,
        *,
        reason: str,
        filter_name: str | None = None,
    ) -> BusinessQueryResult:
        failure_metadata = {**metadata, "reason": reason}
        if filter_name is not None:
            failure_metadata["filter_name"] = filter_name
        return BusinessQueryResult(
            query_type=query_type.value,
            success=False,
            data={},
            metadata=failure_metadata,
        )
