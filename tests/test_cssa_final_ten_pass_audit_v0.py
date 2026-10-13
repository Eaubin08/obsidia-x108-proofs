"""Final CSSA ten-pass freeze: independent evidence and non-escalation checks."""
import pytest
from periphery.cssa_final_ten_pass_audit_v0 import audit_cssa_final_ten_passes_v0

def inputs():
    return dict(
        lot_a={"verdict":"LOT_A_CLOSED_SIMULATION","season_event_count":904,
            "verified_public_role_count":11,"native_writes":0,"real_authorizations":0,
            "decision_authority":"KX108_ONLY","scope":"SYNTHETIC_STRUCTURAL_ONLY"},
        lot_b={"verdict":"LOT_B_CLOSED_SIMULATION","lot_a_verdict":"LOT_A_CLOSED_SIMULATION",
            "matchday_stream_count":11,"incident_routes":[{"incident":str(i)} for i in range(7)],
            "mail_sent":0,"crm_writes":0,"external_actions":0,"real_approvals":0,
            "world_action_allowed":False,"decision_authority":"KX108_ONLY",
            "scope":"SYNTHETIC_STRUCTURAL_ONLY"},
        lot_c={"verdict":"LOT_C_CLOSED_SIMULATION","source_kinds":["CALENDAR","CRM","DOCUMENT","MAIL"],
            "kx108_sandbox_evidence":True,"native_writes":0,"mail_sends":0,
            "calendar_writes":0,"external_calls":0,"real_operator_approval":False,
            "actual_world_action":False,"decision_authority":"KX108_ONLY",
            "scope":"SIMULATED_OFFLINE_ONLY"},
        regression={"passed":268,"skipped":1,"failed":0,"user_confirmed":True},
        branch="feat/cssa-v01-active",working_tree_clean=True)

def test_all_ten_passes_close_simulation_only():
    r=audit_cssa_final_ten_passes_v0(**inputs())
    assert r["verdict"]=="CSSA_THREE_LOTS_CLOSED_SIMULATION"
    assert r["freeze_eligible"] is True
    assert r["passes_total"]==10
    assert r["production_readiness"]=="NOT_VERIFIED"
    assert r["real_cssa_authority"] is False
    assert r["receipt_kind"]=="DIAGNOSTIC_ONLY_NOT_SOVEREIGN"
    assert len(r["diagnostic_sha256"])==64

@pytest.mark.parametrize("field,replacement,expected",[
    ("lot_a",{"verdict":"LOT_A_BLOCKED"},"LOT_A_904_OR_11_ROLES_NOT_PROVEN"),
    ("lot_b",{"verdict":"LOT_B_BLOCKED"},"LOT_B_CHAIN_INVALID"),
    ("lot_c",{"verdict":"LOT_C_BLOCKED"},"LOT_C_FOUR_SOURCES_INCOMPLETE"),
    ("regression",{"passed":267,"skipped":1,"failed":1,"user_confirmed":True},"REGRESSION_NOT_USER_VERIFIED_BASELINE"),
    ("branch","main","UNAUTHORIZED_BRANCH"),
    ("working_tree_clean",False,"DIRTY_WORKTREE"),
])
def test_missing_proof_or_bad_branch_blocks(field,replacement,expected):
    p=inputs()
    p[field]=replacement
    r=audit_cssa_final_ten_passes_v0(**p)
    assert r["verdict"]=="CSSA_FINAL_AUDIT_BLOCKED"
    assert expected in r["issues"]

@pytest.mark.parametrize("lot,field",[
    ("lot_a","native_writes"),("lot_b","external_actions"),
    ("lot_c","mail_sends"),("lot_c","calendar_writes"),
])
def test_external_or_native_effect_claim_blocks(lot,field):
    p=inputs()
    p[lot][field]=1
    r=audit_cssa_final_ten_passes_v0(**p)
    assert not r["freeze_eligible"]

def test_regression_not_attested_blocks():
    p=inputs()
    p["regression"]["user_confirmed"]=False
    assert "REGRESSION_EVIDENCE_NOT_ATTESTED" in audit_cssa_final_ten_passes_v0(**p)["issues"]

def test_real_world_action_claim_blocks():
    p=inputs()
    p["lot_c"]["actual_world_action"]=True
    assert "REAL_ACTION_CLAIM" in audit_cssa_final_ten_passes_v0(**p)["issues"]
