import re
import unicodedata
from collections import defaultdict

from app.domain.operation_catalog import OPERATION_SYNONYMS
from app.domain.operations import BusinessOperation
from app.schemas.operation import OperationResolution


class OperationResolver:
    def resolve(self, question: str) -> OperationResolution:
        normalized = self._normalize(question)
        if not normalized:
            return OperationResolution()

        matches_by_operation: dict[BusinessOperation, list[str]] = defaultdict(list)
        occupied_spans: list[tuple[int, int]] = []

        candidates: list[tuple[BusinessOperation, str, str]] = []
        for operation, synonyms in OPERATION_SYNONYMS.items():
            for synonym in synonyms:
                normalized_synonym = self._normalize(synonym)
                if normalized_synonym:
                    candidates.append((operation, synonym, normalized_synonym))

        candidates.sort(key=lambda item: len(item[2]), reverse=True)

        for operation, original_term, normalized_term in candidates:
            for start, end in self._find_term_spans(normalized_term, normalized):
                if self._overlaps(start, end, occupied_spans):
                    continue
                matches_by_operation[operation].append(original_term)
                occupied_spans.append((start, end))

        if not matches_by_operation:
            return OperationResolution()

        total_matches = sum(len(terms) for terms in matches_by_operation.values())
        best_operation = max(
            matches_by_operation,
            key=lambda operation: len(matches_by_operation[operation]),
        )
        matched_terms = matches_by_operation[best_operation]
        confidence = round(len(matched_terms) / total_matches, 4)

        return OperationResolution(
            operation=best_operation,
            confidence=confidence,
            matched_terms=matched_terms,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        lowered = text.lower().strip()
        decomposed = unicodedata.normalize("NFD", lowered)
        without_accents = "".join(
            char for char in decomposed if unicodedata.category(char) != "Mn"
        )
        cleaned = re.sub(r"[^\w\s]", " ", without_accents)
        return re.sub(r"\s+", " ", cleaned).strip()

    @staticmethod
    def _find_term_spans(term: str, text: str) -> list[tuple[int, int]]:
        if not term:
            return []

        if " " in term:
            spans: list[tuple[int, int]] = []
            start = 0
            while True:
                index = text.find(term, start)
                if index == -1:
                    break
                spans.append((index, index + len(term)))
                start = index + len(term)
            return spans

        pattern = rf"\b{re.escape(term)}\b"
        return [(match.start(), match.end()) for match in re.finditer(pattern, text)]

    @staticmethod
    def _overlaps(start: int, end: int, occupied_spans: list[tuple[int, int]]) -> bool:
        return any(not (end <= occupied_start or start >= occupied_end) for occupied_start, occupied_end in occupied_spans)
