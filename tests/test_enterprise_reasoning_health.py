import pytest

from app.enterprise_reasoning.health import ReasoningHealthError, validate_reasoning_health


def test_health_ok() -> None:
    result = validate_reasoning_health(
        {
            "missing_evidence": [],
            "invalid_confidence": [],
            "incomplete_objects": [{"reasoning_id": 1}],
            "duplicate_findings": [],
            "contradictory_rules": [],
            "incompatible_recommendations": [],
        }
    )
    assert result["status"] == "healthy"


def test_health_contradictory_and_incompatible() -> None:
    with pytest.raises(ReasoningHealthError, match="contradictorias"):
        validate_reasoning_health({"contradictory_rules": [{"reasoning_id": 1}]})
    with pytest.raises(ReasoningHealthError, match="incompatibles"):
        validate_reasoning_health({"incompatible_recommendations": [{"reasoning_id": 1}]})

    with pytest.raises(ReasoningHealthError, match="duplicados"):
        validate_reasoning_health({"duplicate_findings": [{"reasoning_id": 1}]})
