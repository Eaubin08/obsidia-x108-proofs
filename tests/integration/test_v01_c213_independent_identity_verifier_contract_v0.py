"""C2.13: caller-provided verifiers are not trusted enrollment."""
from periphery.enterprise_independent_identity_verifier_contract_v0 import (
    IdentityVerificationRequestV0, inspect_unbound_identity_verifier_v0
)

def request():
    return IdentityVerificationRequestV0(
        organization_id="org-a",actor_id="actor-a",issuer_ref="issuer-a",
        capability_id="mail.send",action_request_hash="a"*64)

def test_missing_verifier_blocks():
    result=inspect_unbound_identity_verifier_v0(request=request())
    assert result["reason"]=="C213_INDEPENDENT_IDENTITY_VERIFIER_UNBOUND"
    assert result["egress_allowed"] is False

def test_caller_forged_positive_verifier_cannot_grant():
    class UntrustedVerifier:
        def verify_independently(self, req):
            raise AssertionError("Untrusted verifier must not be called")
    result=inspect_unbound_identity_verifier_v0(
        request=request(),verifier=UntrustedVerifier())
    assert result["reason"]=="C213_VERIFIER_TRUST_ROOT_UNATTESTED"
    assert result["organization_authority_verified"] is False

def test_missing_org_and_invalid_request_block():
    assert inspect_unbound_identity_verifier_v0(
        request=None)["status"]=="BLOCK"
    missing=IdentityVerificationRequestV0("","actor-a","issuer-a","mail.send","a"*64)
    assert inspect_unbound_identity_verifier_v0(
        request=missing)["reason"]=="C213_IDENTITY_BINDING_INCOMPLETE"
