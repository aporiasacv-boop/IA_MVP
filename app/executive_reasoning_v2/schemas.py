from pydantic import BaseModel, Field

from app.executive_reasoning_v2.constants import REASONING_V2_SECTIONS


class ExecutiveReasoningV2Payload(BaseModel):
    executive_summary: str | None = None
    findings: list[str] = Field(default_factory=list)
    interpretation: str | None = None
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    next_analyses: list[str] = Field(default_factory=list)

    def generated_sections(self) -> list[str]:
        sections: list[str] = []
        if self.executive_summary:
            sections.append("executive_summary")
        if self.findings:
            sections.append("findings")
        if self.interpretation:
            sections.append("interpretation")
        if self.risks:
            sections.append("risks")
        if self.opportunities:
            sections.append("opportunities")
        if self.recommendations:
            sections.append("recommendations")
        if self.limitations:
            sections.append("limitations")
        if self.next_analyses:
            sections.append("next_analyses")
        return sections

    def has_content(self) -> bool:
        return bool(self.generated_sections())

    def to_panel_payload(self) -> dict:
        return {
            "executive_summary": self.executive_summary,
            "findings": self.findings,
            "business_interpretation": self.interpretation,
            "possible_risks": self.risks,
            "opportunities": self.opportunities,
            "recommendations": self.recommendations,
            "limitations": self.limitations,
            "next_analyses": self.next_analyses,
            "next_questions": self.next_analyses,
            "source": "executive_reasoning_v2",
        }

    def to_executive_answer(self) -> str:
        if self.executive_summary:
            return self.executive_summary.strip()
        if self.findings:
            return (
                "Con la evidencia disponible puedo concluir lo siguiente:\n"
                + "\n".join(f"- {item}" for item in self.findings)
            )
        if self.interpretation:
            return self.interpretation.strip()
        return "Con la evidencia disponible no puedo emitir una conclusión ejecutiva completa."
