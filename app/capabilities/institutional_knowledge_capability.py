from app.enterprise_knowledge_service.integration.consumers import (
    knowledge_for_capability_discovery,
    knowledge_for_chat,
)
from app.schemas.hybrid_chat import HybridChatResult


class InstitutionalKnowledgeCapability:
    """Resuelve consultas de identidad del producto y conocimiento institucional.

    Encapsula el comportamiento previo de ``knowledge_for_chat()`` sin alterar
    la lógica ni los componentes internos de EKS.
    """

    def execute(
        self,
        message: str,
        session_id: str | None = None,
    ) -> HybridChatResult | None:
        _ = session_id
        identity_result, knowledge_result = knowledge_for_chat(message)
        if identity_result is not None:
            return identity_result
        if knowledge_result is not None:
            return knowledge_result
        return None

    def resolve_system_capabilities(self, message: str) -> HybridChatResult:
        """Resuelve consultas clasificadas como SYSTEM_CAPABILITIES por el planner."""
        resolved = self.execute(message)
        if resolved is not None:
            return resolved

        payload = knowledge_for_capability_discovery()
        answer, capabilities, examples = (
            payload.answer,
            payload.capabilities,
            payload.examples,
        )
        return HybridChatResult(
            handled_by="business_knowledge",
            success=True,
            answer=answer,
            metadata={
                "handled_by": "business_knowledge",
                "query_type": "SYSTEM_CAPABILITIES",
                "confidence": 1.0,
                "knowledge_source": "knowledge_pack/executive/capacidades-asistente.md",
                "knowledge_match_type": "system_capabilities_redirect",
                "capabilities_count": len(capabilities),
                "example_questions_count": len(examples),
            },
        )
