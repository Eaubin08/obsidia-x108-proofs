"""Pass 2 closure acceptance: licence, staff, delegation, refusal and no authority."""
from dataclasses import replace
import pytest
from periphery.cssa_admin_licence_people_closure_pass2_v0 import CSSAAdminCaseV0, plan_cssa_admin_case_v0, close_cssa_pass2_admin_campaign_v0
from periphery.native_ops.intake_bundle_v0 import verify_native_case_task_intake_plan_v0

def case(kind="LICENCE", **kw):
    base=dict(case_id="synthetic-"+kind, kind=kind, source_ref="sim:cssa:source",
        evidence_refs=("sim:cssa:evidence",), responsible_role="RESP_ADMIN",
        assigned_actor_ref="SIMULATED:RESP_ADMIN",delegation_authority_ref=None,
        occurred_at="2026-10-07T10:00:00+00:00",due_at="2026-10-18T12:00:00+00:00")
    base.update(kw)
    return CSSAAdminCaseV0(**base)

@pytest.mark.parametrize("kind",["LICENCE","OFFICIAL_REGISTRATION","STAFF_AVAILABILITY","VOLUNTEER_ABSENCE"])
def test_native_review_draft_for_admin_families(kind):
    result=plan_cssa_admin_case_v0(case(kind))
    assert result["status"]=="DRAFT_REVIEW_ONLY"
    assert verify_native_case_task_intake_plan_v0(result["plan"])==(True,None)
    assert result["plan"].allowed_to_act is False
    assert result["approved"] is False

@pytest.mark.parametrize("kind",["DELEGATION","SUBSTITUTION"])
def test_delegation_without_authority_holds(kind):
    result=plan_cssa_admin_case_v0(case(kind))
    assert result["status"]=="HOLD"
    assert "DELEGATION_AUTHORITY_NOT_VERIFIED" in result["reasons"]
    assert result["plan"] is None

def test_delegation_reference_is_not_actual_permission():
    result=plan_cssa_admin_case_v0(case("DELEGATION",delegation_authority_ref="sim:mandate:1"))
    assert result["status"]=="DRAFT_REVIEW_ONLY"
    assert result["approved"] is False

@pytest.mark.parametrize("patch",[
    {"source_ref":None},{"evidence_refs":()}, {"assigned_actor_ref":None},
    {"responsible_role":None},{"occurred_at":"2026-10-07"},{"due_at":None},
])
def test_missing_provenance_and_ownership_holds(patch):
    result=plan_cssa_admin_case_v0(case(**patch))
    assert result["status"]=="HOLD"
    assert result["plan"] is None

def test_contradiction_blocks():
    result=plan_cssa_admin_case_v0(case(contradictions=("PLAYER_INELIGIBLE",)))
    assert result["status"]=="BLOCK"

def test_no_real_club_authority_claim_is_accepted():
    with pytest.raises(ValueError,match="SIMULATION_ONLY"):
        plan_cssa_admin_case_v0(case(real_club_access=True))

def test_complete_campaign_aggregates_drafts_holds_and_blocks():
    cases=tuple(case(kind) for kind in ["LICENCE","OFFICIAL_REGISTRATION","STAFF_AVAILABILITY","VOLUNTEER_ABSENCE","DELEGATION","SUBSTITUTION"])
    result=close_cssa_pass2_admin_campaign_v0(cases)
    assert result["cases"]==6
    assert result["counts"]=={"DRAFT_REVIEW_ONLY":4,"HOLD":2,"BLOCK":0}
    assert result["canonical_native_writes"]==0
    assert result["external_actions"]==0
    assert result["human_approvals"]==0
    assert result["operational_club_readiness"]=="NOT_VERIFIED"

def test_duplicate_case_is_rejected():
    with pytest.raises(ValueError,match="DUPLICATE"):
        close_cssa_pass2_admin_campaign_v0((case(),case()))