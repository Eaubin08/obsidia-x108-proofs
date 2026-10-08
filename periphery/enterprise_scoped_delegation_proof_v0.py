"""C2.2 scoped delegation signature verifier; simulation only, no execution grant.

A verifier with an externally supplied trusted key validates proof integrity,
scope, audience, expiry and exact connector binding. This does not attest the
issuer's legal organizational authority or replace SovereignTicket/KX108 checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re

_HEX = re.compile(r"^[0-9a-f]{64}$")
SCHEMA = "OBSIDIA_C22_SCOPED_DELEGATION_PROOF_V0"


@dataclass(frozen=True)
class ScopedDelegationProofV0:
    schema: str
    issuer_id: str
    organization_id: str
    principal_id: str
    delegate_id: str
    connector_id: str
    capability_id: str
    action_request_hash: str
    expires_at: str
    nonce: str
    signature: str


def _payload(proof):
    return {k: v for k, v in vars(proof).items() if k != "signature"}


def sign_fixture_only(proof, *, secret):
    """Test fixture signer, NOT proof of an organization's authority."""
    from dataclasses import replace
    return replace(proof, signature=hmac.new(
        secret, json.dumps(_payload(proof), sort_keys=True, separators=(",", ":")).encode(),
        hashlib.sha256
    ).hexdigest())


def verify_scoped_delegation_v0(proof, *, trusted_issuer_id, verifier_secret,
                                organization_id, principal_id, delegate_id,
                                connector_id, capability_id, action_request_hash,
                                now):
    if not isinstance(proof, ScopedDelegationProofV0):
        return False, "C22_PROOF_TYPE_INVALID"
    if proof.schema != SCHEMA or not isinstance(proof.signature, str):
        return False, "C22_SCHEMA_INVALID"
    expected = (trusted_issuer_id, organization_id, principal_id, delegate_id,
                connector_id, capability_id, action_request_hash)
    actual = (proof.issuer_id, proof.organization_id, proof.principal_id,
              proof.delegate_id, proof.connector_id, proof.capability_id,
              proof.action_request_hash)
    if not all(isinstance(x, str) and x for x in expected + actual):
        return False, "C22_SCOPE_INCOMPLETE"
    if actual != expected or not _HEX.fullmatch(proof.action_request_hash):
        return False, "C22_SCOPE_MISMATCH"
    if not isinstance(proof.nonce, str) or len(proof.nonce) < 16:
        return False, "C22_NONCE_INVALID"
    if not isinstance(verifier_secret, bytes) or len(verifier_secret) < 32:
        return False, "C22_TRUST_ROOT_UNAVAILABLE"
    try:
        expiry = datetime.fromisoformat(proof.expires_at)
        if expiry.tzinfo is None or now.tzinfo is None:
            return False, "C22_TIMEZONE_REQUIRED"
        if now.astimezone(timezone.utc) >= expiry.astimezone(timezone.utc):
            return False, "C22_DELEGATION_EXPIRED"
    except (TypeError, ValueError, AttributeError):
        return False, "C22_EXPIRY_INVALID"
    expected_signature = hmac.new(
        verifier_secret,
        json.dumps(_payload(proof), sort_keys=True, separators=(",", ":")).encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected_signature, proof.signature):
        return False, "C22_SIGNATURE_INVALID"
    return True, None
