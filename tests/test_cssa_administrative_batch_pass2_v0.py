"""Pass 2: full administrative batch with original F3G engine outputs."""
import importlib
import json
import os
import sys
from pathlib import Path
from datetime import date
import pytest
from periphery.cssa_administrative_batch_pass2_v0 import (CssaAdministrativeBindingV0, assemble_cssa_administrative_batch_v0)
from periphery.native_ops.intake_bundle_v0 import verify_native_case_task_intake_plan_v0

ROOT = Path(os.environ["CSSA_HISTORICAL_REPO"]).resolve() if os.environ.get("CSSA_HISTORICAL_REPO") else None
pytestmark = pytest.mark.skipif(ROOT is None, reason="historical CSSA checkout not configured")

def historical_catalogs():
    if ROOT is None:
        pytest.skip("original CSSA checkout missing")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    specs = [
        ("organizations.cssa.compliance.contract_compliance_v0", "assess_contract_catalog_v0", "organizations/cssa/compliance/contract_compliance_cases_v0.json"),
        ("organizations.cssa.compliance.contract_compliance_v0", "assess_compliance_catalog_v0", "organizations/cssa/compliance/contract_compliance_cases_v0.json"),
        ("organizations.cssa.institutions.institutional_relations_v0", "assess_institutional_catalog_v0", "organizations/cssa/institutions/institutional_cases_v0.json"),
        ("organizations.cssa.root_cause.root_cause_recurrence_v0", "assess_root_cause_catalog_v0", "organizations/cssa/root_cause/root_cause_cases_v0.json"),
    ]
    rows = []
    for module, fn, path in specs:
        fixture = json.loads((ROOT / path).read_text(encoding="utf-8"))
        assert fixture["status"] == "SIMULATED_NOT_OBSERVED"
        rows.extend(getattr(importlib.import_module(module), fn)(fixture, as_of=date.fromisoformat(fixture["as_of"])))
    return rows

def binding():
    return CssaAdministrativeBindingV0("sim:cssa:source", ("sim:cssa:evidence",), "SIMULATED:MANAGER", "2026-10-07T00:00:00+00:00", "2026-10-20T00:00:00+00:00")

def test_integrated_real_historical_admin_catalogs_review_only():
    assessments = historical_catalogs()
    from periphery.cssa_historical_semantic_adapter_v0 import project_historical_cssa_assessment_v0
    all_bindings = {}
    for x in assessments:
        p = project_historical_cssa_assessment_v0(x)
        all_bindings[p.source_family + ":" + p.source_case_id] = binding()
    result = assemble_cssa_administrative_batch_v0(assessments, all_bindings)
    assert len(result["entries"]) == len(assessments)
    assert len(result["entries"]) >= 25
    assert result["status"] == "REVIEW_ONLY"
    assert result["native_writes"] == 0
    assert result["external_effect"] is False
    assert result["approval_granted"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    for e in result["entries"]:
        if e["plan"] is not None:
            assert e["status"] == "NATIVE_INTAKE_DRAFT_FOR_REVIEW"
            assert verify_native_case_task_intake_plan_v0(e["plan"]) == (True, None)
            assert e["plan"].allowed_to_act is False
        else:
            assert e["status"] in ("HOLD", "BLOCK")
    assert any(e["status"] == "BLOCK" for e in result["entries"])
    assert any(e["plan"] is not None for e in result["entries"])

def test_omitted_bindings_hold_or_block_without_intake():
    result = assemble_cssa_administrative_batch_v0(historical_catalogs(), {})
    assert all(e["plan"] is None for e in result["entries"])
    assert all(e["status"] in ("HOLD", "BLOCK") for e in result["entries"])
    assert result["native_writes"] == 0

def test_missing_source_for_all_cases_holds_or_blocks():
    rows = historical_catalogs()
    from periphery.cssa_historical_semantic_adapter_v0 import project_historical_cssa_assessment_v0
    bindings = {}
    for x in rows:
        p = project_historical_cssa_assessment_v0(x)
        bindings[p.source_family + ":" + p.source_case_id] = CssaAdministrativeBindingV0(None, ("sim:evidence",), "SIMULATED:MANAGER", "2026-10-07T00:00:00+00:00", "2026-10-20T00:00:00+00:00")
    result = assemble_cssa_administrative_batch_v0(rows, bindings)
    assert all(e["plan"] is None for e in result["entries"])
    assert all(e["status"] in ("HOLD", "BLOCK") for e in result["entries"])