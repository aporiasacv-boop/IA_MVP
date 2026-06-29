from dataclasses import dataclass

from app.capabilities.business_resolution_capability import BusinessResolutionStage
from app.capabilities.business_understanding_capability import BusinessUnderstandingStage
from app.capabilities.executive_reasoning_capability import ExecutiveReasoningStage
from app.capabilities.guided_fallback_capability import GuidedFallbackStage
from app.conversation_memory.context_resolver import ContextResolution
from app.conversation_memory.schemas import ConversationContext
from app.slot_clarification.schemas import SlotClarificationResult


@dataclass(frozen=True)
class BusinessPipelineState:
    """Estado compartido entre etapas del Business Pipeline."""

    session_id: str
    context: ConversationContext
    memory_resolution: ContextResolution | None
    conversation_memory_stage_ms: float | None = None
    business_understanding: BusinessUnderstandingStage | None = None
    slot_clarification: SlotClarificationResult | None = None
    slot_clarification_stage_ms: float | None = None
    business_resolution: BusinessResolutionStage | None = None
    executive_reasoning: ExecutiveReasoningStage | None = None
    guided_fallback: GuidedFallbackStage | None = None
