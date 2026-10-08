"""C2.15 offline asymmetric signed organizational identity fixture.

Cryptography provides integrity against a pinned public key; an offline fixture
does NOT establish legal organization control or production authorization.
No egress, no decision issuance and no trusted ticket issuance.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import json

@dataclass(frozen=True)
class OfflineOrganizationIdentityClaimV0:
    organization_id: str
    actor_id: str
    issuer: str
    audience: str
    capability_id: str
    action_request_hash: str
    expires_at: str
    signature_b64: str

def canonical_claim_payload_v0(claim):
    return json.dumps({
        k: getattr(claim,k) for k in (
            "organization_id","actor_id","issuer","audience",
            "capability_id","action_request_hash","expires_at")
    },sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def inspect_offline_identity_claim_v0(*, claim, pinned_public_key_pem,
                                      expected_organization,expected_actor,
                                      expected_issuer,expected_audience,
                                      expected_capability,expected_request_hash,
                                      now):
    def deny(reason):
        return {"status":"BLOCK","reason":reason,
                "cryptographic_fixture_valid":False,
                "organization_authority_verified":False,
                "egress_allowed":False,"execution_authority":False}
    if not isinstance(claim,OfflineOrganizationIdentityClaimV0):
        return deny("C215_CLAIM_MISSING")
    expectations=(
        (claim.organization_id,expected_organization),
        (claim.actor_id,expected_actor),(claim.issuer,expected_issuer),
        (claim.audience,expected_audience),
        (claim.capability_id,expected_capability),
        (claim.action_request_hash,expected_request_hash))
    if any(not isinstance(a,str) or not a or a!=b for a,b in expectations):
        return deny("C215_IDENTITY_SCOPE_MISMATCH")
    try:
        expiry=datetime.fromisoformat(claim.expires_at)
        if expiry.tzinfo is None or now.tzinfo is None:
            return deny("C215_TIMEZONE_REQUIRED")
        if now.astimezone(timezone.utc)>=expiry.astimezone(timezone.utc):
            return deny("C215_EXPIRED")
        signature=base64.b64decode(claim.signature_b64,validate=True)
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        public=load_pem_public_key(pinned_public_key_pem)
        if not isinstance(public,Ed25519PublicKey):
            return deny("C215_KEY_TYPE_NOT_SUPPORTED")
        public.verify(signature,canonical_claim_payload_v0(claim))
    except Exception:
        return deny("C215_SIGNATURE_OR_KEY_INVALID")
    return {"status":"BLOCK",
            "reason":"C215_OFFLINE_ISSUER_NOT_ORGANIZATION_ATTESTED",
            "cryptographic_fixture_valid":True,
            "organization_authority_verified":False,
            "egress_allowed":False,"execution_authority":False}
