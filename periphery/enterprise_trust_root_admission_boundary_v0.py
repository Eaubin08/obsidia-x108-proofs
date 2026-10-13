"""C2.14 read-only trust-root admission manifest, ALWAYS FAIL CLOSED.

An operator-authored configuration is not equivalent to independent enrollment.
No actual OIDC/JWKS lookup, trusted identity verifier, authorization or egress.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class OrganizationTrustRootCandidateV0:
    organization_id: str
    identity_provider_issuer: str
    audience: str
    key_fingerprint_sha256: str
    enrollment_evidence_ref: str
    enrolled_by: str

def inspect_trust_root_admission_v0(*, candidate, expected_organization_id):
    def deny(reason):
        return {"status":"BLOCK", "reason":reason,
                "trusted_issuer_admitted":False,
                "organization_authority_verified":False,
                "egress_allowed":False, "execution_authority":False}
    if not isinstance(candidate,OrganizationTrustRootCandidateV0):
        return deny("C214_TRUST_ROOT_CANDIDATE_MISSING")
    if not isinstance(expected_organization_id,str) or not expected_organization_id:
        return deny("C214_EXPECTED_ORGANIZATION_MISSING")
    if candidate.organization_id!=expected_organization_id:
        return deny("C214_CROSS_TENANT_TRUST_ROOT")
    if any(not isinstance(x,str) or not x for x in (
        candidate.identity_provider_issuer,candidate.audience,
        candidate.key_fingerprint_sha256,candidate.enrollment_evidence_ref,
        candidate.enrolled_by)):
        return deny("C214_TRUST_ROOT_MANIFEST_INCOMPLETE")
    if len(candidate.key_fingerprint_sha256)!=64 or any(
        c not in "0123456789abcdef" for c in candidate.key_fingerprint_sha256
    ):
        return deny("C214_FINGERPRINT_INVALID")
    return deny("C214_INDEPENDENT_TRUST_ROOT_ENROLLMENT_UNAVAILABLE")
