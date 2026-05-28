from __future__ import annotations

from typing import Any, Dict, List

from ..constants import AGENT_IDS
from ..models import AgentSignal
from ..utils import infer_actor, infer_conditions, infer_tools, normalize_lines

AGENT_ROLE = {
    "id": AGENT_IDS[0],
    "name": "SOP extractor",
    "purpose": "Convert raw human process material into ordered candidate steps.",
    "authority": "none; readonly signal only",
    "input": "raw SOP text, meeting note, ticket, operator instruction",
    "output": "ordered candidate steps with actor/tool/condition hints",
    "hard_limits": ["no optimization", "no decision", "no execution", "no rewrite of validated content"],
}


def extract_sop(sop_text: str, title: str = "Untitled workflow") -> AgentSignal:
    """Agent 1 — SOP extractor.

    This agent is intentionally conservative. It turns text into ordered step
    candidates and carries the source line so later agents can replay the
    extraction. It does not simplify business meaning or remove friction.
    """
    lines = normalize_lines(sop_text)
    steps: List[Dict[str, Any]] = []

    for idx, line in enumerate(lines, start=1):
        sid = f"STEP_{idx:03d}"
        step = {
            "index": idx,
            "step_id": sid,
            "title": line[:100],
            "description": line,
            "source_line": line,
            "actor": infer_actor(line),
            "input_refs": [f"source_line:{idx}"],
            "output_refs": [f"candidate_step:{sid}"],
            "tools": infer_tools(line),
            "conditions": infer_conditions(line),
            "next_steps": [f"STEP_{idx + 1:03d}"] if idx < len(lines) else [],
            "previous_steps": [f"STEP_{idx - 1:03d}"] if idx > 1 else [],
            "extraction_method": "ordered_line_preserving_heuristic_v4",
            "candidate_only": True,
        }
        steps.append(step)

    payload = {
        "title": title,
        "extracted_step_count": len(steps),
        "steps": steps,
        "source_excerpt": sop_text[:2000],
        "role_manifest": AGENT_ROLE,
        "limitations": [
            "heuristic_line_based_extraction",
            "does_not_infer_missing_steps_as_truth",
            "readonly_signal_only",
            "no_execution",
        ],
    }
    status = "SOP_EXTRACTION_READY" if steps else "LOW_MATERIAL"
    return AgentSignal(
        agent_id=AGENT_IDS[0],
        signal_family="sop_extraction_signal",
        status=status,
        summary=f"Extracted {len(steps)} ordered candidate SOP steps as readonly structure.",
        payload=payload,
        confidence=0.70 if steps else 0.0,
        warnings=[] if steps else ["NO_STEPS_EXTRACTED"],
        trace=["input_sop_text", "normalize_lines", "actor_tool_condition_hints", "candidate_steps"],
        role="SOP_EXTRACTOR_READONLY",
    )
