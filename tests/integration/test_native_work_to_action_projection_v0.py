import inspect
from dataclasses import replace

from periphery.common import ActionCandidate
from periphery.native_ops.common_v0 import NativeEntityStoreV0, canonical_hash
from periphery.native_ops.intake_bundle_v0 import build_native_human_approval_v0
from periphery.native_ops.native_work_to_action_projection_v0 import (
    ACTION_TYPE_CALENDAR_CREATE_EVENT,
    REASON_CALENDAR_DEADLINE_PROJECTION,
    REASON_EXTERNAL_SURFACE_NOT_PROVEN,
    STATUS_ACTION_CANDIDATE,
    STATUS_NO_ACTION,
    build_world_action_request_from_action_candidate_v0,
    project_native_work_to_action_v0,
    verify_native_work_action_projection_v0,
)
import periphery.native_ops.native_work_to_action_projection_v0 as projection_module
from periphery.native_sources.enterprise_office_interpreted_e2e_v0 import (
    run_interpreted_autonomous_office_e2e_v0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    materialize_enterprise_source_sandbox_v0,
)

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from obsidia_world_action_pre_execution_v0 import (  # noqa: E402
    run_world_action_pre_execution_v0,
)


def run_office(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    result = run_interpreted_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )
    store = NativeEntityStoreV0(tmp_path / "native")
    committed = {
        item_id: value
        for item_id, value in result["results"].items()
        if isinstance(value, dict)
        and value.get("status") == "NATIVE_INTAKE_COMMITTED"
    }
    return result, store, committed


def build_projections(tmp_path):
    result, store, committed = run_office(tmp_path)
    projections = {}
    for item_id, value in committed.items():
        projections[item_id] = project_native_work_to_action_v0(
            store=store,
            case_id=value["case_id"],
            task_id=value["task_id"],
            followup_id=value["followup_id"],
        )
    return result, store, committed, projections


def sandbox_request(projection):
    candidate = projection.action_candidate
    assert candidate is not None
    target_ref = f"sim:calendar:work-deadline:{projection.projection_id}"
    return build_world_action_request_from_action_candidate_v0(
        candidate,
        connector_id="OBSIDIA_CALENDAR_SANDBOX",
        connector_action="CREATE_EVENT",
        connector_args={
            "projection_id": projection.projection_id,
            "title": candidate.payload["title"],
            "due_at": candidate.payload["due_at"],
            "fixture_mode": "SIMULATED_NOT_OBSERVED",
        },
        target_ref=target_ref,
        target_prestate_hash=canonical_hash({
            "target_ref": target_ref,
            "state": "ABSENT_SIMULATED_EVENT",
        }),
        required_scope="calendar:event:create",
        effect_class="EXTERNAL_DATA_MUTATION",
        world_call_class="REVERSIBLE_WORLD_CALL",
        action_risk_class="ACTION_PLAN",
        autonomy_level=3,
    )


def test_three_committed_native_work_items_project_to_two_actions_and_one_no_action(tmp_path):
    result, _, committed, projections = build_projections(tmp_path)

    assert result["committed_case_count"] == 3
    assert len(committed) == 3
    assert len(projections) == 3

    assert projections["mail-action-001"].status == STATUS_ACTION_CANDIDATE
    assert projections["contract-renewal.md"].status == STATUS_ACTION_CANDIDATE
    assert projections["mail-incident-001"].status == STATUS_NO_ACTION

    assert projections["mail-action-001"].reason_code == REASON_CALENDAR_DEADLINE_PROJECTION
    assert projections["contract-renewal.md"].reason_code == REASON_CALENDAR_DEADLINE_PROJECTION
    assert projections["mail-incident-001"].reason_code == REASON_EXTERNAL_SURFACE_NOT_PROVEN


def test_projection_reuses_existing_action_candidate_contract(tmp_path):
    _, _, _, projections = build_projections(tmp_path)

    for item_id in ("mail-action-001", "contract-renewal.md"):
        projection = projections[item_id]
        assert isinstance(projection.action_candidate, ActionCandidate)
        assert projection.action_candidate.action_type == ACTION_TYPE_CALENDAR_CREATE_EVENT
        assert projection.action_candidate.domain == "native_operations"
        assert projection.action_candidate.irreversible is False
        assert projection.action_candidate.payload["surface_id"] == "CALENDAR"
        assert projection.action_candidate.payload["operation_id"] == "CREATE_EVENT"

    incident = projections["mail-incident-001"]
    assert incident.action_candidate is None


def test_projection_preserves_native_state_binding_and_is_self_verifying(tmp_path):
    _, _, _, projections = build_projections(tmp_path)

    for projection in projections.values():
        assert verify_native_work_action_projection_v0(projection) == (True, None)
        assert len(projection.case_state_hash) == 64
        assert len(projection.task_state_hash) == 64
        assert len(projection.followup_state_hash) == 64
        assert len(projection.projection_hash) == 64
        assert projection.allowed_to_decide is False
        assert projection.allowed_to_act is False
        assert projection.emits_act is False
        assert projection.decision_authority == "KX108_ONLY"

    first = projections["mail-action-001"]
    tampered = replace(first, projection_hash="0" * 64)
    assert verify_native_work_action_projection_v0(tampered) == (
        False,
        "WORK_ACTION_PROJECTION_HASH_MISMATCH",
    )


def test_projection_is_deterministic(tmp_path):
    _, _, _, first = build_projections(tmp_path / "first")
    _, _, _, second = build_projections(tmp_path / "second")

    assert set(first) == set(second)
    for item_id in first:
        assert first[item_id].projection_hash == second[item_id].projection_hash
        assert first[item_id].to_dict() == second[item_id].to_dict()


def test_no_mail_action_is_invented_without_structured_recipient_or_content(tmp_path):
    _, _, _, projections = build_projections(tmp_path)

    candidates = [
        projection.action_candidate
        for projection in projections.values()
        if projection.action_candidate is not None
    ]
    assert len(candidates) == 2
    assert {candidate.payload["surface_id"] for candidate in candidates} == {
        "CALENDAR"
    }
    assert all("recipient" not in candidate.payload for candidate in candidates)
    assert all("body" not in candidate.payload for candidate in candidates)


def test_existing_action_candidate_binds_to_canonical_world_action_request(tmp_path):
    _, _, _, projections = build_projections(tmp_path)

    for item_id in ("mail-action-001", "contract-renewal.md"):
        projection = projections[item_id]
        request = sandbox_request(projection)

        assert request["domain_id"] == "native_operations"
        assert request["surface_id"] == "CALENDAR"
        assert request["operation_id"] == "CREATE_EVENT"
        assert request["connector_id"] == "OBSIDIA_CALENDAR_SANDBOX"
        assert request["decision_authority"] == "KX108_ONLY"
        assert request["allowed_to_decide"] is False
        assert request["allowed_to_act"] is False
        assert request["emits_act"] is False
        assert len(request["request_hash"]) == 64
        assert len(request["connector_call_hash"]) == 64
        assert len(request["idempotency_key"]) == 64


def test_projected_actions_reach_real_world_action_pre_and_kx108_without_execution(tmp_path):
    _, _, _, projections = build_projections(tmp_path)

    decisions = []
    for item_id in ("mail-action-001", "contract-renewal.md"):
        projection = projections[item_id]
        request = sandbox_request(projection)
        approval = build_native_human_approval_v0(
            request,
            approval_id=f"approval:{projection.projection_id}",
            approved_by="HUMAN:SANDBOX_OPERATOR",
            approval_reference=f"native-work-action:{projection.projection_id}",
        )
        root = tmp_path / "world-action" / projection.projection_id
        pre = run_world_action_pre_execution_v0(
            request=request,
            human_approval=approval,
            evidence_refs=list(projection.evidence_refs),
            unknowns=[],
            contradictions=[],
            risk_flags=[],
            context_store_dir=root / "contexts",
            decision_store_dir=root / "decisions",
        )
        decisions.append(pre)

    assert len(decisions) == 2
    assert all(item.x108_gate == "ALLOW" for item in decisions)
    assert all(item.decision_authority == "KX108_ONLY" for item in decisions)
    assert all(item.egress_allowed is False for item in decisions)
    assert all(item.world_action_runtime_activated is False for item in decisions)


def test_projection_module_has_no_execution_authority():
    source = inspect.getsource(projection_module)
    assert "execute_bounded_connector_v0" not in source
    assert "issue_live_sovereign_ticket_v0" not in source
    assert "apply_crm_mutation_v0" not in source
    assert "apply_task_mutation_v0" not in source
    assert "allowed_to_decide: bool = False" in source
    assert "allowed_to_act: bool = False" in source
    assert "emits_act: bool = False" in source
