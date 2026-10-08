"""C2.41 canonical SQLite trigger catalog (offline, deny-only)."""
from periphery.enterprise_sqlite_trigger_definition_audit_v0 import EXPECTED
from periphery.enterprise_sqlite_state_update_guard_v0 import TRIGGER_SQL as STATE_SQL
from periphery.enterprise_sqlite_reservation_binding_guard_v0 import TRIGGER_SQL as BINDING_SQL

def normalize_sql(sql):
    return " ".join(sql.split()).replace(" IF NOT EXISTS "," ").rstrip(";")

EXPECTED_TRIGGER_SQL={
    **{name: f"CREATE TRIGGER {name} BEFORE {verb} ON {table} BEGIN SELECT RAISE(ABORT,'{message}'); END"
       for name,(table,verb,message) in EXPECTED.items()},
    "c232_state_transition_guard":STATE_SQL,
    "c234_reservation_binding_immutable":BINDING_SQL,
}

def canonical_guards_present_v0(db):
    """Check existing caller's SQLite transaction without committing."""
    catalog=dict(db.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger'").fetchall())
    return all(isinstance(catalog.get(name),str)
               and normalize_sql(catalog[name])==normalize_sql(reference)
               for name,reference in EXPECTED_TRIGGER_SQL.items())
