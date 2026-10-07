import json
from pathlib import Path

from periphery.native_sources.enterprise_office_e2e_v0 import (
    run_autonomous_office_e2e_v0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    materialize_enterprise_source_sandbox_v0,
)
from scripts.kernel.kx108_runtime_link_facts_v1 import runtime_link_facts

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs" / "preforge" / "OBSIDIA_ENTERPRISE_PREFORGE_FREEZE_V0.json"


def test_preforge_manifest_freezes_expected_stack_and_next_forge_scope():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["schema"] == "OBSIDIA_ENTERPRISE_PREFORGE_FREEZE_V0"
    assert data["status"] == "PREFORGE_CANDIDATE"

    assert data["canonical_stack"] == [
        "SOURCE_RUNTIME_NATIVE_V0",
        "MAIL_NATIVE_CONNECTOR_V0",
        "DOCUMENT_NATIVE_CONNECTOR_V0",
        "CALENDAR_NATIVE_CONNECTOR_V0",
        "TASKS_NATIVE_V0",
        "CRM_NATIVE_V0",
        "NATIVE_CASE_TASK_INTAKE_V0",
        "WORLD_ACTION_PRE_EXECUTION",
        "KX108_ONLY",
        "RECEIPTS_REPLAY",
    ]

    invariants = data["invariants"]
    assert invariants["decision_authority"] == "KX108_ONLY"
    assert invariants["world_action_runtime_activated"] is False
    assert invariants["runtime_allowed_now"] is False
    assert invariants["execution_authority"] is False
    assert invariants["memory_write"] is False
    assert invariants["kernel_mutation"] is False
    assert invariants["emits_act"] is False
    assert invariants["main_merge"] is False

    next_forge = data["forge_next"]
    assert next_forge["scope"] == "SOURCE_INTERPRETATION_NATIVE_V0"
    assert next_forge["authority"]["allowed_to_decide"] is False
    assert next_forge["authority"]["allowed_to_act"] is False
    assert next_forge["authority"]["decision_authority"] == "KX108_ONLY"
    assert "No protected-core changes" in next_forge["acceptance"]


def test_preforge_runtime_facts_expose_new_native_stack_without_live_activation():
    facts = runtime_link_facts()

    assert facts["native_tasks_crm_domains_present"] is True
    assert facts["native_source_runtime_present"] is True
    assert facts["native_source_connectors_present"] is True
    assert facts["enterprise_source_sandbox_present"] is True
    assert facts["autonomous_office_e2e_contract_present"] is True
    assert facts["autonomous_office_e2e_status"] == (
        "SANDBOX_ONLY_NOT_PRODUCTION_INTERPRETER"
    )

    assert facts["world_action_pre_execution_rail_present"] is True
    assert facts["world_action_runtime_activated"] is False
    assert facts["runtime_allowed_now"] is False
    assert facts["execution_authority"] is False
    assert facts["memory_write"] is False
    assert facts["kernel_mutation"] is False
    assert facts["emits_act"] is False
    assert facts["decision_authority"] == "KX108_ONLY"


def test_preforge_e2e_acceptance_snapshot(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    result = run_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )

    assert result["status"] == "SANDBOX_ONLY_NOT_PRODUCTION_INTERPRETER"
    assert result["sandbox_truth_status"] == "SIMULATED_NOT_OBSERVED"
    assert result["source_observation_count"] == 12
    assert result["source_packet_count"] == 12
    assert result["committed_case_count"] == 3
    assert result["canonical_mutation_count"] == 12
    assert result["duplicate_suppressed_count"] == 1
    assert result["hold_count"] == 1
    assert result["block_count"] == 1
    assert result["information_only_count"] == 2
    assert result["network_call_performed"] is False
    assert result["external_action"] is False
    assert result["decision_authority"] == "KX108_ONLY"


def test_open_source_policy_keeps_obsidia_contracts_sovereign():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    policy = data["open_source_adoption_policy"]
    assert policy["sequence"] == [
        "LICENSE_AUDIT",
        "SECURITY_SCOPE_AUDIT",
        "ADAPTER_TO_OBSIDIA_CONTRACT",
        "CONFORMANCE_TESTS",
        "OPTIONAL_COMPONENT",
    ]
    for protected_contract in (
        "KX108_ONLY",
        "WORLD_ACTION",
        "TASKS_NATIVE_V0",
        "CRM_NATIVE_V0",
        "SOURCE_RUNTIME_NATIVE_V0",
    ):
        assert protected_contract in policy["oss_must_not_replace"]
