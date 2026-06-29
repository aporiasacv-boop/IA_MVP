from dataclasses import dataclass, field


@dataclass
class ConversationResponseMetrics:
    generation_ms: float = 0.0
    provider: str = ""
    model: str = ""
    fallback_used: bool = False
    llm_applied: bool = False

    def to_metadata(self) -> dict:
        return {
            "conversation_llm_generation_ms": round(self.generation_ms, 2),
            "conversation_llm_provider": self.provider,
            "conversation_llm_model": self.model,
            "conversation_llm_fallback_used": self.fallback_used,
            "conversation_llm_applied": self.llm_applied,
        }


_metrics = ConversationResponseMetrics()


def record_generation(metrics: ConversationResponseMetrics) -> None:
    global _metrics
    _metrics = metrics


def get_last_metrics() -> ConversationResponseMetrics:
    return _metrics


def reset_metrics() -> None:
    global _metrics
    _metrics = ConversationResponseMetrics()
