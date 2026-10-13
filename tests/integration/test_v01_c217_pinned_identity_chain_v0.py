"""C2.17 integration of pinned Ed25519 fixture and durable revocation."""
from dataclasses import replace
from datetime import datetime, timezone
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from periphery.enterprise_offline_pinned_key_registry_v0 import OfflinePinnedKeyRegistryV0
from periphery.enterprise_offline_asymmetric_identity_fixture_v0 import OfflineOrganizationIdentityClaimV0, canonical_claim_payload_v0
from periphery.enterprise_pinned_identity_chain_v0 import inspect_pinned_identity_claim_fixture_v0

NOW=datetime(2026,10,8,12,tzinfo=timezone.utc)

def setup(tmp_path):
    private=Ed25519PrivateKey.generate()
    public=private.public_key().public_bytes(Encoding.PEM,PublicFormat.SubjectPublicKeyInfo)
    claim=OfflineOrganizationIdentityClaimV0(
        "org-a","actor-a","issuer-a","aud-a","calendar.read",
        "a"*64,"2099-01-01T00:00:00+00:00","")
    claim=replace(claim,signature_b64=base64.b64encode(private.sign(canonical_claim_payload_v0(claim))).decode())
    db=tmp_path/"keys.db"
    registry=OfflinePinnedKeyRegistryV0(db)
    fp=registry.enroll_fixture(organization="org-a",issuer="issuer-a",audience="aud-a",public_key_pem=public)
    params=dict(registry=registry,claim=claim,public_key_pem=public,expected_organization="org-a",
        expected_actor="actor-a",expected_issuer="issuer-a",expected_audience="aud-a",
        expected_capability="calendar.read",expected_request_hash="a"*64,now=NOW)
    return db,fp,params

def test_matching_signature_and_pin_still_block(tmp_path):
    _,_,params=setup(tmp_path)
    result=inspect_pinned_identity_claim_fixture_v0(**params)
    assert result["cryptographic_fixture_valid"] is True
    assert result["reason"]=="C217_ORGANIZATION_AUTHORITY_UNATTESTED"
    assert result["egress_allowed"] is False

def test_revocation_persists_and_blocks_signed_claim(tmp_path):
    db,fp,params=setup(tmp_path)
    params["registry"].revoke(organization="org-a",issuer="issuer-a",audience="aud-a",fingerprint=fp)
    params["registry"]=OfflinePinnedKeyRegistryV0(db)
    result=inspect_pinned_identity_claim_fixture_v0(**params)
    assert result["reason"]=="C217_PIN_REJECTED:BLOCK:C216_KEY_REVOKED"

def test_wrong_actor_and_tenant_denied(tmp_path):
    _,_,params=setup(tmp_path)
    params["expected_actor"]="actor-b"
    assert inspect_pinned_identity_claim_fixture_v0(**params)["cryptographic_fixture_valid"] is False
    params["expected_actor"]="actor-a"
    params["expected_organization"]="org-b"
    assert inspect_pinned_identity_claim_fixture_v0(**params)["reason"].startswith("C217_PIN_REJECTED")
