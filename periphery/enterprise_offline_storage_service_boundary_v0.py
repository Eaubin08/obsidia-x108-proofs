"""C2.43 offline storage service boundary simulation, deny-only.

The business facade does not expose a database path, SQL handle, or execution.
This is a Python capability wrapper, NOT OS/process isolation.
"""
from periphery.enterprise_guarded_offline_reservation_v0 import GuardedOfflineReservationV0

class OfflineStorageServiceV0:
    def __init__(self, db_path):
        self._backend=GuardedOfflineReservationV0(db_path)

    def initialize_fixture(self):
        return self._backend.initialize_fixture()

    def request_fixture(self, operation, payload):
        if not isinstance(payload,dict):
            return "BLOCK:C243_INVALID_PAYLOAD"
        if operation=="enroll":
            if set(payload)!={"scope"}: return "BLOCK:C243_FIELDS_DENIED"
            return self._backend.enroll_fixture(payload["scope"])
        if operation=="reserve":
            if set(payload)!={"scope","generation","nonce","idempotency_key"}:
                return "BLOCK:C243_FIELDS_DENIED"
            return self._backend.reserve_fixture(**payload)
        if operation=="close":
            if set(payload)!={"idempotency_key","disposition"}:
                return "BLOCK:C243_FIELDS_DENIED"
            return self._backend.close_fixture(**payload)
        if operation=="revoke":
            if set(payload)!={"scope"}: return "BLOCK:C243_FIELDS_DENIED"
            return self._backend.revoke_fixture(payload["scope"])
        if operation=="inspect":
            if set(payload)!={"idempotency_key"}: return "BLOCK:C243_FIELDS_DENIED"
            return self._backend.inspect_fixture(payload["idempotency_key"])
        return "BLOCK:C243_OPERATION_DENIED"
