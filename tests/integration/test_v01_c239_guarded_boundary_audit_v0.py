"""C2.39 regression of opt-in guard boundary and known direct database bypass."""
import sqlite3
from periphery.enterprise_guarded_boundary_audit_v0 import GuardedBoundaryAuditV0
from periphery.enterprise_guarded_offline_reservation_v0 import GuardedOfflineReservationV0
from periphery.enterprise_transaction_guarded_reservation_v0 import TransactionGuardedReservationV0
from periphery.enterprise_unified_sqlite_guards_v0 import UnifiedOfflineSqliteGuardsV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c239-idempotency-key-00001"
NONCE="c239-nonce-00000000001"

def test_guarded_facade_and_boundary_snapshot(tmp_path):
    path=tmp_path/"ledger.db"
    facade=GuardedOfflineReservationV0(path)
    facade.initialize_fixture()
    assert GuardedBoundaryAuditV0.required_entrypoint_type() is TransactionGuardedReservationV0
    audit=GuardedBoundaryAuditV0(path).inspect()
    assert audit["reason"]=="C239_LOCAL_BOUNDARY_PRESENT_NOT_ENFORCED_GLOBALLY"
    assert audit["egress_allowed"] is False
    assert facade.enroll_fixture(SCOPE)=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
    assert facade.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"

def test_deleted_guard_blocks_facade_and_audit(tmp_path):
    path=tmp_path/"ledger.db"
    facade=GuardedOfflineReservationV0(path)
    facade.initialize_fixture()
    with sqlite3.connect(path) as db:
        db.execute("DROP TRIGGER c234_reservation_binding_immutable")
    assert GuardedBoundaryAuditV0(path).inspect()["reason"]=="C239_GUARD_INCONSISTENT"
    assert facade.enroll_fixture(SCOPE)=="BLOCK:C236_GUARDS_NOT_READY"

def test_raw_sqlite_and_base_class_remain_bypassable_not_authorized(tmp_path):
    path=tmp_path/"ledger.db"
    facade=GuardedOfflineReservationV0(path)
    facade.initialize_fixture()
    # Privileged raw SQLite can insert a scope without passing the guarded facade.
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO scopes(organization,delegate,connector,capability) VALUES(?,?,?,?)",SCOPE)
    assert facade.reserve_fixture(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY)=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert GuardedBoundaryAuditV0(path).inspect()["status"]=="BLOCK"
