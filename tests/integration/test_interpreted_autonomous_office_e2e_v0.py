import inspect

from periphery.native_ops.common_v0 import NativeEntityStoreV0
from periphery.native_ops.crm_native_v0 import DOMAIN_ID as CRM_DOMAIN, KIND_RECORD
from periphery.native_ops.tasks_native_v0 import DOMAIN_ID as TASK_DOMAIN, ENTITY_KIND as TASK_KIND
from periphery.native_sources.enterprise_office_interpreted_e2e_v0 import (
    STATUS,
    run_interpreted_autonomous_office_e2e_v0,
)
import periphery.native_sources.enterprise_office_interpreted_e2e_v0 as interpreted_runner_module
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    load_enterprise_sandbox_truth_v0,
    materialize_enterprise_source_sandbox_v0,
)


def run(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    result = run_interpreted_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )
    return paths, result


def test_interpreted_e2e_matches_sandbox_oracle_without_using_it_for_routing(tmp_path):
    paths, result = run(tmp_path)
    truth = load_enterprise_sandbox_truth_v0(paths)
    expected = truth["expected_global"]

    assert result["status"] == STATUS
    assert result["truth_manifest_used_for_routing"] is False
    assert result["interpretation_candidate_count"] == 12
    assert result["intake_policy_instruction_count"] == 12
    assert len(result["intake_policy_batch_hash"]) == 64
    assert result["source_observation_count"] == 12
    assert result["source_packet_count"] == 12

    assert result["committed_case_count"] == expected["unique_actionable_cases"]
    assert result["canonical_mutation_count"] == 12
    assert result["duplicate_suppressed_count"] == expected["duplicate_groups"]
    assert result["hold_count"] == expected["hold_groups"]
    assert result["block_count"] == expected["block_groups"]
    assert result["information_only_count"] == expected["information_only_items"]
    assert result["external_action"] is expected["external_mutation"]
    assert result["network_call_performed"] is False
    assert result["decision_authority"] == expected["decision_authority"]


def test_interpreted_e2e_expected_work_paths(tmp_path):
    _, result = run(tmp_path)
    results = result["results"]

    assert results["mail-action-001"]["status"] == "NATIVE_INTAKE_COMMITTED"
    assert results["mail-incident-001"]["status"] == "NATIVE_INTAKE_COMMITTED"
    assert results["contract-renewal.md"]["status"] == "NATIVE_INTAKE_COMMITTED"

    assert results["mail-action-001-duplicate"]["status"] == "DUPLICATE_SUPPRESSED"
    assert results["mail-missing-evidence-001"]["status"] == "NATIVE_INTAKE_GATED_NO_MUTATION"
    assert results["mail-missing-evidence-001"]["gate"] == "HOLD"

    conflict = results["supplier-order:SO-77"]
    assert conflict["status"] == "NATIVE_INTAKE_GATED_NO_MUTATION"
    assert conflict["gate"] == "BLOCK"

    assert results["mail-info-001"]["status"] == "NO_WORK_INFORMATION_ONLY"
    assert results["policy-info.md"]["status"] == "NO_WORK_INFORMATION_ONLY"
    assert results["supplier-terms.md"]["status"] == "CONTEXT_ONLY_SUPPORTING_CONSTRAINT"
    assert results["event-routine-001"]["status"] == "ROUTINE_CALENDAR_CONTEXT_ONLY"
    assert results["event-deadline-001"]["status"] == "EXISTING_CALENDAR_CONTEXT_ONLY"


def test_interpreted_e2e_commits_exactly_three_cases_and_tasks(tmp_path):
    _, result = run(tmp_path)
    store = NativeEntityStoreV0(tmp_path / "native")

    crm_root = tmp_path / "native" / CRM_DOMAIN / KIND_RECORD
    task_root = tmp_path / "native" / TASK_DOMAIN / TASK_KIND
    crm_ids = sorted(path.name for path in crm_root.iterdir() if path.is_dir())
    task_ids = sorted(path.name for path in task_root.iterdir() if path.is_dir())

    assert len(crm_ids) == 3
    assert len(task_ids) == 3
    assert result["canonical_mutation_count"] == 12

    for entity_id in crm_ids:
        state, replay_hash = store.replay(CRM_DOMAIN, KIND_RECORD, entity_id)
        assert state["record_type"] == "CASE"
        assert replay_hash == store.state_hash(CRM_DOMAIN, KIND_RECORD, entity_id)

    for entity_id in task_ids:
        state, replay_hash = store.replay(TASK_DOMAIN, TASK_KIND, entity_id)
        assert state["status"] == "TODO"
        assert replay_hash == store.state_hash(TASK_DOMAIN, TASK_KIND, entity_id)


def test_interpreted_hold_block_and_duplicate_create_no_partial_extra_state(tmp_path):
    _, result = run(tmp_path)

    assert result["results"]["mail-missing-evidence-001"]["canonical_mutation_count"] == 0
    assert result["results"]["supplier-order:SO-77"]["canonical_mutation_count"] == 0
    assert result["results"]["mail-action-001-duplicate"]["canonical_mutation_count"] == 0

    native_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (tmp_path / "native").rglob("*.json")
    )
    assert "Resolve conflicting source instructions" not in native_text
    assert "Clarify incomplete request" not in native_text


def test_runner_does_not_import_or_load_truth_manifest_for_routing():
    source = inspect.getsource(interpreted_runner_module)
    assert "load_enterprise_sandbox_truth_v0" not in source
    assert "truth_manifest.json" not in source
    assert "mail_truth" not in source
    assert "document_truth" not in source
    assert "calendar_truth" not in source


def test_interpreted_result_is_deterministic(tmp_path):
    _, first = run(tmp_path / "first")
    _, second = run(tmp_path / "second")

    assert first["interpretation_hashes"] == second["interpretation_hashes"]
    assert first["correlation_hash"] == second["correlation_hash"]
    assert first["intake_policy_batch_hash"] == second["intake_policy_batch_hash"]
    assert first["committed_case_count"] == second["committed_case_count"]
    assert first["canonical_mutation_count"] == second["canonical_mutation_count"]
    assert first["duplicate_suppressed_count"] == second["duplicate_suppressed_count"]
    assert first["hold_count"] == second["hold_count"]
    assert first["block_count"] == second["block_count"]
    assert first["information_only_count"] == second["information_only_count"]


def test_runner_delegates_intake_conversion_to_native_policy():
    source = inspect.getsource(interpreted_runner_module)
    assert "project_interpretations_to_native_intake_v0" in source
    assert "build_native_case_task_intake_plan_v0" not in source
    assert "_build_plan_from_candidate" not in source
    assert "_review_policy_due_at" not in source
    assert "CASE_CONFLICT" not in source
    assert "CASE_MISSING_EVIDENCE" not in source
