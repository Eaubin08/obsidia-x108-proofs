"""CSSA-specific fail-closed bridge for *historical* F3F/F3G assessments.

Read-only semantic projection. Never equates historical expected_gate=ALLOW to
KX108 authorization; never creates a native mutation, action or approval.
Callers supply objects produced by original CSSA assessors (separate repo).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any


_TYPES = {
    "StressAssessmentV0": ("F3F_STRESS", "scenario_id", "event_date"),
    "ContractAssessmentV0": ("F3G_CONTRACT", "case_id", "assessed_at"),
    "ComplianceAssessmentV0": ("F3G_COMPLIANCE", "case_id", "assessed_at"),
    "InstitutionalAssessmentV0": ("F3G_INSTITUTION", "case_id", "assessed_at"),
    "RootCauseAssessmentV0": ("F3G_ROOT_CAUSE", "case_id", "assessed_at"),
    "BuvetteAssessmentV0": ("F3G_BUVETTE", "case_id", "assessed_at"),
}


@dataclass(frozen=True)
class CssaSemanticWorkProposalV0:
    schema: str
    source_family: str
    source_case_id: str
    assessed_at: str
    disposition: str
    reasons: tuple[str, ...]
    source_evidence_refs: tuple[str, ...]
    source_expected_gate: str | None
    owner_ref: str | None
    native_case_type_proposed: str
    canonical_intake_allowed: bool = False
    action_candidate: None = None
    approved_by: None = None
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    emits_act: bool = False
    decision_authority: str = "KX108_ONLY"

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["reasons"] = list(self.reasons)
        out["source_evidence_refs"] = list(self.source_evidence_refs)
        return out


def project_historical_cssa_assessment_v0(assessment: object) -> CssaSemanticWorkProposalV0:
    typ = type(assessment).__name__
    if typ not in _TYPES:
        raise ValueError("CSSA_SEMANTIC_UNSUPPORTED_ASSESSMENT_TYPE")
    family, id_field, date_field = _TYPES[typ]
    # Require structural dataclass outputs of original deterministic assessors;
    # mere user dictionaries are not accepted as historical assessed evidence.
    if not hasattr(type(assessment), "__dataclass_fields__"):
        raise ValueError("CSSA_SEMANTIC_DATACLASS_REQUIRED")
    case_id = getattr(assessment, id_field, None)
    assessed_at = getattr(assessment, date_field, None)
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("CSSA_SEMANTIC_CASE_ID_REQUIRED")
    if not isinstance(assessed_at, str) or not assessed_at.strip():
        raise ValueError("CSSA_SEMANTIC_ASSESSMENT_DATE_REQUIRED")
    if getattr(assessment, "decision_authority", "KX108_ONLY") != "KX108_ONLY":
        raise ValueError("CSSA_SEMANTIC_AUTHORITY_MISMATCH")
    if getattr(assessment, "external_action", False) is not False:
        raise ValueError("CSSA_SEMANTIC_EXTERNAL_ACTION_FORBIDDEN")
    def vals(field: str) -> tuple[str, ...]:
        raw = getattr(assessment, field, ())
        if not isinstance(raw, (list, tuple)) or any(not isinstance(v, str) for v in raw):
            raise ValueError("CSSA_SEMANTIC_INVALID_" + field.upper())
        return tuple(raw)

    unknowns = vals("unknowns")
    contradictions = vals("contradictions")
    risks = vals("risk_flags")
    evidence = vals("source_ids" if typ == "StressAssessmentV0" else "evidence_refs")
    if typ == "StressAssessmentV0" and getattr(assessment, "conflicts", ()):
        contradictions += ("RESOURCE_CONFLICTS_PRESENT",)
    reasons = []
    if contradictions:
        reasons.extend("CONTRADICTION:" + s for s in contradictions)
    if unknowns:
        reasons.extend("UNKNOWN:" + s for s in unknowns)
    if risks:
        reasons.extend("RISK:" + s for s in risks)
    if not evidence:
        reasons.append("EVIDENCE_NOT_PROVIDED")
    # Historical fixtures and public descriptions are never production approvals.
    if not reasons:
        reasons.append("HUMAN_REVIEW_AND_NATIVE_MAPPING_REQUIRED")
    disposition = "BLOCK" if contradictions else "HOLD"
    owner = getattr(assessment, "responsible_role", None)
    if owner is not None and not isinstance(owner, str):
        raise ValueError("CSSA_SEMANTIC_OWNER_INVALID")
    expected = getattr(assessment, "expected_gate", None)
    if expected is not None and expected not in ("ALLOW", "HOLD", "BLOCK"):
        raise ValueError("CSSA_SEMANTIC_EXPECTED_GATE_INVALID")
    return CssaSemanticWorkProposalV0(
        schema="CSSA_HISTORICAL_ASSESSMENT_SEMANTIC_PROJECTION_V0",
        source_family=family,
        source_case_id=case_id,
        assessed_at=assessed_at,
        disposition=disposition,
        reasons=tuple(reasons),
        source_evidence_refs=evidence,
        source_expected_gate=expected,
        owner_ref=owner,
        native_case_type_proposed=str(getattr(assessment, "case_type", family)),
    )


def verify_historical_cssa_semantic_projection_v0(value: CssaSemanticWorkProposalV0) -> bool:
    return (
        isinstance(value, CssaSemanticWorkProposalV0)
        and value.schema == "CSSA_HISTORICAL_ASSESSMENT_SEMANTIC_PROJECTION_V0"
        and value.source_family in {x[0] for x in _TYPES.values()}
        and bool(value.source_case_id)
        and value.disposition in ("HOLD", "BLOCK")
        and value.reasons != ()
        and value.canonical_intake_allowed is False
        and value.action_candidate is None
        and value.approved_by is None
        and value.allowed_to_decide is False
        and value.allowed_to_act is False
        and value.emits_act is False
        and value.decision_authority == "KX108_ONLY"
    )
