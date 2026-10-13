import sqlite3
import pytest
from periphery.enterprise_transaction_guarded_reservation_v0 import TransactionGuardedReservationV0
from periphery.enterprise_unified_sqlite_guards_v0 import UnifiedOfflineSqliteGuardsV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c240-idempotency-key-00001"
NONCE="c240-nonce-00000000001"

def setup(tmp_path):
    path=tmp_path/"state.db"
    ledger=TransactionGuardedReservationV0(path)
    UnifiedOfflineSqliteGuardsV0(path).install_fixture()
    return path,ledger

def test_canonical_triggers_allow_logged_no_execution_flow(tmp_path):
    _,ledger=setup(tmp_path)
    assert ledger.enroll_fixture(SCOPE)=="C238_SCOPE_ENROLLED_FIXTURE_ONLY"
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert ledger.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

@pytest.mark.parametrize("name",[
    "c230_journal_no_update",
    "c230_journal_no_delete",
    "c230_reservation_no_delete",
    "c230_receipt_no_update",
    "c230_receipt_no_delete",
])
def test_replacement_trigger_with_expected_keywords_is_rejected(tmp_path,name):
    path,ledger=setup(tmp_path)
    # Mimics expected shape and abort token, but adds another instruction.
    with sqlite3.connect(path) as db:
        original=db.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND name=?",(name,)).fetchone()[0]
        db.execute("DROP TRIGGER "+name)
        malicious=original.replace("SELECT RAISE(ABORT,", "SELECT 1; SELECT RAISE(ABORT,")
        db.execute(malicious)
    assert ledger.enroll_fixture(SCOPE)=="BLOCK:C238_GUARD_INVALID"
    with ledger._connect() as db:
        assert db.execute("SELECT COUNT(*) FROM scopes").fetchone()[0]==0

def test_missing_guard_rejects_reservation(tmp_path):
    path,ledger=setup(tmp_path)
    with sqlite3.connect(path) as db:
        db.execute("DROP TRIGGER c230_journal_no_delete")
    assert ledger.enroll_fixture(SCOPE)=="BLOCK:C238_GUARD_INVALID"
