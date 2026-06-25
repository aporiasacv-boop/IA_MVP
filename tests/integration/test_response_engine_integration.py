import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.database import SessionLocal
from app.main import app
from app.query_engine.query_planner import BusinessQueryPlanner
from app.query_executor.business_query_executor import BusinessQueryExecutor
from app.repositories.query_executor.cliente_repository import ClienteRepository
from app.repositories.query_executor.proveedor_repository import ProveedorRepository
from app.repositories.query_executor.system_repository import SystemRepository
from app.response_engine.deterministic_response_engine import DeterministicResponseEngine
from app.services.semantic_intent_builder import SemanticIntentBuilder


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def pipeline():
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL Data Mart no disponible: {exc}")

    components = {
        "intent_builder": SemanticIntentBuilder(),
        "planner": BusinessQueryPlanner(),
        "executor": BusinessQueryExecutor(
            ClienteRepository(session),
            ProveedorRepository(session),
            SystemRepository(session),
        ),
        "response_engine": DeterministicResponseEngine(),
    }
    yield components
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


def test_integration_full_pipeline_count_clientes(pipeline: dict) -> None:
    question = "¿Cuántos clientes existen?"
    intent = pipeline["intent_builder"].build(question)
    query = pipeline["planner"].plan(intent)
    query_result = pipeline["executor"].execute(query)
    response = pipeline["response_engine"].generate(query_result)

    assert query_result.success is True
    assert query_result.query_type == "COUNT_CLIENTES"
    assert response.success is True
    assert response.query_type == "COUNT_CLIENTES"
    assert response.answer.startswith("Actualmente existen ")
    assert "clientes registrados." in response.answer


def test_integration_full_pipeline_top_clientes(pipeline: dict) -> None:
    question = "Muéstrame los principales clientes"
    intent = pipeline["intent_builder"].build(question)
    query = pipeline["planner"].plan(intent)
    query_result = pipeline["executor"].execute(query)
    response = pipeline["response_engine"].generate(query_result)

    assert query_result.success is True
    assert query_result.query_type == "TOP_CLIENTES"
    assert response.success is True
    assert "Los principales clientes identificados son:" in response.answer


def test_integration_full_pipeline_max_proveedor_mes(pipeline: dict) -> None:
    question = "¿Qué proveedor tuvo más movimiento en junio?"
    intent = pipeline["intent_builder"].build(question)
    query = pipeline["planner"].plan(intent)
    query_result = pipeline["executor"].execute(query)
    response = pipeline["response_engine"].generate(query_result)

    assert query_result.query_type == "MAX_PROVEEDOR_MES"
    if query_result.success:
        assert response.success is True
        assert "El proveedor con mayor movimiento" in response.answer
    else:
        assert response.success is False
        assert "no existe una consulta empresarial configurada" in response.answer


def test_integration_respond_endpoint_count_clientes(integration_client: TestClient) -> None:
    response = integration_client.get(
        "/api/query/respond",
        params={"question": "¿Cuántos clientes existen?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["query_type"] == "COUNT_CLIENTES"
    assert "clientes registrados" in data["answer"]


def test_integration_respond_endpoint_count_proveedores(integration_client: TestClient) -> None:
    response = integration_client.get(
        "/api/query/respond",
        params={"question": "¿Cuántos proveedores existen?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["query_type"] == "COUNT_PROVEEDORES"
    assert "proveedores registrados" in data["answer"]


def test_integration_respond_endpoint_top_proveedores(integration_client: TestClient) -> None:
    response = integration_client.get(
        "/api/query/respond",
        params={"question": "Muéstrame los principales proveedores"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["query_type"] == "TOP_PROVEEDORES"
    assert "Los principales proveedores identificados son:" in data["answer"]


def test_integration_respond_endpoint_unsupported(integration_client: TestClient) -> None:
    response = integration_client.get(
        "/api/query/respond",
        params={"question": "Hola buenos dias"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "no existe una consulta empresarial configurada" in data["answer"]
