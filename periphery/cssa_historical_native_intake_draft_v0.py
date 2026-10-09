"""CSSA historical semantic assessment → non-executing native intake draft.

Deliberately does not call execute_native_case_task_intake_v0. Source evidence
must be explicitly attested by the caller; a simulation never proves club
authority. A proposed plan is not a permission to create native state.
"""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256

from periphery.cssa_historical_semantic_adapter_v0 import (
    CssaSemanticWorkProposalV0, verify_historical_cssa_semantic_projection_v0,
)
from periphery.native_ops.intake_bundle_v0 import (
    build_native_case_task_intake_plan_v0,
    verify_native_case_task_intake_plan_v0,
)

_ALLOWED_CASE_TYPES = {
    "F3G_CONTRACT": "CONTRACT_REVIEW",
    "F3G_COMPLIANCE": "COMPLIANCE_REVIEW",
    "F3G_INSTITUTION": "INSTITUTIONAL_REVIEW",
    "F3G_ROOT_CAUSE": "INCIDENT_REVIEW",
    "F3G_BUVETTE": "MATCHDAY_OPERATIONS_REVIEW",
    "F3F_STRESS": "SEASON_CONFLICT_REVIEW",
}


def draft_cssa_historical_native_intake_v0(
    proposal: CssaSemanticWorkProposalV0, *,
    observed_source_ref: str | None,
    observed_evidence_refs: tuple[str, ...] = (),
    occurred_at: str | None,
    due_at: str | None,
    proposed_owner_ref: str | None,
) -> dict:
    """Produce a review-only canonical intake plan when evidence is sufficient.

    observed_* means explicit caller-supplied provenance reference, not a
    verification of the external issuer or authenticity of the reference.
    """
    if not verify_historical_cssa_semantic_projection_v0(proposal):
        raise ValueError("CSSA_INTAKE_PROJECTION_INVALID")
    reasons = []
    if proposal.disposition == "BLOCK":
        reasons.append("HISTORICAL_ASSESSMENT_BLOCKED")
    if not observed_source_ref or not observed_source_ref.strip():
        reasons.append("OBSERVED_SOURCE_REFERENCE_MISSING")
    if not observed_evidence_refs or any(
        not isinstance(s, str) or not s.strip() for s in observed_evidence_refs
    ):
        reasons.append("OBSERVED_EVIDENCE_REFERENCES_MISSING")
    if not proposed_owner_ref or not proposed_owner_ref.strip():
        reasons.append("RESPONSIBLE_OWNER_NOT_BOUND")
    for field, value in (("OCCURRED_AT", occurred_at), ("DUE_AT", due_at)):
        if not isinstance(value, str):
            reasons.append(field + "_MISSING")
            continue
        try:
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                reasons.append(field + "_TIMEZONE_REQUIRED")
        except ValueError:
            reasons.append(field + "_INVALID")
    if reasons:
        return {
            "status": "BLOCK" if proposal.disposition == "BLOCK" else "HOLD",
            "reasons": reasons,
            "native_plan": None,
            "canonical_intake_committed": False,
            "approval_granted": False,
            "action_candidate": None,
            "decision_authority": "KX108_ONLY",
        }
    seed = sha256((
        proposal.source_family + "|" + proposal.source_case_id + "|" +
        observed_source_ref + "|" + due_at
    ).encode("utf-8")).hexdigest()[:24]
    plan = build_native_case_task_intake_plan_v0(
        intake_id="cssa-history:" + seed,
        case_id="cssa-history-case:" + seed,
        task_id="cssa-history-task:" + seed,
        interaction_id="cssa-history-interaction:" + seed,
        followup_id="cssa-history-followup:" + seed,
        case_type=_ALLOWED_CASE_TYPES[proposal.source_family],
        title="CSSA review: " + proposal.source_family + " / " + proposal.source_case_id,
        summary="Historical CSSA assessment for human review; no execution authority",
        owner_ref=proposed_owner_ref,
        priority="NORMAL",
        occurred_at=occurred_at,
        due_at=due_at,
        source_refs=(observed_source_ref,),
        evidence_refs=observed_evidence_refs,
        tags=("CSSA", "HISTORICAL_ASSESSMENT", "REVIEW_ONLY"),
    )
    if verify_native_case_task_intake_plan_v0(plan) != (True, None):
        raise ValueError("CSSA_INTAKE_NATIVE_PLAN_INVALID")
    return {
        "status": "NATIVE_INTAKE_DRAFT_FOR_REVIEW",
        "reasons": ["HUMAN_AUTHORITY_AND_KX108_GATE_STILL_REQUIRED"],
        "native_plan": plan,
        "canonical_intake_committed": False,
        "approval_granted": False,
        "action_candidate": None,
        "decision_authority": "KX108_ONLY",
    }
