"""C0 contract convergence and C1 non-sovereign Company Model tests."""
from __future__ import annotations

import copy
import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from periphery.company_model_v0 import (
    SCHEMA, company_node_v0, company_relation_v0,
    company_model_snapshot_v0, verify_company_model_snapshot_v0,
)

ROOT = Path(__file__).resolve().parents[2]
C0 = ROOT / "docs" / "runtime" / "V01_ENTERPRISE_C0_CONTRACT_CONVERGENCE_V0.json"
T0 = "2026-10-08T10:00:00+02:00"


def node(org, id, kind, state="DECLARED", evidence=()):
    return company_node_v0(
        organization_id=org, record_id=id, kind=kind,
        claim_state=state, valid_at=T0,
        provenance_refs=("fixture:org-team-interview",), evidence_refs=evidence,
    )


def link(org, ident, source, target, kind="USES_TOOL"):
    return company_relation_v0(
        organization_id=org, relation_id=ident,
        from_record_id=source, to_record_id=target, relation_kind=kind,
        claim_state="DECLARED", valid_at=T0,
        provenance_refs=("fixture:declared-process-map",),
    )


def graph(org):
    return company_model_snapshot_v0(
        org,
        (node(org, org, "ORGANIZATION"), node(org, "erp", "TOOL_INSTANCE"),
         node(org, "finance", "PROCESS"), node(org, "trading", "DOMAIN_BINDING")),
        (link(org, "org-uses-erp", org, "erp"),
         link(org, "org-finance", org, "finance", "OPERATES_PROCESS"),
         link(org, "org-trading", org, "trading", "BINDS_DOMAIN")),
    )


def test_c0_registry_reuses_existing_contracts_without_new_kernel():
    registry = json.loads(C0.read_text(encoding="utf8"))
    assert registry["schema"] == "V01_ENTERPRISE_C0_CONTRACT_CONVERGENCE_V0"
    assert registry["authority"] == "KX108_ONLY"
    assert registry["kernel_changes"] is False
    assert registry["global_ci_green"] is False
    assert len(registry["contracts"]) == 12
    ids = {x["id"] for x in registry["contracts"]}
    assert len(ids) == 12
    assert {"UDIP_DOMAIN_SPEC", "UNIVERSAL_ENTERPRISE_ADAPTER",
            "COGNITIVE_PROVIDER_BINDER", "KX_POST_ACTIVATION_POLICY",
            "COMPANY_MODEL_C1"} <= ids
    for item in registry["contracts"]:
        assert item["inputs"] and item["outputs"] and item["invariant"]
        assert item["action"] in {"REUSE", "ADAPT", "NEW"}
        if item["reference"]["branch"] != "codex/udip-domain-packs-v0" and item["reference"]["branch"] != "feat/premiere-mise-au-monde-udip-v0":
            assert (ROOT / item["reference"]["path"]).exists()


def test_two_unrelated_companies_use_same_domain_and_erp_without_data_overlap():
    a, b = graph("company-a"), graph("company-b")
    assert a["schema"] == b["schema"] == SCHEMA
    assert a["organization_id"] != b["organization_id"]
    assert a["snapshot_hash"] != b["snapshot_hash"]
    assert set(x["record_id"] for x in a["nodes"]) == (
        {"company-a", "erp", "finance", "trading"}
    )
    assert "erp" in {x["record_id"] for x in b["nodes"]}
    assert a["canonical_truth"] is False
    assert a["organization_authority_verified"] is False
    assert a["allowed_to_decide"] is False
    assert a["allowed_to_act"] is False
    assert a["decision_authority"] == "KX108_ONLY"
    assert verify_company_model_snapshot_v0(a) == (True, None)
    assert verify_company_model_snapshot_v0(b) == (True, None)


def test_company_model_json_roundtrip_and_order_independence():
    a = graph("company-a")
    assert verify_company_model_snapshot_v0(json.loads(json.dumps(a))) == (True, None)
    nodes = [node("company-a", "erp", "TOOL_INSTANCE"),
             node("company-a", "company-a", "ORGANIZATION")]
    assert company_model_snapshot_v0("company-a", nodes, []) == (
        company_model_snapshot_v0("company-a", reversed(nodes), [])
    )


def test_cross_tenant_nodes_fail_closed():
    with pytest.raises(ValueError, match="CROSS_TENANT_NODE"):
        company_model_snapshot_v0("company-a", [
            node("company-a", "company-a", "ORGANIZATION"),
            node("company-b", "erp", "TOOL_INSTANCE"),
        ], [])
    with pytest.raises(ValueError, match="CROSS_TENANT_RELATION"):
        company_model_snapshot_v0("company-a", [
            node("company-a", "company-a", "ORGANIZATION"),
            node("company-a", "erp", "TOOL_INSTANCE"),
        ], [link("company-b", "x", "company-a", "erp")])


def test_dangling_relation_rejected_and_other_tenant_not_implicitly_resolved():
    with pytest.raises(ValueError, match="DANGLING_RELATION"):
        company_model_snapshot_v0("company-a", [
            node("company-a", "company-a", "ORGANIZATION")
        ], [link("company-a", "edge", "company-a", "external-erp")])


def test_source_evidence_does_not_promote_organizational_truth():
    record = node("company-a", "mail", "SOURCE", "PROVEN_CLAIM",
                  evidence=("registration:012345",))
    assert record.verification == "UNVERIFIED_ORGANIZATIONAL_CLAIM"
    model = company_model_snapshot_v0("company-a", [
        node("company-a", "company-a", "ORGANIZATION"), record
    ], [])
    assert model["organization_authority_verified"] is False
    assert model["canonical_truth"] is False
    assert model["nodes"][1]["verification"] == "UNVERIFIED_ORGANIZATIONAL_CLAIM"
    with pytest.raises(ValueError, match="EVIDENCE_REQUIRED"):
        node("company-a", "mail", "SOURCE", "OBSERVED_CLAIM")


def test_mutating_consent_or_inventing_authority_is_rejected():
    graph0 = graph("company-a")
    manipulated = copy.deepcopy(graph0)
    manipulated["allowed_to_act"] = True
    assert verify_company_model_snapshot_v0(manipulated)[0] is False
    altered = copy.deepcopy(graph0)
    altered["nodes"][0]["verification"] = "PROVEN"
    assert verify_company_model_snapshot_v0(altered)[0] is False
    elevated = copy.deepcopy(graph0)
    elevated["organization_authority_verified"] = True
    assert verify_company_model_snapshot_v0(elevated)[0] is False


def test_model_ids_integrity_duplicate_and_node_hash_enforced():
    root = node("company-a", "company-a", "ORGANIZATION")
    erp = node("company-a", "erp", "TOOL_INSTANCE")
    with pytest.raises(ValueError, match="DUPLICATE_NODE"):
        company_model_snapshot_v0("company-a", [root, erp, erp], [])
    with pytest.raises(ValueError, match="OBJECT_HASH_INVALID"):
        company_model_snapshot_v0("company-a", [root, replace(erp, node_hash="0"*64)], [])
    with pytest.raises(FrozenInstanceError):
        root.allowed_to_act = True


def test_versioned_org_root_is_mandatory_and_no_opaque_metadata_or_credentials():
    with pytest.raises(ValueError, match="ORGANIZATION_ROOT_REQUIRED"):
        company_model_snapshot_v0("company-a", [node("company-a", "erp", "TOOL_INSTANCE")], [])
    with pytest.raises(ValueError, match="ID_INVALID"):
        node("company-a", "secret/text", "SOURCE")
    with pytest.raises(ValueError, match="REF_INVALID"):
        company_node_v0(organization_id="company-a", record_id="erp",
            kind="TOOL_INSTANCE", claim_state="DECLARED", valid_at=T0,
            provenance_refs=("api_key=super-secret",))
    assert "connector_args" not in graph("company-a")
    assert "approved_by" not in graph("company-a")


def test_organisational_claim_is_never_an_execution_ticket():
    result = graph("company-a")
    assert result["truth_scope"] == "PROVENANCE_BOUND_CLAIMS_NOT_VERIFIED_ORG_TRUTH"
    assert result["readonly"] is True
    assert result["is_execution_authority"] is False
    assert all(x["allowed_to_decide"] is False and x["allowed_to_act"] is False
               for x in result["nodes"] + result["relations"])
