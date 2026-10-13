"""Opt-in CROSS-REPOSITORY tests using real original F3F/F3G engines and fixtures.

Set CSSA_HISTORICAL_REPO to an isolated checkout of
Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-
branch feat/f3g-j-cssa-matchday-buvette-restauration-v0.
No test doubles. No native writes, approvals, or external actions.
"""
import importlib
import json
import os
from pathlib import Path
import sys
from datetime import date

import pytest
from periphery.cssa_historical_semantic_adapter_v0 import (
    project_historical_cssa_assessment_v0,
    verify_historical_cssa_semantic_projection_v0,
)

SOURCE = os.environ.get("CSSA_HISTORICAL_REPO", "").strip()
ROOT = Path(SOURCE).resolve() if SOURCE else None
if ROOT is not None and not (ROOT / "organizations" / "cssa").is_dir():
    raise RuntimeError("CSSA_HISTORICAL_REPO_MISSING_CSSA_PACKAGE")
pytestmark = pytest.mark.skipif(ROOT is None, reason="CSSA_HISTORICAL_REPO not configured")


def _source():
    if ROOT is None:
        pytest.skip("Original CSSA checkout not configured")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return ROOT


def _fixture(relpath):
    return json.loads((_source() / relpath).read_text(encoding="utf-8"))


def _module(name):
    _source()
    return importlib.import_module(name)


def _assert_safe(rows, family):
    assert rows
    for row in rows:
        projection = project_historical_cssa_assessment_v0(row)
        assert verify_historical_cssa_semantic_projection_v0(projection)
        assert projection.source_family == family
        assert projection.source_case_id == row.event_id
        assert projection.source_expected_gate == row.expected_gate
        assert projection.canonical_intake_allowed is False
        assert projection.action_candidate is None
        assert projection.approved_by is None
        assert projection.disposition in ("BLOCK", "HOLD")
        if getattr(row, "contradictions", ()):
            assert projection.disposition == "BLOCK"


def test_original_f3f_stress_engine_and_12_scenarios():
    m = _module("organizations.cssa.stress.organizational_stress_v0")
    rows = m.assess_catalog_v0(
        _fixture("organizations/cssa/stress/stress_scenarios_v0.json"),
        _fixture("organizations/cssa/stress/resources_v0.json"),
    )
    assert len(rows) == 12
    assert m.catalog_summary_v0(rows)["gate_counts"] == {
        "ALLOW": 2, "HOLD": 5, "BLOCK": 5,
    }
    _assert_safe(rows, "F3F_STRESS")


@pytest.mark.parametrize("kind,method,path,group,family", [
    ("contract", "assess_contract_catalog_v0",
     "organizations/cssa/compliance/contract_compliance_cases_v0.json",
     "contracts", "F3G_CONTRACT"),
    ("compliance", "assess_compliance_catalog_v0",
     "organizations/cssa/compliance/contract_compliance_cases_v0.json",
     "compliance_cases", "F3G_COMPLIANCE"),
    ("institution", "assess_institutional_catalog_v0",
     "organizations/cssa/institutions/institutional_cases_v0.json",
     "cases", "F3G_INSTITUTION"),
    ("root_cause", "assess_root_cause_catalog_v0",
     "organizations/cssa/root_cause/root_cause_cases_v0.json",
     "cases", "F3G_ROOT_CAUSE"),
    ("buvette", "assess_buvette_catalog_v0",
     "organizations/cssa/matchday_food/buvette_restauration_cases_v0.json",
     "cases", "F3G_BUVETTE"),
])
def test_original_f3g_engine_catalogs_flow_into_safe_adapter(
    kind, method, path, group, family,
):
    packages = {
        "contract": "organizations.cssa.compliance.contract_compliance_v0",
        "compliance": "organizations.cssa.compliance.contract_compliance_v0",
        "institution": "organizations.cssa.institutions.institutional_relations_v0",
        "root_cause": "organizations.cssa.root_cause.root_cause_recurrence_v0",
        "buvette": "organizations.cssa.matchday_food.buvette_restauration_v0",
    }
    m = _module(packages[kind])
    catalog = _fixture(path)
    assert catalog["status"] == "SIMULATED_NOT_OBSERVED"
    rows = getattr(m, method)(catalog, as_of=date.fromisoformat(catalog["as_of"]))
    assert len(rows) == len(catalog[group])
    _assert_safe(rows, family)


def test_historical_11_role_identifiers_are_exactly_preserved():
    roles = _fixture("organizations/cssa/coverage/announced_manager_role_coverage_v0.json")
    ids = {row["id"] for row in roles["requirements"]}
    assert len(ids) == 11
    assert ids == {
        "ADMINISTRATION_DAILY", "INSTITUTIONAL_RELATIONS",
        "PEOPLE_MANAGEMENT_DELEGATION", "CROSS_POLE_COORDINATION",
        "MATCHDAY_TICKETING", "MATCHDAY_SECURITY",
        "MATCHDAY_WELCOME_HOSPITALITY",
        "MATCHDAY_BUVETTE_RESTAURATION",
        "WRITTEN_PROCESS_RESPONSIBILITY",
        "ROOT_CAUSE_DURABILITY", "DECISION_EXECUTION",
    }
    assert roles["global_boundaries"]["real_field_evidence"] is False
    assert roles["global_boundaries"]["external_action"] is False
