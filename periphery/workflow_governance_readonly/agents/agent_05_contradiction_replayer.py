from __future__ import annotations

from typing import Any, Dict, List

from ..constants import AGENT_IDS
from ..models import AgentSignal

AGENT_ROLE = {
    "id": AGENT_IDS[4],
    "name": "Contradiction / replay checker",
    "purpose": "Check that extracted, risk, compliance and evidence mappings remain structurally coherent.",
    "authority": "none; replay warnings only",
    "output": "structural replay trace, coverage checks, contradiction warnings",
}


def replay_contradictions(
    extraction_payload: Dict[str, Any],
    risk_payload: Dict[str, Any],
    evidence_payload: Dict[str, Any],
    compliance_payload: Dict[str, Any] | None = None,
) -> AgentSignal:
    """Agent 5 — contradiction/replay checker.

    This performs structural replay only. It checks coverage and missing proof
    mappings without making a decision about the underlying operation.
    """
    steps = extraction_payload.get("steps", [])
    risk_steps = {s.get("step_id"): s for s in risk_payload.get("risk_annotated_steps", [])}
    evidence_steps = {s.get("step_id"): s for s in evidence_payload.get("evidence_by_step", [])}
    compliance_steps = {}
    if compliance_payload:
        compliance_steps = {s.get("step_id"): s for s in compliance_payload.get("compliance_mapped_steps", [])}

    warnings: List[str] = []
    replay_trace: List[Dict[str, Any]] = []

    for step in steps:
        sid = step.get("step_id")
        risk = risk_steps.get(sid)
        evidence = evidence_steps.get(sid)
        compliance = compliance_steps.get(sid) if compliance_steps else None
        if not risk:
            warnings.append(f"MISSING_RISK_MAPPING:{sid}")
        if compliance_steps and not compliance:
            warnings.append(f"MISSING_COMPLIANCE_MAPPING:{sid}")
        if not evidence:
            warnings.append(f"MISSING_EVIDENCE_MAPPING:{sid}")
        if risk and risk.get("criticality") in {"high", "critical"}:
            required = evidence.get("required_evidence", []) if evidence else []
            if "x108_gate_required" not in required:
                warnings.append(f"MISSING_X108_GATE_REQUIRED_EVIDENCE:{sid}")

        replay_trace.append({
            "step_id": sid,
            "has_risk_mapping": bool(risk),
            "has_compliance_mapping": bool(compliance) if compliance_steps else "not_supplied",
            "has_evidence_mapping": bool(evidence),
            "criticality": risk.get("criticality") if risk else None,
            "x108_review_required": bool(risk.get("x108_review_required")) if risk else False,
            "replay_scope": "structure_only_no_side_effects",
        })

    payload = {
        "replay_trace": replay_trace,
        "contradiction_warnings": warnings,
        "coverage": {
            "step_count": len(steps),
            "risk_count": len(risk_steps),
            "compliance_count": len(compliance_steps) if compliance_steps else None,
            "evidence_count": len(evidence_steps),
        },
        "structural_replay_possible": len(steps) > 0,
        "replay_scope": "structure_only_no_execution",
        "role_manifest": AGENT_ROLE,
    }
    status = "CONTRADICTION_REPLAY_READY" if not warnings else "CONTRADICTION_WARNINGS_PRESENT"
    return AgentSignal(
        agent_id=AGENT_IDS[4],
        signal_family="contradiction_signal",
        status=status,
        summary=f"Replay checked {len(steps)} steps; warnings={len(warnings)}.",
        payload=payload,
        confidence=0.74 if steps else 0.0,
        warnings=warnings,
        trace=["extraction_payload", "risk_payload", "compliance_payload", "evidence_payload", "structure_replay"],
        role="CONTRADICTION_REPLAYER_READONLY",
    )
