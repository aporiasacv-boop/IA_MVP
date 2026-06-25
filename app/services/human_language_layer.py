import time
from dataclasses import dataclass, field

from app.services.intent_normalizer import IntentNormalizer
from app.services.spell_corrector import SpellCorrector


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


@dataclass(frozen=True)
class HumanLanguageResult:
    original_question: str
    normalized_question: str
    corrections_applied: list[str] = field(default_factory=list)
    intent_hint: str | None = None


class HumanLanguageLayer:
    def __init__(
        self,
        spell_corrector: SpellCorrector | None = None,
        intent_normalizer: IntentNormalizer | None = None,
    ) -> None:
        self.spell_corrector = spell_corrector or SpellCorrector()
        self.intent_normalizer = intent_normalizer or IntentNormalizer()

    def process(
        self,
        question: str,
        timings: object | None = None,
    ) -> HumanLanguageResult:
        original = question.strip()

        spell_started = time.perf_counter()
        spell_result = self.spell_corrector.correct(original)
        if timings is not None:
            timings.spell_correction_ms = _elapsed_ms(spell_started)

        normalized, intent_hint = self.intent_normalizer.normalize(
            spell_result.text,
            timings=timings,
        )
        return HumanLanguageResult(
            original_question=original,
            normalized_question=normalized,
            corrections_applied=list(spell_result.corrections_applied),
            intent_hint=intent_hint,
        )
