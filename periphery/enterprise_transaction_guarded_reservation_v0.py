"""C2.38 offline guarded reservation writes, verifying triggers under BEGIN IMMEDIATE.

A local SQLite guard check is not independent attestation or execution authority.
"""
from periphery.enterprise_atomic_reservation_journal_v0 import AtomicOfflineReservationJournalV0
from periphery.enterprise_sqlite_trigger_definition_audit_v0 import EXPECTED
from periphery.enterprise_sqlite_state_update_guard_v0 import TRIGGER_SQL as STATE_SQL
from periphery.enterprise_sqlite_reservation_binding_guard_v0 import TRIGGER_SQL as BINDING_SQL

def _normalize(sql):
    return " ".join(sql.split()).replace(" IF NOT EXISTS "," ").rstrip(";")

class TransactionGuardedReservationV0(AtomicOfflineReservationJournalV0):
    def _guard_transaction(self,db):
        catalog=dict(db.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger'").fetchall())
        for name,(table,verb,message) in EXPECTED.items():
            sql=catalog.get(name)
            if not isinstance(sql,str):
                return False
            upper=" ".join(sql.upper().split())
            if not (f"BEFORE {verb} ON {table.upper()}" in upper
                    and f"RAISE(ABORT,'{message}')" in upper):
                return False
        return all(isinstance(catalog.get(name),str) and _normalize(catalog[name])==_normalize(ref)
                   for name,ref in (
                       ("c232_state_transition_guard",STATE_SQL),
                       ("c234_reservation_binding_immutable",BINDING_SQL)))

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
