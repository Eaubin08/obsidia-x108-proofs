"""C2.41 one canonical SQLite trigger validation primitive, fixture-only."""
from periphery.enterprise_transaction_guarded_reservation_v0 import (
    CANONICAL_LEGACY_TRIGGERS, _normalize,
)
from periphery.enterprise_sqlite_state_update_guard_v0 import TRIGGER_SQL as STATE_SQL
from periphery.enterprise_sqlite_reservation_binding_guard_v0 import TRIGGER_SQL as BINDING_SQL

EXPECTED_TRIGGER_SQL = {
    **CANONICAL_LEGACY_TRIGGERS,
    "c232_state_transition_guard": STATE_SQL,
    "c234_reservation_binding_immutable": BINDING_SQL,
}

def canonical_guards_present_v0(db):
    """Use caller's existing SQLite transaction; never commit or grant authority."""
    rows=db.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger'").fetchall()
    catalog=dict(rows)
    return all(
        isinstance(catalog.get(name),str)
        and _normalize(catalog[name])==_normalize(reference)
        for name,reference in EXPECTED_TRIGGER_SQL.items()
    )
