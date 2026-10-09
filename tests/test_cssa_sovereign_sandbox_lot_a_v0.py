"""CSSA Lot A governed sandbox E2E — CSSA-origin action, not enterprise-only fixture."""
from periphery.cssa_sovereign_sandbox_lot_a_v0 import (
    run_cssa_sovereign_sandbox_lot_a,
)


def deadline(**overrides):
    return dict({
        "id": "licence",
        "kind": "DEADLINE",
        "owner": "manager",
        "slot": "2026-10-20T16:00:00+00:00",
        "source_ref": "cssa:fiction:licence",
        "regulatory_basis_proven": True,
        "due_at": "2026-10-20T16:00:00+00:00",
    }, **overrides)


def test_cssa_origin_action_traverses_real_sandbox_governance_and_replay(tmp_path):
    result = run_cssa_sovereign_sandbox_lot_a(
        [deadline()], root=tmp_path / "cssa", simulate_operator_approval=True,
    )
    assert result["status"] == "CSSA_LOT_A_SANDBOX_E2E_PROVEN"
    assert result["intake_mutations"] == 4
    assert result["cssa_source_case_id"].startswith("cssa-case-")
    assert result["cssa_source_task_id"].startswith("cssa-task-")
    assert result["cssa_source_followup_id"].startswith("cssa-followup-")
    assert result["cssa_action_executed"] is True
    assert result["real_operator_approval"] is False
    assert result["sandbox_operator_approval_simulated"] is True
    execution = result["execution"]
    assert execution["kx108_gate"] == "ALLOW"
    assert execution["execution_status"] == "SANDBOX_EXECUTED_RECEIPT_STORED"
    assert execution["execution_replay_ok"] is True
    assert execution["duplicate_status"] == "BLOCKED"
    assert execution["duplicate_adapter_called"] is False
    assert execution["adapter_call_count"] == 1
    for name in ("projection_hash", "request_hash", "approval_hash",
                 "sovereign_ticket_hash", "execution_receipt_hash"):
        assert len(execution[name]) == 64
    assert result["network_call_performed"] is False
    assert result["real_external_effect"] is False
    assert result["external_actions"] == []


def test_no_approval_no_native_or_sandbox_effect(tmp_path):
    root = tmp_path / "cssa"
    result = run_cssa_sovereign_sandbox_lot_a([deadline()], root=root)
    assert result["status"] == "HOLD"
    assert result["cssa_action_executed"] is False
    assert not root.exists()


def test_cssa_conflict_blocks_before_sovereign_runtime(tmp_path):
    root = tmp_path / "cssa"
    result = run_cssa_sovereign_sandbox_lot_a(
        [deadline(contradicted=True)], root=root,
        simulate_operator_approval=True,
    )
    assert result["status"] == "BLOCK"
    assert result["cssa_action_executed"] is False
    assert not root.exists()


def test_unknown_regulatory_basis_fails_closed(tmp_path):
    result = run_cssa_sovereign_sandbox_lot_a(
        [deadline(regulatory_basis_proven=False)],
        root=tmp_path / "blocked", simulate_operator_approval=True,
    )
    assert result["status"] == "BLOCK"
    assert result["real_external_effect"] is False
