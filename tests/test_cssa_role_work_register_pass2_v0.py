"""Cross-repo pass 2 full responsibility register acceptance against source fixtures."""
import importlib
import json
import os
import sys
from datetime import date
from pathlib import Path
import pytest
from periphery.cssa_role_work_register_pass2_v0 import assemble_cssa_role_work_register_v0
from periphery.cssa_administrative_batch_pass2_v0 import CssaAdministrativeBindingV0
from periphery.cssa_historical_semantic_adapter_v0 import project_historical_cssa_assessment_v0

ROOT = Path(os.environ["CSSA_HISTORICAL_REPO"]).resolve() if os.environ.get("CSSA_HISTORICAL_REPO") else None
pytestmark = pytest.mark.skipif(ROOT is None, reason="CSSA_HISTORICAL_REPO not set")

def data(path):
    if ROOT is None: pytest.skip("Missing historic checkout")
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def source():
    if ROOT is None: pytest.skip("Missing historic checkout")
    if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
    specs = [
      ("organizations.cssa.stress.organizational_stress_v0","assess_catalog_v0","organizations/cssa/stress/stress_scenarios_v0.json"),
      ("organizations.cssa.compliance.contract_compliance_v0","assess_contract_catalog_v0","organizations/cssa/compliance/contract_compliance_cases_v0.json"),
      ("organizations.cssa.compliance.contract_compliance_v0","assess_compliance_catalog_v0","organizations/cssa/compliance/contract_compliance_cases_v0.json"),
      ("organizations.cssa.institutions.institutional_relations_v0","assess_institutional_catalog_v0","organizations/cssa/institutions/institutional_cases_v0.json"),
      ("organizations.cssa.root_cause.root_cause_recurrence_v0","assess_root_cause_catalog_v0","organizations/cssa/root_cause/root_cause_cases_v0.json"),
      ("organizations.cssa.matchday_food.buvette_restauration_v0","assess_buvette_catalog_v0","organizations/cssa/matchday_food/buvette_restauration_cases_v0.json"),
    ]
    rows=[]
    for module,method,fixture in specs:
        catalog=data(fixture)
        assert catalog["status"] == "SIMULATED_NOT_OBSERVED"
        m=importlib.import_module(module)
        if method == "assess_catalog_v0":
            result=getattr(m,method)(catalog,data("organizations/cssa/stress/resources_v0.json"))
        else:
            result=getattr(m,method)(catalog,as_of=date.fromisoformat(catalog["as_of"]))
        rows.extend(result)
    return rows

def test_full_role_register_all_historic_engines_and_hard_boundaries():
    rows=source()
    bindings={}
    for assessment in rows:
        proposal=project_historical_cssa_assessment_v0(assessment)
        bindings[proposal.source_family+":"+proposal.source_case_id]=CssaAdministrativeBindingV0(
            "sim:historical:source",("sim:historical:evidence",),
            "SIMULATED:OWNER","2026-10-07T00:00:00+00:00","2026-10-20T00:00:00+00:00")
    result=assemble_cssa_role_work_register_v0(rows,bindings,data("organizations/cssa/coverage/announced_manager_role_coverage_v0.json"))
    assert result["role_count"] == 11
    assert result["family_count"] == 6
    assert len(result["work_batch"]["entries"]) == len(rows)
    assert result["canonical_native_writes"] == 0
    assert result["real_approvals"] == 0
    assert result["field_authority_verified"] is False
    assert all(x["operational_readiness"] == "NOT_VERIFIED" for x in result["role_matrix"])
    assert all(x["real_authority_proven"] is False for x in result["role_matrix"])
    assert result["work_batch"]["native_writes"] == 0

def test_full_role_register_withholds_every_plan_when_bindings_missing():
    result=assemble_cssa_role_work_register_v0(source(),{},data("organizations/cssa/coverage/announced_manager_role_coverage_v0.json"))
    assert all(x["plan"] is None for x in result["work_batch"]["entries"])
    assert all(x["status"] in {"HOLD","BLOCK"} for x in result["work_batch"]["entries"])

def test_role_contract_rejects_false_real_authority():
    roles=data("organizations/cssa/coverage/announced_manager_role_coverage_v0.json")
    roles["global_boundaries"]["real_field_evidence"]=True
    with pytest.raises(ValueError,match="AUTHORITY_MISMATCH"):
        assemble_cssa_role_work_register_v0([],{},roles)