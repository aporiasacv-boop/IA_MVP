import pytest

from app.evidence_package.health import EvidencePackageHealthError, validate_evidence_health
from app.evidence_package.metrics import EvidencePackageMetrics


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    EvidencePackageMetrics.reset_for_tests()


def test_health_ok() -> None:
    result = validate_evidence_health(
        {
            "missing_evidence": [],
            "missing_eko": [],
            "missing_ero": [],
            "invalid_confidence": [],
            "duplicate_evidence": [],
            "inconsistent_limitations": [],
        }
    )
    assert result["status"] == "healthy"


def test_health_missing_evidence() -> None:
    with pytest.raises(EvidencePackageHealthError, match="evidencia"):
        validate_evidence_health({"missing_evidence": [{"package_id": "x"}]})


def test_health_missing_eko() -> None:
    with pytest.raises(EvidencePackageHealthError, match="EKO"):
        validate_evidence_health({"missing_eko": [{"package_id": "x"}]})


def test_health_missing_ero() -> None:
    with pytest.raises(EvidencePackageHealthError, match="ERO"):
        validate_evidence_health({"missing_ero": [{"package_id": "x"}]})


def test_health_duplicate() -> None:
    with pytest.raises(EvidencePackageHealthError, match="duplicada"):
        validate_evidence_health({"duplicate_evidence": [{"package_id": "x"}]})


def test_health_invalid_confidence() -> None:
    with pytest.raises(EvidencePackageHealthError, match="confidence"):
        validate_evidence_health({"invalid_confidence": [{"package_id": "x"}]})


def test_health_inconsistent() -> None:
    with pytest.raises(EvidencePackageHealthError, match="inconsistentes"):
        validate_evidence_health({"inconsistent_limitations": [{"package_id": "x"}]})


def test_metrics_record() -> None:
    EvidencePackageMetrics.record_build(
        package_id="p1",
        package_size=1000,
        evidence_items=5,
        confidence=0.85,
        build_time_seconds=0.1,
        has_evidence=True,
        missing_eko=False,
        missing_ero=False,
        invalid_confidence=False,
        duplicate_evidence=False,
        inconsistent_limitations=False,
    )
    snap = EvidencePackageMetrics.snapshot()
    assert snap["evidence_packages_total"] == 1
