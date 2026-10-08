"""C2.26 read-only local reservation/receipt integrity audit.

This checks for inconsistencies, not malicious coordinated SQL rewriting.
Every verdict is BLOCK and forbids provider dispatch.
"""
from __future__ import annotations
import hashlib
import json
import sqlite3

def audit_reservation_integrity_v0(lifecycle):
    def result(reason, count=0):
        return {"status":"BLOCK","reason":reason,"records_checked":count,
                "egress_allowed":False,"execution_authority":False}
    try:
        with lifecycle._connect() as db:
            db.execute("BEGIN")
            reservations=db.execute("""SELECT r.idempotency_key,r.organization,r.delegate,
                r.connector,r.capability,r.generation,r.nonce,r.status,
                s.generation,s.revoked
                FROM reservations r LEFT JOIN scopes s
                ON s.organization=r.organization AND s.delegate=r.delegate
                AND s.connector=r.connector AND s.capability=r.capability
                ORDER BY r.idempotency_key""").fetchall()
            receipts=db.execute("SELECT idempotency_key,final_status,receipt_hash FROM lifecycle_receipts").fetchall()
            db.commit()
    except (sqlite3.Error,AttributeError,TypeError):
        return result("C226_STORAGE_UNAVAILABLE")
    receipt_map={r[0]:(r[1],r[2]) for r in receipts}
    if len(receipt_map)!=len(receipts):
        return result("C226_DUPLICATE_RECEIPT",len(reservations))
    keys=set()
    for key,org,delegate,connector,capability,gen,nonce,state,scope_gen,revoked in reservations:
        keys.add(key)
        if scope_gen is None:
            return result("C226_ORPHAN_RESERVATION",len(reservations))
        if state=="RESERVED_NO_EXECUTION" and (revoked or gen!=scope_gen):
            return result("C226_STALE_ACTIVE_RESERVATION",len(reservations))
        if state=="INVALIDATED" and not revoked:
            return result("C226_INVALIDATION_INCONSISTENT",len(reservations))
        if state in ("CLOSED_NO_EXECUTION","ABANDONED_NO_EXECUTION"):
            receipt=receipt_map.get(key)
            if receipt is None or receipt[0]!=state:
                return result("C226_RECEIPT_MISSING_OR_MISMATCHED",len(reservations))
            expected=hashlib.sha256(json.dumps(
                {"idempotency_key":key,"final_status":state},
                sort_keys=True,separators=(",",":")).encode()).hexdigest()
            if receipt[1]!=expected:
                return result("C226_RECEIPT_HASH_INVALID",len(reservations))
        elif state not in ("RESERVED_NO_EXECUTION","INVALIDATED"):
            return result("C226_UNKNOWN_TRANSITION",len(reservations))
        elif key in receipt_map:
            return result("C226_NONTERMINAL_RECEIPT",len(reservations))
    if any(key not in keys for key in receipt_map):
        return result("C226_ORPHAN_RECEIPT",len(reservations))
    return result("C226_LOCAL_INTEGRITY_CONSISTENT_NOT_ATTESTED",len(reservations))
