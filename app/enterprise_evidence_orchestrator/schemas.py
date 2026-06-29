from pydantic import BaseModel, Field


class CollectedEvidenceItem(BaseModel):
    evidence_id: str
    evidence_label: str
    capability: str
    query_type: str
    source: str
    answer: str
    confidence: float | None = None
    success: bool = True


class EnterpriseEvidencePackage(BaseModel):
    business_goal: str
    evidence_items: list[CollectedEvidenceItem] = Field(default_factory=list)
    coverage: float = 0.0
    sources: list[str] = Field(default_factory=list)
    query_types: list[str] = Field(default_factory=list)
    execution_summary: str = ""
    missing_evidence: list[str] = Field(default_factory=list)
    confidence: float = 0.0

    def observability_metadata(
        self,
        *,
        executed_capabilities: list[str],
        completed_capabilities: list[str],
        failed_capabilities: list[str],
        total_execution_time_ms: float,
    ) -> dict:
        return {
            "executed_capabilities": executed_capabilities,
            "completed_capabilities": completed_capabilities,
            "failed_capabilities": failed_capabilities,
            "total_execution_time_ms": round(total_execution_time_ms, 2),
            "evidence_count": len(self.evidence_items),
            "package_coverage": round(self.coverage, 2),
            "enterprise_evidence_package": self.model_dump(),
        }
