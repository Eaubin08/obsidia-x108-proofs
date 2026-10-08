"""C2.30 SQLite hardening audit: deny direct changes with triggers.

Triggers are defensive local fixture controls, NOT trusted append-only storage.
A database owner can drop triggers/rewrite files. No authority or egress.
"""
from __future__ import annotations
import sqlite3

class LocalWriteGuardV0:
    def __init__(self, path):
        self.path=str(path)
        if self.path==":memory:":
            raise ValueError("C230_PERSISTENT_DATABASE_REQUIRED")

    def install_fixture_triggers(self):
        with sqlite3.connect(self.path) as db:
            db.executescript("""
                CREATE TRIGGER IF NOT EXISTS c230_journal_no_update
                BEFORE UPDATE ON transition_events BEGIN
                    SELECT RAISE(ABORT,'C230_JOURNAL_UPDATE_FORBIDDEN');
                END;
                CREATE TRIGGER IF NOT EXISTS c230_journal_no_delete
                BEFORE DELETE ON transition_events BEGIN
                    SELECT RAISE(ABORT,'C230_JOURNAL_DELETE_FORBIDDEN');
                END;
                CREATE TRIGGER IF NOT EXISTS c230_reservation_no_delete
                BEFORE DELETE ON reservations BEGIN
                    SELECT RAISE(ABORT,'C230_RESERVATION_DELETE_FORBIDDEN');
                END;
                CREATE TRIGGER IF NOT EXISTS c230_receipt_no_update
                BEFORE UPDATE ON lifecycle_receipts BEGIN
                    SELECT RAISE(ABORT,'C230_RECEIPT_UPDATE_FORBIDDEN');
                END;
                CREATE TRIGGER IF NOT EXISTS c230_receipt_no_delete
                BEFORE DELETE ON lifecycle_receipts BEGIN
                    SELECT RAISE(ABORT,'C230_RECEIPT_DELETE_FORBIDDEN');
                END;
            """)
        return "LOCAL_FIXTURE_TRIGGERS_INSTALLED_NO_AUTHORITY"

    def inspect_triggers(self):
        names={"c230_journal_no_update","c230_journal_no_delete",
               "c230_reservation_no_delete","c230_receipt_no_update",
               "c230_receipt_no_delete"}
        try:
            with sqlite3.connect(self.path) as db:
                rows=db.execute("SELECT name FROM sqlite_master WHERE type='trigger'").fetchall()
        except sqlite3.Error:
            return {"status":"BLOCK","reason":"C230_DATABASE_UNAVAILABLE","egress_allowed":False}
        missing=sorted(names-{name for (name,) in rows})
        return {"status":"BLOCK","reason":"C230_TRIGGERS_MISSING" if missing
                else "C230_LOCAL_TRIGGERS_PRESENT_NOT_ATTESTED",
                "missing":missing,"egress_allowed":False}
