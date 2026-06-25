from dataclasses import dataclass

from app.utils.text_normalizer import normalize_for_matching


@dataclass
class CapabilityDiscoveryV2MetricsState:
    capability_discovery_v2_responses: int = 0
    capability_discovery_response_length: int = 0


v2_metrics = CapabilityDiscoveryV2MetricsState()


class CapabilityDiscoveryV2Metrics:
    @staticmethod
    def record_response(answer: str) -> None:
        v2_metrics.capability_discovery_v2_responses += 1
        v2_metrics.capability_discovery_response_length = len(answer.splitlines())

    @staticmethod
    def snapshot() -> dict[str, int]:
        return {
            "capability_discovery_v2_responses": (
                v2_metrics.capability_discovery_v2_responses
            ),
            "capability_discovery_response_length": (
                v2_metrics.capability_discovery_response_length
            ),
        }

    @staticmethod
    def reset() -> None:
        v2_metrics.capability_discovery_v2_responses = 0
        v2_metrics.capability_discovery_response_length = 0


def contains_forbidden_term(answer: str) -> str | None:
    normalized = normalize_for_matching(answer)
    from app.capability_discovery.v2.constants import FORBIDDEN_VISIBLE_TERMS

    for term in FORBIDDEN_VISIBLE_TERMS:
        if term in normalized:
            return term
    return None
