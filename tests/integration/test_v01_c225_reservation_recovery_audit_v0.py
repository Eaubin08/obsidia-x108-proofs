"""C2.25 recovery inspection must never launch an action or automatic retry."""
from periphery.enterprise_offline_reservation_lifecycle_v0 import OfflineReservationLifecycleV0
from periphery.enterprise_offline_reservation_recovery_audit_v0 import inspect_reservation_recovery_v0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c225-idempotency-00001"
NONCE="c225-proof-nonce-00001"

def fixture(tmp_path):
    ledger=OfflineReservationLifecycleV0(tmp_path/"state.db")
    ledger.enroll_fixture(SCOPE)
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    return ledger

def test_unfinished_after_restart_requires_manual_review(tmp_path):
    fixture(tmp_path)
    restarted=OfflineReservationLifecycleV0(tmp_path/"state.db")
    result=inspect_reservation_recovery_v0(lifecycle=restarted,idempotency_key=KEY)
    assert result["reason"]=="C225_UNFINISHED_REQUIRES_MANUAL_REVIEW"
    assert result["automatic_retry"] is False
    assert restarted.inspect(KEY)=="RESERVED_NO_EXECUTION"

def test_closed_receipt_survives_restart_and_blocks(tmp_path):
    ledger=fixture(tmp_path)
    ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")
    restarted=OfflineReservationLifecycleV0(tmp_path/"state.db")
    result=inspect_reservation_recovery_v0(lifecycle=restarted,idempotency_key=KEY)
    assert result["reason"]=="C225_CLOSED_NO_EXECUTION_RECEIPT_VERIFIED"
    assert result["egress_allowed"] is False

def test_corrupt_and_missing_receipt_refused(tmp_path):
    ledger=fixture(tmp_path)
    ledger.close_fixture(idempotency_key=KEY,disposition="ABANDONED_NO_EXECUTION")
    with ledger._connect() as db:
        db.execute("UPDATE lifecycle_receipts SET receipt_hash=? WHERE idempotency_key=?",("0"*64,KEY))
    assert inspect_reservation_recovery_v0(lifecycle=ledger,idempotency_key=KEY)["reason"]=="C225_RECEIPT_HASH_INVALID"
    with ledger._connect() as db:
        db.execute("DELETE FROM lifecycle_receipts WHERE idempotency_key=?",(KEY,))
    assert inspect_reservation_recovery_v0(lifecycle=ledger,idempotency_key=KEY)["reason"]=="C225_RECEIPT_MISSING_OR_MISMATCHED"

def test_revoked_during_recovery_remains_blocked(tmp_path):
    ledger=fixture(tmp_path)
    assert ledger.revoke(SCOPE)
    restarted=OfflineReservationLifecycleV0(tmp_path/"state.db")
    assert inspect_reservation_recovery_v0(lifecycle=restarted,idempotency_key=KEY)["reason"]=="C225_REVOKED_OR_INVALIDATED"
    assert inspect_reservation_recovery_v0(lifecycle=restarted,idempotency_key="missing")["status"]=="BLOCK"
