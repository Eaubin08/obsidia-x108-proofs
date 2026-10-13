"""C2.33 demonstrate direct SQLite bypasses remain possible and detected only partly."""
import sqlite3
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_sqlite_write_guard_audit_v0 import LocalWriteGuardV0
from periphery.enterprise_sqlite_state_update_guard_v0 import install_state_guard_fixture_v0
from periphery.enterprise_sqlite_bypass_audit_v0 import inspect_sqlite_bypass_v0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c233-idempotency-key-00001"

def fixture(tmp_path):
    db=AtomicOfflineReservationJournalV0(tmp_path/"ledger.db")
    db.enroll_fixture(SCOPE)
    db.reserve_fixture(scope=SCOPE,generation=0,nonce="c233-nonce-000000001",idempotency_key=KEY)
    LocalWriteGuardV0(db.path).install_fixture_triggers()
    install_state_guard_fixture_v0(db.path)
    return db

def test_consistent_fixture_always_blocks(tmp_path):
    db=fixture(tmp_path)
    v=inspect_sqlite_bypass_v0(ledger=db)
    assert v["reason"]=="C233_LOCAL_CONTROLS_CONSISTENT_NOT_INDEPENDENTLY_ATTESTED"
    assert v["egress_allowed"] is False

def test_direct_status_guard_does_not_cover_other_columns(tmp_path):
    db=fixture(tmp_path)
    with db._connect() as connection:
        connection.execute("UPDATE reservations SET generation=88 WHERE idempotency_key=?",(KEY,))
    # Current chain verifier checks state only, so this bypass is not yet detected.
    assert inspect_sqlite_bypass_v0(ledger=db)["reason"]=="C233_LOCAL_CONTROLS_CONSISTENT_NOT_INDEPENDENTLY_ATTESTED"

def test_trigger_drop_detected(tmp_path):
    db=fixture(tmp_path)
    with db._connect() as connection:
        connection.execute("DROP TRIGGER c232_state_transition_guard")
    assert inspect_sqlite_bypass_v0(ledger=db)["reason"].startswith("C233_STATE_GUARD_INVALID:")

def test_fake_event_breaks_local_consistency(tmp_path):
    db=fixture(tmp_path)
    with db._connect() as connection:
        connection.execute("INSERT INTO transition_events VALUES(?,?,?,?,?)",
            (2,KEY,"CLOSED_NO_EXECUTION","0"*64,"1"*64))
    assert inspect_sqlite_bypass_v0(ledger=db)["reason"].startswith("C233_JOURNAL_STATE_DRIFT:")
