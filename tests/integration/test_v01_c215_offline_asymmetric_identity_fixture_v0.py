"""C2.15 verifies Ed25519 signature integrity but not organization authority."""
from dataclasses import replace
from datetime import datetime, timezone
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from periphery.enterprise_offline_asymmetric_identity_fixture_v0 import (
    OfflineOrganizationIdentityClaimV0, canonical_claim_payload_v0,
    inspect_offline_identity_claim_v0,
)

NOW=datetime(2026,10,8,12,tzinfo=timezone.utc)

def fixture():
    private=Ed25519PrivateKey.generate()
    public=private.public_key().public_bytes(Encoding.PEM,PublicFormat.SubjectPublicKeyInfo)
    claim=OfflineOrganizationIdentityClaimV0(
        "org-a","actor-a","fixture-issuer","fixture-audience",
        "calendar.read","a"*64,"2099-01-01T00:00:00+00:00","")
    sig=base64.b64encode(private.sign(canonical_claim_payload_v0(claim))).decode()
    return public,replace(claim,signature_b64=sig)

def inspect(public,claim,**kw):
    args=dict(claim=claim,pinned_public_key_pem=public,
              expected_organization="org-a",expected_actor="actor-a",
              expected_issuer="fixture-issuer",expected_audience="fixture-audience",
              expected_capability="calendar.read",expected_request_hash="a"*64,
              now=NOW)
    args.update(kw)
    return inspect_offline_identity_claim_v0(**args)

def test_valid_signature_still_not_organization_authority():
    key,claim=fixture()
    result=inspect(key,claim)
    assert result["cryptographic_fixture_valid"] is True
    assert result["organization_authority_verified"] is False
    assert result["egress_allowed"] is False
    assert result["reason"]=="C215_OFFLINE_ISSUER_NOT_ORGANIZATION_ATTESTED"

def test_scope_and_signature_substitution_fail():
    key,claim=fixture()
    assert inspect(key,replace(claim,actor_id="actor-b"))["status"]=="BLOCK"
    assert inspect(key,replace(claim,actor_id="actor-b"))["cryptographic_fixture_valid"] is False
    other=Ed25519PrivateKey.generate().public_key().public_bytes(Encoding.PEM,PublicFormat.SubjectPublicKeyInfo)
    assert inspect(other,claim)["reason"]=="C215_SIGNATURE_OR_KEY_INVALID"

def test_expiration_and_issuer_mismatch_block():
    key,claim=fixture()
    assert inspect(key,claim,now=datetime(2100,1,1,tzinfo=timezone.utc))["reason"]=="C215_EXPIRED"
    assert inspect(key,claim,expected_issuer="untrusted")["reason"]=="C215_IDENTITY_SCOPE_MISMATCH"
