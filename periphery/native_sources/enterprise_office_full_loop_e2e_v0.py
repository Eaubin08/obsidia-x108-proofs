"""ENTERPRISE_OFFICE_FULL_LOOP_E2E_V0.

Closes the native enterprise-office loop in deterministic sandbox mode:

sources
→ native source runtime
→ interpretation/correlation
→ intake policy
→ governed CRM/TASKS intake
→ native work-to-action projection
→ canonical WorldActionRequest
→ exact HumanApproval
→ WORLD_ACTION_PRE / KX108
→ activation policy
→ LiveSovereignTicket
→ bounded deterministic sandbox executor
→ immutable execution receipt
→ replay + duplicate-execution block

No external network or real external effect is permitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from periphery.native_ops.common_v0 import (
    DECISION_AUTHORITY,
    NativeEntityStoreV0,
    canonical_hash,
)
from periphery.native_ops.native_work_to_action_projection_v0 import (
    STATUS_ACTION_CANDIDATE,
    STATUS_NO_ACTION,
    build_world_action_request_from_action_candidate_v0,
    project_native_work_to_action_v0,
    verify_native_work_action_projection_v0,
)
from periphery.native_ops.world_action_bridge_v0 import (
    build_native_human_approval_v0,
)
from periphery.native_sources.enterprise_office_interpreted_e2e_v0 import (
    run_interpreted_autonomous_office_e2e_v0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    EnterpriseSandboxPathsV0,
)
from periphery.world_calls.bounded_connector_executor_v0 import (
    ConnectorProviderOutcomeV0,
    OUTCOME_CONFIRMED_SUCCESS,
    execute_bounded_connector_v0,
    replay_execution_receipt_v0,
    verify_execution_receipt_v0,
)
from periphery.world_calls.external_runtime_activation_policy_v0 import (
    build_activation_policy_v0,
)
from periphery.world_calls.live_sovereign_ticket_v0 import (
    issue_live_sovereign_ticket_v0,
)

import sys

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from obsidia_world_action_pre_execution_v0 import (  # noqa: E402
    run_world_action_pre_execution_v0,
)

STATUS = "ENTERPRISE_OFFICE_FULL_LOOP_E2E_V0_PROVEN"
SANDBOX_CONNECTOR_ID = "OBSIDIA_CALENDAR_SANDBOX"
SANDBOX_CONNECTOR_ACTION = "CREATE_EVENT"
SANDBOX_SCOPE = "calendar:event:create"
POLICY_CREATED_AT = "2026-10-01T00:00:00+00:00"
POLICY_EXPIRES_AT = "2099-01-01T00:00:00+00:00"
EXECUTION_TIME = "2026-10-07T12:00:00+00:00"
PROVIDER_OBSERVED_AT = "2026-10-07T12:00:01+00:00"


@dataclass
class DeterministicCalendarSandboxAdapterV0:
    connector_id: str = SANDBOX_CONNECTOR_ID
    connector_action: str = SANDBOX_CONNECTOR_ACTION
    required_scope: str = SANDBOX_SCOPE
    provider_id: str = "OBSIDIA_ENTERPRISE_CALENDAR_SANDBOX_V0"
    execution_mode: str = "SANDBOX_DETERMINISTIC"
    external_network_capable: bool = False
    side_effect_free: bool = True
    retry_after_confirmed_no_effect: bool = False
    call_count: int = 0

    def execute(
        self,
        connector_args: Mapping[str, Any],
    ) -> ConnectorProviderOutcomeV0:
        self.call_count += 1
        digest = canonical_hash({
            "schema": "ENTERPRISE_CALENDAR_SANDBOX_OUTCOME_V0",
            "connector_args": dict(connector_args),
            "provider_id": self.provider_id,
        })
        return ConnectorProviderOutcomeV0(
            status=OUTCOME_CONFIRMED_SUCCESS,
            provider_receipt_ref=f"sandbox-calendar-receipt:{digest[:24]}",
            provider_state_ref=f"sandbox-calendar-state:{digest[24:48]}",
            detail_digest=digest,
            observed_at=PROVIDER_OBSERVED_AT,
        )


def _committed_work_items(
    office_result: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    return {
        item_id: value
        for item_id, value in office_result["results"].items()
        if isinstance(value, Mapping)
        and value.get("status") == "NATIVE_INTAKE_COMMITTED"
    }


def _build_request(projection) -> dict[str, Any]:
    candidate = projection.action_candidate
    if candidate is None:
        raise ValueError("FULL_LOOP_ACTION_CANDIDATE_REQUIRED")
    target_ref = f"sim:calendar:work-deadline:{projection.projection_id}"
    return build_world_action_request_from_action_candidate_v0(
        candidate,
        connector_id=SANDBOX_CONNECTOR_ID,
        connector_action=SANDBOX_CONNECTOR_ACTION,
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
        required_scope=SANDBOX_SCOPE,
        effect_class="EXTERNAL_DATA_MUTATION",
        world_call_class="REVERSIBLE_WORLD_CALL",
        action_risk_class="ACTION_PLAN",
        autonomy_level=3,
    )


def _build_policy(projection_id: str):
    return build_activation_policy_v0(
        policy_id=f"enterprise-office-sandbox:{projection_id}",
        environment="ENTERPRISE_OFFICE_SANDBOX",
        enabled=True,
        allowed_operations=[(
            SANDBOX_CONNECTOR_ID,
            SANDBOX_CONNECTOR_ACTION,
            SANDBOX_SCOPE,
        )],
        allowed_world_call_classes=("REVERSIBLE_WORLD_CALL",),
        allowed_action_risk_classes=("ACTION_PLAN",),
        max_autonomy_level=3,
        created_at=POLICY_CREATED_AT,
        expires_at=POLICY_EXPIRES_AT,
        operator_approval_ref=(
            f"HUMAN:SANDBOX_OPERATOR:{projection_id}"
        ),
    )


def _execute_projection(
    *,
    projection,
    governance_root: Path,
    execution_root: Path,
) -> dict[str, Any]:
    ok, reason = verify_native_work_action_projection_v0(projection)
    if not ok:
        raise ValueError(f"FULL_LOOP_PROJECTION_INVALID:{reason}")

    request = _build_request(projection)
    approval = build_native_human_approval_v0(
        request,
        approval_id=f"approval:{projection.projection_id}",
        approved_by="HUMAN:SANDBOX_OPERATOR",
        approval_reference=f"enterprise-full-loop:{projection.projection_id}",
    )

    action_root = governance_root / projection.projection_hash[:20]
    context_dir = action_root / "contexts"
    decision_dir = action_root / "decisions"
    pre = run_world_action_pre_execution_v0(
        request=request,
        human_approval=approval,
        evidence_refs=list(projection.evidence_refs),
        unknowns=[],
        contradictions=[],
        risk_flags=[],
        context_store_dir=context_dir,
        decision_store_dir=decision_dir,
    )
    if pre.x108_gate != "ALLOW":
        raise ValueError(f"FULL_LOOP_KX108_PRE_NOT_ALLOW:{pre.x108_gate}")

    policy = _build_policy(projection.projection_id)
    ticket = issue_live_sovereign_ticket_v0(
        decision_record_id=pre.decision_record_id,
        activation_policy=policy,
        decision_store_dir=decision_dir,
        context_store_dir=context_dir,
        ttl_seconds=120,
        now=EXECUTION_TIME,
    )

    receipt_dir = execution_root / projection.projection_hash[:20] / "receipts"
    reconciliation_dir = (
        execution_root / projection.projection_hash[:20] / "reconciliations"
    )
    adapter = DeterministicCalendarSandboxAdapterV0()
    executed = execute_bounded_connector_v0(
        ticket=ticket,
        activation_policy=policy,
        connector_args=request["connector_args"],
        observed_target_ref=request["target_ref"],
        observed_target_prestate_hash=request["target_prestate_hash"],
        adapter=adapter,
        receipt_store_dir=receipt_dir,
        reconciliation_store_dir=reconciliation_dir,
        now=EXECUTION_TIME,
    )
    if executed.receipt is None:
        raise ValueError(
            f"FULL_LOOP_EXECUTION_RECEIPT_REQUIRED:{executed.status}:"
            f"{executed.reason}"
        )
    if verify_execution_receipt_v0(executed.receipt) != (True, None):
        raise ValueError("FULL_LOOP_EXECUTION_RECEIPT_VERIFY_FAILED")

    replay = replay_execution_receipt_v0(
        executed.receipt.receipt_id,
        store_dir=receipt_dir,
        expected_ticket_hash=ticket.ticket_hash,
        expected_connector_call_hash=ticket.connector_call_hash,
        expected_idempotency_key=ticket.idempotency_key,
    )
    if replay != (True, None):
        raise ValueError(f"FULL_LOOP_EXECUTION_REPLAY_FAILED:{replay}")

    duplicate_adapter = DeterministicCalendarSandboxAdapterV0()
    duplicate = execute_bounded_connector_v0(
        ticket=ticket,
        activation_policy=policy,
        connector_args=request["connector_args"],
        observed_target_ref=request["target_ref"],
        observed_target_prestate_hash=request["target_prestate_hash"],
        adapter=duplicate_adapter,
        receipt_store_dir=receipt_dir,
        reconciliation_store_dir=reconciliation_dir,
        now=EXECUTION_TIME,
    )

    return {
        "projection_id": projection.projection_id,
        "projection_hash": projection.projection_hash,
        "action_id": projection.action_candidate.action_id,
        "request_hash": request["request_hash"],
        "approval_hash": approval["approval_hash"],
        "kx108_gate": pre.x108_gate,
        "decision_record_id": pre.decision_record_id,
        "decision_record_hash": pre.decision_record_hash,
        "activation_policy_hash": policy.policy_hash,
        "sovereign_ticket_id": ticket.ticket_id,
        "sovereign_ticket_hash": ticket.ticket_hash,
        "execution_status": executed.status,
        "execution_receipt_id": executed.receipt.receipt_id,
        "execution_receipt_hash": executed.receipt.receipt_hash,
        "execution_replay_ok": replay[0],
        "duplicate_status": duplicate.status,
        "duplicate_reason": duplicate.reason,
        "duplicate_adapter_called": duplicate.adapter_called,
        "adapter_call_count": adapter.call_count,
        "network_call_performed": executed.network_call_performed,
        "real_external_effect": executed.real_external_effect,
    }


def run_enterprise_office_full_loop_e2e_v0(
    *,
    paths: EnterpriseSandboxPathsV0,
    runtime_root: Path,
    native_store_root: Path,
    governance_root: Path,
    execution_root: Path,
) -> dict[str, Any]:
    office = run_interpreted_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=runtime_root,
        native_store_root=native_store_root,
        governance_root=governance_root / "intake",
    )
    store = NativeEntityStoreV0(native_store_root)
    committed = _committed_work_items(office)

    projections: dict[str, Any] = {}
    executions: dict[str, dict[str, Any]] = {}
    for item_id, work in sorted(committed.items()):
        projection = project_native_work_to_action_v0(
            store=store,
            case_id=str(work["case_id"]),
            task_id=str(work["task_id"]),
            followup_id=str(work["followup_id"]),
        )
        projections[item_id] = projection

        if projection.status == STATUS_ACTION_CANDIDATE:
            executions[item_id] = _execute_projection(
                projection=projection,
                governance_root=governance_root / "world_action",
                execution_root=execution_root,
            )
        elif projection.status != STATUS_NO_ACTION:
            raise ValueError(
                f"FULL_LOOP_PROJECTION_STATUS_UNSUPPORTED:{projection.status}"
            )

    action_count = sum(
        1 for value in projections.values()
        if value.status == STATUS_ACTION_CANDIDATE
    )
    no_action_count = sum(
        1 for value in projections.values()
        if value.status == STATUS_NO_ACTION
    )
    execution_receipt_hashes = sorted(
        value["execution_receipt_hash"] for value in executions.values()
    )

    stable_intent = {
        "schema": "OBSIDIA_ENTERPRISE_OFFICE_FULL_LOOP_STABLE_INTENT_V0",
        "projection_hashes": {
            item_id: projection.projection_hash
            for item_id, projection in sorted(projections.items())
        },
        "action_bindings": {
            item_id: {
                "projection_hash": value["projection_hash"],
                "request_hash": value["request_hash"],
                "approval_hash": value["approval_hash"],
                "activation_policy_hash": value["activation_policy_hash"],
            }
            for item_id, value in sorted(executions.items())
        },
        "decision_authority": DECISION_AUTHORITY,
    }

    summary = {
        "schema": "OBSIDIA_ENTERPRISE_OFFICE_FULL_LOOP_E2E_RESULT_V0",
        "status": STATUS,
        "upstream_result_hash": office["result_hash"],
        "truth_manifest_used_for_routing": office[
            "truth_manifest_used_for_routing"
        ],
        "source_observation_count": office["source_observation_count"],
        "source_packet_count": office["source_packet_count"],
        "interpretation_candidate_count": office[
            "interpretation_candidate_count"
        ],
        "intake_policy_instruction_count": office[
            "intake_policy_instruction_count"
        ],
        "committed_case_count": office["committed_case_count"],
        "canonical_mutation_count": office["canonical_mutation_count"],
        "hold_count": office["hold_count"],
        "block_count": office["block_count"],
        "information_only_count": office["information_only_count"],
        "duplicate_suppressed_count": office["duplicate_suppressed_count"],
        "work_projection_count": len(projections),
        "action_candidate_count": action_count,
        "no_action_count": no_action_count,
        "sandbox_execution_count": len(executions),
        "execution_receipt_count": len(executions),
        "execution_replay_ok_count": sum(
            1 for value in executions.values()
            if value["execution_replay_ok"]
        ),
        "duplicate_execution_block_count": sum(
            1 for value in executions.values()
            if value["duplicate_status"] == "BLOCKED"
            and value["duplicate_reason"]
            == "DUPLICATE_CONFIRMED_EXECUTION_BLOCK"
            and value["duplicate_adapter_called"] is False
        ),
        "network_call_performed": any(
            value["network_call_performed"] for value in executions.values()
        ),
        "real_external_effect": any(
            value["real_external_effect"] for value in executions.values()
        ),
        "execution_receipt_hashes": execution_receipt_hashes,
        "stable_intent_hash": canonical_hash(stable_intent),
        "runtime_evidence_time_bound": True,
        "projection_hashes": {
            item_id: projection.projection_hash
            for item_id, projection in sorted(projections.items())
        },
        "executions": executions,
        "decision_authority": DECISION_AUTHORITY,
    }
    summary["result_hash"] = canonical_hash(summary)
    return summary
