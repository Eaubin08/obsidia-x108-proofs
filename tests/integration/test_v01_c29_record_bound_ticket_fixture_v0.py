from dataclasses import replace
from datetime import datetime, timezone
from periphery.enterprise_record_bound_ticket_fixture_v0 import (
    SCHEMA, TicketRecordBindingFixtureV0, sign_ticket_record_fixture_v0,
    verify_ticket_record_fixture_v0,
)
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket

KEY = bytes(range(32))
NOW = datetime(2026,10,8,12,tzinfo=timezone.utc)

def scenario():
    ticket = issue_sovereign_ticket("world-a", "fixture-os3", "ALLOW",
                                    "calendar:write", 3, "REVERSIBLE_WORLD_CALL")
    record = dict(decision_record_id="record-a",decision_record_hash="a"*64,
                  action_id="world-a",required_scope="calendar:write")
    binding = TicketRecordBindingFixtureV0(
        SCHEMA, "test-issuer", record["decision_record_id"],
        record["decision_record_hash"], record["action_id"],
        record["required_scope"], ticket.ticket_id, ticket.hash,
        "2099-01-01T00:00:00+00:00", "")
    return record,ticket,sign_ticket_record_fixture_v0(binding,fixture_key=KEY)

def check(record,ticket,binding,**kwargs):
    opts=dict(trusted_fixture_issuer="test-issuer",verifier_key=KEY,
              record=record,ticket=ticket,now=NOW)
    opts.update(kwargs)
    return verify_ticket_record_fixture_v0(binding,**opts)

def test_signed_fixture_matches_exact_record_and_ticket():
    r,t,b=scenario()
    assert check(r,t,b)==(True,None)

def test_record_mutation_and_ticket_swap_denied():
    r,t,b=scenario()
    assert check(dict(r,decision_record_hash="b"*64),t,b)[0] is False
    other=issue_sovereign_ticket("world-a","fixture-os3","ALLOW",
                                  "calendar:write",3,"REVERSIBLE_WORLD_CALL")
    assert check(r,other,b)[0] is False

def test_signature_and_issuer_tamper_denied():
    r,t,b=scenario()
    assert check(r,t,replace(b,signature="0"*64))==(False,"C29_SIGNATURE_INVALID")
    assert check(r,t,b,trusted_fixture_issuer="untrusted")[0] is False

def test_expiration_and_absent_trust_root_denied():
    r,t,b=scenario()
    assert check(r,t,b,now=datetime(2099,1,1,tzinfo=timezone.utc))[0] is False
    assert check(r,t,b,verifier_key=b"")[0] is False

def test_missing_record_or_ticket_denied():
    r,t,b=scenario()
    assert check(None,t,b)[0] is False
    assert check(r,None,b)[0] is False
