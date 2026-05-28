from __future__ import annotations

from ..agents.agent_01_sop_extractor import AGENT_ROLE, extract_sop

SKILL_SPEC = {
    "skill_id": "SKILL_EXTRACT_SOP_READONLY",
    "wrapped_agent": AGENT_ROLE,
    "contract": "raw SOP text becomes ordered candidate steps; no optimization; no decision",
}

__all__ = ["extract_sop", "SKILL_SPEC"]
