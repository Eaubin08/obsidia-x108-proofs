"""C2.31 local structural SQLite trigger SQL inspection, always fail-closed.

A trusted local reference to the expected SQL is still not an external anchor.
This audit detects missing or modified trigger bodies, not privileged rewrites.
"""
import re
import sqlite3

EXPECTED = {
    "c230_journal_no_update": ("transition_events","UPDATE","C230_JOURNAL_UPDATE_FORBIDDEN"),
    "c230_journal_no_delete": ("transition_events","DELETE","C230_JOURNAL_DELETE_FORBIDDEN"),
    "c230_reservation_no_delete": ("reservations","DELETE","C230_RESERVATION_DELETE_FORBIDDEN"),
    "c230_receipt_no_update": ("lifecycle_receipts","UPDATE","C230_RECEIPT_UPDATE_FORBIDDEN"),
    "c230_receipt_no_delete": ("lifecycle_receipts","DELETE","C230_RECEIPT_DELETE_FORBIDDEN"),
}
def inspect_trigger_definitions_v0(database_path):
    def block(reason):
        return {"status":"BLOCK","reason":reason,"egress_allowed":False,
                "execution_authority":False}
    try:
        with sqlite3.connect(str(database_path)) as db:
            rows=dict(db.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger'").fetchall())
    except sqlite3.Error:
        return block("C231_TRIGGER_CATALOG_UNAVAILABLE")
    for name,(table,verb,message) in EXPECTED.items():
        sql=rows.get(name)
        if not isinstance(sql,str):
            return block("C231_REQUIRED_TRIGGER_MISSING")
        normalized=" ".join(sql.upper().split())
        if (not re.search(r"BEFORE\s+"+verb+r"\s+ON\s+"+table.upper()+r"\b",normalized)
            or "RAISE(ABORT,'"+message+"')" not in normalized
            or "BEGIN" not in normalized or "END" not in normalized):
            return block("C231_TRIGGER_DEFINITION_DRIFT")
    return block("C231_LOCAL_TRIGGER_DEFINITIONS_MATCH_NOT_ATTESTED")
