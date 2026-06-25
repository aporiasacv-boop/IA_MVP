from datetime import datetime
from unittest.mock import MagicMock

from app.enterprise_reasoning.repository import EnterpriseReasoningRepository, ReasoningBuildEngine
from tests.test_enterprise_reasoning_builder import _sample_eko


def test_build_engine_processes_eko() -> None:
    repo = MagicMock(spec=EnterpriseReasoningRepository)
    repo.session = MagicMock()
    eko = _sample_eko()
    repo.fetch_eko_payloads.return_value = [
        {"canonical_id": 1, "knowledge_payload": eko.model_dump(mode="json"), "canonical_name": "WALMART"}
    ]
    repo.upsert_object.return_value = (MagicMock(), True)
    engine = ReasoningBuildEngine(repo)
    result = engine.run_idempotent(now=datetime(2026, 6, 24))
    assert result["entities_processed"] == 1
    repo.session.commit.assert_called_once()
