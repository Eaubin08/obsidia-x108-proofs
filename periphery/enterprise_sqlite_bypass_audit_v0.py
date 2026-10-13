"""C2.33 local SQLite bypass detector — no independent attestation or egress.

Detects unlogged column edits and journal/state drift; explicitly cannot
prevent a privileged writer from rewriting the entire DB and trigger catalog.
"""
from __future__ import annotations
from periphery.enterprise_sqlite_trigger_definition_audit_v0 import inspect_trigger_definitions_v0
from periphery.enterprise_sqlite_state_update_guard_v0 import inspect_state_guard_fixture_v0

def inspect_sqlite_bypass_v0(*, ledger):
    def block(reason):
        return {"status":"BLOCK","reason":reason,"egress_allowed":False,
                "execution_authority":False}
    try:
        triggers=inspect_trigger_definitions_v0(ledger.path)
        if triggers["reason"]!="C231_LOCAL_TRIGGER_DEFINITIONS_MATCH_NOT_ATTESTED":
            return block("C233_LEGACY_TRIGGER_INVALID:"+triggers["reason"])
        state_guard=inspect_state_guard_fixture_v0(ledger.path)
        if state_guard["reason"]!="C232_LOCAL_GUARD_PRESENT_NOT_ATTESTED":
            return block("C233_STATE_GUARD_INVALID:"+state_guard["reason"])
        chain=ledger.verify_logged_fixture()
    except Exception:
        return block("C233_AUDIT_UNAVAILABLE")
    if chain!="BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED":
        return block("C233_JOURNAL_STATE_DRIFT:"+chain)
    return block("C233_LOCAL_CONTROLS_CONSISTENT_NOT_INDEPENDENTLY_ATTESTED")
