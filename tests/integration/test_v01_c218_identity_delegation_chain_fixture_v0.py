"""C2.18: identity signature, delegation scope and durable revocation tests."""
from dataclasses import replace
from datetime import datetime, timezone
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from periphery.enterprise_offline_asymmetric_identity_fixture_v0 import OfflineOrganizationIdentityClaimV0, canonical_claim_payload_v0
from periphery.enterprise_offline_pinned_key_registry_v0 import OfflinePinnedKeyRegistryV0
from periphery.enterprise_scoped_delegation_proof_v0 import ScopedDelegationProofV0, SCHEMA, sign_fixture_only
from periphery.enterprise_durable_revocation_ledger_v0 import DurableDelegationLedgerV0
from periphery.enterprise_identity_delegation_chain_fixture_v0 import inspect_identity_delegation_fixture_v0

NOW=datetime(2026,10,8,12,tzinfo=timezone.utc)
SECRET=bytes(range(32))
SCOPE=("org-a","delegate-a","calendar","calendar.read")

def scenario(tmp_path):
    private=Ed25519PrivateKey.generate()
    public=private.public_key().public_bytes(Encoding.PEM,PublicFormat.SubjectPublicKeyInfo)
    claim=OfflineOrganizationIdentityClaimV0("org-a","actor-a","issuer-a","aud-a",
        "calendar.read","a"*64,"2099-01-01T00:00:00+00:00","")
    claim=replace(claim,signature_b64=base64.b64encode(private.sign(canonical_claim_payload_v0(claim))).decode())
    registry=OfflinePinnedKeyRegistryV0(tmp_path/"keys.db")
    fp=registry.enroll_fixture(organization="org-a",issuer="issuer-a",audience="aud-a",public_key_pem=public)
    delegation=ScopedDelegationProofV0(SCHEMA,"delegation-issuer","org-a","actor-a",
        "delegate-a","calendar","calendar.read","a"*64,
        "2099-01-01T00:00:00+00:00","c218-nonce-00000001","")
    delegation=sign_fixture_only(delegation,secret=SECRET)
    ledger=DurableDelegationLedgerV0(tmp_path/"ledger.db")
    ledger.register_fixture(SCOPE)
    args=dict(registry=registry,claim=claim,public_key_pem=public,
        delegation=delegation,delegation_secret=SECRET,delegation_issuer="delegation-issuer",
        organization="org-a",actor="actor-a",delegate="delegate-a",connector="calendar",
        capability="calendar.read",request_hash="a"*64,audience="aud-a",
        identity_issuer="issuer-a",now=NOW,revocation_ledger=ledger,generation=0)
    return fp,args

def test_valid_fixture_chain_still_denies_execution(tmp_path):
    _,args=scenario(tmp_path)
    result=inspect_identity_delegation_fixture_v0(**args)
    assert result["reason"]=="C218_ORGANIZATION_DELEGATION_AUTHORITY_UNVERIFIED"
    assert result["egress_allowed"] is False

def test_revocation_after_restart_blocks(tmp_path):
    _,args=scenario(tmp_path)
    args["revocation_ledger"].revoke(SCOPE)
    args["revocation_ledger"]=DurableDelegationLedgerV0(tmp_path/"ledger.db")
    assert "C23_REVOKED" in inspect_identity_delegation_fixture_v0(**args)["reason"]

def test_cross_tenant_and_delegate_scope_rejected(tmp_path):
    _,args=scenario(tmp_path)
    args["organization"]="org-b"
    assert "IDENTITY_REJECTED" in inspect_identity_delegation_fixture_v0(**args)["reason"]
    other=tmp_path/"other"
    other.mkdir()
    _,args=scenario(other)
    args["delegate"]="different"
    assert "DELEGATION_REJECTED" in inspect_identity_delegation_fixture_v0(**args)["reason"]

def test_expired_delegation_rejected(tmp_path):
    _,args=scenario(tmp_path)
    args["now"]=datetime(2100,1,1,tzinfo=timezone.utc)
    assert inspect_identity_delegation_fixture_v0(**args)["status"]=="BLOCK"
