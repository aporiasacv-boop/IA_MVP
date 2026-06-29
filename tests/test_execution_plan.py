from app.capability_registry.constants import BUSINESS_PIPELINE, INSTITUTIONAL_KNOWLEDGE
from app.execution_plan.plan import ExecutionPlan


def test_default_inquiry_plan_has_static_two_step_flow():
    plan = ExecutionPlan.default_inquiry()

    assert len(plan.steps) == 2
    assert plan.steps[0].step_id == INSTITUTIONAL_KNOWLEDGE
    assert plan.steps[1].step_id == BUSINESS_PIPELINE
