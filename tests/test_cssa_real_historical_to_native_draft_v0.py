"""Real F3G engines → semantic proposal → native review-only intake plan.

Opt-in: CSSA_HISTORICAL_REPO must point at original CSSA checkout.
Do not create canonical native state or attribute operational authority.
"""
import importlib
import json
import os
from datetime import date
from pathlib import Path
import sys

import pytest

from periphery.cssa_historical_semantic_adapter_v0 import project_historical_cssa_assessment_v0
from periphery.cssa_historical_native_intake_draft_v0 import draft_cssa_historical_native_intake_v0
from periphery.native_ops.intake_bundle_v0 import verify_native_case_task_intake_plan_v0

SOURCE = os.environ.get("CSSA_HISTORICAL_REPO", "").strip()
ROOT = Path(SOURCE).resolve() if SOURCE else None
pytestmark = pytest.mark.skipif(ROOT is None, reason="original CSSA repo not configured")


def _load_engine(module, fixture):
    if ROOT is None:
        pytest.skip("original CSSA repo not configured")
    if not (ROOT / "organizations" / "cssa").is_dir():
        raise ValueError("ORIGINAL_CSSA_REPO_NOT_FOUND")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    engine = importlib.import_module(module)
    data = json.loads((ROOT / fixture).read_text(encoding="utf-8"))
    assert data["status"] == "SIMULATED_NOT_OBSERVED"
    return engine, data


def _draft(assessment, *, evidence=True, source=True, owner=True, due=True):
    semantic = project_historical_cssa_assessment_v0(assessment)
    return draft_cssa_historical_native_intake_v0(
        semantic,
        observed_source_ref="sim:original:historical" if source else "",
        observed_evidence_refs=("sim:original:evidence",) if evidence else (),
        occurred_at="2026-10-07T00:00:00+00:00",
        due_at="2026-10-20T00:00:00+00:00" if due else None,
        proposed_owner_ref="SIMULATED:CSSA:MANAGER" if owner else None,
    )


def test_genuine_contract_case_reaches_readonly_canonical_native_plan():
    m, catalog = _load_engine(
        "organizations.cssa.compliance.contract_compliance_v0",
        "organizations/cssa/compliance/contract_compliance_cases_v0.json")
    assessment = next(r for r in m.assess_contract_catalog_v0(
        catalog, as_of=date.fromisoformat(catalog["as_of"]))
        if r.case_id == "CONTRACT_VALID_ACTIVE")
    assert assessment.expected_gate == "ALLOW"
    result = _draft(assessment)
    assert result["status"] == "NATIVE_INTAKE_DRAFT_FOR_REVIEW"
    plan = result["native_plan"]
    assert plan.case_type == "CONTRACT_REVIEW"
    assert verify_native_case_task_intake_plan_v0(plan) == (True, None)
    assert plan.allowed_to_act is False
    assert result["canonical_intake_committed"] is False
    assert result["approval_granted"] is False


def test_real_institution_acknowledgement_does_not_authorize_native_intake():
    m, catalog = _load_engine(
        "organizations.cssa.institutions.institutional_relations_v0",
        "organizations/cssa/institutions/institutional_cases_v0.json")
    assessment = next(r for r in m.assess_institutional_catalog_v0(
        catalog, as_of=date.fromisoformat(catalog["as_of"]))
        if r.case_id == "INST_ACK_NOT_APPROVAL")
    assert assessment.expected_gate == "HOLD"
    result = _draft(assessment)
    assert result["canonical_intake_committed"] is False
    assert result["approval_granted"] is False
    assert result["action_candidate"] is None


def test_real_contract_incomplete_provenance_fails_closed():
    m, catalog = _load_engine(
        "organizations.cssa.compliance.contract_compliance_v0",
        "organizations/cssa/compliance/contract_compliance_cases_v0.json")
    assessment = m.assess_contract_catalog_v0(catalog,
        as_of=date.fromisoformat(catalog["as_of"]))[0]
    result = _draft(assessment, evidence=False)
    assert result["status"] == "HOLD"
    assert result["native_plan"] is None


def test_real_contract_missing_owner_fails_closed():
    m, catalog = _load_engine(
        "organizations.cssa.compliance.contract_compliance_v0",
        "organizations/cssa/compliance/contract_compliance_cases_v0.json")
    assessment = m.assess_contract_catalog_v0(catalog,
        as_of=date.fromisoformat(catalog["as_of"]))[0]
    result = _draft(assessment, owner=False)
    assert result["status"] == "HOLD"
    assert result["native_plan"] is None


def test_real_contract_conflicts_cannot_reach_native_plan():
    m, catalog = _load_engine(
        "organizations.cssa.compliance.contract_compliance_v0",
        "organizations/cssa/compliance/contract_compliance_cases_v0.json")
    rows = m.assess_contract_catalog_v0(catalog,
        as_of=date.fromisoformat(catalog["as_of"]))
    assessment = next(r for r in rows if r.contradictions)
    result = _draft(assessment)
    assert result["status"] == "BLOCK"
    assert result["native_plan"] is None
