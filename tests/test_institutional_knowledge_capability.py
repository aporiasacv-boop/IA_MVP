from unittest.mock import MagicMock, patch

from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.schemas.hybrid_chat import HybridChatResult


def test_execute_returns_identity_result_first():
    capability = InstitutionalKnowledgeCapability()
    identity = HybridChatResult(
        handled_by="product_identity",
        success=True,
        answer="Soy Olnatura Intelligence.",
        metadata={"handled_by": "product_identity"},
    )
    knowledge = HybridChatResult(
        handled_by="business_knowledge",
        success=True,
        answer="No debería usarse.",
        metadata={"handled_by": "business_knowledge"},
    )

    with patch(
        "app.capabilities.institutional_knowledge_capability.knowledge_for_chat",
        return_value=(identity, knowledge),
    ):
        result = capability.execute("como te llamas")

    assert result is identity


def test_execute_returns_knowledge_when_no_identity():
    capability = InstitutionalKnowledgeCapability()
    knowledge = HybridChatResult(
        handled_by="business_knowledge",
        success=True,
        answer="Un cliente es...",
        metadata={"handled_by": "business_knowledge"},
    )

    with patch(
        "app.capabilities.institutional_knowledge_capability.knowledge_for_chat",
        return_value=(None, knowledge),
    ):
        result = capability.execute("que es un cliente")

    assert result is knowledge


def test_execute_returns_none_when_no_match():
    capability = InstitutionalKnowledgeCapability()

    with patch(
        "app.capabilities.institutional_knowledge_capability.knowledge_for_chat",
        return_value=(None, None),
    ):
        result = capability.execute("cuantos clientes existen")

    assert result is None


def test_resolve_system_capabilities_reuses_execute_when_matched():
    capability = InstitutionalKnowledgeCapability()
    knowledge = HybridChatResult(
        handled_by="business_knowledge",
        success=True,
        answer="Puedo consultar clientes.",
        metadata={"query_type": "BUSINESS_KNOWLEDGE", "knowledge_match_type": "capabilities"},
    )

    with patch.object(capability, "execute", return_value=knowledge):
        result = capability.resolve_system_capabilities("¿Qué puedo preguntarte?")

    assert result is knowledge


def test_resolve_system_capabilities_falls_back_to_capability_discovery():
    capability = InstitutionalKnowledgeCapability()
    payload = MagicMock()
    payload.answer = "Puedo consultar clientes y proveedores."
    payload.capabilities = ["clientes", "proveedores"]
    payload.examples = ["¿Cuántos clientes existen?"]

    with patch.object(capability, "execute", return_value=None), patch(
        "app.capabilities.institutional_knowledge_capability.knowledge_for_capability_discovery",
        return_value=payload,
    ):
        result = capability.resolve_system_capabilities("capacidades del sistema")

    assert result.handled_by == "business_knowledge"
    assert result.metadata["query_type"] == "SYSTEM_CAPABILITIES"
    assert result.metadata["knowledge_match_type"] == "system_capabilities_redirect"
    assert result.metadata["capabilities_count"] == 2
    assert result.metadata["example_questions_count"] == 1
    assert "clientes" in result.answer.lower()
