import re
from collections import defaultdict

from app.domain.entities import BusinessEntity
from app.domain.entity_catalog import ENTITY_SYNONYMS, MONTH_NAMES
from app.schemas.entity import EntityResolution
from app.utils.text_normalizer import normalize_for_matching, normalize_text

_CLIENT_CODE_PATTERN = re.compile(r"\bC\d+\b", re.IGNORECASE)
_PROVIDER_CODE_PATTERN = re.compile(r"\bP\d+\b", re.IGNORECASE)
_GENERAL_CODE_PATTERN = re.compile(r"\b[A-Za-z0-9]*\d[A-Za-z0-9]*\b")
_MOVIMIENTO_STRONG_SYNONYMS = frozenset({"movimiento", "movimientos"})
_YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")


class EntityResolver:
    def resolve(self, question: str) -> EntityResolution:
        normalized = normalize_for_matching(question)
        if not normalized:
            return EntityResolution()

        matches_by_entity: dict[BusinessEntity, list[str]] = defaultdict(list)
        occupied_spans: list[tuple[int, int]] = []
        matched_entities_in_order: list[BusinessEntity] = []

        candidates: list[tuple[BusinessEntity, str, str]] = []
        for entity, synonyms in ENTITY_SYNONYMS.items():
            for synonym in synonyms:
                normalized_synonym = normalize_for_matching(synonym)
                if normalized_synonym:
                    candidates.append((entity, synonym, normalized_synonym))

        candidates.sort(key=lambda item: len(item[2]), reverse=True)

        for entity, original_term, normalized_term in candidates:
            for start, end in self._find_term_spans(normalized_term, normalized):
                if self._overlaps(start, end, occupied_spans):
                    continue
                if entity not in matches_by_entity:
                    matched_entities_in_order.append(entity)
                matches_by_entity[entity].append(original_term)
                occupied_spans.append((start, end))

        parameters = self._extract_parameters(question, normalized)
        entities = self._build_entity_list(
            matched_entities_in_order,
            matches_by_entity,
            parameters,
        )
        matched_terms = [
            term
            for entity in matched_entities_in_order
            for term in matches_by_entity[entity]
        ]

        possible_entities = set(matches_by_entity)
        if parameters.get("anio") is not None:
            possible_entities.add(BusinessEntity.ANIO)

        confidence = 0.0
        if possible_entities:
            confidence = round(len(entities) / len(possible_entities), 4)

        return EntityResolution(
            entities=entities,
            parameters=parameters,
            confidence=confidence,
            matched_terms=matched_terms,
        )

    def _build_entity_list(
        self,
        matched_entities_in_order: list[BusinessEntity],
        matches_by_entity: dict[BusinessEntity, list[str]],
        parameters: dict,
    ) -> list[BusinessEntity]:
        entities: list[BusinessEntity] = []

        for entity in matched_entities_in_order:
            if entity == BusinessEntity.MES and parameters.get("mes") is not None:
                continue
            if entity == BusinessEntity.MOVIMIENTO and not self._has_strong_movimiento_match(
                matches_by_entity[entity],
            ):
                continue
            if entity not in entities:
                entities.append(entity)

        if parameters.get("anio") is not None and BusinessEntity.ANIO not in entities:
            entities.append(BusinessEntity.ANIO)

        return entities

    def _extract_parameters(self, question: str, normalized: str) -> dict:
        parameters: dict = {}

        for month in MONTH_NAMES:
            normalized_month = normalize_for_matching(month)
            if self._find_term_spans(normalized_month, normalized):
                parameters["mes"] = normalize_text(month)
                break

        year_match = _YEAR_PATTERN.search(question)
        if year_match:
            parameters["anio"] = int(year_match.group())

        codigo = self._extract_codigo(question)
        if codigo:
            parameters["codigo"] = codigo

        return parameters

    @staticmethod
    def _extract_codigo(question: str) -> str | None:
        candidates: list[tuple[int, int, str]] = []

        for match in _CLIENT_CODE_PATTERN.finditer(question):
            candidates.append((match.start(), match.end(), match.group()))
        for match in _PROVIDER_CODE_PATTERN.finditer(question):
            candidates.append((match.start(), match.end(), match.group()))
        for match in _GENERAL_CODE_PATTERN.finditer(question):
            token = match.group()
            if len(token) >= 5 and re.search(r"[A-Za-z]", token):
                candidates.append((match.start(), match.end(), token))

        if not candidates:
            return None

        candidates.sort(key=lambda item: (-(item[1] - item[0]), item[0]))
        return candidates[0][2]

    @staticmethod
    def _has_strong_movimiento_match(matched_terms: list[str]) -> bool:
        return any(
            normalize_for_matching(term) in _MOVIMIENTO_STRONG_SYNONYMS
            for term in matched_terms
        )

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
        return any(
            not (end <= occupied_start or start >= occupied_end)
            for occupied_start, occupied_end in occupied_spans
        )
