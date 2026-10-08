"""C2.37 transaction-scoped local SQLite guard checks (offline fixture only).

Uses one BEGIN IMMEDIATE connection for trigger inspection + a read-only
reservation snapshot. This is not yet an atomic authorized write path.
"""
import sqlite3
from periphery.enterprise_sqlite_trigger_definition_audit_v0 import EXPECTED
from periphery.enterprise_sqlite_state_update_guard_v0 import TRIGGER_SQL as STATE_SQL
from periphery.enterprise_sqlite_reservation_binding_guard_v0 import TRIGGER_SQL as BINDING_SQL

def _normalize(value):
    return " ".join(value.split()).replace(" IF NOT EXISTS "," ").rstrip(";")

def inspect_guarded_snapshot_v0(path, idempotency_key):
    def deny(reason):
        return {"status":"BLOCK","reason":reason,"egress_allowed":False,
                "execution_authority":False}
    try:
        with sqlite3.connect(str(path),timeout=10,isolation_level=None) as db:
            db.execute("PRAGMA busy_timeout=10000")
            db.execute("BEGIN IMMEDIATE")
            catalog=dict(db.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger'").fetchall())
            for name,(table,verb,message) in EXPECTED.items():
                sql=catalog.get(name)
                if not isinstance(sql,str):
                    db.rollback();return deny("C237_LEGACY_GUARD_MISSING")
                uppercase=" ".join(sql.upper().split())
                if not (f"BEFORE {verb} ON {table.upper()}" in uppercase
                        and f"RAISE(ABORT,'{message}')" in uppercase):
                    db.rollback();return deny("C237_LEGACY_GUARD_MODIFIED")
            for name,reference in (
                ("c232_state_transition_guard",STATE_SQL),
                ("c234_reservation_binding_immutable",BINDING_SQL),
            ):
                if name not in catalog or _normalize(catalog[name])!=_normalize(reference):
                    db.rollback();return deny("C237_REQUIRED_GUARD_MODIFIED")
            row=db.execute("SELECT status FROM reservations WHERE idempotency_key=?",(idempotency_key,)).fetchone()
            db.commit()
    except (sqlite3.Error,TypeError,ValueError):
        return deny("C237_SNAPSHOT_UNAVAILABLE")
    return deny("C237_SNAPSHOT_VERIFIED_NO_EXECUTION" if row is not None else "C237_RESERVATION_UNKNOWN")
