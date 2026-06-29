from app.capabilities.contract import Capability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.conversational_enrichment_capability import ConversationalEnrichmentCapability
from app.capability_registry.constants import (
    BUSINESS_PIPELINE,
    CONVERSATIONAL_ENRICHMENT,
    INSTITUTIONAL_KNOWLEDGE,
)


class CapabilityRegistry:
    """Catálogo oficial de Capabilities registradas explícitamente.

    No descubre, no planifica ni ejecuta lógica de negocio: solo expone
    las Capabilities conocidas del sistema.
    """

    def __init__(
        self,
        *,
        institutional_knowledge: InstitutionalKnowledgeCapability | None = None,
        business_pipeline: BusinessPipelineCapability | None = None,
        conversational_enrichment: ConversationalEnrichmentCapability | None = None,
    ) -> None:
        self._institutional_knowledge = (
            institutional_knowledge or InstitutionalKnowledgeCapability()
        )
        if business_pipeline is None:
            raise ValueError("business_pipeline capability es obligatoria en el catálogo")
        self._business_pipeline = business_pipeline
        self._conversational_enrichment = (
            conversational_enrichment or ConversationalEnrichmentCapability()
        )

    def get(self, step_id: str) -> Capability:
        if step_id == INSTITUTIONAL_KNOWLEDGE:
            return self._institutional_knowledge
        if step_id == BUSINESS_PIPELINE:
            return self._business_pipeline
        raise KeyError(f"Capability no registrada en el catálogo: {step_id}")

    def institutional_knowledge(self) -> InstitutionalKnowledgeCapability:
        """Capability registrada bajo ``INSTITUTIONAL_KNOWLEDGE``."""
        return self._institutional_knowledge

    def business_pipeline(self) -> BusinessPipelineCapability:
        """Capability registrada bajo ``BUSINESS_PIPELINE``."""
        return self._business_pipeline

    def conversational_enrichment(self) -> ConversationalEnrichmentCapability:
        """Capability registrada bajo ``CONVERSATIONAL_ENRICHMENT``."""
        return self._conversational_enrichment

    def registered_names(self) -> tuple[str, ...]:
        """Identificadores de pasos actualmente en el catálogo."""
        return (INSTITUTIONAL_KNOWLEDGE, BUSINESS_PIPELINE, CONVERSATIONAL_ENRICHMENT)
