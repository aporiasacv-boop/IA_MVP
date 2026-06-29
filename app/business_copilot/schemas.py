from pydantic import BaseModel, Field


class CopilotProposal(BaseModel):
    title: str
    rationale: str
    action_label: str
    query: str
    proposal_type: str


class CopilotPayload(BaseModel):
    proposals: list[CopilotProposal] = Field(default_factory=list)
