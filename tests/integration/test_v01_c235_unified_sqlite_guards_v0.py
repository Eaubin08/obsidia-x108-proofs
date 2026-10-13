import sqlite3
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_unified_sqlite_guards_v0 import UnifiedOfflineSqliteGuardsV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c235-idempotency-key-00001"

def fixture(tmp_path):
    path=tmp_path/"state.db"
    ledger=AtomicOfflineReservationJournalV0(path)
    ledger.enroll_fixture(SCOPE)
    ledger.reserve_fixture(scope=SCOPE,generation=0,nonce="c235-nonce-0000000001",idempotency_key=KEY)
    return ledger, UnifiedOfflineSqliteGuardsV0(path)

def test_uninitialized_guards_fail_closed(tmp_path):
    _,guards=fixture(tmp_path)
    assert guards.inspect()["reason"].startswith("C235_REQUIRED_GUARD_INVALID:")
    assert guards.inspect()["egress_allowed"] is False

def test_install_all_and_preserve_logged_close(tmp_path):
    ledger,guards=fixture(tmp_path)
    assert guards.install_fixture()=="C235_LOCAL_FIXTURE_GUARDS_INITIALIZED_NO_EXECUTION_AUTHORITY"
    assert guards.inspect()["reason"]=="C235_LOCAL_GUARDS_PRESENT_NOT_ATTESTED"
    assert ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert ledger.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

def test_guard_drop_detected(tmp_path):
    ledger,guards=fixture(tmp_path)
    guards.install_fixture()
    with ledger._connect() as db:
        db.execute("DROP TRIGGER c234_reservation_binding_immutable")
    assert guards.inspect()["reason"].startswith("C235_REQUIRED_GUARD_INVALID:")

def test_install_twice_is_idempotent(tmp_path):
    _,guards=fixture(tmp_path)
    assert guards.install_fixture()==guards.install_fixture()
