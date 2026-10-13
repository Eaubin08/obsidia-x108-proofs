"""C2.11 issuer revocation + signed record/ticket fixture fail-closed tests."""
import hashlib
from datetime import datetime, timezone
from periphery.enterprise_issuer_trust_registry_fixture_v0 import FixtureIssuerTrustRegistryV0
from periphery.enterprise_fixture_trust_chain_v0 import inspect_fixture_trust_chain_v0
from periphery.enterprise_record_bound_ticket_fixture_v0 import (
    SCHEMA, TicketRecordBindingFixtureV0, sign_ticket_record_fixture_v0,
)
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket

KEY=bytes(range(32))
NOW=datetime(2026,10,8,12,tzinfo=timezone.utc)

def setup(tmp_path):
    registry=FixtureIssuerTrustRegistryV0(tmp_path/"issuers.db")
    registry.register_fixture(organization="org-a",issuer="fixture-issuer",
                              key_digest=hashlib.sha256(KEY).hexdigest())
    record=dict(decision_record_id="record-a",decision_record_hash="a"*64,
                action_id="action-a",required_scope="calendar:write")
    ticket=issue_sovereign_ticket("action-a","os3-fixture","ALLOW",
                                 "calendar:write",3,"REVERSIBLE_WORLD_CALL")
    b=TicketRecordBindingFixtureV0(
        SCHEMA,"fixture-issuer","record-a","a"*64,
        "action-a","calendar:write",ticket.ticket_id,ticket.hash,
        "2099-01-01T00:00:00+00:00","")
    signed=sign_ticket_record_fixture_v0(b,fixture_key=KEY)
    return dict(organization="org-a",registry=registry,issuer_ref="fixture-issuer",
                verifier_key=KEY,binding=signed,record=record,ticket=ticket,now=NOW)

def test_fully_matching_fixtures_still_block(tmp_path):
    p=setup(tmp_path)
    v=inspect_fixture_trust_chain_v0(**p)
    assert v["status"]=="BLOCK"
    assert v["reason"]=="C211_ORGANIZATION_AUTHORITY_UNVERIFIED"
    assert v["egress_allowed"] is False

def test_durable_revoked_issuer_blocks(tmp_path):
    p=setup(tmp_path)
    assert p["registry"].revoke(organization="org-a",issuer="fixture-issuer")
    p["registry"]=FixtureIssuerTrustRegistryV0(tmp_path/"issuers.db")
    assert inspect_fixture_trust_chain_v0(**p)["reason"]=="BLOCK:C210_ISSUER_REVOKED"

def test_cross_tenant_blocks(tmp_path):
    p=setup(tmp_path)
    p["organization"]="org-b"
    assert inspect_fixture_trust_chain_v0(**p)["reason"]=="BLOCK:C210_ISSUER_UNKNOWN"

def test_mismatched_record_and_wrong_key_block(tmp_path):
    p=setup(tmp_path)
    p["record"]=dict(p["record"],decision_record_hash="b"*64)
    assert inspect_fixture_trust_chain_v0(**p)["reason"].startswith("C211_BINDING_INVALID:")
    p=setup(tmp_path)
    p["verifier_key"]=b"z"*32
    assert inspect_fixture_trust_chain_v0(**p)["reason"]=="BLOCK:C210_ISSUER_KEY_MISMATCH"
