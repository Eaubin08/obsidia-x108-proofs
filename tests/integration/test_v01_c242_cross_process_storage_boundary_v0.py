"""C2.42 cross-process lock and direct access exposure regression."""
import multiprocessing as mp
import sqlite3
from periphery.enterprise_unified_sqlite_guards_v0 import UnifiedOfflineSqliteGuardsV0
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_cross_process_storage_audit_v0 import audit_storage_boundary_v0

def hold_lock(path,ready,release):
    with sqlite3.connect(path,isolation_level=None,timeout=5) as db:
        db.execute("BEGIN IMMEDIATE")
        ready.set()
        release.wait(10)
        db.rollback()

def test_cross_process_writer_lock_fails_closed(tmp_path):
    path=tmp_path/"state.db"
    AtomicOfflineReservationJournalV0(path)
    UnifiedOfflineSqliteGuardsV0(path).install_fixture()
    ready,release=mp.Event(),mp.Event()
    worker=mp.Process(target=hold_lock,args=(str(path),ready,release))
    worker.start()
    try:
        assert ready.wait(5)
        result=audit_storage_boundary_v0(path)
        assert result["reason"]=="C242_STORAGE_LOCKED_OR_UNAVAILABLE"
        assert result["egress_allowed"] is False
    finally:
        release.set()
        worker.join(10)
        if worker.is_alive():
            worker.terminate();worker.join()

def test_local_catalog_not_process_isolation(tmp_path):
    path=tmp_path/"state.db"
    AtomicOfflineReservationJournalV0(path)
    UnifiedOfflineSqliteGuardsV0(path).install_fixture()
    result=audit_storage_boundary_v0(path)
    assert result["reason"]=="C242_LOCAL_GUARDS_PRESENT_NOT_PROCESS_ISOLATED"
    assert result["status"]=="BLOCK"

def test_raw_sql_can_still_bypass_facade(tmp_path):
    path=tmp_path/"state.db"
    AtomicOfflineReservationJournalV0(path)
    UnifiedOfflineSqliteGuardsV0(path).install_fixture()
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO scopes(organization,delegate,connector,capability) VALUES(?,?,?,?)",("unverified-org","delegate","fixture","capability"))
    assert audit_storage_boundary_v0(path)["reason"]=="C242_LOCAL_GUARDS_PRESENT_NOT_PROCESS_ISOLATED"

def test_removed_trigger_detected(tmp_path):
    path=tmp_path/"state.db"
    AtomicOfflineReservationJournalV0(path)
    UnifiedOfflineSqliteGuardsV0(path).install_fixture()
    with sqlite3.connect(path) as db:
        db.execute("DROP TRIGGER c234_reservation_binding_immutable")
    assert audit_storage_boundary_v0(path)["reason"]=="C242_GUARD_CATALOG_INVALID"
