from unittest.mock import MagicMock

import pytest

from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.business_query_executor import BusinessQueryExecutor


@pytest.fixture
def cliente_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def proveedor_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def system_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def executor(
    cliente_repository: MagicMock,
    proveedor_repository: MagicMock,
    system_repository: MagicMock,
) -> BusinessQueryExecutor:
    return BusinessQueryExecutor(cliente_repository, proveedor_repository, system_repository)


def test_execute_count_clientes(
    executor: BusinessQueryExecutor,
    cliente_repository: MagicMock,
) -> None:
    cliente_repository.count_clientes.return_value = 50
    query = BusinessQuery(query_type=BusinessQueryType.COUNT_CLIENTES)

    result = executor.execute(query)

    assert result.success is True
    assert result.query_type == "COUNT_CLIENTES"
    assert result.data == {"total": 50}
    cliente_repository.count_clientes.assert_called_once_with()


def test_execute_count_proveedores(
    executor: BusinessQueryExecutor,
    proveedor_repository: MagicMock,
) -> None:
    proveedor_repository.count_proveedores.return_value = 766
    query = BusinessQuery(query_type=BusinessQueryType.COUNT_PROVEEDORES)

    result = executor.execute(query)

    assert result.success is True
    assert result.query_type == "COUNT_PROVEEDORES"
    assert result.data == {"total": 766}
    proveedor_repository.count_proveedores.assert_called_once_with()


def test_execute_top_clientes(
    executor: BusinessQueryExecutor,
    cliente_repository: MagicMock,
) -> None:
    cliente_repository.top_clientes.return_value = [
        {
            "ranking": 1,
            "cliente_codigo": "C001",
            "cliente_nombre": "Cliente Uno",
            "movimientos": 10,
            "monto_total": 1000.0,
            "monto_promedio": 100.0,
        }
    ]
    query = BusinessQuery(query_type=BusinessQueryType.TOP_CLIENTES)

    result = executor.execute(query)

    assert result.success is True
    assert result.query_type == "TOP_CLIENTES"
    assert len(result.data["items"]) == 1
    assert result.metadata["limit"] == 10
    cliente_repository.top_clientes.assert_called_once_with(limit=10)


def test_execute_top_clientes_with_limit(
    executor: BusinessQueryExecutor,
    cliente_repository: MagicMock,
) -> None:
    cliente_repository.top_clientes.return_value = []
    query = BusinessQuery(
        query_type=BusinessQueryType.TOP_CLIENTES,
        filters={"limit": 5},
    )

    result = executor.execute(query)

    assert result.success is True
    assert result.metadata["limit"] == 5
    cliente_repository.top_clientes.assert_called_once_with(limit=5)


def test_execute_top_proveedores(
    executor: BusinessQueryExecutor,
    proveedor_repository: MagicMock,
) -> None:
    proveedor_repository.top_proveedores.return_value = [
        {
            "ranking": 1,
            "proveedor_codigo": "P001",
            "proveedor_nombre": "Proveedor Uno",
            "movimientos": 20,
            "monto_total": 2000.0,
            "monto_promedio": 100.0,
        }
    ]
    query = BusinessQuery(query_type=BusinessQueryType.TOP_PROVEEDORES)

    result = executor.execute(query)

    assert result.success is True
    assert result.query_type == "TOP_PROVEEDORES"
    assert len(result.data["items"]) == 1
    proveedor_repository.top_proveedores.assert_called_once_with(limit=10)


def test_execute_max_proveedor_mes(
    executor: BusinessQueryExecutor,
    proveedor_repository: MagicMock,
) -> None:
    proveedor_repository.max_proveedor_mes.return_value = {
        "anio": 2025,
        "mes": 6,
        "proveedor_codigo": "P001",
        "proveedor_nombre": "Proveedor Uno",
        "movimientos": 30,
        "monto_total": 3000.0,
        "monto_promedio": 100.0,
    }
    query = BusinessQuery(
        query_type=BusinessQueryType.MAX_PROVEEDOR_MES,
        filters={"mes": 6},
    )

    result = executor.execute(query)

    assert result.success is True
    assert result.query_type == "MAX_PROVEEDOR_MES"
    assert result.data["proveedor_codigo"] == "P001"
    proveedor_repository.max_proveedor_mes.assert_called_once_with(mes=6, anio=None)


def test_execute_max_proveedor_mes_with_anio(
    executor: BusinessQueryExecutor,
    proveedor_repository: MagicMock,
) -> None:
    proveedor_repository.max_proveedor_mes.return_value = {
        "anio": 2025,
        "mes": 6,
        "proveedor_codigo": "P001",
        "proveedor_nombre": "Proveedor Uno",
        "movimientos": 30,
        "monto_total": 3000.0,
        "monto_promedio": 100.0,
    }
    query = BusinessQuery(
        query_type=BusinessQueryType.MAX_PROVEEDOR_MES,
        filters={"mes": 6, "anio": 2025},
    )

    result = executor.execute(query)

    assert result.success is True
    proveedor_repository.max_proveedor_mes.assert_called_once_with(mes=6, anio=2025)


def test_execute_max_proveedor_mes_missing_filter(
    executor: BusinessQueryExecutor,
    proveedor_repository: MagicMock,
) -> None:
    query = BusinessQuery(query_type=BusinessQueryType.MAX_PROVEEDOR_MES)

    result = executor.execute(query)

    assert result.success is False
    assert result.data == {}
    assert result.metadata["reason"] == "missing_required_filter"
    proveedor_repository.max_proveedor_mes.assert_not_called()


def test_execute_max_proveedor_mes_no_data(
    executor: BusinessQueryExecutor,
    proveedor_repository: MagicMock,
) -> None:
    proveedor_repository.max_proveedor_mes.return_value = None
    query = BusinessQuery(
        query_type=BusinessQueryType.MAX_PROVEEDOR_MES,
        filters={"mes": 6},
    )

    result = executor.execute(query)

    assert result.success is False
    assert result.metadata["reason"] == "no_data_for_period"


def test_execute_system_capabilities(
    executor: BusinessQueryExecutor,
    system_repository: MagicMock,
) -> None:
    system_repository.get_system_capabilities.return_value = {
        "clientes": True,
        "proveedores": True,
        "cuentas": True,
        "kpis": True,
        "top_clientes": True,
        "top_proveedores": True,
        "actividad_mensual": True,
        "insights": True,
    }
    query = BusinessQuery(query_type=BusinessQueryType.SYSTEM_CAPABILITIES)

    result = executor.execute(query)

    assert result.success is True
    assert result.query_type == "SYSTEM_CAPABILITIES"
    assert result.data["clientes"] is True
    system_repository.get_system_capabilities.assert_called_once_with()


def test_execute_data_coverage(
    executor: BusinessQueryExecutor,
    system_repository: MagicMock,
) -> None:
    system_repository.get_data_coverage.return_value = {
        "fecha_min": "2025-01-01",
        "fecha_max": "2025-12-31",
    }
    query = BusinessQuery(query_type=BusinessQueryType.DATA_COVERAGE)

    result = executor.execute(query)

    assert result.success is True
    assert result.query_type == "DATA_COVERAGE"
    assert result.data["fecha_min"] == "2025-01-01"
    system_repository.get_data_coverage.assert_called_once_with()


def test_execute_dataset_info(
    executor: BusinessQueryExecutor,
    system_repository: MagicMock,
) -> None:
    system_repository.get_dataset_info.return_value = {
        "total_movimientos": 386_480,
        "total_clientes": 50,
        "total_proveedores": 766,
    }
    query = BusinessQuery(query_type=BusinessQueryType.DATASET_INFO)

    result = executor.execute(query)

    assert result.success is True
    assert result.query_type == "DATASET_INFO"
    assert result.data["total_movimientos"] == 386_480
    system_repository.get_dataset_info.assert_called_once_with()


@pytest.mark.parametrize(
    "query_type",
    [
        BusinessQueryType.UNSUPPORTED,
        BusinessQueryType.MAX_TRANSACCION_CLIENTE,
        BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA,
    ],
)
def test_execute_unsupported_query_types(
    executor: BusinessQueryExecutor,
    query_type: BusinessQueryType,
) -> None:
    query = BusinessQuery(query_type=query_type, filters={"cliente_codigo": "C001"})

    result = executor.execute(query)

    assert result.success is False
    assert result.query_type == query_type.value
    assert result.data == {}
    assert result.metadata["reason"] == "unsupported_query_type"
