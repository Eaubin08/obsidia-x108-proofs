"""C2.7 negative tests never treat canonical record checking as a permission."""
from periphery.enterprise_world_action_kx108_record_boundary_v0 import (
    inspect_world_action_kx108_record_v0,
)

BINDING = {
    "world_action_request_hash": "a"*64,
    "connector_call_hash": "b"*64,
    "human_approval_hash": "c"*64,
    "target_prestate_hash": "d"*64,
    "required_scope": "calendar:write",
    "idempotency_key": "test-idempotency-1",
    "source_domain": "administration",
    "action_id": "action-test-1",
}


def inspect(record, expected=None):
    return inspect_world_action_kx108_record_v0(
        record=record, expected_binding=BINDING if expected is None else expected
    )


def test_missing_record_refused():
    assert inspect(None)["reason"] == "C27_RECORD_MISSING"


def test_missing_expected_binding_refused():
    assert inspect({}, expected={})["reason"] == "C27_EXPECTED_BINDING_INCOMPLETE"


def test_wrong_phase_refused():
    assert inspect({"decision_phase": "POST_EXECUTION"})["reason"] == "C27_WRONG_DECISION_PHASE"


def test_mismatched_action_binding_refused():
    record = dict(BINDING, decision_phase="WORLD_ACTION_PRE_EXECUTION")
    record["action_id"] = "other-action"
    assert inspect(record)["reason"] == "C27_WORLD_ACTION_BINDING_MISMATCH"


def test_forged_allow_record_cannot_bypass_canonical_verifier():
    record = dict(BINDING, decision_phase="WORLD_ACTION_PRE_EXECUTION",
                  x108_gate="ALLOW", decision_authority="KX108_ONLY")
    result = inspect(record)
    assert result["status"] == "BLOCK"
    assert result["reason"] == "C27_CANONICAL_RECORD_NOT_VERIFIED"
    assert result["execution_authority"] is False
