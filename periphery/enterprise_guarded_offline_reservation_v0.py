"""C2.36 fail-closed guarded entrypoint for offline reservation fixture.

This is an opt-in façade, not a replacement for independent trust/permissions.
"""
from periphery.enterprise_transaction_guarded_reservation_v0 import TransactionGuardedReservationV0
from periphery.enterprise_unified_sqlite_guards_v0 import UnifiedOfflineSqliteGuardsV0

class GuardedOfflineReservationV0:
    def __init__(self,path):
        self._ledger=TransactionGuardedReservationV0(path)
        self._guards=UnifiedOfflineSqliteGuardsV0(path)

    def initialize_fixture(self):
        return self._guards.install_fixture()

    def _ready(self):
        try:
            return self._guards.inspect().get("reason")=="C235_LOCAL_GUARDS_PRESENT_NOT_ATTESTED"
        except Exception:
            return False

    def enroll_fixture(self,scope):
        if not self._ready():
            return "BLOCK:C236_GUARDS_NOT_READY"
        outcome=self._ledger.enroll_fixture(scope)
        return "C236_SCOPE_ENROLLED_FIXTURE_ONLY" if outcome=="C238_SCOPE_ENROLLED_FIXTURE_ONLY" else outcome

    def reserve_fixture(self,*,scope,generation,nonce,idempotency_key):
        if not self._ready():
            return "BLOCK:C236_GUARDS_NOT_READY"
        return self._ledger.reserve_fixture(scope=scope,generation=generation,
            nonce=nonce,idempotency_key=idempotency_key)

    def close_fixture(self,*,idempotency_key,disposition):
        if not self._ready():
            return "BLOCK:C236_GUARDS_NOT_READY"
        return self._ledger.close_fixture(idempotency_key=idempotency_key,
                                          disposition=disposition)

    def revoke_fixture(self,scope):
        if not self._ready():
            return "BLOCK:C236_GUARDS_NOT_READY"
        return self._ledger.revoke(scope)

    def inspect_fixture(self,idempotency_key):
        if not self._ready():
            return "BLOCK:C236_GUARDS_NOT_READY"
        return self._ledger.inspect(idempotency_key)
