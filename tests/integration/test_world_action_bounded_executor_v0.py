import datetime
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from obsidia_world_action_pre_execution_v0 import (  # noqa: E402
    run_world_action_pre_execution_v0,
)
from periphery.world_calls.bounded_connector_executor_v0 import (  # noqa: E402
    ConnectorProviderOutcomeV0,
    OUTCOME_CONFIRMED_NO_EFFECT,
    OUTCOME_CONFIRMED_SUCCESS,
    OUTCOME_PROVIDER_REJECTED,
    OUTCOME_UNKNOWN,
    RECONCILIATION_CONFIRMED_NO_EFFECT,
    RECONCILIATION_CONFIRMED_SUCCESS,
    execute_bounded_connector_v0,
    load_execution_receipt_v0,
    reconcile_unknown_outcome_v0,
    replay_execution_receipt_v0,
    verify_execution_receipt_v0,
    verify_reconciliation_v0,
)
from periphery.world_calls.external_runtime_activation_policy_v0 import (  # noqa: E402
    build_activation_policy_v0,
)
from periphery.world_calls.live_sovereign_ticket_v0 import (  # noqa: E402
    issue_live_sovereign_ticket_v0,
)


def canonical_hash(value):
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def build_request():
    args = {
        "record_id": "customer-001",
        "field": "status",
        "value": "confirmed",
    }
    request = {
        "request_id": "world-executor-001",
        "proposal_id": "proposal-executor-001",
        "proposal_hash": canonical_hash({"proposal": "executor"}),
        "domain_id": "ecom",
        "surface_id": "CRM",
        "operation_id": "UPDATE_RECORD",
        "effect_class": "EXTERNAL_DATA_MUTATION",
        "connector_id": "CRM_TEST",
        "connector_action": "UPDATE_RECORD",
        "connector_args": args,
        "target_ref": "crm:test:customer-001",
        "target_prestate_hash": canonical_hash(
            {"target": "customer-001", "status": "pending"}
        ),
        "required_scope": "crm:write:test",
        "world_call_class": "REVERSIBLE_WORLD_CALL",
        "action_risk_class": "ACTION_EXTERNAL_API",
        "autonomy_level": 4,
        "irreversible": False,
        "retry_policy": "NEVER_AUTORETRY_ON_UNKNOWN",
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
    }
    request["connector_call_hash"] = canonical_hash(
        {
            "connector_id": request["connector_id"],
            "connector_action": request["connector_action"],
            "connector_args": request["connector_args"],
        }
    )
    request["idempotency_key"] = canonical_hash(
        {
            "schema": "UNIVERSAL_WORLD_ACTION_IDEMPOTENCY_V0",
            "proposal_hash": request["proposal_hash"],
            "connector_call_hash": request["connector_call_hash"],
            "target_prestate_hash": request["target_prestate_hash"],
            "required_scope": request["required_scope"],
        }
    )
    request["request_hash"] = canonical_hash(
        {
            "schema": "UNIVERSAL_WORLD_ACTION_REQUEST_V0",
            "request_id": request["request_id"],
            "proposal_id": request["proposal_id"],
            "proposal_hash": request["proposal_hash"],
            "domain_id": request["domain_id"],
            "surface_id": request["surface_id"],
            "operation_id": request["operation_id"],
            "effect_class": request["effect_class"],
            "connector_id": request["connector_id"],
            "connector_action": request["connector_action"],
            "connector_args": request["connector_args"],
            "connector_call_hash": request["connector_call_hash"],
            "target_ref": request["target_ref"],
            "target_prestate_hash": request["target_prestate_hash"],
            "required_scope": request["required_scope"],
            "world_call_class": request["world_call_class"],
            "action_risk_class": request["action_risk_class"],
            "autonomy_level": request["autonomy_level"],
            "irreversible": request["irreversible"],
            "retry_policy": request["retry_policy"],
            "idempotency_key": request["idempotency_key"],
            "decision_authority": request["decision_authority"],
        }
    )
    return request


def build_approval(request):
    approval = {
        "schema": "UNIVERSAL_WORLD_ACTION_HUMAN_APPROVAL_V0",
        "approval_id": "approval-executor-001",
        "approved_by": "HUMAN:TEST_OPERATOR",
        "approval_reference": "review:executor-001",
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "proposal_hash": request["proposal_hash"],
        "domain_id": request["domain_id"],
        "surface_id": request["surface_id"],
        "operation_id": request["operation_id"],
        "connector_id": request["connector_id"],
        "connector_action": request["connector_action"],
        "connector_call_hash": request["connector_call_hash"],
        "target_ref": request["target_ref"],
        "target_prestate_hash": request["target_prestate_hash"],
        "required_scope": request["required_scope"],
        "idempotency_key": request["idempotency_key"],
        "decision_authority": "KX108_ONLY",
        "is_execution_authority": False,
    }
    approval["approval_hash"] = canonical_hash(approval)
    return approval


def build_policy(request):
    now = datetime.datetime.now(datetime.timezone.utc)
    return build_activation_policy_v0(
        policy_id="executor-policy-v0",
        environment="TEST_ONLY",
        enabled=True,
        allowed_operations=[
            (
                request["connector_id"],
                request["connector_action"],
                request["required_scope"],
            )
        ],
        created_at=now.isoformat(),
        expires_at=(now + datetime.timedelta(hours=1)).isoformat(),
        operator_approval_ref="TEST_OPERATOR_ENABLE",
    )


def prepare_live(tmp_path):
    request = build_request()
    pre = run_world_action_pre_execution_v0(
        request=request,
        human_approval=build_approval(request),
        evidence_refs=["fixture:bounded-executor"],
        context_store_dir=tmp_path / "contexts",
        decision_store_dir=tmp_path / "decisions",
    )
    assert pre.x108_gate == "ALLOW"
    policy = build_policy(request)
    ticket = issue_live_sovereign_ticket_v0(
        decision_record_id=pre.decision_record_id,
        activation_policy=policy,
        decision_store_dir=tmp_path / "decisions",
        context_store_dir=tmp_path / "contexts",
    )
    return request, pre, policy, ticket


class SandboxAdapter:
    def __init__(
        self,
        request,
        outcome_status=OUTCOME_CONFIRMED_SUCCESS,
        *,
        external_network_capable=False,
        side_effect_free=True,
        execution_mode="SANDBOX_DETERMINISTIC",
        retry_after_confirmed_no_effect=True,
        connector_id=None,
        connector_action=None,
        required_scope=None,
    ):
        self.connector_id = connector_id or request["connector_id"]
        self.connector_action = connector_action or request["connector_action"]
        self.required_scope = required_scope or request["required_scope"]
        self.provider_id = "SANDBOX_CRM_PROVIDER_V0"
        self.execution_mode = execution_mode
        self.external_network_capable = external_network_capable
        self.side_effect_free = side_effect_free
        self.retry_after_confirmed_no_effect = (
            retry_after_confirmed_no_effect
        )
        self.outcome_status = outcome_status
        self.call_count = 0

    def execute(self, connector_args):
        self.call_count += 1
        observed = datetime.datetime.now(datetime.timezone.utc).isoformat()
        suffix = str(self.call_count)
        return ConnectorProviderOutcomeV0(
            status=self.outcome_status,
            provider_receipt_ref=f"sandbox-receipt-{suffix}",
            provider_state_ref=f"sandbox-state-{suffix}",
            detail_digest=canonical_hash(
                {
                    "args": dict(connector_args),
                    "outcome": self.outcome_status,
                    "call": self.call_count,
                }
            ),
            observed_at=observed,
        )


def execute(
    tmp_path,
    request,
    policy,
    ticket,
    adapter,
    *,
    connector_args=None,
):
    return execute_bounded_connector_v0(
        ticket=ticket,
        activation_policy=policy,
        connector_args=connector_args or request["connector_args"],
        observed_target_ref=request["target_ref"],
        observed_target_prestate_hash=request["target_prestate_hash"],
        adapter=adapter,
        receipt_store_dir=tmp_path / "receipts",
        reconciliation_store_dir=tmp_path / "reconciliations",
    )


def test_success_produces_append_only_replayable_sandbox_receipt(tmp_path):
    request, _, policy, ticket = prepare_live(tmp_path)
    adapter = SandboxAdapter(request)

    result = execute(tmp_path, request, policy, ticket, adapter)
    assert result.status == "SANDBOX_EXECUTED_RECEIPT_STORED"
    assert result.adapter_called is True
    assert result.network_call_performed is False
    assert result.real_external_effect is False
    assert adapter.call_count == 1

    receipt = result.receipt
    assert receipt is not None
    assert receipt.provider_outcome_status == OUTCOME_CONFIRMED_SUCCESS
    assert receipt.sandbox_execution is True
    assert receipt.real_external_effect is False
    assert receipt.retry_allowed is False
    assert receipt.recovery_state == "COMPLETED"
    assert verify_execution_receipt_v0(receipt) == (True, None)

    assert replay_execution_receipt_v0(
        receipt.receipt_id,
        store_dir=tmp_path / "receipts",
        expected_ticket_hash=ticket.ticket_hash,
        expected_connector_call_hash=ticket.connector_call_hash,
        expected_idempotency_key=ticket.idempotency_key,
    ) == (True, None)


def test_confirmed_success_blocks_duplicate_before_adapter(tmp_path):
    request, _, policy, ticket = prepare_live(tmp_path)
    adapter = SandboxAdapter(request)

    first = execute(tmp_path, request, policy, ticket, adapter)
    assert first.receipt is not None
    assert adapter.call_count == 1

    second = execute(tmp_path, request, policy, ticket, adapter)
    assert second.status == "BLOCKED"
    assert second.reason == "DUPLICATE_CONFIRMED_EXECUTION_BLOCK"
    assert second.adapter_called is False
    assert adapter.call_count == 1


def test_unknown_outcome_blocks_retry_until_reconciled(tmp_path):
    request, _, policy, ticket = prepare_live(tmp_path)
    unknown = SandboxAdapter(request, OUTCOME_UNKNOWN)

    first = execute(tmp_path, request, policy, ticket, unknown)
    assert first.receipt is not None
    assert first.receipt.recovery_state == "RECONCILIATION_REQUIRED"
    assert first.receipt.retry_allowed is False
    assert unknown.call_count == 1

    second_adapter = SandboxAdapter(request, OUTCOME_CONFIRMED_SUCCESS)
    blocked = execute(
        tmp_path, request, policy, ticket, second_adapter
    )
    assert blocked.status == "BLOCKED"
    assert blocked.reason == (
        "UNKNOWN_PRIOR_OUTCOME_RECONCILIATION_REQUIRED"
    )
    assert second_adapter.call_count == 0


def test_unknown_reconciled_no_effect_can_retry_then_success_blocks(tmp_path):
    request, _, policy, ticket = prepare_live(tmp_path)
    unknown = SandboxAdapter(request, OUTCOME_UNKNOWN)
    first = execute(tmp_path, request, policy, ticket, unknown)
    assert first.receipt is not None

    reconciliation = reconcile_unknown_outcome_v0(
        unknown_receipt_id=first.receipt.receipt_id,
        resolution=RECONCILIATION_CONFIRMED_NO_EFFECT,
        provider_verification_ref="sandbox-provider-check:no-effect",
        human_review_ref="human-review:confirmed-no-effect",
        receipt_store_dir=tmp_path / "receipts",
        reconciliation_store_dir=tmp_path / "reconciliations",
    )
    assert verify_reconciliation_v0(reconciliation) == (True, None)
    assert reconciliation.is_execution_authority is False

    success = SandboxAdapter(request, OUTCOME_CONFIRMED_SUCCESS)
    retried = execute(tmp_path, request, policy, ticket, success)
    assert retried.status == "SANDBOX_EXECUTED_RECEIPT_STORED"
    assert success.call_count == 1

    duplicate = execute(
        tmp_path,
        request,
        policy,
        ticket,
        SandboxAdapter(request),
    )
    assert duplicate.status == "BLOCKED"
    assert duplicate.reason == "DUPLICATE_CONFIRMED_EXECUTION_BLOCK"


def test_unknown_reconciled_success_blocks_retry(tmp_path):
    request, _, policy, ticket = prepare_live(tmp_path)
    unknown = SandboxAdapter(request, OUTCOME_UNKNOWN)
    first = execute(tmp_path, request, policy, ticket, unknown)
    assert first.receipt is not None

    reconcile_unknown_outcome_v0(
        unknown_receipt_id=first.receipt.receipt_id,
        resolution=RECONCILIATION_CONFIRMED_SUCCESS,
        provider_verification_ref="sandbox-provider-check:success",
        human_review_ref="human-review:confirmed-success",
        receipt_store_dir=tmp_path / "receipts",
        reconciliation_store_dir=tmp_path / "reconciliations",
    )

    retry = SandboxAdapter(request)
    blocked = execute(tmp_path, request, policy, ticket, retry)
    assert blocked.status == "BLOCKED"
    assert blocked.reason == (
        "RECONCILED_CONFIRMED_EXECUTION_DUPLICATE_BLOCK"
    )
    assert retry.call_count == 0


def test_confirmed_no_effect_can_retry_when_adapter_policy_allows(tmp_path):
    request, _, policy, ticket = prepare_live(tmp_path)
    no_effect = SandboxAdapter(
        request,
        OUTCOME_CONFIRMED_NO_EFFECT,
        retry_after_confirmed_no_effect=True,
    )
    first = execute(tmp_path, request, policy, ticket, no_effect)
    assert first.receipt is not None
    assert first.receipt.retry_allowed is True
    assert first.receipt.recovery_state == "CONFIRMED_NO_EFFECT"

    second = SandboxAdapter(request, OUTCOME_CONFIRMED_SUCCESS)
    retried = execute(tmp_path, request, policy, ticket, second)
    assert retried.status == "SANDBOX_EXECUTED_RECEIPT_STORED"
    assert second.call_count == 1


def test_provider_rejection_requires_new_decision(tmp_path):
    request, _, policy, ticket = prepare_live(tmp_path)
    rejected = SandboxAdapter(request, OUTCOME_PROVIDER_REJECTED)
    first = execute(tmp_path, request, policy, ticket, rejected)
    assert first.receipt is not None
    assert first.receipt.recovery_state == "NEW_DECISION_REQUIRED"

    retry = SandboxAdapter(request)
    blocked = execute(tmp_path, request, policy, ticket, retry)
    assert blocked.status == "BLOCKED"
    assert blocked.reason == "PROVIDER_REJECTED_NEW_DECISION_REQUIRED"
    assert retry.call_count == 0


def test_changed_connector_args_are_blocked_before_adapter(tmp_path):
    request, _, policy, ticket = prepare_live(tmp_path)
    adapter = SandboxAdapter(request)
    changed = dict(request["connector_args"])
    changed["value"] = "tampered"

    result = execute(
        tmp_path,
        request,
        policy,
        ticket,
        adapter,
        connector_args=changed,
    )
    assert result.status == "BLOCKED"
    assert result.reason.startswith("GATEWAY_NOT_READY:")
    assert "connector_call_hash" in result.reason
    assert result.adapter_called is False
    assert adapter.call_count == 0


@pytest.mark.parametrize(
    "kwargs,reason",
    [
        (
            {"external_network_capable": True},
            "EXTERNAL_NETWORK_ADAPTER_FORBIDDEN_V0",
        ),
        (
            {"side_effect_free": False},
            "SIDE_EFFECTING_ADAPTER_FORBIDDEN_V0",
        ),
        (
            {"execution_mode": "REAL_NETWORK"},
            "REAL_CONNECTOR_EXECUTOR_NOT_BOUND_V0",
        ),
        (
            {"connector_id": "OTHER_CONNECTOR"},
            "CONNECTOR_ADAPTER_BINDING_MISMATCH",
        ),
    ],
)
def test_real_or_mismatched_adapters_are_blocked(
    tmp_path,
    kwargs,
    reason,
):
    request, _, policy, ticket = prepare_live(tmp_path)
    adapter = SandboxAdapter(request, **kwargs)

    result = execute(tmp_path, request, policy, ticket, adapter)
    assert result.status == "BLOCKED"
    assert result.reason == reason
    assert result.adapter_called is False
    assert adapter.call_count == 0
    assert result.network_call_performed is False
    assert result.real_external_effect is False


def test_receipt_tamper_breaks_verification_and_replay(tmp_path):
    request, _, policy, ticket = prepare_live(tmp_path)
    result = execute(
        tmp_path,
        request,
        policy,
        ticket,
        SandboxAdapter(request),
    )
    receipt = result.receipt
    assert receipt is not None

    stored = load_execution_receipt_v0(
        receipt.receipt_id,
        tmp_path / "receipts",
    )
    stored["connector_call_hash"] = "f" * 64
    ok, reason = verify_execution_receipt_v0(stored)
    assert ok is False
    assert reason == "EXECUTION_RECEIPT_HASH_MISMATCH"
