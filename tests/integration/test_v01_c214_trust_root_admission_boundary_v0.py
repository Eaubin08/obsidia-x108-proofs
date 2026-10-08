from periphery.enterprise_trust_root_admission_boundary_v0 import OrganizationTrustRootCandidateV0, inspect_trust_root_admission_v0

def test_unbound_root():
    c=OrganizationTrustRootCandidateV0("org-a","issuer-a","audience-a","a"*64,"evidence-a","admin-a")
    r=inspect_trust_root_admission_v0(candidate=c,expected_organization_id="org-a")
    assert r["status"]=="BLOCK"
    assert r["trusted_issuer_admitted"] is False
    assert r["egress_allowed"] is False

def test_cross_tenant():
    c=OrganizationTrustRootCandidateV0("org-a","issuer-a","audience-a","a"*64,"evidence-a","admin-a")
    assert inspect_trust_root_admission_v0(candidate=c,expected_organization_id="org-b")["status"]=="BLOCK"
