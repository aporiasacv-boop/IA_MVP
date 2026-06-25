import pytest

from app.query_executor.query_result import BusinessQueryResult
from app.response_engine.deterministic_response_engine import DeterministicResponseEngine
from app.response_engine.response_templates import UNSUPPORTED_TEMPLATE


@pytest.fixture
def engine() -> DeterministicResponseEngine:
    return DeterministicResponseEngine()


def test_generate_count_clientes(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="COUNT_CLIENTES",
            success=True,
            data={"total": 50},
        )
    )

    assert result.success is True
    assert result.query_type == "COUNT_CLIENTES"
    assert result.answer == "Actualmente existen 50 clientes registrados."


def test_generate_count_proveedores(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="COUNT_PROVEEDORES",
            success=True,
            data={"total": 766},
        )
    )

    assert result.success is True
    assert result.query_type == "COUNT_PROVEEDORES"
    assert result.answer == "Actualmente existen 766 proveedores registrados."


def test_generate_top_clientes(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="TOP_CLIENTES",
            success=True,
            data={
                "items": [
                    {
                        "ranking": 1,
                        "cliente_codigo": "C001",
                        "cliente_nombre": "Cliente Uno",
                        "movimientos": 10,
                        "monto_total": 1000.0,
                        "monto_promedio": 100.0,
                    },
                    {
                        "ranking": 2,
                        "cliente_codigo": "C002",
                        "cliente_nombre": "Cliente Dos",
                        "movimientos": 8,
                        "monto_total": 800.0,
                        "monto_promedio": 100.0,
                    },
                ]
            },
        )
    )

    assert result.success is True
    assert result.query_type == "TOP_CLIENTES"
    assert "Los principales clientes identificados son:" in result.answer
    assert "1. Cliente Uno (C001) — 10 movimientos" in result.answer
    assert "2. Cliente Dos (C002) — 8 movimientos" in result.answer


def test_generate_top_clientes_empty(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="TOP_CLIENTES",
            success=True,
            data={"items": []},
        )
    )

    assert result.success is True
    assert "No se encontraron clientes para mostrar." in result.answer


def test_generate_top_proveedores(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="TOP_PROVEEDORES",
            success=True,
            data={
                "items": [
                    {
                        "ranking": 1,
                        "proveedor_codigo": "P001",
                        "proveedor_nombre": "Proveedor Uno",
                        "movimientos": 20,
                        "monto_total": 2000.0,
                        "monto_promedio": 100.0,
                    }
                ]
            },
        )
    )

    assert result.success is True
    assert result.query_type == "TOP_PROVEEDORES"
    assert "Los principales proveedores identificados son:" in result.answer
    assert "1. Proveedor Uno (P001) — 20 movimientos" in result.answer


def test_generate_max_proveedor_mes(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="MAX_PROVEEDOR_MES",
            success=True,
            data={
                "anio": 2025,
                "mes": 6,
                "proveedor_codigo": "P001",
                "proveedor_nombre": "Proveedor Uno",
                "movimientos": 30,
                "monto_total": 3000.0,
                "monto_promedio": 100.0,
            },
        )
    )

    assert result.success is True
    assert result.query_type == "MAX_PROVEEDOR_MES"
    assert (
        result.answer
        == "El proveedor con mayor movimiento durante el mes consultado fue Proveedor Uno "
        "con un volumen total de 3,000.00."
    )


def test_generate_unsupported_query_type(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="UNSUPPORTED",
            success=False,
            data={},
            metadata={"reason": "unsupported_query_type"},
        )
    )

    assert result.success is False
    assert result.query_type == "UNSUPPORTED"
    assert result.answer == UNSUPPORTED_TEMPLATE


def test_generate_failed_execution(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="MAX_PROVEEDOR_MES",
            success=False,
            data={},
            metadata={"reason": "no_data_for_period"},
        )
    )

    assert result.success is False
    assert result.answer == UNSUPPORTED_TEMPLATE


def test_generate_unknown_successful_query_type(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="LOOKUP_CLIENTE_BY_CUENTA",
            success=True,
            data={"cliente_codigo": "C001"},
        )
    )

    assert result.success is False
    assert result.answer == UNSUPPORTED_TEMPLATE


def test_generate_system_capabilities(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="SYSTEM_CAPABILITIES",
            success=True,
            data={
                "clientes": True,
                "proveedores": True,
                "cuentas": True,
                "kpis": True,
                "top_clientes": True,
                "top_proveedores": True,
                "actividad_mensual": True,
                "insights": True,
            },
        )
    )

    assert result.success is True
    assert result.query_type == "SYSTEM_CAPABILITIES"
    assert "Actualmente puedo consultar información relacionada con:" in result.answer
    assert "• Clientes" in result.answer
    assert "• Rankings" in result.answer
    assert "• Insights empresariales" in result.answer


def test_generate_data_coverage(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="DATA_COVERAGE",
            success=True,
            data={"fecha_min": "2025-01-01", "fecha_max": "2025-12-31"},
        )
    )

    assert result.success is True
    assert result.query_type == "DATA_COVERAGE"
    assert (
        result.answer
        == "Los datos disponibles abarcan desde el 2025-01-01 hasta el 2025-12-31."
    )


def test_generate_dataset_info(engine: DeterministicResponseEngine) -> None:
    result = engine.generate(
        BusinessQueryResult(
            query_type="DATASET_INFO",
            success=True,
            data={
                "total_movimientos": 386_480,
                "total_clientes": 50,
                "total_proveedores": 766,
            },
        )
    )

    assert result.success is True
    assert result.query_type == "DATASET_INFO"
    assert "386,480 movimientos" in result.answer
    assert "50 clientes" in result.answer
    assert "766 proveedores" in result.answer
