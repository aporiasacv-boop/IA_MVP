import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.database import SessionLocal
from app.main import app
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.business_query_executor import BusinessQueryExecutor
from app.repositories.query_executor.cliente_repository import ClienteRepository
from app.repositories.query_executor.proveedor_repository import ProveedorRepository
from app.repositories.query_executor.system_repository import SystemRepository
from app.services.semantic_intent_builder import SemanticIntentBuilder
from app.query_engine.query_planner import BusinessQueryPlanner


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def datamart_executor() -> BusinessQueryExecutor:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL Data Mart no disponible: {exc}")

    executor = BusinessQueryExecutor(
        ClienteRepository(session),
        ProveedorRepository(session),
        SystemRepository(session),
    )
    yield executor
    session.close()


@pytest.fixture(scope="module")
def integration_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL Data Mart no disponible: {exc}")
    session.close()
    return TestClient(app)


def test_integration_count_clientes(datamart_executor: BusinessQueryExecutor) -> None:
    result = datamart_executor.execute(
        BusinessQuery(query_type=BusinessQueryType.COUNT_CLIENTES),
    )

    assert result.success is True
    assert result.query_type == "COUNT_CLIENTES"
    assert isinstance(result.data["total"], int)
    assert result.data["total"] >= 0


def test_integration_count_proveedores(datamart_executor: BusinessQueryExecutor) -> None:
    result = datamart_executor.execute(
        BusinessQuery(query_type=BusinessQueryType.COUNT_PROVEEDORES),
    )

    assert result.success is True
    assert result.query_type == "COUNT_PROVEEDORES"
    assert isinstance(result.data["total"], int)
    assert result.data["total"] >= 0


def test_integration_top_clientes(datamart_executor: BusinessQueryExecutor) -> None:
    result = datamart_executor.execute(
        BusinessQuery(query_type=BusinessQueryType.TOP_CLIENTES, filters={"limit": 5}),
    )

    assert result.success is True
    assert result.query_type == "TOP_CLIENTES"
    assert isinstance(result.data["items"], list)
    if result.data["items"]:
        item = result.data["items"][0]
        assert "cliente_codigo" in item
        assert "cliente_nombre" in item
        assert "movimientos" in item


def test_integration_top_proveedores(datamart_executor: BusinessQueryExecutor) -> None:
    result = datamart_executor.execute(
        BusinessQuery(query_type=BusinessQueryType.TOP_PROVEEDORES, filters={"limit": 5}),
    )

    assert result.success is True
    assert result.query_type == "TOP_PROVEEDORES"
    assert isinstance(result.data["items"], list)
    if result.data["items"]:
        item = result.data["items"][0]
        assert "proveedor_codigo" in item
        assert "proveedor_nombre" in item
        assert "movimientos" in item


def test_integration_execute_endpoint_count_clientes(integration_client: TestClient) -> None:
    response = integration_client.get(
        "/api/query/execute",
        params={"question": "¿Cuántos clientes existen?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "COUNT_CLIENTES"
    assert data["success"] is True
    assert "total" in data["data"]


def test_integration_execute_endpoint_top_clientes(integration_client: TestClient) -> None:
    builder = SemanticIntentBuilder()
    planner = BusinessQueryPlanner()
    intent = builder.build("Muéstrame los principales clientes")
    planned = planner.plan(intent)
    assert planned.query_type == BusinessQueryType.TOP_CLIENTES

    response = integration_client.get(
        "/api/query/execute",
        params={"question": "Muéstrame los principales clientes"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "TOP_CLIENTES"
    assert data["success"] is True
    assert "items" in data["data"]
