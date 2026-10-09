"""CSSA Pass 2: complete review-only work register, including structural gaps.

Inputs are real historical assessments and the original public role contract.
No real actor/delegation is assumed. No native or external mutation.
"""
from __future__ import annotations
from collections import Counter
from typing import Mapping
from periphery.cssa_administrative_batch_pass2_v0 import assemble_cssa_administrative_batch_v0

_ROLE_FAMILIES = {
 "ADMINISTRATION_DAILY": ("F3G_CONTRACT", "F3G_COMPLIANCE"),
 "INSTITUTIONAL_RELATIONS": ("F3G_INSTITUTION",),
 "PEOPLE_MANAGEMENT_DELEGATION": (),
 "CROSS_POLE_COORDINATION": ("F3F_STRESS",),
 "MATCHDAY_TICKETING": (),
 "MATCHDAY_SECURITY": (),
 "MATCHDAY_WELCOME_HOSPITALITY": (),
 "MATCHDAY_BUVETTE_RESTAURATION": ("F3G_BUVETTE",),
 "WRITTEN_PROCESS_RESPONSIBILITY": ("F3G_COMPLIANCE",),
 "ROOT_CAUSE_DURABILITY": ("F3G_ROOT_CAUSE",),
 "DECISION_EXECUTION": (),
}

def assemble_cssa_role_work_register_v0(assessments, bindings, role_contract: Mapping) -> dict:
    """Crosswalk all 11 published duties; never upgrade public roles to authority."""
    if role_contract.get("status") != "PUBLIC_ANNOUNCED_ROLE_CONTRACT_READONLY":
        raise ValueError("CSSA_ROLE_CONTRACT_NOT_PUBLIC_READONLY")
    boundaries = role_contract.get("global_boundaries", {})
    if (boundaries.get("real_field_evidence") is not False
            or boundaries.get("external_action") is not False
            or boundaries.get("decision_authority") != "KX108_ONLY"):
        raise ValueError("CSSA_ROLE_CONTRACT_AUTHORITY_MISMATCH")
    roles = role_contract.get("requirements", [])
    ids = [x["id"] for x in roles]
    if len(ids) != 11 or set(ids) != set(_ROLE_FAMILIES):
        raise ValueError("CSSA_ROLE_MATRIX_NOT_EXACT_11")
    batch = assemble_cssa_administrative_batch_v0(assessments, bindings)
    families = {e["id"].split(":", 1)[0] for e in batch["entries"]}
    matrix = []
    for r in roles:
        role = r["id"]
        expected = _ROLE_FAMILIES[role]
        connected = tuple(x for x in expected if x in families)
        missing = tuple(x for x in expected if x not in families)
        gaps = tuple(r.get("open_gaps", []))
        matrix.append({
            "role_id": role,
            "historical_coverage": r["coverage_level"],
            "connected_assessment_families": connected,
            "unconnected_assessment_families": missing,
            "public_contract_open_gaps": gaps,
            "real_authority_proven": False,
            "operational_readiness": "NOT_VERIFIED",
        })
    return {
        "schema": "CSSA_PASS2_ROLE_WORK_REGISTER_V0",
        "work_batch": batch,
        "role_matrix": matrix,
        "role_count": len(matrix),
        "family_count": len(families),
        "family_set": tuple(sorted(families)),
        "coverage_counts": dict(Counter(x["historical_coverage"] for x in matrix)),
        "canonical_native_writes": 0,
        "real_approvals": 0,
        "field_authority_verified": False,
        "decision_authority": "KX108_ONLY",
    }