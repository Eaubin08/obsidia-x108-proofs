"""C2.45 recover ambiguous IPC reserve outcomes without automatic retries.

Read-only reconciliation by idempotency key. A matching local reservation does
NOT prove receipt by an external system or grant execution authority.
"""
from periphery.enterprise_offline_storage_service_boundary_v0 import OfflineStorageServiceV0

def reconcile_ambiguous_reservation_fixture_v0(path, *, idempotency_key):
    def block(reason):
        return {"status":"BLOCK","reason":reason,"automatic_retry":False,
                "egress_allowed":False,"execution_authority":False}
    if not isinstance(idempotency_key,str) or len(idempotency_key)<16:
        return block("C245_INVALID_KEY")
    try:
        service=OfflineStorageServiceV0(path)
        state=service.request_fixture("inspect",{"idempotency_key":idempotency_key})
    except Exception:
        return block("C245_RECONCILIATION_UNAVAILABLE")
    if state=="RESERVED_NO_EXECUTION":
        return block("C245_RESERVATION_FOUND_NO_EXECUTION")
    if state in ("CLOSED_NO_EXECUTION","ABANDONED_NO_EXECUTION","INVALIDATED"):
        return block("C245_TERMINAL_NO_EXECUTION:"+state)
    if state=="UNKNOWN":
        return block("C245_RESERVATION_NOT_FOUND_NO_AUTO_RETRY")
    return block("C245_STORAGE_GUARD_OR_STATE_UNAVAILABLE")
