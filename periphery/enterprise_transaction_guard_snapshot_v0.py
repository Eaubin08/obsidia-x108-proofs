"""C2.37 transaction-scoped local SQLite guard checks (offline fixture only).

Uses one BEGIN IMMEDIATE connection for trigger inspection + a read-only
reservation snapshot. This is not yet an atomic authorized write path.
"""
import sqlite3
from periphery.enterprise_canonical_guard_catalog_v0 import canonical_guards_present_v0
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
            if not canonical_guards_present_v0(db):
                db.rollback();return deny("C237_REQUIRED_GUARD_MODIFIED")
            row=db.execute("SELECT status FROM reservations WHERE idempotency_key=?",(idempotency_key,)).fetchone()
            db.commit()
    except (sqlite3.Error,TypeError,ValueError):
        return deny("C237_SNAPSHOT_UNAVAILABLE")
    return deny("C237_SNAPSHOT_VERIFIED_NO_EXECUTION" if row is not None else "C237_RESERVATION_UNKNOWN")
