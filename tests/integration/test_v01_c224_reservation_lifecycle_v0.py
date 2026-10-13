from periphery.enterprise_offline_reservation_lifecycle_v0 import OfflineReservationLifecycleV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c224-idempotency-000001"
NONCE="c224-nonce-0000000001"

def initialized(path):
    x=OfflineReservationLifecycleV0(path)
    x.enroll_fixture(SCOPE)
    assert x.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,
        idempotency_key=KEY)=="RESERVED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    return x

def test_close_survives_restart_with_receipt(tmp_path):
    path=tmp_path/"state.db"
    x=initialized(path)
    assert x.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="CLOSED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    y=OfflineReservationLifecycleV0(path)
    assert y.inspect(KEY)=="CLOSED_NO_EXECUTION"
    assert len(y.receipt(KEY)["receipt_hash"])==64
    assert y.close_fixture(idempotency_key=KEY,disposition="ABANDONED_NO_EXECUTION")=="BLOCK:C224_ALREADY_TERMINAL_OR_REVOKED"

def test_interrupted_reservation_can_be_abandoned(tmp_path):
    path=tmp_path/"state.db"
    initialized(path)
    restarted=OfflineReservationLifecycleV0(path)
    assert restarted.inspect(KEY)=="RESERVED_NO_EXECUTION"
    assert restarted.close_fixture(idempotency_key=KEY,disposition="ABANDONED_NO_EXECUTION")=="CLOSED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    assert restarted.receipt(KEY)["status"]=="ABANDONED_NO_EXECUTION"

def test_revocation_prevents_stale_closure(tmp_path):
    x=initialized(tmp_path/"state.db")
    assert x.revoke(SCOPE)
    assert x.inspect(KEY)=="INVALIDATED"
    assert x.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="BLOCK:C224_ALREADY_TERMINAL_OR_REVOKED"
    assert x.receipt(KEY) is None

def test_no_executed_transition(tmp_path):
    x=initialized(tmp_path/"state.db")
    assert x.close_fixture(idempotency_key=KEY,disposition="EXECUTED")=="BLOCK:C224_DISPOSITION_NOT_PERMITTED"
    assert x.inspect(KEY)=="RESERVED_NO_EXECUTION"
