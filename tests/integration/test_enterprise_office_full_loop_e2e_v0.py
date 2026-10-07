from pathlib import Path

from periphery.native_sources.enterprise_office_full_loop_e2e_v0 import (
    run_enterprise_office_full_loop_e2e_v0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    materialize_enterprise_source_sandbox_v0,
)
import periphery.native_sources.enterprise_office_full_loop_e2e_v0 as full_loop_module
import inspect


def run_loop(tmp_path: Path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    return run_enterprise_office_full_loop_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
        execution_root=tmp_path / "execution",
    )


def test_full_loop_closes_source_to_sandbox_execution_chain(tmp_path):
    result = run_loop(tmp_path)

    assert result["status"] == "ENTERPRISE_OFFICE_FULL_LOOP_E2E_V0_PROVEN"
    assert result["truth_manifest_used_for_routing"] is False

    assert result["source_observation_count"] == 12
    assert result["source_packet_count"] == 12
    assert result["interpretation_candidate_count"] == 12
    assert result["intake_policy_instruction_count"] == 12

    assert result["committed_case_count"] == 3
    assert result["canonical_mutation_count"] == 12
    assert result["work_projection_count"] == 3
    assert result["action_candidate_count"] == 2
    assert result["no_action_count"] == 1

    assert result["sandbox_execution_count"] == 2
    assert result["execution_receipt_count"] == 2
    assert result["execution_replay_ok_count"] == 2
    assert result["duplicate_execution_block_count"] == 2

    assert result["network_call_performed"] is False
    assert result["real_external_effect"] is False
    assert result["decision_authority"] == "KX108_ONLY"


def test_full_loop_preserves_upstream_hold_block_info_and_duplicate_counts(tmp_path):
    result = run_loop(tmp_path)

    assert result["hold_count"] == 1
    assert result["block_count"] == 1
    assert result["information_only_count"] == 2
    assert result["duplicate_suppressed_count"] == 1


def test_two_projected_calendar_actions_reach_executor_and_receipts(tmp_path):
    result = run_loop(tmp_path)

    assert set(result["executions"]) == {
        "contract-renewal.md",
        "mail-action-001",
    }

    for execution in result["executions"].values():
        assert execution["kx108_gate"] == "ALLOW"
        assert execution["execution_status"] == "SANDBOX_EXECUTED_RECEIPT_STORED"
        assert execution["execution_replay_ok"] is True
        assert execution["adapter_call_count"] == 1
        assert execution["duplicate_status"] == "BLOCKED"
        assert execution["duplicate_reason"] == "DUPLICATE_CONFIRMED_EXECUTION_BLOCK"
        assert execution["duplicate_adapter_called"] is False
        assert execution["network_call_performed"] is False
        assert execution["real_external_effect"] is False
        assert len(execution["projection_hash"]) == 64
        assert len(execution["request_hash"]) == 64
        assert len(execution["approval_hash"]) == 64
        assert len(execution["decision_record_hash"]) == 64
        assert len(execution["activation_policy_hash"]) == 64
        assert len(execution["sovereign_ticket_hash"]) == 64
        assert len(execution["execution_receipt_hash"]) == 64


def test_full_loop_is_deterministic_across_clean_roots(tmp_path):
    first = run_loop(tmp_path / "first")
    second = run_loop(tmp_path / "second")

    assert first["result_hash"] == second["result_hash"]
    assert first["projection_hashes"] == second["projection_hashes"]
    assert first["execution_receipt_hashes"] == second["execution_receipt_hashes"]

    for item_id in first["executions"]:
        a = first["executions"][item_id]
        b = second["executions"][item_id]
        assert a["projection_hash"] == b["projection_hash"]
        assert a["request_hash"] == b["request_hash"]
        assert a["approval_hash"] == b["approval_hash"]
        assert a["decision_record_hash"] == b["decision_record_hash"]
        assert a["activation_policy_hash"] == b["activation_policy_hash"]
        assert a["sovereign_ticket_hash"] == b["sovereign_ticket_hash"]
        assert a["execution_receipt_hash"] == b["execution_receipt_hash"]


def test_full_loop_runner_does_not_bind_real_provider_or_network():
    source = inspect.getsource(full_loop_module)

    assert "GoogleCalendar" not in source
    assert "Gmail" not in source
    assert "REAL_NETWORK" not in source
    assert 'external_network_capable: bool = False' in source
    assert 'side_effect_free: bool = True' in source
    assert 'execution_mode: str = "SANDBOX_DETERMINISTIC"' in source
    assert "real_external_effect" in source
