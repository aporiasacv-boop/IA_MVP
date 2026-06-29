import time

from fastapi import APIRouter, Depends
from pydantic_core import to_jsonable_python

from app.api.deps import (
    get_capability_plan_executor,
    get_capability_reasoning_audit,
    get_capability_reasoner,
    get_enterprise_evidence_orchestrator,
    get_enterprise_evidence_planner,
    get_conversation_intelligence_gateway,
    get_conversation_presenter,
    get_conversation_response_generator,
    get_enterprise_personality_engine,
    get_enterprise_reasoning_engine,
    get_enterprise_runtime,
    get_executive_reasoning_v2_engine,
    get_executive_insight_engine,
    get_business_copilot_engine,
    get_executive_advisor_service,
    get_governed_route_executor,
    get_reasoning_governor,
)
from app.enterprise_evidence_orchestrator.engine import EnterpriseEvidenceOrchestrator
from app.enterprise_evidence_planner.engine import EnterpriseEvidencePlanner
from app.capability_plan_executor.engine import CapabilityPlanExecutor
from app.capability_reasoning_audit.engine import CapabilityReasoningAudit
from app.capability_reasoner.engine import CapabilityReasoner
from app.business_copilot.engine import BusinessCopilotEngine
from app.executive_advisor.service import ExecutiveAdvisorService
from app.executive_reasoning_v2.engine import ExecutiveReasoningV2Engine
from app.executive_insight.engine import ExecutiveInsightEngine
from app.enterprise_personality.engine import EnterprisePersonalityEngine
from app.conversation_ux.constants import GATEWAY_DECISION_CONVERSATION
from app.conversation_ux.gateway import ConversationIntelligenceGateway, GatewayRouteOutcome
from app.conversation_ux.presenter import ConversationPresenter
from app.conversation_ux.response_generator import ConversationResponseGenerator
from app.enterprise_runtime.runtime import EnterpriseRuntime
from app.operational_metrics.service import record_hybrid_operational_query
from app.reasoning_engine.constants import ROUTE_CONVERSATION
from app.reasoning_engine.engine import EnterpriseReasoningEngine
from app.reasoning_engine.governed_executor import GovernedRouteExecutor
from app.reasoning_engine.governor import (
    GOVERNANCE_RULE_FALLBACK,
    GovernanceOutcome,
    ReasoningGovernor,
)
from app.reasoning_engine.metrics import record_governance
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult

router = APIRouter(prefix="/api", tags=["chat"])


def _with_response_time(result: HybridChatResult, elapsed_ms: float) -> HybridChatResult:
    return HybridChatResult(
        handled_by=result.handled_by,
        success=result.success,
        answer=result.answer,
        suggestions=result.suggestions,
        metadata={**result.metadata, "response_time_ms": round(elapsed_ms, 2)},
    )


def _json_safe_result(result: HybridChatResult) -> HybridChatResult:
    return HybridChatResult(
        handled_by=result.handled_by,
        success=result.success,
        answer=result.answer,
        suggestions=result.suggestions,
        metadata=to_jsonable_python(result.metadata),
    )


def _synthetic_gateway_outcome(route: str, reason: str) -> GatewayRouteOutcome:
    if route == ROUTE_CONVERSATION:
        return GatewayRouteOutcome(
            decision=GATEWAY_DECISION_CONVERSATION,
            reason=reason,
            time_ms=0.0,
        )
    return GatewayRouteOutcome(
        decision="business",
        reason=reason,
        time_ms=0.0,
    )


def _apply_governance_metadata(
    result: HybridChatResult,
    governance,
) -> HybridChatResult:
    return HybridChatResult(
        handled_by=result.handled_by,
        success=result.success,
        answer=result.answer,
        suggestions=result.suggestions,
        metadata={**result.metadata, **governance.to_metadata()},
    )


def _finalize_conversation_response(
    message: str,
    result: HybridChatResult,
    *,
    personality_engine: EnterprisePersonalityEngine,
    response_generator: ConversationResponseGenerator,
    force_generate: bool = False,
) -> HybridChatResult:
    if result.metadata.get("conversation_ux_applied"):
        result = personality_engine.apply(message, result)
    if force_generate or result.metadata.get("conversation_ux_applied"):
        return response_generator.generate(message, result)
    return result


@router.post(
    "/chat/hybrid",
    response_model=HybridChatResult,
    summary="Chat hibrido experimental",
    description=(
        "Enruta la pregunta al pipeline empresarial determinista o al chat legacy "
        "segun el query_type planificado. No reemplaza /api/chat."
    ),
)
def hybrid_chat(
    request: HybridChatRequest,
    enterprise_runtime: EnterpriseRuntime = Depends(get_enterprise_runtime),
    conversation_gateway: ConversationIntelligenceGateway = Depends(
        get_conversation_intelligence_gateway
    ),
    conversation_presenter: ConversationPresenter = Depends(get_conversation_presenter),
    conversation_response_generator: ConversationResponseGenerator = Depends(
        get_conversation_response_generator
    ),
    enterprise_reasoning_engine: EnterpriseReasoningEngine = Depends(
        get_enterprise_reasoning_engine
    ),
    reasoning_governor: ReasoningGovernor = Depends(get_reasoning_governor),
    governed_route_executor: GovernedRouteExecutor = Depends(get_governed_route_executor),
    enterprise_personality_engine: EnterprisePersonalityEngine = Depends(
        get_enterprise_personality_engine
    ),
    executive_insight_engine: ExecutiveInsightEngine = Depends(get_executive_insight_engine),
    executive_reasoning_v2_engine: ExecutiveReasoningV2Engine = Depends(
        get_executive_reasoning_v2_engine
    ),
    business_copilot_engine: BusinessCopilotEngine = Depends(get_business_copilot_engine),
    executive_advisor_service: ExecutiveAdvisorService = Depends(get_executive_advisor_service),
    capability_reasoning_audit: CapabilityReasoningAudit = Depends(get_capability_reasoning_audit),
    capability_reasoner: CapabilityReasoner = Depends(get_capability_reasoner),
    capability_plan_executor: CapabilityPlanExecutor = Depends(get_capability_plan_executor),
    enterprise_evidence_planner: EnterpriseEvidencePlanner = Depends(get_enterprise_evidence_planner),
    enterprise_evidence_orchestrator: EnterpriseEvidenceOrchestrator = Depends(
        get_enterprise_evidence_orchestrator
    ),
) -> HybridChatResult:
    started = time.perf_counter()
    reasoning_decision = enterprise_reasoning_engine.analyze(request.message)
    governance = reasoning_governor.evaluate(reasoning_decision)
    record_governance(
        governed=governance.governed,
        pipeline_skipped=governance.pipeline_skipped,
        rule=governance.rule,
        time_ms=governance.time_ms,
    )

    result: HybridChatResult | None = None
    gateway_outcome: GatewayRouteOutcome | None = None
    pipeline_skipped = False

    if governance.governed and governance.route is not None:
        try:
            result = governed_route_executor.execute(
                governance.route,
                request.message,
                session_id=request.session_id,
                decision=reasoning_decision,
            )
            result = conversation_presenter.enhance(request.message, result)
            result = _finalize_conversation_response(
                request.message,
                result,
                personality_engine=enterprise_personality_engine,
                response_generator=conversation_response_generator,
                force_generate=(
                    governance.route == ROUTE_CONVERSATION
                    or bool(result.metadata.get("conversation_ux_applied"))
                ),
            )
            pipeline_skipped = True
            gateway_outcome = _synthetic_gateway_outcome(
                governance.route,
                governance.reason,
            )
        except Exception:
            governance = GovernanceOutcome(
                governed=False,
                route=reasoning_decision.recommended_route if reasoning_decision else None,
                rule=GOVERNANCE_RULE_FALLBACK,
                reason="governed_execution_failed",
                confidence=reasoning_decision.confidence if reasoning_decision else 0.0,
                time_ms=governance.time_ms,
                pipeline_skipped=False,
            )
            result = None

    if result is None:
        gateway_outcome = conversation_gateway.route(request.message, request.session_id)
        if gateway_outcome.decision == GATEWAY_DECISION_CONVERSATION:
            assert gateway_outcome.result is not None
            result = _finalize_conversation_response(
                request.message,
                gateway_outcome.result,
                personality_engine=enterprise_personality_engine,
                response_generator=conversation_response_generator,
                force_generate=True,
            )
        else:
            result = enterprise_runtime.process_inquiry(
                request.message,
                session_id=request.session_id,
            )
            result = conversation_presenter.enhance(request.message, result)
            result = _finalize_conversation_response(
                request.message,
                result,
                personality_engine=enterprise_personality_engine,
                response_generator=conversation_response_generator,
            )

    assert gateway_outcome is not None
    assert result is not None

    result = ConversationIntelligenceGateway.apply_metadata(result, gateway_outcome)
    result = _apply_governance_metadata(result, governance)
    result = enterprise_reasoning_engine.observe(
        reasoning_decision,
        result,
        gateway_outcome,
    )
    result = enterprise_evidence_planner.enrich_result(
        question=request.message,
        reasoning_decision=reasoning_decision,
        result=result,
    )
    result = enterprise_evidence_orchestrator.orchestrate(
        question=request.message,
        session_id=request.session_id,
        result=result,
    )
    result = capability_reasoner.enrich_result(
        question=request.message,
        reasoning_decision=reasoning_decision,
        result=result,
    )
    result = capability_plan_executor.try_execute(
        question=request.message,
        session_id=request.session_id,
        result=result,
    )
    result = capability_reasoning_audit.observe(
        question=request.message,
        reasoning_decision=reasoning_decision,
        result=result,
        gateway_outcome=gateway_outcome,
        governance=governance,
    )
    if pipeline_skipped and not result.metadata.get("pipeline_skipped"):
        result = HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={**result.metadata, "pipeline_skipped": True},
        )
    result = executive_reasoning_v2_engine.enrich(
        request.message,
        result,
        session_id=request.session_id,
    )
    result = executive_insight_engine.enrich(
        request.message,
        result,
        session_id=request.session_id,
    )
    result = business_copilot_engine.enrich(
        request.message,
        result,
        session_id=request.session_id,
    )
    result = executive_advisor_service.enrich_hybrid_result(
        result,
        session_id=request.session_id,
    )
    result = _with_response_time(result, (time.perf_counter() - started) * 1000)
    result = _json_safe_result(result)
    record_hybrid_operational_query(request, result, result.metadata.get("response_time_ms", 0.0))
    return result
