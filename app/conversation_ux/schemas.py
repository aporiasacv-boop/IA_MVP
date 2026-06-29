from dataclasses import dataclass, field

from app.conversation_ux.classifier import ConversationCategory


@dataclass(frozen=True)
class ConversationGenerationContext:
    """Información validada para redacción conversacional con LLM."""

    user_message: str
    conversation_category: ConversationCategory
    pipeline_answer: str
    template_answer: str
    dataset_snapshot: dict = field(default_factory=dict)
    capabilities: tuple[str, ...] = ()
    capability_examples: tuple[str, ...] = ()
    suggested_questions: tuple[str, ...] = ()
    pipeline_metadata: dict = field(default_factory=dict)
