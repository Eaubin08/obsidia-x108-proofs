"""C2.10 fixture-only issuer enrollment/revocation tests."""
import pytest
from periphery.enterprise_issuer_trust_registry_fixture_v0 import FixtureIssuerTrustRegistryV0

def test_restart_preserves_issuer_revocation(tmp_path):
    path=tmp_path/"issuer.db"
    r=FixtureIssuerTrustRegistryV0(path)
    r.register_fixture(organization="org-a",issuer="issuer-a",key_digest="a"*64)
    assert r.check_fixture(organization="org-a",issuer="issuer-a",key_digest="a"*64)=="FIXTURE_ISSUER_MATCH_NO_ORGANIZATION_AUTHORITY"
    assert r.revoke(organization="org-a",issuer="issuer-a") is True
    another=FixtureIssuerTrustRegistryV0(path)
    assert another.check_fixture(organization="org-a",issuer="issuer-a",key_digest="a"*64)=="BLOCK:C210_ISSUER_REVOKED"

def test_tenant_isolation_and_key_swap_denial(tmp_path):
    r=FixtureIssuerTrustRegistryV0(tmp_path/"issuer.db")
    r.register_fixture(organization="org-a",issuer="issuer-a",key_digest="a"*64)
    assert r.check_fixture(organization="org-b",issuer="issuer-a",key_digest="a"*64)=="BLOCK:C210_ISSUER_UNKNOWN"
    assert r.check_fixture(organization="org-a",issuer="issuer-a",key_digest="b"*64)=="BLOCK:C210_ISSUER_KEY_MISMATCH"
    with pytest.raises(ValueError,match="IMMUTABLE"):
        r.register_fixture(organization="org-a",issuer="issuer-a",key_digest="b"*64)

def test_revoked_issuer_cannot_be_reenrolled(tmp_path):
    r=FixtureIssuerTrustRegistryV0(tmp_path/"issuer.db")
    r.register_fixture(organization="org-a",issuer="issuer-a",key_digest="a"*64)
    r.revoke(organization="org-a",issuer="issuer-a")
    with pytest.raises(ValueError,match="REVOKED"):
        r.register_fixture(organization="org-a",issuer="issuer-a",key_digest="a"*64)

def test_unknown_revocation_never_enrolls(tmp_path):
    r=FixtureIssuerTrustRegistryV0(tmp_path/"issuer.db")
    assert r.revoke(organization="org-a",issuer="missing") is False
    assert r.check_fixture(organization="org-a",issuer="missing",key_digest="a"*64)=="BLOCK:C210_ISSUER_UNKNOWN"
