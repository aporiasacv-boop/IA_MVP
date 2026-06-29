from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    evidence_id: str
    label: str
    capability: str


class EnterpriseEvidencePlan(BaseModel):
    business_goal: str
    required_evidence: list[str] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list)
    estimated_coverage: float = 0.0
    missing_evidence: list[str] = Field(default_factory=list)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)

    def observability_metadata(self, planning_time_ms: float) -> dict:
        return {
            "business_goal": self.business_goal,
            "required_evidence": self.required_evidence,
            "required_capabilities": self.required_capabilities,
            "execution_order": self.execution_order,
            "estimated_coverage": round(self.estimated_coverage, 2),
            "missing_evidence": self.missing_evidence,
            "planning_time_ms": round(planning_time_ms, 2),
            "enterprise_evidence_plan": self.model_dump(),
        }
