import pytest

from app.suggested_questions.engine import SuggestedQuestionsEngine
from app.suggested_questions.health import (
    SuggestedQuestionsHealthError,
    validate_suggested_questions_health,
)


def test_suggested_questions_health_validation_passes() -> None:
    report = validate_suggested_questions_health(SuggestedQuestionsEngine())

    assert report["samples_validated"] >= 5
    assert report["min_questions"] >= 3
    assert report["max_questions"] <= 4


def test_health_validation_rejects_duplicate_questions() -> None:
    class BrokenEngine(SuggestedQuestionsEngine):
        def generate(self, **kwargs):
            from app.suggested_questions.schemas import SuggestedQuestionsResult

            return SuggestedQuestionsResult(
                questions=["¿Cuántos clientes existen?", "¿Cuántos clientes existen?"],
                source="test",
                confidence=0.9,
                metadata={},
            )

    with pytest.raises(SuggestedQuestionsHealthError, match="únicas"):
        validate_suggested_questions_health(BrokenEngine())


def test_generate_fills_minimum_with_valid_defaults() -> None:
    engine = SuggestedQuestionsEngine(top_questions_provider=lambda limit: [])
    result = engine.generate(current_query_type="INVALID_TYPE_NAME")
    assert len(result.questions) >= 3
