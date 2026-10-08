"""C2.39 explicit local protected-boundary audit; fixture-only and deny-only.

Do not confuse Python API discipline with process isolation or DB ownership.
"""
import sqlite3
from periphery.enterprise_transaction_guarded_reservation_v0 import TransactionGuardedReservationV0
from periphery.enterprise_sqlite_trigger_definition_audit_v0 import inspect_trigger_definitions_v0
from periphery.enterprise_sqlite_state_update_guard_v0 import inspect_state_guard_fixture_v0
from periphery.enterprise_sqlite_reservation_binding_guard_v0 import inspect_reservation_binding_guard_fixture_v0

class GuardedBoundaryAuditV0:
    def __init__(self,path):
        self.path=str(path)
    def inspect(self):
        def block(reason):
            return {"status":"BLOCK","reason":reason,"execution_authority":False,"egress_allowed":False}
        checks=(
            (inspect_trigger_definitions_v0,"C231_LOCAL_TRIGGER_DEFINITIONS_MATCH_NOT_ATTESTED"),
            (inspect_state_guard_fixture_v0,"C232_LOCAL_GUARD_PRESENT_NOT_ATTESTED"),
            (inspect_reservation_binding_guard_fixture_v0,"C234_LOCAL_BINDING_GUARD_PRESENT_NOT_ATTESTED"),
        )
        try:
            with sqlite3.connect(self.path,timeout=10,isolation_level=None) as db:
                db.execute("BEGIN IMMEDIATE")
                # This fixture audit is observational; the three helper checks use
                # separate connections, therefore they are NOT an atomic attestation.
                db.commit()
            for check,expected in checks:
                if check(self.path).get("reason")!=expected:
                    return block("C239_GUARD_INCONSISTENT")
        except (sqlite3.Error,TypeError,ValueError):
            return block("C239_AUDIT_UNAVAILABLE")
        return block("C239_LOCAL_BOUNDARY_PRESENT_NOT_ENFORCED_GLOBALLY")

    @staticmethod
    def required_entrypoint_type():
        return TransactionGuardedReservationV0
