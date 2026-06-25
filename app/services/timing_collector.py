import time
from dataclasses import dataclass, field

from app.schemas.timings import ChatTimings


def elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


@dataclass
class TimingCollector:
    spell_correction_ms: float = 0
    synonym_resolution_ms: float = 0
    intent_normalization_ms: float = 0
    social_layer_ms: float = 0
    identity_layer_ms: float = 0
    token_optimization_ms: float = 0
    system_explanation_ms: float = 0
    capability_layer_ms: float = 0
    entity_extraction_ms: float = 0
    router_ms: float = 0
    deterministic_ms: float = 0
    query_ms: float = 0
    context_ms: float = 0
    prompt_ms: float = 0
    llm_ms: float = 0
    total_ms: float = 0
    _started_at: float = field(default_factory=time.perf_counter)

    def mark_total(self) -> None:
        self.total_ms = elapsed_ms(self._started_at)

    def to_model(self) -> ChatTimings:
        return ChatTimings(
            spell_correction_ms=self.spell_correction_ms,
            synonym_resolution_ms=self.synonym_resolution_ms,
            intent_normalization_ms=self.intent_normalization_ms,
            social_layer_ms=self.social_layer_ms,
            identity_layer_ms=self.identity_layer_ms,
            token_optimization_ms=self.token_optimization_ms,
            system_explanation_ms=self.system_explanation_ms,
            capability_layer_ms=self.capability_layer_ms,
            entity_extraction_ms=self.entity_extraction_ms,
            router_ms=self.router_ms,
            deterministic_ms=self.deterministic_ms,
            query_ms=self.query_ms,
            context_ms=self.context_ms,
            prompt_ms=self.prompt_ms,
            llm_ms=self.llm_ms,
            total_ms=self.total_ms,
        )
