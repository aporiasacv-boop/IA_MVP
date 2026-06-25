import re
from datetime import datetime
from decimal import Decimal

from app.semantic_intent.catalog_loader import (
    build_verb_patterns,
    load_contexts,
    load_objects,
    normalize_text,
)
from app.semantic_intent.constants import SBEP_VERSION, SCOPE_PATTERNS, TIME_PATTERNS
from app.semantic_intent.schemas import (
    DetectedObject,
    DetectedVerb,
    SemanticParseResult,
)

CONSTRAINT_PATTERNS = (
    "sin movimientos",
    "inactivo",
    "inactiva",
    "mayor a",
    "menor a",
    "más de",
    "mas de",
    "menos de",
    "al menos",
    "con riesgo",
    "con alerta",
)

ENTITY_HINT_PATTERN = re.compile(r"\b([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s&.-]{2,})\b")
YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")


def _detect_verb(normalized: str) -> DetectedVerb | None:
    for pattern, verb, matched in build_verb_patterns():
        if pattern in normalized:
            return DetectedVerb(
                verb_id=verb.verb_id,
                category=verb.category,
                matched_text=matched,
                confidence=Decimal("0.9000") if pattern == normalize_text(verb.verb_id.replace("_", " ")) else Decimal("0.8200"),
            )
    return None


def _detect_objects(normalized: str) -> list[DetectedObject]:
    found: list[DetectedObject] = []
    seen: set[str] = set()
    for obj in load_objects():
        candidates = [obj.object_id, *obj.aliases]
        for candidate in candidates:
            token = normalize_text(candidate)
            if token in normalized and obj.object_id not in seen:
                found.append(
                    DetectedObject(
                        object_id=obj.object_id,
                        matched_text=candidate,
                        confidence=Decimal("0.8500"),
                    )
                )
                seen.add(obj.object_id)
                break
    if len(found) > 3:
        for item in found:
            item.ambiguous = True
    return found


def _detect_context(normalized: str) -> list[str]:
    contexts: list[str] = []
    for ctx in load_contexts():
        tokens = [ctx.context_id, *ctx.aliases]
        if any(normalize_text(token) in normalized for token in tokens):
            contexts.append(ctx.context_id)
    return contexts


def _detect_scope(normalized: str) -> list[str]:
    return [scope for scope in SCOPE_PATTERNS if scope in normalized]


def _detect_time(normalized: str) -> list[str]:
    times = [token for token in TIME_PATTERNS if token in normalized]
    times.extend(YEAR_PATTERN.findall(normalized))
    return sorted(set(times))


def _detect_constraints(normalized: str) -> list[str]:
    return [item for item in CONSTRAINT_PATTERNS if item in normalized]


def _detect_entity_hints(original: str, normalized: str) -> list[str]:
    hints = [match.strip() for match in ENTITY_HINT_PATTERN.findall(original)]
    quoted = re.findall(r'"([^"]+)"', original)
    hints.extend(quoted)
    return sorted({normalize_text(h).upper() if len(h) < 4 else h.strip() for h in hints if h.strip()})


def _compute_confidence(
  verb: DetectedVerb | None,
  objects: list[DetectedObject],
  contexts: list[str],
) -> Decimal:
    score = 0.0
    if verb:
        score += 0.45
    if objects:
        score += 0.25
    if contexts:
        score += 0.1
    if verb and objects:
        score += 0.15
    if objects and any(obj.ambiguous for obj in objects):
        score -= 0.1
    if not verb:
        score = 0.2
    return Decimal(str(round(max(min(score, 1.0), 0.0), 4)))


def parse_semantic_question(question: str, *, now: datetime | None = None) -> SemanticParseResult:
    timestamp = now or datetime.now()
    normalized = normalize_text(question)
    verb = _detect_verb(normalized)
    objects = _detect_objects(normalized)
    contexts = _detect_context(normalized)
    scope = _detect_scope(normalized)
    time_refs = _detect_time(normalized)
    constraints = _detect_constraints(normalized)
    entity_hints = _detect_entity_hints(question, normalized)

    unknown_tokens: list[str] = []
    if verb is None:
        unknown_tokens.append("verb")

    confidence = _compute_confidence(verb, objects, contexts)

    return SemanticParseResult(
        schema_version=SBEP_VERSION,
        original_question=question,
        normalized_question=normalized,
        business_verb=verb,
        business_objects=objects,
        business_context=contexts,
        business_scope=scope,
        business_time=time_refs,
        business_constraints=constraints,
        entity_hints=entity_hints,
        unknown_tokens=unknown_tokens,
        confidence=confidence,
        parsed_at=timestamp,
        metadata={
            "deterministic": True,
            "contains_llm_output": False,
            "contains_sql": False,
        },
    )
