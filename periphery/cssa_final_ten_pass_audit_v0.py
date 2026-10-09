"""CSSA Pass 10: exact ten-pass simulation closure, strictly non-operational.

Verifies independent Lot A/B/C diagnostic evidence, provenance and guard rails.
This is a report, not a sovereign execution receipt or deployment approval.
"""
from __future__ import annotations
from collections.abc import Mapping
from hashlib import sha256
import json

EXPECTED=("LOT_A_CLOSED_SIMULATION","LOT_B_CLOSED_SIMULATION","LOT_C_CLOSED_SIMULATION")

def audit_cssa_final_ten_passes_v0(*,lot_a:Mapping,lot_b:Mapping,lot_c:Mapping,
                                  regression:Mapping,branch:str,working_tree_clean:bool) -> dict:
    issues=[]
    if lot_a.get("verdict")!=EXPECTED[0] or lot_a.get("season_event_count")!=904 or lot_a.get("verified_public_role_count")!=11:
        issues.append("LOT_A_904_OR_11_ROLES_NOT_PROVEN")
    if lot_b.get("verdict")!=EXPECTED[1] or lot_b.get("lot_a_verdict")!=EXPECTED[0]:
        issues.append("LOT_B_CHAIN_INVALID")
    if lot_b.get("matchday_stream_count")!=11 or len(lot_b.get("incident_routes",()))!=7:
        issues.append("LOT_B_MATCHDAY_OR_CASCADE_INCOMPLETE")
    if lot_c.get("verdict")!=EXPECTED[2] or sorted(lot_c.get("source_kinds",()))!=["CALENDAR","CRM","DOCUMENT","MAIL"]:
        issues.append("LOT_C_FOUR_SOURCES_INCOMPLETE")
    if not lot_c.get("kx108_sandbox_evidence"):
        issues.append("LOT_C_KX108_SANDBOX_PROOF_ABSENT")
    for name,report,zero_fields in (
        ("A",lot_a,("native_writes","real_authorizations")),
        ("B",lot_b,("mail_sent","crm_writes","external_actions","real_approvals")),
        ("C",lot_c,("native_writes","mail_sends","calendar_writes","external_calls")),
    ):
        for field in zero_fields:
            if report.get(field)!=0:
                issues.append("UNSAFE_"+name+"_"+field.upper())
        if report.get("decision_authority")!="KX108_ONLY":
            issues.append("AUTHORITY_"+name+"_INVALID")
        if report.get("scope") not in ("SYNTHETIC_STRUCTURAL_ONLY","SIMULATED_OFFLINE_ONLY"):
            issues.append("SCOPE_"+name+"_UNVERIFIED")
    if lot_c.get("real_operator_approval") is not False or lot_c.get("actual_world_action") is not False:
        issues.append("REAL_ACTION_CLAIM")
    if lot_b.get("world_action_allowed") is not False:
        issues.append("LOT_B_WORLD_ACTION_CLAIM")
    if regression.get("passed")!=268 or regression.get("skipped")!=1 or regression.get("failed")!=0:
        issues.append("REGRESSION_NOT_USER_VERIFIED_BASELINE")
    if not regression.get("user_confirmed"):
        issues.append("REGRESSION_EVIDENCE_NOT_ATTESTED")
    if branch!="feat/cssa-v01-active":
        issues.append("UNAUTHORIZED_BRANCH")
    if working_tree_clean is not True:
        issues.append("DIRTY_WORKTREE")
    # A clean tree attestation applies to the user's previous run; commits created
    # after that run require one new user-side verification before freeze acceptance.
    result={
        "schema":"CSSA_FINAL_TEN_PASS_AUDIT_V0",
        "verdict":"CSSA_THREE_LOTS_CLOSED_SIMULATION" if not issues else "CSSA_FINAL_AUDIT_BLOCKED",
        "issues":issues,"passes_total":10,"lot_a":lot_a.get("verdict"),
        "lot_b":lot_b.get("verdict"),"lot_c":lot_c.get("verdict"),
        "baseline_passed":regression.get("passed"),"baseline_skipped":regression.get("skipped"),
        "baseline_failed":regression.get("failed"),"branch":branch,
        "scope":"SIMULATED_AND_OFFLINE_ONLY",
        "freeze_eligible":not issues,"production_readiness":"NOT_VERIFIED",
        "real_cssa_authority":False,"external_effects":0,
        "main_modified":False,"decision_authority":"KX108_ONLY",
        "receipt_kind":"DIAGNOSTIC_ONLY_NOT_SOVEREIGN"
    }
    result["diagnostic_sha256"]=sha256(json.dumps(result,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
    return result
