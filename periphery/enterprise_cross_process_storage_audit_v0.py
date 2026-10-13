"""C2.42 local cross-process SQLite boundary check; no execution authority."""
import sqlite3
from periphery.enterprise_canonical_guard_catalog_v0 import canonical_guards_present_v0

def audit_storage_boundary_v0(path):
    def deny(reason):
        return {"status":"BLOCK","reason":reason,"egress_allowed":False,
                "execution_authority":False}
    try:
        with sqlite3.connect(str(path),timeout=1,isolation_level=None) as db:
            db.execute("PRAGMA busy_timeout=1000")
            db.execute("BEGIN IMMEDIATE")
            if not canonical_guards_present_v0(db):
                db.rollback()
                return deny("C242_GUARD_CATALOG_INVALID")
            db.commit()
    except sqlite3.Error:
        return deny("C242_STORAGE_LOCKED_OR_UNAVAILABLE")
    return deny("C242_LOCAL_GUARDS_PRESENT_NOT_PROCESS_ISOLATED")
