import importlib, json, os, sys
from pathlib import Path
from datetime import date
from dataclasses import replace
import pytest
from periphery.cssa_lot_a_pass3_closure_v0 import close_cssa_lot_a_pass3_v0
from periphery.cssa_admin_licence_people_closure_pass2_v0 import CSSAAdminCaseV0, close_cssa_pass2_admin_campaign_v0
from periphery.cssa_role_work_register_pass2_v0 import assemble_cssa_role_work_register_v0
from periphery.cssa_administrative_batch_pass2_v0 import CssaAdministrativeBindingV0
from periphery.cssa_historical_semantic_adapter_v0 import project_historical_cssa_assessment_v0

ROOT = Path(os.environ["CSSA_HISTORICAL_REPO"]).resolve() if os.environ.get("CSSA_HISTORICAL_REPO") else None
pytestmark = pytest.mark.skipif(ROOT is None, reason="original CSSA checkout not set")

def fixture(path):
    if ROOT is None: pytest.skip("original CSSA checkout missing")
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def inputs():
    if ROOT is None: pytest.skip("original CSSA checkout missing")
    if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
    season=importlib.import_module("organizations.cssa.season_simulation.full_season_v0")
    stress=importlib.import_module("organizations.cssa.stress.organizational_stress_v0")
    resources=fixture("organizations/cssa/stress/resources_v0.json")
    corpus=season.build_full_season_corpus_v0(fixture("organizations/cssa/season/public_model_v0.json"))
    stress_rows=stress.assess_catalog_v0(fixture("organizations/cssa/stress/stress_scenarios_v0.json"),resources)
    pressure=stress.season_workload_pressure_v0(corpus.events,resources)
    specs=[
       ("organizations.cssa.compliance.contract_compliance_v0","assess_contract_catalog_v0","organizations/cssa/compliance/contract_compliance_cases_v0.json"),
       ("organizations.cssa.compliance.contract_compliance_v0","assess_compliance_catalog_v0","organizations/cssa/compliance/contract_compliance_cases_v0.json"),
       ("organizations.cssa.institutions.institutional_relations_v0","assess_institutional_catalog_v0","organizations/cssa/institutions/institutional_cases_v0.json"),
       ("organizations.cssa.root_cause.root_cause_recurrence_v0","assess_root_cause_catalog_v0","organizations/cssa/root_cause/root_cause_cases_v0.json"),
       ("organizations.cssa.matchday_food.buvette_restauration_v0","assess_buvette_catalog_v0","organizations/cssa/matchday_food/buvette_restauration_cases_v0.json"),
    ]
    rows=list(stress_rows)
    for mod,func,path in specs:
        src=fixture(path)
        rows.extend(getattr(importlib.import_module(mod),func)(src,as_of=date.fromisoformat(src["as_of"])))
    bindings={}
    for row in rows:
        p=project_historical_cssa_assessment_v0(row)
        bindings[p.source_family+":"+p.source_case_id]=CssaAdministrativeBindingV0("sim:historic:source",("sim:historic:proof",),"SIMULATED:OWNER","2026-10-07T12:00:00+00:00","2026-10-20T12:00:00+00:00")
    contract=fixture("organizations/cssa/coverage/announced_manager_role_coverage_v0.json")
    register=assemble_cssa_role_work_register_v0(rows,bindings,contract)
    admin=close_cssa_pass2_admin_campaign_v0(tuple(CSSAAdminCaseV0(
        case_id="sim:"+kind,kind=kind,source_ref="sim:source",evidence_refs=("sim:proof",),
        responsible_role="RESP_ADMIN",assigned_actor_ref="SIMULATED:OWNER",
        delegation_authority_ref=None,occurred_at="2026-10-07T12:00:00+00:00",
        due_at="2026-10-20T12:00:00+00:00"
    ) for kind in ("LICENCE","OFFICIAL_REGISTRATION","STAFF_AVAILABILITY","VOLUNTEER_ABSENCE","DELEGATION","SUBSTITUTION")))
    return dict(corpus=corpus,stress_assessments=stress_rows,season_pressure=pressure,role_contract=contract,admin_register=register,native_review_proof=admin)

def test_entire_original_season_and_eleven_roles_close_simulation():
    result=close_cssa_lot_a_pass3_v0(**inputs())
    assert result["verdict"]=="LOT_A_CLOSED_SIMULATION", result["failures"]
    assert result["season_event_count"]==904
    assert result["stress_gate_counts"]=={"ALLOW":2,"HOLD":5,"BLOCK":5}
    assert result["verified_public_role_count"]==11
    assert len(result["original_assessment_families"])==6
    assert result["native_review_cases"]==6
    assert result["native_writes"]==0 and result["real_authorizations"]==0
    assert result["field_readiness"]=="NOT_VERIFIED"

def test_one_missing_season_event_blocks():
    data=inputs()
    data["corpus"]=replace(data["corpus"],events=data["corpus"].events[:-1])
    assert close_cssa_lot_a_pass3_v0(**data)["verdict"]=="LOT_A_BLOCKED"

def test_native_side_effect_blocks():
    data=inputs()
    data["native_review_proof"]=dict(data["native_review_proof"],canonical_native_writes=1)
    assert close_cssa_lot_a_pass3_v0(**data)["verdict"]=="LOT_A_BLOCKED"

def test_forged_field_authority_blocks():
    data=inputs()
    data["admin_register"]=dict(data["admin_register"],field_authority_verified=True)
    assert close_cssa_lot_a_pass3_v0(**data)["verdict"]=="LOT_A_BLOCKED"
