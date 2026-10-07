from pathlib import Path

from periphery.native_ops.common_v0 import NativeEntityStoreV0
from periphery.native_ops.crm_native_v0 import DOMAIN_ID as CRM_DOMAIN, KIND_RECORD
from periphery.native_ops.tasks_native_v0 import DOMAIN_ID as TASK_DOMAIN, ENTITY_KIND as TASK_KIND
from periphery.native_sources.enterprise_office_e2e_v0 import (
    STATUS,
    run_autonomous_office_e2e_v0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    materialize_enterprise_source_sandbox_v0,
)


def test_autonomous_office_e2e_runs_full_stack_with_expected_outcomes(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    result = run_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )

    assert result["status"] == STATUS
    assert result["sandbox_truth_status"] == "SIMULATED_NOT_OBSERVED"
    assert result["source_observation_count"] == 12
    assert result["source_packet_count"] == 12
    assert result["committed_case_count"] == 3
    assert result["canonical_mutation_count"] == 12
    assert result["duplicate_suppressed_count"] == 1
    assert result["hold_count"] == 1
    assert result["block_count"] == 1
    assert result["information_only_count"] == 2
    assert result["external_action"] is False
    assert result["network_call_performed"] is False
    assert result["decision_authority"] == "KX108_ONLY"

    assert result["results"]["mail-action-001"]["status"] == "NATIVE_INTAKE_COMMITTED"
    assert result["results"]["mail-incident-001"]["status"] == "NATIVE_INTAKE_COMMITTED"
    assert result["results"]["contract-renewal.md"]["status"] == "NATIVE_INTAKE_COMMITTED"
    assert result["results"]["mail-action-001-duplicate"]["status"] == "DUPLICATE_SUPPRESSED"
    assert result["results"]["supplier-order-so77"]["gate"] == "BLOCK"
    assert result["results"]["mail-missing-evidence-001"]["gate"] == "HOLD"


def test_autonomous_office_commits_exactly_three_crm_cases_and_tasks(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    run_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )
    store = NativeEntityStoreV0(tmp_path / "native")

    crm_root = tmp_path / "native" / CRM_DOMAIN / KIND_RECORD
    task_root = tmp_path / "native" / TASK_DOMAIN / TASK_KIND
    crm_ids = sorted(path.name for path in crm_root.iterdir() if path.is_dir())
    task_ids = sorted(path.name for path in task_root.iterdir() if path.is_dir())

    assert len(crm_ids) == 3
    assert len(task_ids) == 3
    for entity_id in crm_ids:
        state, replay_hash = store.replay(CRM_DOMAIN, KIND_RECORD, entity_id)
        assert state["record_type"] == "CASE"
        assert replay_hash == store.state_hash(CRM_DOMAIN, KIND_RECORD, entity_id)
    for entity_id in task_ids:
        state, replay_hash = store.replay(TASK_DOMAIN, TASK_KIND, entity_id)
        assert state["status"] == "TODO"
        assert replay_hash == store.state_hash(TASK_DOMAIN, TASK_KIND, entity_id)


def test_hold_and_block_create_no_partial_native_state(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    result = run_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )

    blocked = result["results"]["supplier-order-so77"]
    held = result["results"]["mail-missing-evidence-001"]
    assert blocked["canonical_mutation_count"] == 0
    assert held["canonical_mutation_count"] == 0

    native_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (tmp_path / "native").rglob("*.json")
    )
    assert "Resolve supplier order conflict" not in native_text
    assert "Clarify incomplete request" not in native_text


def test_duplicate_does_not_create_second_case_or_task(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    result = run_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )
    primary = result["results"]["mail-action-001"]
    duplicate = result["results"]["mail-action-001-duplicate"]

    assert duplicate["status"] == "DUPLICATE_SUPPRESSED"
    assert duplicate["canonical_case_id"] == primary["case_id"]
    assert duplicate["canonical_mutation_count"] == 0


def test_information_and_routine_calendar_do_not_create_work(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    result = run_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )

    assert result["results"]["mail-info-001"]["canonical_mutation_count"] == 0
    assert result["results"]["policy-info.md"]["canonical_mutation_count"] == 0
    assert result["results"]["event-routine-001"]["canonical_mutation_count"] == 0
    assert result["results"]["event-deadline-001"]["canonical_mutation_count"] == 0


def test_e2e_is_explicitly_sandbox_only_not_production_classifier(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    result = run_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )
    assert result["status"] == "SANDBOX_ONLY_NOT_PRODUCTION_INTERPRETER"
    assert result["sandbox_truth_status"] == "SIMULATED_NOT_OBSERVED"
