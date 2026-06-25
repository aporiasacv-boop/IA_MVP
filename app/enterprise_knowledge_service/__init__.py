"""Enterprise Knowledge Service (EKS) — servicio transversal de conocimiento."""

from app.enterprise_knowledge_service.service import (
    EnterpriseKnowledgePlatformService,
    EnterpriseKnowledgeService,
    get_enterprise_knowledge_platform_service,
    get_enterprise_knowledge_service,
)

__all__ = [
    "EnterpriseKnowledgePlatformService",
    "EnterpriseKnowledgeService",
    "get_enterprise_knowledge_platform_service",
    "get_enterprise_knowledge_service",
]
