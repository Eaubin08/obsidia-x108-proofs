"""C2.35 unified local SQLite guard installation; offline fail-closed fixture.

No provider egress or independent storage attestation.
"""
import sqlite3
from periphery.enterprise_canonical_guard_catalog_v0 import canonical_guards_present_v0
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
        try:
            with sqlite3.connect(self.path,timeout=10,isolation_level=None) as db:
                db.execute("BEGIN IMMEDIATE")
                valid=canonical_guards_present_v0(db)
                db.commit()
        except (sqlite3.Error,TypeError,ValueError):
            valid=False
        return {"status":"BLOCK","reason":("C235_LOCAL_GUARDS_PRESENT_NOT_ATTESTED" if valid
                else "C235_REQUIRED_GUARD_INVALID:CANONICAL_DEFINITION"),
                "egress_allowed":False,"execution_authority":False}

    def install_fixture(self):
        LocalWriteGuardV0(self.path).install_fixture_triggers()
        install_state_guard_fixture_v0(self.path)
        install_reservation_binding_guard_fixture_v0(self.path)
        result=self.inspect()
        if result["reason"]!="C235_LOCAL_GUARDS_PRESENT_NOT_ATTESTED":
            raise RuntimeError(result["reason"])
        return "C235_LOCAL_FIXTURE_GUARDS_INITIALIZED_NO_EXECUTION_AUTHORITY"
