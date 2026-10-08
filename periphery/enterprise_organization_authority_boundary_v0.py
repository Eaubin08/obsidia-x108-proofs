"""C2.12 organizational authority evidence boundary.

No production identity provider is connected. This gate rejects claimed
identity, unverified consent and fixture-enrolled issuers. No ACT path.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class OrganizationAuthorityEvidenceV0:
    organization_id: str
    actor_id: str
    issuer_ref: str
    requested_capability: str
    identity_provider_ref: str | None = None
    verified_identity_record_ref: str | None = None
    verified_delegation_record_ref: str | None = None
    organization_control_record_ref: str | None = None

def inspect_organization_authority_evidence_v0(*, evidence, expected_org,
                                                expected_actor, expected_issuer,
                                                expected_capability):
    def deny(reason):
        return {"status": "BLOCK", "reason": reason,
                "organization_authority_verified": False,
                "egress_allowed": False, "execution_authority": False}
    if not isinstance(evidence, OrganizationAuthorityEvidenceV0):
        return deny("C212_ORGANIZATION_EVIDENCE_MISSING")
    if not all(isinstance(x,str) and x for x in (
        expected_org, expected_actor, expected_issuer, expected_capability)):
        return deny("C212_EXPECTED_AUTHORITY_CONTEXT_MISSING")
    if (evidence.organization_id != expected_org
        or evidence.actor_id != expected_actor
        or evidence.issuer_ref != expected_issuer
        or evidence.requested_capability != expected_capability):
        return deny("C212_AUTHORITY_SUBJECT_SCOPE_MISMATCH")
    if not all(isinstance(x,str) and x for x in (
        evidence.identity_provider_ref,
        evidence.verified_identity_record_ref,
        evidence.verified_delegation_record_ref,
        evidence.organization_control_record_ref)):
        return deny("C212_INDEPENDENT_AUTHORITY_EVIDENCE_INCOMPLETE")
    # These reference strings can be forged. No provider-authenticated identity,
    # organizational control, delegated scopes or revocation freshness verified.
    return deny("C212_INDEPENDENT_ORGANIZATION_VERIFIER_NOT_BOUND")
