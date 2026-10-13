"""C2.16 isolated key pin and revocation tests."""
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from periphery.enterprise_offline_pinned_key_registry_v0 import OfflinePinnedKeyRegistryV0

def key():
    return Ed25519PrivateKey.generate().public_key().public_bytes(
        Encoding.PEM,PublicFormat.SubjectPublicKeyInfo)

def test_restart_keeps_revocation(tmp_path):
    path=tmp_path/"keys.db"
    registry=OfflinePinnedKeyRegistryV0(path)
    public=key()
    fp=registry.enroll_fixture(organization="org-a",issuer="issuer-a",
                                audience="aud-a",public_key_pem=public)
    assert registry.inspect_fixture(organization="org-a",issuer="issuer-a",
        audience="aud-a",public_key_pem=public)=="PINNED_FIXTURE_ONLY_NO_ORGANIZATION_AUTHORITY"
    assert registry.revoke(organization="org-a",issuer="issuer-a",audience="aud-a",fingerprint=fp)
    reopened=OfflinePinnedKeyRegistryV0(path)
    assert reopened.inspect_fixture(organization="org-a",issuer="issuer-a",
        audience="aud-a",public_key_pem=public)=="BLOCK:C216_KEY_REVOKED"
    with pytest.raises(ValueError,match="REVOKED"):
        reopened.enroll_fixture(organization="org-a",issuer="issuer-a",
            audience="aud-a",public_key_pem=public)

def test_other_tenant_and_swapped_key_are_denied(tmp_path):
    registry=OfflinePinnedKeyRegistryV0(tmp_path/"keys.db")
    public=key()
    registry.enroll_fixture(organization="org-a",issuer="issuer-a",
                             audience="aud-a",public_key_pem=public)
    assert registry.inspect_fixture(organization="org-b",issuer="issuer-a",
        audience="aud-a",public_key_pem=public)=="BLOCK:C216_KEY_NOT_ENROLLED"
    assert registry.inspect_fixture(organization="org-a",issuer="issuer-a",
        audience="aud-b",public_key_pem=public)=="BLOCK:C216_KEY_NOT_ENROLLED"
    assert registry.inspect_fixture(organization="org-a",issuer="issuer-a",
        audience="aud-a",public_key_pem=key())=="BLOCK:C216_KEY_NOT_ENROLLED"
