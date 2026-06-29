from pydantic import BaseModel, Field


class AuditedCapability(BaseModel):
    capability_id: str
    label: str
    compatibility: str
    rationale: str


class CapabilityDecision(BaseModel):
    selected_capability: str
    final_route: str
    fallback_used: bool
    fallback_type: str | None = None
    handled_by: str
    reason: str


class CapabilityEvaluation(BaseModel):
    selected_was_sufficient: bool
    reusable_capabilities_exist: bool
    could_combine_capabilities: bool
    classification: str
    summary: str
    notes: list[str] = Field(default_factory=list)


class CapabilityReasoningAuditReport(BaseModel):
    question: str
    intent: str | None = None
    confidence: float | None = None
    explanation: str | None = None
    available_capabilities: list[AuditedCapability] = Field(default_factory=list)
    decision: CapabilityDecision
    evaluation: CapabilityEvaluation
    report_text: str

    def observability_metadata(self, audit_ms: float) -> dict:
        return {
            "audit_reasoning_ms": round(audit_ms, 2),
            "audit_capability_count": len(self.available_capabilities),
            "audit_selected_capability": self.decision.selected_capability,
            "audit_final_route": self.decision.final_route,
            "capability_reasoning_audit": self.model_dump(),
        }
