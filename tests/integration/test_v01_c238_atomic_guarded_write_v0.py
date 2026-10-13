import sqlite3
from periphery.enterprise_transaction_guarded_reservation_v0 import TransactionGuardedReservationV0
from periphery.enterprise_guarded_offline_reservation_v0 import GuardedOfflineReservationV0
from periphery.enterprise_unified_sqlite_guards_v0 import UnifiedOfflineSqliteGuardsV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c238-idempotency-key-00001"
NONCE="c238-nonce-0000000001"

def fixture(tmp_path):
    path=tmp_path/"ledger.db"
    ledger=TransactionGuardedReservationV0(path)
    UnifiedOfflineSqliteGuardsV0(path).install_fixture()
    assert ledger.enroll_fixture(SCOPE)=="C238_SCOPE_ENROLLED_FIXTURE_ONLY"
    return ledger,path

def test_reserve_and_close_verify_inside_transaction(tmp_path):
    ledger,path=fixture(tmp_path)
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert ledger.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

def test_missing_trigger_denies_write_without_event(tmp_path):
    ledger,path=fixture(tmp_path)
    with sqlite3.connect(path) as db:
        db.execute("DROP TRIGGER c234_reservation_binding_immutable")
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="BLOCK:C238_GUARD_INVALID"
    assert ledger.inspect(KEY)=="UNKNOWN"

def test_revoke_under_missing_guard_does_not_mutate(tmp_path):
    ledger,path=fixture(tmp_path)
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    with sqlite3.connect(path) as db:
        db.execute("DROP TRIGGER c230_journal_no_update")
    assert ledger.revoke(SCOPE)=="BLOCK:C238_GUARD_INVALID"
    assert ledger.inspect(KEY)=="RESERVED_NO_EXECUTION"

def test_facade_uses_transaction_guarded_ledger(tmp_path):
    path=tmp_path/"ledger.db"
    facade=GuardedOfflineReservationV0(path)
    facade.initialize_fixture()
    assert facade.enroll_fixture(SCOPE)=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
    assert facade.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
