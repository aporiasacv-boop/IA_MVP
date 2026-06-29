import json
import re

from app.business_copilot.constants import COPILOT_MAX_PROPOSALS
from app.business_copilot.schemas import CopilotPayload, CopilotProposal


def parse_copilot_response(text: str) -> CopilotPayload | None:
    cleaned = text.strip()
    if not cleaned:
        return None

    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        payload = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    try:
        parsed = CopilotPayload.model_validate(payload)
    except Exception:
        return None

    proposals = [proposal for proposal in parsed.proposals if _is_valid_proposal(proposal)]
    if not proposals:
        return None

    return CopilotPayload(proposals=proposals[:COPILOT_MAX_PROPOSALS])


def _is_valid_proposal(proposal: CopilotProposal) -> bool:
    return bool(
        proposal.title.strip()
        and proposal.rationale.strip()
        and proposal.action_label.strip()
        and proposal.query.strip()
        and proposal.proposal_type.strip()
    )
