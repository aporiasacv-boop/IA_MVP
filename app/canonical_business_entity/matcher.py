from dataclasses import dataclass
from decimal import Decimal

from app.canonical_business_entity.constants import (
    MIN_FUZZY_SCORE,
    MIN_SUGGESTION_SCORE,
    MIN_TOKEN_OVERLAP_SCORE,
    RULE_BRAND_TOKEN,
    RULE_FUZZY_NAME,
    RULE_NORMALIZED_NAME_EXACT,
    RULE_RFC_EXACT,
    RULE_TOKEN_OVERLAP,
)
from app.canonical_business_entity.normalizer import (
    brand_token_score,
    extract_rfc,
    fuzzy_name_score,
    normalize_organization_name,
    token_overlap_score,
)


@dataclass(frozen=True)
class EntityRecord:
    entity_id: int
    entity_code: str
    entity_name: str
    source_column: str

    @property
    def normalized_name(self) -> str:
        return normalize_organization_name(self.entity_name)

    @property
    def rfc(self) -> str | None:
        return extract_rfc(self.entity_code, self.entity_name)


@dataclass(frozen=True)
class MatchCandidate:
    source_entity_id: int
    candidate_entity_id: int
    rule_used: str
    score: Decimal


def _ordered_pair(left_id: int, right_id: int) -> tuple[int, int]:
    return (left_id, right_id) if left_id < right_id else (right_id, left_id)


def generate_match_candidates(entities: list[EntityRecord]) -> list[MatchCandidate]:
    """Genera pares de sugerencia sin aplicar merge."""
    results: list[MatchCandidate] = []
    seen: set[tuple[int, int, str]] = set()

    def add(source: EntityRecord, candidate: EntityRecord, rule: str, score: float) -> None:
        if source.entity_id == candidate.entity_id:
            return
        if score < MIN_SUGGESTION_SCORE:
            return
        pair = _ordered_pair(source.entity_id, candidate.entity_id)
        key = (pair[0], pair[1], rule)
        if key in seen:
            return
        seen.add(key)
        results.append(
            MatchCandidate(
                source_entity_id=pair[0],
                candidate_entity_id=pair[1],
                rule_used=rule,
                score=Decimal(str(round(score, 4))),
            )
        )

    by_rfc: dict[str, list[EntityRecord]] = {}
    by_normalized: dict[str, list[EntityRecord]] = {}

    for entity in entities:
        if entity.rfc:
            by_rfc.setdefault(entity.rfc, []).append(entity)
        if entity.normalized_name:
            by_normalized.setdefault(entity.normalized_name, []).append(entity)

    for group in by_rfc.values():
        if len(group) < 2:
            continue
        for index, source in enumerate(group):
            for candidate in group[index + 1 :]:
                add(source, candidate, RULE_RFC_EXACT, 0.95)

    for group in by_normalized.values():
        if len(group) < 2:
            continue
        for index, source in enumerate(group):
            for candidate in group[index + 1 :]:
                add(source, candidate, RULE_NORMALIZED_NAME_EXACT, 0.90)

    for index, source in enumerate(entities):
        for candidate in entities[index + 1 :]:
            left_norm = source.normalized_name
            right_norm = candidate.normalized_name
            if not left_norm or not right_norm:
                continue

            overlap = token_overlap_score(left_norm, right_norm)
            if overlap >= MIN_TOKEN_OVERLAP_SCORE:
                add(source, candidate, RULE_TOKEN_OVERLAP, min(0.85, 0.65 + overlap * 0.25))

            fuzzy = fuzzy_name_score(left_norm, right_norm)
            if fuzzy >= MIN_FUZZY_SCORE:
                add(source, candidate, RULE_FUZZY_NAME, fuzzy)

            brand = brand_token_score(left_norm, right_norm)
            if brand > 0:
                add(source, candidate, RULE_BRAND_TOKEN, brand)

    return results
