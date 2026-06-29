from pydantic import BaseModel, Field


class CandidateCapability(BaseModel):
    capability_id: str
    label: str
    score: float


class CapabilityReasonerPlan(BaseModel):
    reasoning_goal: str
    candidate_capabilities: list[CandidateCapability] = Field(default_factory=list)
    selected_capabilities: list[str] = Field(default_factory=list)
    estimated_coverage: float
    recommended_plan: str
    fallback_recommended: bool

    def observability_metadata(self) -> dict:
        return {
            "reasoning_goal": self.reasoning_goal,
            "candidate_capabilities": [
                {"capability_id": item.capability_id, "score": round(item.score, 2)}
                for item in self.candidate_capabilities
            ],
            "selected_capabilities": self.selected_capabilities,
            "estimated_coverage": round(self.estimated_coverage, 2),
            "recommended_plan": self.recommended_plan,
            "fallback_recommended": self.fallback_recommended,
            "capability_reasoner_plan": self.model_dump(),
        }
