"""C2.35 unified local SQLite guard installation; offline fail-closed fixture.

No provider egress or independent storage attestation.
"""
from periphery.enterprise_sqlite_write_guard_audit_v0 import LocalWriteGuardV0
from periphery.enterprise_sqlite_trigger_definition_audit_v0 import inspect_trigger_definitions_v0
from periphery.enterprise_sqlite_state_update_guard_v0 import (
    install_state_guard_fixture_v0, inspect_state_guard_fixture_v0,
)
from periphery.enterprise_sqlite_reservation_binding_guard_v0 import (
    install_reservation_binding_guard_fixture_v0,
    inspect_reservation_binding_guard_fixture_v0,
)

class UnifiedOfflineSqliteGuardsV0:
    def __init__(self,path):
        self.path=str(path)

    def inspect(self):
        outcomes=(
            (inspect_trigger_definitions_v0(self.path),"C231_LOCAL_TRIGGER_DEFINITIONS_MATCH_NOT_ATTESTED"),
            (inspect_state_guard_fixture_v0(self.path),"C232_LOCAL_GUARD_PRESENT_NOT_ATTESTED"),
            (inspect_reservation_binding_guard_fixture_v0(self.path),"C234_LOCAL_BINDING_GUARD_PRESENT_NOT_ATTESTED"),
        )
        for outcome,expected in outcomes:
            if outcome.get("reason")!=expected:
                return {"status":"BLOCK","reason":"C235_REQUIRED_GUARD_INVALID:"+outcome.get("reason","UNKNOWN"),
                        "egress_allowed":False,"execution_authority":False}
        return {"status":"BLOCK","reason":"C235_LOCAL_GUARDS_PRESENT_NOT_ATTESTED",
                "egress_allowed":False,"execution_authority":False}

    def install_fixture(self):
        LocalWriteGuardV0(self.path).install_fixture_triggers()
        install_state_guard_fixture_v0(self.path)
        install_reservation_binding_guard_fixture_v0(self.path)
        result=self.inspect()
        if result["reason"]!="C235_LOCAL_GUARDS_PRESENT_NOT_ATTESTED":
            raise RuntimeError(result["reason"])
        return "C235_LOCAL_FIXTURE_GUARDS_INITIALIZED_NO_EXECUTION_AUTHORITY"
