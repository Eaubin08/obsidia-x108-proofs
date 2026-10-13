"""Lot C unified acceptance (passes 7-9), with true KX108 sandbox receipt."""
from dataclasses import replace
import pytest
from periphery.cssa_lot_c_universal_passes7_9_v0 import (
    CSSAEnterpriseSourceV0,route_cssa_universal_source_v0,build_cssa_lot_c_cockpit_v0,
)
from periphery.native_ops.intake_bundle_v0 import verify_native_case_task_intake_plan_v0
from periphery.cssa_sovereign_sandbox_lot_a_v0 import run_cssa_sovereign_sandbox_lot_a

def source(kind,**kwargs):
    data=dict(source_id="sim:"+kind,kind=kind,mode="SIMULATED_FIXTURE",
        scope="CSSA_SYNTHETIC_OFFICE",reference="sim:reference:"+kind,
        evidence_refs=("sim:evidence:"+kind,),owner_ref="SIMULATED:OWNER",
        observed_at="2026-10-07T10:00:00+00:00",
        due_at="2026-10-20T10:00:00+00:00",task_kind="FOLLOWUP_REVIEW",
        title="Synthetic CSSA office review",summary="Review only",
        classified_operational=True,human_review_ref="SIMULATED:REVIEWER")
    data.update(kwargs)
    return CSSAEnterpriseSourceV0(**data)

def proof(tmp_path):
    return run_cssa_sovereign_sandbox_lot_a(
        [dict(id="licence",kind="DEADLINE",owner="manager",
            slot="2026-10-20T16:00:00+00:00",source_ref="cssa:fiction:licence",
            regulatory_basis_proven=True,due_at="2026-10-20T16:00:00+00:00")],
        root=tmp_path/"cssa",simulate_operator_approval=True)

def inputs(tmp_path):
    return dict(lot_a=dict(verdict="LOT_A_CLOSED_SIMULATION",season_event_count=904,
        native_writes=0),lot_b=dict(verdict="LOT_B_CLOSED_SIMULATION",
        matchday_stream_count=11,crm_writes=0),
        observations=(source("MAIL"),source("CALENDAR"),source("DOCUMENT"),
            source("CRM"),source("MAIL",source_id="sim:personal",
                scope="PERSONAL_INBOX",classified_operational=False),
            source("DOCUMENT",source_id="sim:ambiguous",classified_operational=False)),
        sandbox_proof=proof(tmp_path),
        portable_config=dict(run_mode="OFFLINE_READONLY",branch="feat/cssa-v01-active",
            provider_network_allowed=False,real_club_credentials_loaded=False,
            shared_kernel_mutable=False))

def test_single_lot_c_covers_all_passes_true_sandbox_proof(tmp_path):
    result=build_cssa_lot_c_cockpit_v0(**inputs(tmp_path))
    assert result["verdict"]=="LOT_C_CLOSED_SIMULATION",result["failures"]
    assert result["source_kinds"]==["CALENDAR","CRM","DOCUMENT","MAIL"]
    assert result["crm_plan_count"]==4
    assert result["calendar_candidate_count"]==4
    assert result["email_draft_count"]==1
    assert result["mail_sends"]==result["calendar_writes"]==result["native_writes"]==0
    assert result["external_calls"]==0 and result["real_operator_approval"] is False
    assert len(result["diagnostic_sha256"])==64

@pytest.mark.parametrize("kind",["MAIL","CALENDAR","DOCUMENT","CRM"])
def test_real_native_bundle_prepared_not_applied(kind):
    r=route_cssa_universal_source_v0(source(kind))
    assert r["status"]=="DRAFT_REVIEW_ONLY"
    assert verify_native_case_task_intake_plan_v0(r["plan"])==(True,None)
    assert r["crm_writes"]==0 and r["external_effect"] is False

def test_personal_inbox_quarantined():
    r=route_cssa_universal_source_v0(source("MAIL",scope="PERSONAL_INBOX"))
    assert r["status"]=="PERSONAL_READONLY"
    assert r["plan"] is None

@pytest.mark.parametrize("patch",[
    {"reference":None},{"evidence_refs":()},{"owner_ref":None},
    {"human_review_ref":None},{"observed_at":"2026-10-07"},
    {"due_at":None},{"classified_operational":False},
    {"mode":"CSSA_OPERATIONAL_UNVERIFIED"},
    {"external_permission_verified":True},
])
def test_non_verified_source_never_becomes_a_plan(patch):
    r=route_cssa_universal_source_v0(source("MAIL",**patch))
    assert r["status"]=="HOLD"
    assert r["plan"] is None

def test_contradiction_blocks_before_plan():
    r=route_cssa_universal_source_v0(source("MAIL",known_contradictions=("SOURCE_CONFLICT",)))
    assert r["status"]=="BLOCK" and r["plan"] is None

@pytest.mark.parametrize("field,value,expected",[
    ("sandbox_proof",None,"UNIVERSAL_KX108_SANDBOX_PROOF_MISSING"),
    ("lot_a",{"verdict":"LOT_A_BLOCKED"},"LOT_A_EVIDENCE_INVALID"),
    ("lot_b",{"verdict":"LOT_B_BLOCKED"},"LOT_B_EVIDENCE_INVALID"),
    ("portable_config",{"run_mode":"LIVE"},"PORTABLE_PROFILE_UNSAFE"),
])
def test_evidence_or_portable_policy_missing_blocks(tmp_path,field,value,expected):
    data=inputs(tmp_path)
    data[field]=value
    result=build_cssa_lot_c_cockpit_v0(**data)
    assert result["verdict"]=="LOT_C_BLOCKED"
    assert expected in result["failures"]

def test_sandbox_proof_tampering_blocks(tmp_path):
    data=inputs(tmp_path)
    data["sandbox_proof"]=dict(data["sandbox_proof"],real_operator_approval=True)
    result=build_cssa_lot_c_cockpit_v0(**data)
    assert result["verdict"]=="LOT_C_BLOCKED"

def test_duplicate_connector_ref_rejected(tmp_path):
    data=inputs(tmp_path)
    data["observations"]=(source("MAIL"),source("MAIL"))
    with pytest.raises(ValueError,match="DUPLICATE_SOURCE"):
        build_cssa_lot_c_cockpit_v0(**data)
