"""C2 convergence: same Company Model contract across three fictional tenants.

This is a read-only claim fixture, not a business identity attestation.
"""
import pytest
from periphery.company_model_v0 import (
    company_node_v0, company_model_snapshot_v0,
    verify_company_model_snapshot_v0,
)

AT="2026-10-08T12:00:00+00:00"
ORGS=("cssa-fixture","pme-fixture","association-fixture")

def make_nodes(org):
    return [
        company_node_v0(organization_id=org,record_id=org,kind="ORGANIZATION",
            claim_state="DECLARED",valid_at=AT,provenance_refs=("fixture:synthetic",)),
        company_node_v0(organization_id=org,record_id="admin",kind="TEAM_ROLE",
            claim_state="DECLARED",valid_at=AT,provenance_refs=("fixture:synthetic",)),
    ]

def test_three_distinct_organizations_share_contract_without_authority():
    snapshots=[company_model_snapshot_v0(org,make_nodes(org),[]) for org in ORGS]
    assert len({x["snapshot_hash"] for x in snapshots})==3
    for snapshot in snapshots:
        assert verify_company_model_snapshot_v0(snapshot)==(True,None)
        assert snapshot["allowed_to_decide"] is False
        assert snapshot["allowed_to_act"] is False
        assert snapshot["organization_authority_verified"] is False

def test_cross_tenant_claim_never_enters_another_snapshot():
    with pytest.raises(ValueError,match="CROSS_TENANT"):
        company_model_snapshot_v0(ORGS[0],make_nodes(ORGS[0])+make_nodes(ORGS[1]),[])

def test_claim_snapshot_does_not_automatically_become_verified_truth():
    snapshot=company_model_snapshot_v0(ORGS[0],make_nodes(ORGS[0]),[])
    snapshot["organization_authority_verified"]=True
    assert verify_company_model_snapshot_v0(snapshot)[0] is False
