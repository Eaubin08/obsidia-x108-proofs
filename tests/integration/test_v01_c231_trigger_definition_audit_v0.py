import sqlite3
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_sqlite_write_guard_audit_v0 import LocalWriteGuardV0
from periphery.enterprise_sqlite_trigger_definition_audit_v0 import inspect_trigger_definitions_v0

def fixture(tmp_path):
    path=tmp_path/"audit.db"
    AtomicOfflineReservationJournalV0(path)
    LocalWriteGuardV0(path).install_fixture_triggers()
    return path

def test_expected_trigger_bodies_report_local_match_only(tmp_path):
    path=fixture(tmp_path)
    r=inspect_trigger_definitions_v0(path)
    assert r["reason"]=="C231_LOCAL_TRIGGER_DEFINITIONS_MATCH_NOT_ATTESTED"
    assert r["egress_allowed"] is False

def test_replaced_trigger_body_is_detected(tmp_path):
    path=fixture(tmp_path)
    with sqlite3.connect(path) as db:
        db.execute("DROP TRIGGER c230_journal_no_update")
        db.execute("""CREATE TRIGGER c230_journal_no_update
            BEFORE UPDATE ON transition_events BEGIN SELECT 1; END""")
    assert inspect_trigger_definitions_v0(path)["reason"]=="C231_TRIGGER_DEFINITION_DRIFT"

def test_missing_trigger_denied(tmp_path):
    path=fixture(tmp_path)
    with sqlite3.connect(path) as db:
        db.execute("DROP TRIGGER c230_receipt_no_delete")
    assert inspect_trigger_definitions_v0(path)["reason"]=="C231_REQUIRED_TRIGGER_MISSING"
