"""C2.25 read-only recovery audit of reservation and receipt consistency.

Unknown, still reserved, revoked, and corrupt records never imply execution.
No automatic replay, renewal, dispatch or mutation during recovery inspection.
"""
from __future__ import annotations
import hashlib
import json

def inspect_reservation_recovery_v0(*, lifecycle, idempotency_key):
    def block(reason):
        return {"status":"BLOCK","reason":reason,"egress_allowed":False,
                "execution_authority":False,"automatic_retry":False}
    if not isinstance(idempotency_key,str) or not idempotency_key:
        return block("C225_INVALID_IDEMPOTENCY_KEY")
    try:
        state=lifecycle.inspect(idempotency_key)
        receipt=lifecycle.receipt(idempotency_key)
    except Exception:
        return block("C225_RECOVERY_STORAGE_UNAVAILABLE")
    if state=="UNKNOWN":
        return block("C225_RESERVATION_UNKNOWN")
    if state=="RESERVED_NO_EXECUTION":
        return block("C225_UNFINISHED_REQUIRES_MANUAL_REVIEW")
    if state=="INVALIDATED":
        return block("C225_REVOKED_OR_INVALIDATED")
    if state not in ("CLOSED_NO_EXECUTION","ABANDONED_NO_EXECUTION"):
        return block("C225_STATE_UNKNOWN")
    if not isinstance(receipt,dict) or receipt.get("status")!=state:
        return block("C225_RECEIPT_MISSING_OR_MISMATCHED")
    expected=hashlib.sha256(json.dumps(
        {"idempotency_key":idempotency_key,"final_status":state},
        sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if receipt.get("receipt_hash")!=expected:
        return block("C225_RECEIPT_HASH_INVALID")
    return block("C225_CLOSED_NO_EXECUTION_RECEIPT_VERIFIED")
