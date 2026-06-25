from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.ai_orchestration.hallucination_guard import (
    evaluate_evidence_sufficiency,
    validate_llm_response,
)
from app.ai_orchestration.prompt_builder import build_executive_prompt
from app.evidence_package.example_data import build_example_package
from app.evidence_package.schemas import EvidenceLimitation


def test_prompt_builder_from_eep() -> None:
    package = build_example_package()
    prompt = build_executive_prompt(package)
    assert package.question in prompt
    assert "PREGUNTA:" in prompt
    assert "CONTEXTO EMPRESARIAL:" in prompt
    assert "SELECT" not in prompt
    assert "schema_version" not in prompt
    assert "package_id" not in prompt


def test_prompt_includes_limitations() -> None:
    package = build_example_package()
    package.limitations.append(
        EvidenceLimitation(
            code="missing_ero",
            description="ERO no disponible",
            severity="high",
            source="ero",
        )
    )
    prompt = build_executive_prompt(package)
    assert "LIMITACIONES:" in prompt
    assert "ERO no disponible" in prompt


def test_guard_sufficient_evidence() -> None:
    package = build_example_package()
    result = evaluate_evidence_sufficiency(package)
    assert result.triggered is False


def test_guard_insufficient_evidence() -> None:
    package = build_example_package()
    package.evidence = []
    package.knowledge = []
    package.reasoning = []
    package.facts = []
    package.limitations.append(
        EvidenceLimitation(
            code="missing_eko",
            description="Sin EKO",
            severity="critical",
            source="eko",
        )
    )
    result = evaluate_evidence_sufficiency(package)
    assert result.triggered is True
    assert result.insufficient_evidence is True


def test_validate_empty_response() -> None:
    package = build_example_package()
    result = validate_llm_response("", package)
    assert result.triggered is True
