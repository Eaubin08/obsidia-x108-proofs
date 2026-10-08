"""C2.13 external identity verifier contract, deny-only until bound.

Never accept a caller boolean or string reference as organizational authority.
A future independent verifier must supply verifiable evidence under a trusted
administrative configuration, not an object built by an action requester.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class IdentityVerificationRequestV0:
    organization_id: str
    actor_id: str
    issuer_ref: str
    capability_id: str
    action_request_hash: str

class IndependentOrganizationVerifierV0(Protocol):
    def verify_independently(self, request: IdentityVerificationRequestV0) -> object:
        """A trusted implementation is not supplied in C2.13."""

def inspect_unbound_identity_verifier_v0(*, request, verifier=None):
    def denied(reason):
        return {"status": "BLOCK", "reason": reason, "egress_allowed": False,
                "organization_authority_verified": False,
                "execution_authority": False}
    if not isinstance(request, IdentityVerificationRequestV0):
        return denied("C213_IDENTITY_REQUEST_INVALID")
    if any(not isinstance(value, str) or not value for value in (
        request.organization_id, request.actor_id, request.issuer_ref,
        request.capability_id, request.action_request_hash)):
        return denied("C213_IDENTITY_BINDING_INCOMPLETE")
    if verifier is None:
        return denied("C213_INDEPENDENT_IDENTITY_VERIFIER_UNBOUND")
    # Do not call a caller-provided implementation: its returned 'verified'
    # flag could forge trust. A production trust root must be pinned by a
    # privileged enrollment flow, which does not exist in this prototype.
    return denied("C213_VERIFIER_TRUST_ROOT_UNATTESTED")
