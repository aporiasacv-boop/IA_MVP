_audit_metrics = {
    "audits_total": 0,
    "fallback_with_reusable": 0,
    "incorrect_total": 0,
}


def record_audit_metrics(*, fallback_with_reusable: bool, incorrect: bool) -> None:
    _audit_metrics["audits_total"] += 1
    if fallback_with_reusable:
        _audit_metrics["fallback_with_reusable"] += 1
    if incorrect:
        _audit_metrics["incorrect_total"] += 1


def audit_metrics_snapshot() -> dict:
    return dict(_audit_metrics)


def reset_audit_metrics_for_tests() -> None:
    _audit_metrics["audits_total"] = 0
    _audit_metrics["fallback_with_reusable"] = 0
    _audit_metrics["incorrect_total"] = 0
