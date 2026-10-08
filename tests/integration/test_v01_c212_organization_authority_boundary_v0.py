"""C2.12: user-supplied evidence reference strings are not authority."""
from dataclasses import replace
from periphery.enterprise_organization_authority_boundary_v0 import (
    OrganizationAuthorityEvidenceV0, inspect_organization_authority_evidence_v0
)

def inspect(e):
    return inspect_organization_authority_evidence_v0(
        evidence=e, expected_org="org-a", expected_actor="actor-a",
        expected_issuer="issuer-a", expected_capability="calendar.write")

def test_missing_evidence_fails_closed():
    assert inspect(None)["reason"] == "C212_ORGANIZATION_EVIDENCE_MISSING"

def test_cross_tenant_and_scope_mismatch():
    e=OrganizationAuthorityEvidenceV0("org-b","actor-a","issuer-a","calendar.write")
    assert inspect(e)["reason"] == "C212_AUTHORITY_SUBJECT_SCOPE_MISMATCH"
    assert inspect(replace(e,organization_id="org-a",
                           requested_capability="mail.send"))["status"] == "BLOCK"

def test_partial_evidence_is_not_authority():
    e=OrganizationAuthorityEvidenceV0("org-a","actor-a","issuer-a","calendar.write",
                                       identity_provider_ref="provider-claimed")
    r=inspect(e)
    assert r["reason"] == "C212_INDEPENDENT_AUTHORITY_EVIDENCE_INCOMPLETE"
    assert r["egress_allowed"] is False

def test_even_complete_claimed_reference_strings_are_not_attested():
    e=OrganizationAuthorityEvidenceV0(
        "org-a","actor-a","issuer-a","calendar.write",
        identity_provider_ref="https://issuer.example.invalid",
        verified_identity_record_ref="identity-claim",
        verified_delegation_record_ref="delegation-claim",
        organization_control_record_ref="registry-claim")
    r=inspect(e)
    assert r["reason"] == "C212_INDEPENDENT_ORGANIZATION_VERIFIER_NOT_BOUND"
    assert r["organization_authority_verified"] is False
    assert r["execution_authority"] is False
