"""C2.24 offline reservation lifecycle; no dispatch states or live authority."""
import hashlib
import json
import sqlite3
from periphery.enterprise_offline_atomic_reservation_ledger_v0 import OfflineReservationLedgerV0

class OfflineReservationLifecycleV0(OfflineReservationLedgerV0):
    def __init__(self,path):
        super().__init__(path)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS lifecycle_receipts(
                idempotency_key TEXT PRIMARY KEY, final_status TEXT NOT NULL,
                receipt_hash TEXT NOT NULL)""")

    def close_fixture(self, *, idempotency_key, disposition):
        if disposition not in ("CLOSED_NO_EXECUTION","ABANDONED_NO_EXECUTION"):
            return "BLOCK:C224_DISPOSITION_NOT_PERMITTED"
        if not isinstance(idempotency_key,str) or not idempotency_key:
            return "BLOCK:C224_IDEMPOTENCY_MISSING"
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT status FROM reservations WHERE idempotency_key=?",
                           (idempotency_key,)).fetchone()
            if row is None:
                db.rollback();return "BLOCK:C224_RESERVATION_UNKNOWN"
            if row[0]!="RESERVED_NO_EXECUTION":
                db.rollback();return "BLOCK:C224_ALREADY_TERMINAL_OR_REVOKED"
            digest=hashlib.sha256(json.dumps(
                {"idempotency_key":idempotency_key,"final_status":disposition},
                sort_keys=True,separators=(",",":")).encode()).hexdigest()
            db.execute("UPDATE reservations SET status=? WHERE idempotency_key=?",
                       (disposition,idempotency_key))
            db.execute("INSERT INTO lifecycle_receipts VALUES(?,?,?)",
                       (idempotency_key,disposition,digest))
            db.commit()
        return "CLOSED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"

    def receipt(self,idempotency_key):
        with self._connect() as db:
            row=db.execute("SELECT final_status,receipt_hash FROM lifecycle_receipts WHERE idempotency_key=?",
                           (idempotency_key,)).fetchone()
        return {"status":row[0],"receipt_hash":row[1]} if row else None
