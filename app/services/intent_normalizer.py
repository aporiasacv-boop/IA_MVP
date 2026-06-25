import re
import time
import unicodedata

from app.services.business_synonyms import BusinessSynonyms


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


class IntentNormalizer:
    QUESTION_STARTERS = ("que", "quien", "cual", "como", "donde", "cuando", "cuales", "hasta", "desde")

    def __init__(self, synonyms: BusinessSynonyms | None = None) -> None:
        self.synonyms = synonyms or BusinessSynonyms()

    def normalize(
        self,
        text: str,
        timings: object | None = None,
    ) -> tuple[str, str | None]:
        normalized = text.strip()
        normalized = re.sub(r"\s+", " ", normalized)

        synonym_started = time.perf_counter()
        normalized, intent_hint = self.synonyms.apply(normalized)
        if timings is not None:
            timings.synonym_resolution_ms = _elapsed_ms(synonym_started)

        format_started = time.perf_counter()
        normalized = self._ensure_question_format(normalized)

        if intent_hint:
            canonical = self.synonyms.canonical_question(intent_hint)
            if canonical:
                if timings is not None:
                    timings.intent_normalization_ms = _elapsed_ms(format_started)
                return canonical, intent_hint

        if timings is not None:
            timings.intent_normalization_ms = _elapsed_ms(format_started)
        return normalized, intent_hint

    def _ensure_question_format(self, text: str) -> str:
        stripped = text.strip()
        if not stripped:
            return stripped

        lower = self._strip_accents(stripped.lower())
        if stripped.endswith("?"):
            return self._capitalize_question(stripped)

        first_word = lower.split()[0] if lower.split() else ""
        if first_word in self.QUESTION_STARTERS:
            return self._capitalize_question(f"{stripped}?")
        return stripped

    @staticmethod
    def _capitalize_question(text: str) -> str:
        if not text:
            return text
        if text.startswith("¿"):
            return text[0] + text[1].upper() + text[2:]
        return f"¿{text[0].upper()}{text[1:]}"

    @staticmethod
    def _strip_accents(text: str) -> str:
        decomposed = unicodedata.normalize("NFD", text)
        return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
