from datetime import datetime
from unittest.mock import MagicMock

from app.enterprise_knowledge.repository import EnterpriseKnowledgeRepository, KnowledgeBuildEngine


def test_build_engine_updates_existing() -> None:
    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    repo.session = MagicMock()
    repo.fetch_build_contexts.return_value = [
        {"canonical_id": 1, "canonical_name": "A", "normalized_name": "A", "primary_rfc": None, "alias_count": 1}
    ]
    repo.fetch_aliases.return_value = []
    repo.fetch_profile.return_value = None
    repo.fetch_ontology_assignments.return_value = []
    repo.upsert_object.return_value = (MagicMock(), False)
    engine = KnowledgeBuildEngine(repo)
    result = engine.run_idempotent()
    assert result["objects_updated"] == 1
    assert result["objects_created"] == 0

    repo = MagicMock(spec=EnterpriseKnowledgeRepository)
    repo.session = MagicMock()
    repo.fetch_build_contexts.return_value = [
        {"canonical_id": 1, "canonical_name": "A", "normalized_name": "A", "primary_rfc": None, "alias_count": 1}
    ]
    repo.fetch_aliases.return_value = []
    repo.fetch_profile.return_value = None
    repo.fetch_ontology_assignments.return_value = []
    repo.upsert_object.return_value = (MagicMock(), True)
    engine = KnowledgeBuildEngine(repo)
    result = engine.run_idempotent(now=datetime(2026, 6, 24))
    assert result["entities_processed"] == 1
    repo.session.commit.assert_called_once()
