"""C2.34 — local SQLite immutable reservation binding guard (fixture only).

Forbids UPDATE of original request binding fields; does not grant authority.
A privileged database owner can drop triggers or rewrite storage directly.
"""
import sqlite3

BINDING_FIELDS=(
    "idempotency_key","organization","delegate","connector",
    "capability","generation","nonce",
)
TRIGGER_SQL="""CREATE TRIGGER IF NOT EXISTS c234_reservation_binding_immutable
BEFORE UPDATE OF idempotency_key, organization, delegate, connector,
capability, generation, nonce ON reservations
BEGIN
 SELECT RAISE(ABORT,'C234_RESERVATION_BINDING_IMMUTABLE');
END;"""

def _normalized(sql):
    return " ".join(sql.split()).replace(" IF NOT EXISTS "," ")

def install_reservation_binding_guard_fixture_v0(path):
    with sqlite3.connect(str(path)) as db:
        db.execute(TRIGGER_SQL)
    return "C234_LOCAL_BINDING_GUARD_INSTALLED_NO_EXECUTION_AUTHORITY"

def inspect_reservation_binding_guard_fixture_v0(path):
    result={"status":"BLOCK","egress_allowed":False,"execution_authority":False}
    try:
        with sqlite3.connect(str(path)) as db:
            row=db.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND name='c234_reservation_binding_immutable'").fetchone()
    except sqlite3.Error:
        return {**result,"reason":"C234_STORAGE_UNAVAILABLE"}
    if not row or not isinstance(row[0],str) or _normalized(row[0])!=_normalized(TRIGGER_SQL):
        return {**result,"reason":"C234_BINDING_GUARD_MISSING_OR_MODIFIED"}
    return {**result,"reason":"C234_LOCAL_BINDING_GUARD_PRESENT_NOT_ATTESTED"}
