"""C2.34 protected request-binding fields: no real execution."""
import sqlite3
import pytest
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_sqlite_reservation_binding_guard_v0 import (
    BINDING_FIELDS,install_reservation_binding_guard_fixture_v0,
    inspect_reservation_binding_guard_fixture_v0,
)

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c234-idempotency-key-00001"

def fixture(tmp_path):
    path=tmp_path/"state.db"
    ledger=AtomicOfflineReservationJournalV0(path)
    ledger.enroll_fixture(SCOPE)
    assert ledger.reserve_fixture(scope=SCOPE,generation=0,
        nonce="c234-nonce-0000000001",
        idempotency_key=KEY)=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    install_reservation_binding_guard_fixture_v0(path)
    return ledger,path

@pytest.mark.parametrize("column",BINDING_FIELDS)
def test_direct_binding_update_rejected(tmp_path,column):
    ledger,_=fixture(tmp_path)
    value=1 if column=="generation" else "changed"
    with pytest.raises(sqlite3.IntegrityError,match="C234_RESERVATION_BINDING_IMMUTABLE"):
        with ledger._connect() as db:
            db.execute(f"UPDATE reservations SET {column}=? WHERE idempotency_key=?",(value,KEY))
    assert ledger.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

def test_normal_no_execution_closure_still_valid(tmp_path):
    ledger,path=fixture(tmp_path)
    assert ledger.close_fixture(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION")=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert ledger.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"
    result=inspect_reservation_binding_guard_fixture_v0(path)
    assert result["reason"]=="C234_LOCAL_BINDING_GUARD_PRESENT_NOT_ATTESTED"
    assert result["egress_allowed"] is False

def test_normal_revocation_still_valid(tmp_path):
    ledger,_=fixture(tmp_path)
    assert ledger.revoke(SCOPE) is True
    assert ledger.inspect(KEY)=="INVALIDATED"
    assert ledger.verify_logged_fixture()=="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"

def test_dropped_or_modified_trigger_detected(tmp_path):
    ledger,path=fixture(tmp_path)
    with ledger._connect() as db:
        db.execute("DROP TRIGGER c234_reservation_binding_immutable")
        db.execute("CREATE TRIGGER c234_reservation_binding_immutable BEFORE UPDATE OF generation ON reservations BEGIN SELECT 1; END")
    assert inspect_reservation_binding_guard_fixture_v0(path)["reason"]=="C234_BINDING_GUARD_MISSING_OR_MODIFIED"
    with ledger._connect() as db:
        db.execute("DROP TRIGGER c234_reservation_binding_immutable")
    assert inspect_reservation_binding_guard_fixture_v0(path)["reason"]=="C234_BINDING_GUARD_MISSING_OR_MODIFIED"
