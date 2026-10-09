"""End-to-end CSSA synthetic deadline to KX108-gated native work."""
from periphery.cssa_native_lot_a_bridge_v0 import run_cssa_native_lot_a


def deadline(**overrides):
    return dict({
        "id": "licence", "kind": "DEADLINE", "owner": "manager",
        "slot": "2026-10-20T16:00:00+00:00",
        "source_ref": "cssa:fiction:licence",
        "regulatory_basis_proven": True,
        "due_at": "2026-10-20T16:00:00+00:00",
    }, **overrides)


def test_real_native_state_projection_in_isolated_sandbox(tmp_path):
    result = run_cssa_native_lot_a(
        [deadline()], root=tmp_path / "isolated", simulate_operator_approval=True)
    assert result["status"] == "SANDBOX_NATIVE_WORK_COMMITTED_ACTION_NOT_EXECUTED"
    assert result["native_result"]["canonical_mutation_count"] == 4
    assert result["cases"][0]["action_candidate"] is True
    assert result["cases"][0]["projection_status"] == "ACTION_CANDIDATE"
    assert len(result["cases"][0]["projection_hash"]) == 64
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["native_writes_scope"] == "ISOLATED_TEST_ROOT_ONLY"
    assert result["real_external_effect"] is False
    assert result["external_actions"] == []


def test_without_synthetic_operator_approval_does_not_create_store(tmp_path):
    root = tmp_path / "unused"
    result = run_cssa_native_lot_a([deadline()], root=root)
    assert result["status"] == "HOLD"
    assert result["native_writes"] is False
    assert not root.exists()


def test_conflicting_cssa_event_blocks_before_native_store(tmp_path):
    root = tmp_path / "blocked"
    result = run_cssa_native_lot_a(
        [deadline(contradicted=True)], root=root,
        simulate_operator_approval=True)
    assert result["status"] == "BLOCK"
    assert not root.exists()


def test_unknown_regulatory_basis_does_not_create_store(tmp_path):
    root = tmp_path / "blocked"
    result = run_cssa_native_lot_a(
        [deadline(regulatory_basis_proven=False)], root=root,
        simulate_operator_approval=True)
    assert result["status"] == "BLOCK"
    assert not root.exists()


def test_missing_structured_date_holds(tmp_path):
    root = tmp_path / "blocked"
    result = run_cssa_native_lot_a(
        [deadline(due_at=None)], root=root,
        simulate_operator_approval=True)
    assert result["status"] == "HOLD"
    assert not root.exists()
