"""C2.38 offline guarded reservation writes, verifying triggers under BEGIN IMMEDIATE.

A local SQLite guard check is not independent attestation or execution authority.
"""
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_canonical_guard_catalog_v0 import canonical_guards_present_v0
from periphery.enterprise_sqlite_write_guard_audit_v0 import LocalWriteGuardV0
from periphery.enterprise_sqlite_state_update_guard_v0 import TRIGGER_SQL as STATE_SQL
from periphery.enterprise_sqlite_reservation_binding_guard_v0 import TRIGGER_SQL as BINDING_SQL

def _normalize(sql):
    return " ".join(sql.split()).replace(" IF NOT EXISTS "," ").rstrip(";")

CANONICAL_LEGACY_TRIGGERS = {
    name: f"CREATE TRIGGER {name} BEFORE {verb} ON {table} BEGIN SELECT RAISE(ABORT,'{message}'); END"
    for name, (table, verb, message) in {
        'c230_journal_no_update': ('transition_events','UPDATE','C230_JOURNAL_UPDATE_FORBIDDEN'),
        'c230_journal_no_delete': ('transition_events','DELETE','C230_JOURNAL_DELETE_FORBIDDEN'),
        'c230_reservation_no_delete': ('reservations','DELETE','C230_RESERVATION_DELETE_FORBIDDEN'),
        'c230_receipt_no_update': ('lifecycle_receipts','UPDATE','C230_RECEIPT_UPDATE_FORBIDDEN'),
        'c230_receipt_no_delete': ('lifecycle_receipts','DELETE','C230_RECEIPT_DELETE_FORBIDDEN'),
    }.items()
}

class TransactionGuardedReservationV0(AtomicOfflineReservationJournalV0):
    def _guard_transaction(self,db):
        return canonical_guards_present_v0(db)

    def enroll_fixture(self,scope):
        scope=self._scope(scope)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if not self._guard_transaction(db):
                db.rollback()
                return "BLOCK:C238_GUARD_INVALID"
            db.execute("INSERT OR IGNORE INTO scopes(organization,delegate,connector,capability) VALUES(?,?,?,?)",scope)
            db.commit()
        return "C238_SCOPE_ENROLLED_FIXTURE_ONLY"
