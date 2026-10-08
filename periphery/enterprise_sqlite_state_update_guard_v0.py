"""C2.32 local reservation UPDATE guard, not trusted storage.

Only permits recorded RESERVED_NO_EXECUTION -> no-execution terminal transitions
if the latest local journal event matches. Database owners can forge events or
drop triggers; this is not independent cryptographic authorization.
"""
import sqlite3

TRIGGER_SQL = """
CREATE TRIGGER IF NOT EXISTS c232_state_transition_guard
BEFORE UPDATE OF status ON reservations
BEGIN
 SELECT CASE WHEN NOT (
   OLD.status = 'RESERVED_NO_EXECUTION'
   AND NEW.status IN ('CLOSED_NO_EXECUTION','ABANDONED_NO_EXECUTION','INVALIDATED')
   AND NEW.idempotency_key = OLD.idempotency_key
   AND EXISTS (
      SELECT 1 FROM transition_events e
      WHERE e.idempotency_key = OLD.idempotency_key
        AND e.event_kind = NEW.status
        AND e.sequence = (SELECT MAX(sequence) FROM transition_events)
   )
 ) THEN RAISE(ABORT,'C232_UNJOURNALED_STATE_UPDATE') END;
END;
"""

def install_state_guard_fixture_v0(path):
    with sqlite3.connect(str(path)) as db:
        db.execute(TRIGGER_SQL)
    return "C232_LOCAL_GUARD_INSTALLED_NO_EXECUTION_AUTHORITY"

def inspect_state_guard_fixture_v0(path):
    with sqlite3.connect(str(path)) as db:
        row=db.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND name='c232_state_transition_guard'").fetchone()
    return {"status":"BLOCK","reason":("C232_LOCAL_GUARD_PRESENT_NOT_ATTESTED" if row and row[0] and row[0].strip()==TRIGGER_SQL.strip() else "C232_GUARD_MISSING_OR_MODIFIED"),"egress_allowed":False}
