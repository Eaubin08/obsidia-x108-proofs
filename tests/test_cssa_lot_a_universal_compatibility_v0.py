"""CSSA Lot A: integration with existing universal digital twin (not CSSA apply)."""
import pytest

from periphery.cssa_lot_a_universal_compatibility_v0 import (
    run_cssa_lot_a_compatibility,
)


def event(name, *, kind="MATCH", **overrides):
    return dict({
        "id": name, "kind": kind, "slot": "2026-10-20T18:00:00+02:00",
        "owner": "operations", "source_ref": "synthetic:" + name,
    }, **overrides)


def test_cssa_campaign_and_real_universal_baseline_run_together(tmp_path):
    result = run_cssa_lot_a_compatibility(tmp_path / "isolated", [
        event("match", resource="stadium"),
        event("double_booking", resource="stadium"),
        event("deadline", kind="DEADLINE", regulatory_basis_proven=False),
        event("publication", kind="COMMUNICATION", publication_facts_proven=False),
    ])
    assert result["cssa_case_count"] == 4
    assert result["cssa_blocked"] >= 3
    assert result["status"] == "COMPATIBLE_COMPONENTS_BRIDGE_UNPROVEN"
    assert result["cssa_to_native_work_bound"] is False
    assert result["cssa_kx108_decision"] is None
    assert result["cssa_external_actions"] == []
    assert result["universal_enterprise_sandbox_executions"] == 2
    assert result["universal_receipts_replayed"] == 2
    assert result["network_call_performed"] is False
    assert result["real_external_effect"] is False


def test_requires_empty_isolated_root(tmp_path):
    root = tmp_path / "sandbox"
    root.mkdir()
    (root / "existing.txt").write_text("do not overwrite", encoding="utf-8")
    with pytest.raises(ValueError, match="CSSA_LOT_A_ROOT_MUST_BE_EMPTY"):
        run_cssa_lot_a_compatibility(root, [event("match")])


def test_cssa_fail_closed_before_universal_fixture_materialization(tmp_path):
    root = tmp_path / "sandbox"
    with pytest.raises(ValueError, match="CSSA_A_EVENT_IDENTITY_OR_SHAPE_INVALID"):
        run_cssa_lot_a_compatibility(root, [event("same"), event("same")])
    assert not (root / "enterprise").exists()
