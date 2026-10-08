import sqlite3
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_unified_sqlite_guards_v0 import UnifiedOfflineSqliteGuardsV0
from periphery.enterprise_transaction_guard_snapshot_v0 import inspect_guarded_snapshot_v0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c237-reservation-key-000001"

def fixture(tmp_path):
    path=tmp_path/"state.db"
    ledger=AtomicOfflineReservationJournalV0(path)
    ledger.enroll_fixture(SCOPE)
    ledger.reserve_fixture(scope=SCOPE,generation=0,
        nonce="c237-nonce-00000000001",idempotency_key=KEY)
    UnifiedOfflineSqliteGuardsV0(path).install_fixture()
    return path,ledger

def test_snapshot_under_single_lock_never_grants_execution(tmp_path):
    path,_=fixture(tmp_path)
    result=inspect_guarded_snapshot_v0(path,KEY)
    assert result["reason"]=="C237_SNAPSHOT_VERIFIED_NO_EXECUTION"
    assert result["egress_allowed"] is False

def test_missing_guard_fail_closed(tmp_path):
    path,ledger=fixture(tmp_path)
    with ledger._connect() as db:
        db.execute("DROP TRIGGER c234_reservation_binding_immutable")
    assert inspect_guarded_snapshot_v0(path,KEY)["reason"]=="C237_REQUIRED_GUARD_MODIFIED"

def test_unknown_reservation_denied(tmp_path):
    path,_=fixture(tmp_path)
    assert inspect_guarded_snapshot_v0(path,"unknown")["reason"]=="C237_RESERVATION_UNKNOWN"

def test_database_lock_failure_closed(tmp_path):
    path,_=fixture(tmp_path)
    with sqlite3.connect(path,isolation_level=None,timeout=1) as holding:
        holding.execute("BEGIN IMMEDIATE")
        result=inspect_guarded_snapshot_v0(path,KEY)
        assert result["reason"]=="C237_SNAPSHOT_UNAVAILABLE"
        assert result["status"]=="BLOCK"
        holding.rollback()
