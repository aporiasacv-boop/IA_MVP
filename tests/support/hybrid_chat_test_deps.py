"""Dependencias deshabilitadas para invocar hybrid_chat() fuera de FastAPI."""

from unittest.mock import MagicMock

from app.business_copilot.engine import BusinessCopilotEngine
from app.enterprise_evidence_orchestrator.engine import EnterpriseEvidenceOrchestrator
from app.enterprise_evidence_planner.engine import EnterpriseEvidencePlanner
from app.capability_plan_executor.engine import CapabilityPlanExecutor
from app.capability_reasoning_audit.engine import CapabilityReasoningAudit
from app.capability_reasoner.engine import CapabilityReasoner
from app.executive_advisor.engine import ExecutiveAdvisorEngine
from app.executive_advisor.service import ExecutiveAdvisorService
from app.executive_reasoning_v2.engine import ExecutiveReasoningV2Engine
from app.executive_insight.engine import ExecutiveInsightEngine
from app.schemas.hybrid_chat import HybridChatResult


def disabled_executive_layers_kwargs() -> dict:
    advisor_engine = ExecutiveAdvisorEngine(enabled=False)
    advisor_service = ExecutiveAdvisorService(
        advisor_engine=advisor_engine,
        dataset_summary_provider=lambda: {},
        top_queries_provider=lambda: [],
        coverage_report_provider=lambda: {},
        conversation_memory_service=MagicMock(),
    )
    return {
        "executive_insight_engine": ExecutiveInsightEngine(enabled=False),
        "executive_reasoning_v2_engine": ExecutiveReasoningV2Engine(
            enabled=False,
            llm_provider=None,
        ),
        "business_copilot_engine": BusinessCopilotEngine(enabled=False),
        "executive_advisor_service": advisor_service,
        "capability_reasoning_audit": CapabilityReasoningAudit(enabled=False),
        "capability_reasoner": CapabilityReasoner(enabled=False),
        "capability_plan_executor": CapabilityPlanExecutor(
            execute_capability=lambda *_args, **_kwargs: HybridChatResult(
                handled_by="business_pipeline",
                success=True,
                answer="noop",
                metadata={"query_type": "COUNT_CLIENTES"},
            ),
            enabled=False,
        ),
        "enterprise_evidence_planner": EnterpriseEvidencePlanner(enabled=False),
        "enterprise_evidence_orchestrator": EnterpriseEvidenceOrchestrator(
            execute_capability=lambda *_args, **_kwargs: HybridChatResult(
                handled_by="business_pipeline",
                success=True,
                answer="noop",
                metadata={"query_type": "COUNT_CLIENTES"},
            ),
            enabled=False,
        ),
    }
