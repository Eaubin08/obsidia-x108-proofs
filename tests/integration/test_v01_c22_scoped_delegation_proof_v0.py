from dataclasses import replace
from datetime import datetime, timezone
from periphery.enterprise_scoped_delegation_proof_v0 import SCHEMA, ScopedDelegationProofV0, sign_fixture_only, verify_scoped_delegation_v0

KEY = bytes(range(32))
NOW = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)

def sample():
    p = ScopedDelegationProofV0(SCHEMA, "fixture-issuer", "org-a", "human-a", "delegate-a", "calendar", "CALENDAR.EVENT.CREATE", "a"*64, "2026-10-08T13:00:00+00:00", "1234567890abcdef", "")
    return sign_fixture_only(p, secret=KEY)

def check(p, **overrides):
    args = dict(trusted_issuer_id="fixture-issuer", verifier_secret=KEY, organization_id="org-a", principal_id="human-a", delegate_id="delegate-a", connector_id="calendar", capability_id="CALENDAR.EVENT.CREATE", action_request_hash="a"*64, now=NOW)
    args.update(overrides)
    return verify_scoped_delegation_v0(p, **args)

def test_valid_fixture_proof():
    assert check(sample()) == (True, None)

def test_scope_tampering():
    for field, val in [("organization_id", "org-b"), ("delegate_id", "delegate-b"), ("capability_id", "MAIL.SEND"), ("action_request_hash", "b"*64)]:
        assert check(replace(sample(), **{field:val}))[0] is False

def test_expired_and_wrong_issuer():
    assert check(sample(), now=datetime(2026,10,8,13,tzinfo=timezone.utc))[0] is False
    assert check(sample(), trusted_issuer_id="unknown")[0] is False

def test_wrong_key_and_missing_key():
    assert check(sample(), verifier_secret=bytes(range(1,33)))[0] is False
    assert check(sample(), verifier_secret=b"")[0] is False
