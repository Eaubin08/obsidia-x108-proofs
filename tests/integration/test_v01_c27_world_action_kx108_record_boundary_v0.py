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


def test_real_world_action_pipeline_stored_allow_is_bound_but_no_egress(tmp_path):
    """Use the existing pipeline fixture; never synthesize an ALLOW record."""
    import importlib.util
    from pathlib import Path
    from scripts import obsidia_kx108_decision_store as store

    fixture_path = Path(__file__).with_name("test_world_action_pre_execution_v0.py")
    spec = importlib.util.spec_from_file_location("existing_world_action_fixture_c27", fixture_path)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)

    request = fixture.build_request()
    result = fixture.run(tmp_path, request)
    assert result.x108_gate == "ALLOW"
    assert result.egress_allowed is False

    record = store.load_kx108_decision_record(
        result.decision_record_id, tmp_path / "decisions"
    )
    assert store.verify_kx108_decision_record(record) == (True, None)
    expected = {
        key: record[key]
        for key in BINDING
    }
    checked = inspect_world_action_kx108_record_v0(
        record=record, expected_binding=expected
    )
    assert checked["status"] == "VERIFIED_RECORD_ONLY_NO_EXECUTION_AUTHORITY"
    assert checked["egress_allowed"] is False
    assert checked["execution_authority"] is False

    tampered = dict(record)
    tampered["world_action_request_hash"] = "f" * 64
    assert inspect_world_action_kx108_record_v0(
        record=tampered, expected_binding=expected
    )["status"] == "BLOCK"


def test_real_world_action_pipeline_hold_and_block_never_escalate(tmp_path):
    import importlib.util
    from pathlib import Path
    from scripts import obsidia_kx108_decision_store as store

    fixture_path = Path(__file__).with_name("test_world_action_pre_execution_v0.py")
    spec = importlib.util.spec_from_file_location("existing_world_action_fixture_negative_c27", fixture_path)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)

    for gate, extras in (
        ("HOLD", {"unknowns": ("RECIPIENT_SCOPE_UNKNOWN", "FACT_FRESHNESS_UNKNOWN")}),
        ("BLOCK", {"contradictions": ("TARGET_CONFLICT", "AUTHORITY_CONFLICT")}),
    ):
        root = tmp_path / gate.lower()
        result = fixture.run(root, **extras)
        assert result.x108_gate == gate
        record = store.load_kx108_decision_record(
            result.decision_record_id, root / "decisions"
        )
        expected = {key: record[key] for key in BINDING}
        checked = inspect_world_action_kx108_record_v0(
            record=record, expected_binding=expected
        )
        assert checked["status"] == "BLOCK"
        assert checked["reason"] == "C27_SOVEREIGN_GATE_NOT_ALLOW"
