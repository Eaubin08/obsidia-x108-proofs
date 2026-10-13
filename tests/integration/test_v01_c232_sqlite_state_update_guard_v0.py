import sqlite3
import pytest
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_sqlite_state_update_guard_v0 import install_state_guard_fixture_v0,inspect_state_guard_fixture_v0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")

def fixture(tmp_path):
    path=tmp_path/"state.db"
    db=AtomicOfflineReservationJournalV0(path)
    db.enroll_fixture(SCOPE)
    db.reserve_fixture(scope=SCOPE,generation=0,nonce="c232-fixture-nonce-001",idempotency_key="c232-fixture-key-0001")
    install_state_guard_fixture_v0(path)
    return db,path

def test_direct_state_update_rejected(tmp_path):
    ledger,path=fixture(tmp_path)
    with pytest.raises(sqlite3.IntegrityError,match="C232_UNJOURNALED_STATE_UPDATE"):
        with ledger._connect() as connection:
            connection.execute("UPDATE reservations SET status='CLOSED_NO_EXECUTION'")
    assert ledger.inspect("c232-fixture-key-0001")=="RESERVED_NO_EXECUTION"

def test_normal_close_keeps_journal_valid(tmp_path):
    ledger,path=fixture(tmp_path)
    assert ledger.close_fixture(idempotency_key="c232-fixture-key-0001",disposition="CLOSED_NO_EXECUTION")=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert ledger.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"
    assert inspect_state_guard_fixture_v0(path)["status"]=="BLOCK"

def test_normal_revoke_keeps_journal_valid(tmp_path):
    ledger,path=fixture(tmp_path)
    assert ledger.revoke(SCOPE)
    assert ledger.inspect("c232-fixture-key-0001")=="INVALIDATED"
    assert ledger.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

def test_admin_can_remove_trigger_and_is_detected(tmp_path):
    ledger,path=fixture(tmp_path)
    with ledger._connect() as db:
        db.execute("DROP TRIGGER c232_state_transition_guard")
    assert inspect_state_guard_fixture_v0(path)["reason"]=="C232_GUARD_MISSING_OR_MODIFIED"
