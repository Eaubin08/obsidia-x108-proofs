import sqlite3
import pytest
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_sqlite_write_guard_audit_v0 import LocalWriteGuardV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c230-idempotency-key-00001"

def setup(tmp_path):
    path=tmp_path/"state.db"
    ledger=AtomicOfflineReservationJournalV0(path)
    ledger.enroll_fixture(SCOPE)
    ledger.reserve_fixture(scope=SCOPE,generation=0,nonce="c230-proof-nonce-000001",idempotency_key=KEY)
    guard=LocalWriteGuardV0(path)
    guard.install_fixture_triggers()
    return ledger,guard

def test_normal_logged_close_remains_possible(tmp_path):
    ledger,guard=setup(tmp_path)
    assert ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert guard.inspect_triggers()["reason"]=="C230_LOCAL_TRIGGERS_PRESENT_NOT_ATTESTED"
    assert ledger.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

def test_event_and_receipt_tamper_forbidden(tmp_path):
    ledger,_=setup(tmp_path)
    ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")
    with pytest.raises(sqlite3.IntegrityError):
        with ledger._connect() as db:
            db.execute("UPDATE transition_events SET event_kind='INVALIDATED' WHERE sequence=1")
    with pytest.raises(sqlite3.IntegrityError):
        with ledger._connect() as db:
            db.execute("DELETE FROM lifecycle_receipts")

def test_removing_trigger_is_detected_not_prevented(tmp_path):
    ledger,guard=setup(tmp_path)
    with ledger._connect() as db:
        db.execute("DROP TRIGGER c230_journal_no_update")
    assert guard.inspect_triggers()["reason"]=="C230_TRIGGERS_MISSING"
    assert guard.inspect_triggers()["egress_allowed"] is False
