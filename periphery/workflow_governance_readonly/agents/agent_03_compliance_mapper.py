from __future__ import annotations

from typing import Any, Dict, List

from ..constants import AGENT_IDS, CONTROL_FAMILY_HINTS
from ..models import AgentSignal

AGENT_ROLE = {
    "id": AGENT_IDS[2],
    "name": "Compliance / control family mapper",
    "purpose": "Map workflow steps to likely control families without legal verdict.",
    "authority": "none; not legal advice; no compliance verdict",
    "output": "control family hints and review lanes",
}


def map_compliance(risk_payload: Dict[str, Any]) -> AgentSignal:
    """Agent 3 — compliance/control mapper.

    The mapper helps an operator or later governance layer see which control
    families are likely touched by a step. It does not certify compliance.
    """
    steps = risk_payload.get("risk_annotated_steps", [])
    mapped: List[Dict[str, Any]] = []
    all_families = set()

    for step in steps:
        text = f"{step.get('title','')} {step.get('description','')}".lower()
        families = sorted({family for hint, family in CONTROL_FAMILY_HINTS.items() if hint in text})
        if step.get("criticality") in {"high", "critical"}:
            families.append("operator_review")
            families.append("x108_boundary_review")
        families = sorted(set(families))
        all_families.update(families)
        entry = dict(step)
        entry["control_families"] = families
        entry["review_lane"] = "governance_boundary" if step.get("x108_review_required") else "standard_trace"
        entry["legal_advice"] = False
        entry["compliance_verdict"] = False
        entry["candidate_only"] = True
        mapped.append(entry)

    payload = {
        "compliance_mapped_steps": mapped,
        "control_families": sorted(all_families),
        "control_family_count": len(all_families),
        "legal_advice": False,
        "compliance_verdict": False,
        "role_manifest": AGENT_ROLE,
    }
    return AgentSignal(
        agent_id=AGENT_IDS[2],
        signal_family="compliance_signal",
        status="COMPLIANCE_MAPPING_READY",
        summary=f"Mapped {len(mapped)} steps to {len(all_families)} advisory control families.",
        payload=payload,
        confidence=0.58 if mapped else 0.0,
        warnings=["NOT_LEGAL_ADVICE"],
        trace=["risk_annotated_steps", "control_family_hints", "operator_review_hint", "x108_boundary_review_hint"],
        role="COMPLIANCE_MAPPER_READONLY",
    )
