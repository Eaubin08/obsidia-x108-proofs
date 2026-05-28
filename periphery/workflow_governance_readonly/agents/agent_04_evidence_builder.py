from __future__ import annotations

from typing import Any, Dict, List

from ..constants import AGENT_IDS, EVIDENCE_REQUIREMENTS_BY_CRITICALITY
from ..models import AgentSignal

AGENT_ROLE = {
    "id": AGENT_IDS[3],
    "name": "Evidence builder",
    "purpose": "Translate criticality/control families into proof requirements before X108 review.",
    "authority": "none; evidence requirements only",
    "output": "evidence ledger skeleton and global required evidence list",
}


def build_evidence(compliance_payload: Dict[str, Any]) -> AgentSignal:
    """Agent 4 — Evidence builder.

    Input must normally be Agent 3 payload. For defensive compatibility it also
    accepts Agent 2 style `risk_annotated_steps`, but marks this as degraded.
    """
    degraded_input = False
    steps = compliance_payload.get("compliance_mapped_steps")
    if steps is None:
        steps = compliance_payload.get("risk_annotated_steps", [])
        degraded_input = True

    evidence_by_step: List[Dict[str, Any]] = []
    all_required = set()

    for step in steps:
        criticality = step.get("criticality", "low")
        required = list(EVIDENCE_REQUIREMENTS_BY_CRITICALITY.get(criticality, EVIDENCE_REQUIREMENTS_BY_CRITICALITY["low"]))
        if step.get("control_families"):
            required.append("control_family_note")
        if step.get("x108_review_required") and "x108_gate_required" not in required:
            required.append("x108_gate_required")
        required = sorted(set(required))
        all_required.update(required)
        evidence_by_step.append({
            "step_id": step.get("step_id"),
            "criticality": criticality,
            "risk_categories": list(step.get("risk_categories", [])),
            "control_families": list(step.get("control_families", [])),
            "required_evidence": required,
            "evidence_status": "requirements_only_missing_until_supplied",
            "evidence_evaluation": False,
            "x108_review_required": bool(step.get("x108_review_required") or "x108_gate_required" in required),
            "candidate_only": True,
        })

    warnings = ["DEGRADED_INPUT_RISK_PAYLOAD_USED"] if degraded_input else []
    payload = {
        "evidence_by_step": evidence_by_step,
        "global_required_evidence": sorted(all_required),
        "evidence_policy_note": "requirements only; evidence evaluation remains outside this primitive",
        "degraded_input": degraded_input,
        "role_manifest": AGENT_ROLE,
    }
    return AgentSignal(
        agent_id=AGENT_IDS[3],
        signal_family="evidence_signal",
        status="EVIDENCE_REQUIREMENTS_READY",
        summary=f"Built evidence requirements for {len(evidence_by_step)} steps.",
        payload=payload,
        confidence=0.76 if evidence_by_step and not degraded_input else 0.55 if evidence_by_step else 0.0,
        warnings=warnings,
        trace=["compliance_mapped_steps", "criticality_to_evidence", "global_requirements", "x108_gate_requirement_mapping"],
        role="EVIDENCE_BUILDER_READONLY",
    )
