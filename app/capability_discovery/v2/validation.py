from app.enterprise_knowledge_service.integration.consumers import knowledge_for_capability_discovery
from app.capability_discovery.v2.constants import (
    FORBIDDEN_EXAMPLE_PATTERNS,
    MAX_CAPABILITIES,
    MAX_EXAMPLES,
    MAX_RESPONSE_LINES,
)
from app.capability_discovery.v2.metrics import contains_forbidden_term
from app.utils.text_normalizer import normalize_for_matching


class CapabilityDiscoveryV2ValidationError(Exception):
    pass


def validate_v2_discovery_result(
    *,
    answer: str,
    capabilities: list[str],
    example_questions: list[str],
    suggestions_present: bool,
) -> None:
    if len(capabilities) > MAX_CAPABILITIES:
        raise CapabilityDiscoveryV2ValidationError(
            f"Máximo {MAX_CAPABILITIES} capacidades, recibidas {len(capabilities)}"
        )
    if len(example_questions) > MAX_EXAMPLES:
        raise CapabilityDiscoveryV2ValidationError(
            f"Máximo {MAX_EXAMPLES} ejemplos, recibidos {len(example_questions)}"
        )
    if suggestions_present:
        raise CapabilityDiscoveryV2ValidationError(
            "No se permiten suggested_questions en capability_discovery"
        )

    line_count = len(answer.splitlines())
    if line_count > MAX_RESPONSE_LINES:
        raise CapabilityDiscoveryV2ValidationError(
            f"Respuesta excede {MAX_RESPONSE_LINES} líneas: {line_count}"
        )

    forbidden = contains_forbidden_term(answer)
    if forbidden:
        raise CapabilityDiscoveryV2ValidationError(
            f"Término técnico prohibido en respuesta: {forbidden}"
        )

    for question in example_questions:
        normalized = normalize_for_matching(question)
        for pattern in FORBIDDEN_EXAMPLE_PATTERNS:
            if pattern in normalized:
                raise CapabilityDiscoveryV2ValidationError(
                    f"Ejemplo conversacional prohibido: {question}"
                )


def build_validated_v2_discovery_payload() -> tuple[str, list[str], list[str]]:
    payload = knowledge_for_capability_discovery()
    answer, capabilities, example_questions = (
        payload.answer,
        payload.capabilities,
        payload.examples,
    )
    validate_v2_discovery_result(
        answer=answer,
        capabilities=capabilities,
        example_questions=example_questions,
        suggestions_present=False,
    )
    return answer, capabilities, example_questions
