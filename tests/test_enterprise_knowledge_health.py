import pytest

from app.enterprise_knowledge.health import KnowledgeHealthError, validate_knowledge_health


def test_health_ok() -> None:
    result = validate_knowledge_health(
        {
            "incomplete_objects": [{"knowledge_id": 1}],
            "invalid_confidence": [],
            "missing_evidence": [],
            "empty_sections": [],
            "broken_relationships": [],
            "contradictory_facts": [],
        }
    )
    assert result["status"] == "healthy"


def test_health_missing_evidence() -> None:
    with pytest.raises(KnowledgeHealthError, match="evidencia"):
        validate_knowledge_health(
            {
                "incomplete_objects": [],
                "invalid_confidence": [],
                "missing_evidence": [{"knowledge_id": 1}],
                "empty_sections": [],
                "broken_relationships": [],
                "contradictory_facts": [],
            }
        )


def test_health_broken_relationships() -> None:
    with pytest.raises(KnowledgeHealthError, match="relaciones rotas"):
        validate_knowledge_health(
            {
                "incomplete_objects": [],
                "invalid_confidence": [],
                "missing_evidence": [],
                "empty_sections": [],
                "broken_relationships": [{"knowledge_id": 1}],
                "contradictory_facts": [],
            }
        )

def test_health_empty_sections() -> None:
    with pytest.raises(KnowledgeHealthError, match="secciones"):
        validate_knowledge_health(
            {
                "incomplete_objects": [],
                "invalid_confidence": [],
                "missing_evidence": [],
                "empty_sections": [{"knowledge_id": 1}],
                "broken_relationships": [],
                "contradictory_facts": [],
            }
        )


def test_health_contradictory_facts() -> None:
    with pytest.raises(KnowledgeHealthError, match="contradictorios"):
        validate_knowledge_health(
            {
                "incomplete_objects": [],
                "invalid_confidence": [],
                "missing_evidence": [],
                "empty_sections": [],
                "broken_relationships": [],
                "contradictory_facts": [{"knowledge_id": 1}],
            }
        )
