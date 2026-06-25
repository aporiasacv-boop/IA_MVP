from app.semantic_intent.metrics import SemanticIntentMetrics


def test_metrics_record() -> None:
    SemanticIntentMetrics.reset_for_tests()
    SemanticIntentMetrics.record_parse(verb_id="listar", confidence=0.8)
    SemanticIntentMetrics.record_plan(
        plan_id="abc",
        verb_id="listar",
        confidence=0.75,
        incomplete=False,
        incompatible=False,
        ambiguous_objects=False,
    )
    snap = SemanticIntentMetrics.snapshot()
    assert snap["semantic_parses"] == 1
    assert snap["execution_plans"] == 1
    assert snap["planner_success_rate"] == 1.0
