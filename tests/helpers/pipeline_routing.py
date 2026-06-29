from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.business_pipeline_state import BusinessPipelineState


def prepare_pipeline_state(
    preparer: BusinessPipelineCapability,
    message: str,
    session_id: str | None = None,
) -> BusinessPipelineState:
    return preparer._prepare_pipeline_state(message, session_id)


def route_with_prepared_context(
    router,
    preparer: BusinessPipelineCapability,
    message: str,
    session_id: str | None = None,
):
    pipeline_state = prepare_pipeline_state(preparer, message, session_id)
    return router.route(message, pipeline_state=pipeline_state)
