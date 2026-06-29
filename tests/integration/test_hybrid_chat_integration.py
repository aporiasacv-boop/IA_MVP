import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.database import SessionLocal
from app.main import app


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def integration_client() -> TestClient:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        session.execute(
            text(
                """
                ALTER TABLE performance_metrics
                ADD COLUMN IF NOT EXISTS suggested_questions_count INTEGER
                """
            )
        )
        session.commit()
    except Exception as exc:
        session.close()
        pytest.skip(f"PostgreSQL Data Mart no disponible: {exc}")
    session.close()
    return TestClient(app)


def test_integration_hybrid_business_pipeline_count_clientes(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Cuántos clientes existen?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_pipeline"
    assert data["success"] is True
    assert "clientes registrados" in data["answer"]
    assert data["metadata"]["query_type"] == "COUNT_CLIENTES"
    assert data["metadata"]["confidence"] > 0
    assert data["suggestions"] is not None
    assert 3 <= len(data["suggestions"]["questions"]) <= 5
    assert data["metadata"]["suggested_questions_generated"] is True
    assert data["metadata"]["suggested_questions_count"] >= 3
    assert data["metadata"].get("insight_generated") is True
    assert "executive_insight" in data["metadata"]
    assert data["metadata"].get("proposals_generated") is True
    assert "business_copilot_proposals" in data["metadata"]
    assert data["metadata"]["executive_insight"]["executive_summary"]


def test_integration_hybrid_executive_insight_preserves_deterministic_answer(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Cuántos clientes existen?"},
    )
    assert response.status_code == 200
    data = response.json()
    deterministic_answer = data["answer"]
    assert "clientes registrados" in deterministic_answer
    assert data["metadata"].get("insight_generated") is True
    insight = data["metadata"]["executive_insight"]
    assert insight["business_interpretation"]
    second = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Cuántos clientes existen?"},
    ).json()
    assert second["answer"] == deterministic_answer


def test_integration_hybrid_business_pipeline_count_proveedores(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Cuántos proveedores existen?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_pipeline"
    assert data["success"] is True
    assert "proveedores registrados" in data["answer"]
    assert data["metadata"]["query_type"] == "COUNT_PROVEEDORES"


def test_integration_hybrid_business_pipeline_top_clientes(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "Muéstrame los principales clientes"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_pipeline"
    assert data["success"] is True
    assert data["metadata"]["query_type"] == "TOP_CLIENTES"
    assert "principales clientes" in data["answer"]


def test_integration_hybrid_slot_clarification_max_transaccion(
    integration_client: TestClient,
) -> None:
    session_id = "integration-slot-clarification"
    response = integration_client.post(
        "/api/chat/hybrid",
        json={
            "message": "¿Cuál fue la transacción más alta?",
            "session_id": session_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "slot_clarification"
    assert data["success"] is True
    assert "cliente" in data["answer"].lower()
    assert data["metadata"]["pending_query_type"] == "MAX_TRANSACCION_CLIENTE"
    assert data["metadata"]["missing_slots"] == ["cliente_codigo"]
    assert data["metadata"]["session_token"]


def test_integration_hybrid_conversation_memory_clarification_resolution(
    integration_client: TestClient,
) -> None:
    session_id = "integration-memory-clarification"
    first = integration_client.post(
        "/api/chat/hybrid",
        json={
            "message": "¿Cuál fue la transacción más alta?",
            "session_id": session_id,
        },
    )
    assert first.status_code == 200
    assert first.json()["handled_by"] == "slot_clarification"

    second = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "C001", "session_id": session_id},
    )
    assert second.status_code == 200
    data = second.json()
    assert data["handled_by"] == "conversation_memory"
    assert data["metadata"]["clarification_resolved"] is True
    assert data["metadata"]["query_type"] == "MAX_TRANSACCION_CLIENTE"
    assert data["metadata"]["context_hits"] >= 1
    assert data["metadata"]["clarification_resolutions"] >= 1


def test_integration_hybrid_conversation_memory_follow_up_month(
    integration_client: TestClient,
) -> None:
    session_id = "integration-memory-month"
    first = integration_client.post(
        "/api/chat/hybrid",
        json={
            "message": "¿Qué proveedor tuvo más movimiento en junio?",
            "session_id": session_id,
        },
    )
    assert first.status_code == 200
    assert first.json()["handled_by"] == "business_pipeline"

    second = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Y en julio?", "session_id": session_id},
    )
    assert second.status_code == 200
    data = second.json()
    assert data["handled_by"] == "conversation_memory"
    assert data["metadata"]["resolution_type"] == "follow_up"
    assert data["metadata"]["query_type"] == "MAX_PROVEEDOR_MES"


def test_integration_hybrid_product_identity_que_puedes_hacer(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Qué puedes hacer?"},
    )
    assert response.status_code == 200
    data = response.json()
    metadata = data["metadata"]
    if metadata.get("reasoning_governed"):
        assert metadata["pipeline_skipped"] is True
        assert metadata["governance_route"] == "institutional_knowledge"
        assert data["handled_by"] in {"product_identity", "business_knowledge"}
    else:
        assert data["handled_by"] == "conversation_gateway"
        assert metadata["gateway_decision"] == "conversation"
        assert metadata["gateway_reason"] == "capabilities"
    assert data["success"] is True
    assert "Olnatura Intelligence" in data["answer"]
    assert "response_time_ms" in metadata


def test_integration_hybrid_guided_fallback_ambiguous_negocio(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Cómo va el negocio?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "conversation_gateway"
    assert data["metadata"]["gateway_decision"] == "conversation"
    assert data["metadata"]["gateway_reason"] == "executive_general"


def test_integration_hybrid_dataset_info_data_types(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Qué tipos de datos tienes?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_pipeline"
    assert data["metadata"]["query_type"] == "DATASET_INFO"
    assert data["handled_by"] != "guided_fallback"


def test_integration_hybrid_guided_fallback_out_of_domain(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Quién ganó el mundial?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "guided_fallback"
    assert data["metadata"]["fallback_type"] == "OUT_OF_DOMAIN"
    assert "Olnatura" in data["answer"]


def test_integration_hybrid_legacy_chat_generic_question(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "¿Qué es un proveedor?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_knowledge"
    assert data["success"] is True
    assert "contraparte" in data["answer"].lower()


def test_integration_hybrid_legacy_chat_conversational_question(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "Explícame qué observas en estos datos."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "legacy_chat"
    assert data["success"] is True
    assert data["answer"]
    assert "response_mode" in data["metadata"]


def test_integration_hybrid_kpis_uses_business_pipeline(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "KPIs"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "business_pipeline"
    assert data["success"] is True
    assert data["metadata"]["query_type"] == "KPIS"
    assert "movimientos" in data["answer"].lower()


def test_integration_hybrid_resumen_junio_uses_executive_reasoning(
    integration_client: TestClient,
) -> None:
    response = integration_client.post(
        "/api/chat/hybrid",
        json={"message": "Resumen junio"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "executive_reasoning"
    assert data["success"] is True
    assert data["answer"]
