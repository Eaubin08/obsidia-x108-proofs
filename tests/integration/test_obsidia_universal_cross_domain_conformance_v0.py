"""Composed universal stack + multi-métier KX108 proof. All inputs simulated.

This suite does NOT infer actual business semantics or grant real actuation.
It reuses the existing 16-scenario cross-métier fixture and the unchanged
KX108 WORLD_ACTION_PRE / LIVE policy / executor / replay implementations.
"""
from __future__ import annotations

import datetime
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
for folder in (ROOT, SCRIPTS):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from obsidia_world_action_pre_execution_v0 import run_world_action_pre_execution_v0
from periphery.common import ActionCandidate
from periphery.native_ops.common_v0 import canonical_hash
from periphery.native_ops.native_work_to_action_projection_v0 import (
    build_world_action_request_from_action_candidate_v0,
)
from periphery.native_ops.world_action_bridge_v0 import (
    build_native_human_approval_v0,
)
from periphery.universal_enterprise_stack_adapter_v0 import (
    build_enterprise_action_binding_v0,
    build_enterprise_action_capability_v0,
    build_enterprise_stack_manifest_v0,
    build_world_action_request_from_enterprise_binding_v0,
    provider_swap_invariant_v0,
    stable_business_intent_hash_v0,
    verify_enterprise_action_binding_v0,
)
from periphery.world_calls.bounded_connector_executor_v0 import (
    ConnectorProviderOutcomeV0,
    OUTCOME_CONFIRMED_SUCCESS,
    execute_bounded_connector_v0,
    replay_execution_receipt_v0,
)
from periphery.world_calls.external_runtime_activation_policy_v0 import (
    build_activation_policy_v0,
)
from periphery.world_calls.live_sovereign_ticket_v0 import (
    issue_live_sovereign_ticket_v0,
    LiveSovereignTicketError,
)

MATRIX = ROOT / "tests/fixtures/world_action_multidomain_conformance_v0.json"
FIXTURE = json.loads(MATRIX.read_text(encoding="utf-8"))
assert FIXTURE["status"] == "SIMULATED_NOT_OBSERVED"
BY_ID = {x["case_id"]: x for x in FIXTURE["cases"]}

# The selection is anchored to the existing 16-scenario universal rail proof.
ALLOWED = (
    "ADMIN_CRM_MEMBER_UPDATE",
    "ECOM_CRM_CUSTOMER_UPDATE",
    "TRADING_TASK_RISK_REVIEW",
)
HOLD_CASE = "PEOPLE_AUTHORITY_UNKNOWN"
GPS_CASE = "GPS_DEVICE_COMMAND"
FINANCE_CASE = "FINANCE_PAYMENT"

CAPABILITY = {
    "CRM": "CRM.RECORD.UPDATE",
    "TASKS": "TASKS.ITEM.CREATE",
    "PAYMENT": "PAYMENT.TRANSFER.ISSUE",
    "DEVICE": "DEVICE.CONFIG.CHANGE",
}
PROVIDERS = ("NATIVE_SANDBOX", "EXTERNAL_SANDBOX")


def candidate_for(case: dict) -> ActionCandidate:
    return ActionCandidate(
        action_id="cross:" + case["case_id"].lower(),
        domain=case["domain_id"],
        actor_id="OBSIDIA:SIMULATED_DOMAIN_ADAPTER",
        intent=case["operation_id"],
        action_type="SIMULATED:" + case["surface_id"],
        irreversible=case["irreversible"],
        timestamp_plan="2026-10-08T08:00:00+00:00",
        payload={
            "surface_id": case["surface_id"],
            "operation_id": case["operation_id"],
            "fixture_case_id": case["case_id"],
            "evidence_class": "SIMULATED_NOT_OBSERVED",
        },
    )


def manifest_for(case: dict, provider: str, *, autonomy_level: int | None = None):
    assert provider in PROVIDERS
    return build_enterprise_stack_manifest_v0(
        stack_id="cross:" + provider.lower(),
        provider_id=provider,
        action_capabilities=(
            build_enterprise_action_capability_v0(
                capability_id=CAPABILITY[case["surface_id"]],
                surface_id=case["surface_id"],
                operation_id=case["operation_id"],
                connector_id=provider + "_" + case["surface_id"],
                connector_action=case["connector_action"],
                required_scope=case["required_scope"],
                effect_class=case["effect_class"],
                world_call_class=case["world_call_class"],
                action_risk_class=case["action_risk_class"],
                autonomy_level=(
                    case["autonomy_level"]
                    if autonomy_level is None else autonomy_level
                ),
                adapter_ref="fixture:" + provider.lower(),
            ),
        ),
    )


def bind(case: dict, candidate: ActionCandidate, manifest):
    capability = CAPABILITY[case["surface_id"]]
    return build_enterprise_action_binding_v0(
        candidate=candidate,
        capability_id=capability,
        manifest=manifest,
        connector_args={
            "case_id": case["case_id"],
            "domain_id": case["domain_id"],
            "fixture_only": True,
        },
        target_ref=(
            f"sim:{manifest.provider_id.lower()}:{case['domain_id']}:"
            f"{case['case_id'].lower()}"
        ),
        target_prestate_hash=canonical_hash({
            "provider_id": manifest.provider_id,
            "case_id": case["case_id"],
            "prestate": "SANDBOX_UNCHANGED",
        }),
    )


def request_for(case: dict, provider: str):
    candidate = candidate_for(case)
    manifest = manifest_for(case, provider)
    binding = bind(case, candidate, manifest)
    assert verify_enterprise_action_binding_v0(
        binding, candidate=candidate, manifest=manifest
    ) == (True, None)
    request = build_world_action_request_from_enterprise_binding_v0(
        candidate=candidate, manifest=manifest, binding=binding
    )
    assert request["domain_id"] == case["domain_id"]
    assert request["allowed_to_decide"] is False
    assert request["allowed_to_act"] is False
    assert request["emits_act"] is False
    assert request["decision_authority"] == "KX108_ONLY"
    return candidate, manifest, binding, request


def pre_for(case, binding, request, root):
    approval = build_native_human_approval_v0(
        request,
        approval_id="approval:" + binding.binding_id,
        approved_by="HUMAN:SIMULATED_OPERATOR",
        approval_reference="cross-domain:fixture:" + case["case_id"],
    )
    return run_world_action_pre_execution_v0(
        request=request,
        human_approval=approval,
        unknowns=case.get("pre_unknowns", []),
        contradictions=case.get("pre_contradictions", []),
        evidence_refs=[
            "fixture:SIMULATED_NOT_OBSERVED",
            "stable-intent:" + binding.stable_intent_hash,
            "provider-binding:" + binding.binding_hash,
        ],
        context_store_dir=root / "contexts",
        decision_store_dir=root / "decisions",
    )


class NoNetworkAdapter:
    execution_mode = "SANDBOX_DETERMINISTIC"
    external_network_capable = False
    side_effect_free = True
    retry_after_confirmed_no_effect = False

    def __init__(self, binding):
        self.connector_id = binding.connector_id
        self.connector_action = binding.connector_action
        self.required_scope = binding.required_scope
        self.provider_id = "SANDBOX:" + binding.provider_id
        self.calls = 0

    def execute(self, connector_args):
        self.calls += 1
        digest = canonical_hash({
            "provider": self.provider_id,
            "args": dict(connector_args),
        })
        return ConnectorProviderOutcomeV0(
            status=OUTCOME_CONFIRMED_SUCCESS,
            provider_receipt_ref="sandbox:" + digest[:20],
            provider_state_ref="sandbox-state:" + digest[20:40],
            detail_digest=digest,
            observed_at=datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
        )


def policy_for(case, binding):
    now = datetime.datetime.now(datetime.timezone.utc)
    return build_activation_policy_v0(
        policy_id="cross:" + case["case_id"].lower() + ":" +
                  binding.provider_id.lower(),
        environment="UNIVERSAL_CROSS_DOMAIN_SANDBOX",
        enabled=True,
        allowed_operations=[(
            binding.connector_id,
            binding.connector_action,
            binding.required_scope,
        )],
        allowed_world_call_classes=(binding.world_call_class,),
        allowed_action_risk_classes=(binding.action_risk_class,),
        max_autonomy_level=binding.autonomy_level,
        created_at=(now - datetime.timedelta(hours=1)).isoformat(),
        expires_at=(now + datetime.timedelta(hours=1)).isoformat(),
        operator_approval_ref="HUMAN:SANDBOX_OPERATOR",
    )


def test_legacy_matrix_is_full_cross_domain_baseline():
    assert len(FIXTURE["cases"]) == 16
    assert len({x["domain_id"] for x in FIXTURE["cases"]}) >= 10
    assert {x["expected_pre_gate"] for x in FIXTURE["cases"]} == {
        "ALLOW", "HOLD", "BLOCK"
    }
    for key in (*ALLOWED, HOLD_CASE, GPS_CASE, FINANCE_CASE):
        assert key in BY_ID
    assert all(
        BY_ID[key]["expected_stage"] == "EXECUTOR_PASS"
        for key in ALLOWED
    )


@pytest.mark.parametrize("case_id", ALLOWED)
def test_same_domain_intent_survives_native_external_provider_swap(case_id):
    case = BY_ID[case_id]
    candidate = candidate_for(case)
    manifests = [manifest_for(case, p) for p in PROVIDERS]
    bindings = tuple(bind(case, candidate, m) for m in manifests)
    assert provider_swap_invariant_v0(
        candidate=candidate,
        capability_id=CAPABILITY[case["surface_id"]],
        bindings=bindings,
    ) == (True, None)
    stable = stable_business_intent_hash_v0(
        candidate, capability_id=CAPABILITY[case["surface_id"]]
    )
    assert {x.stable_intent_hash for x in bindings} == {stable}
    assert len({x.manifest_hash for x in bindings}) == 2
    assert len({x.binding_hash for x in bindings}) == 2
    requests = [
        build_world_action_request_from_enterprise_binding_v0(
            candidate=candidate, manifest=m, binding=b
        )
        for m, b in zip(manifests, bindings)
    ]
    assert len({x["proposal_hash"] for x in requests}) == 1
    assert len({x["request_hash"] for x in requests}) == 2
    assert len({x["idempotency_key"] for x in requests}) == 2
    assert {x["domain_id"] for x in requests} == {case["domain_id"]}


@pytest.mark.parametrize("case_id", ALLOWED)
@pytest.mark.parametrize("provider", PROVIDERS)
def test_composed_cross_domain_execution_and_receipt_replay(tmp_path, case_id, provider):
    case = BY_ID[case_id]
    _, _, binding, request = request_for(case, provider)
    root = tmp_path / case_id.lower() / provider.lower()
    pre = pre_for(case, binding, request, root)
    assert pre.x108_gate == "ALLOW"
    assert pre.source_domain == case["domain_id"]
    assert pre.decision_authority == "KX108_ONLY"
    assert pre.egress_allowed is False
    assert pre.world_action_runtime_activated is False

    policy = policy_for(case, binding)
    ticket = issue_live_sovereign_ticket_v0(
        decision_record_id=pre.decision_record_id,
        activation_policy=policy,
        decision_store_dir=root / "decisions",
        context_store_dir=root / "contexts",
    )
    assert ticket.source_domain == case["domain_id"]
    adapter = NoNetworkAdapter(binding)
    args = {
        "ticket": ticket,
        "activation_policy": policy,
        "connector_args": request["connector_args"],
        "observed_target_ref": request["target_ref"],
        "observed_target_prestate_hash": request["target_prestate_hash"],
        "adapter": adapter,
        "receipt_store_dir": root / "receipts",
        "reconciliation_store_dir": root / "reconciliations",
    }
    result = execute_bounded_connector_v0(**args)
    assert result.status == "SANDBOX_EXECUTED_RECEIPT_STORED"
    assert result.network_call_performed is False
    assert result.real_external_effect is False
    assert result.receipt is not None
    assert result.receipt.source_domain == case["domain_id"]
    assert result.receipt.decision_authority == "KX108_ONLY"
    assert result.receipt.sandbox_execution is True
    assert replay_execution_receipt_v0(
        result.receipt.receipt_id,
        store_dir=root / "receipts",
        expected_ticket_hash=ticket.ticket_hash,
        expected_connector_call_hash=ticket.connector_call_hash,
        expected_idempotency_key=ticket.idempotency_key,
    ) == (True, None)
    repeat = execute_bounded_connector_v0(**args)
    assert repeat.adapter_called is False
    assert repeat.real_external_effect is False
    assert adapter.calls == 1


@pytest.mark.parametrize("provider", PROVIDERS)
def test_cross_domain_unknown_role_holds_without_ticket(tmp_path, provider):
    case = BY_ID[HOLD_CASE]
    _, _, binding, request = request_for(case, provider)
    root = tmp_path / provider
    pre = pre_for(case, binding, request, root)
    assert pre.x108_gate == "HOLD"
    assert pre.egress_allowed is False
    with pytest.raises(LiveSovereignTicketError, match="LIVE_TICKET_KX108_GATE_NOT_ALLOW"):
        issue_live_sovereign_ticket_v0(
            decision_record_id=pre.decision_record_id,
            activation_policy=policy_for(case, binding),
            decision_store_dir=root / "decisions",
            context_store_dir=root / "contexts",
        )


def test_gps_defense_high_autonomy_cannot_be_bound_to_live_provider():
    case = BY_ID[GPS_CASE]
    assert case["expected_pre_gate"] == "BLOCK"
    assert case["world_call_class"] == "CRITICAL_WORLD_CALL"
    with pytest.raises(ValueError, match="ENTERPRISE_ACTION_AUTONOMY_LEVEL_UNSUPPORTED"):
        manifest_for(case, PROVIDERS[0])


def test_gps_defense_critical_action_is_blocked_by_same_kx108_pre(tmp_path):
    case = BY_ID[GPS_CASE]
    candidate = candidate_for(case)
    request = build_world_action_request_from_action_candidate_v0(
        candidate,
        connector_id="SIMULATED_GPS_DEVICE",
        connector_action=case["connector_action"],
        connector_args={"fixture":"SIMULATED_NOT_OBSERVED"},
        target_ref="sim:gps:defense:receiver",
        target_prestate_hash=canonical_hash({"receiver":"UNCHANGED"}),
        required_scope=case["required_scope"],
        effect_class=case["effect_class"],
        world_call_class=case["world_call_class"],
        action_risk_class=case["action_risk_class"],
        autonomy_level=case["autonomy_level"],
    )
    approval = build_native_human_approval_v0(
        request,approval_id="approval:gps-fixture",
        approved_by="HUMAN:SIMULATED_OPERATOR",
        approval_reference="simulation:gps",
    )
    pre=run_world_action_pre_execution_v0(
        request=request,human_approval=approval,
        evidence_refs=["fixture:SIMULATED_NOT_OBSERVED"],
        context_store_dir=tmp_path/"contexts",
        decision_store_dir=tmp_path/"decisions",
    )
    assert pre.x108_gate == "BLOCK"
    assert pre.egress_allowed is False
    assert pre.source_domain == "gps_defense_aviation"


def test_finance_payment_pre_allow_does_not_bypass_live_policy(tmp_path):
    case=BY_ID[FINANCE_CASE]
    _,_,binding,request=request_for(case,PROVIDERS[0])
    root=tmp_path/"finance"
    pre=pre_for(case,binding,request,root)
    assert pre.x108_gate == "ALLOW"
    assert pre.egress_allowed is False
    with pytest.raises(ValueError,match="ACTIVATION_POLICY_UNSAFE_ACTION_RISK_CLASS"):
        policy_for(case,binding)


def test_tampered_provider_binding_fails_closed_before_kx108():
    case=BY_ID[ALLOWED[0]]
    candidate,manifest,binding,_=request_for(case,PROVIDERS[0])
    tampered=replace(binding,provider_id="MALICIOUS_SWAP")
    assert verify_enterprise_action_binding_v0(
        tampered,candidate=candidate,manifest=manifest
    )[0] is False
    with pytest.raises(ValueError,match="ENTERPRISE_ACTION_BINDING_MANIFEST_MISMATCH"):
        build_world_action_request_from_enterprise_binding_v0(
            candidate=candidate,manifest=manifest,binding=tampered
        )


def test_cross_domain_approval_cannot_be_replayed_for_other_intent():
    admin=BY_ID[ALLOWED[0]]
    ecom=BY_ID[ALLOWED[1]]
    admin_request=request_for(admin,PROVIDERS[0])[3]
    ecom_request=request_for(ecom,PROVIDERS[0])[3]
    assert admin_request["proposal_hash"] != ecom_request["proposal_hash"]
    assert admin_request["request_hash"] != ecom_request["request_hash"]
    assert admin_request["idempotency_key"] != ecom_request["idempotency_key"]
    assert admin_request["domain_id"] != ecom_request["domain_id"]


def test_universal_stack_cannot_forge_unknown_provider_capability():
    case=BY_ID[ALLOWED[0]]
    candidate=candidate_for(case)
    manifest=manifest_for(case,PROVIDERS[0])
    with pytest.raises(ValueError,match="ENTERPRISE_ACTION_CAPABILITY_UNAVAILABLE"):
        build_enterprise_action_binding_v0(
            candidate=candidate,capability_id="BANK.TRANSFER.EXECUTE",
            manifest=manifest,connector_args={},
            target_ref="sim:bank:transfer",
            target_prestate_hash=canonical_hash({"state":"ABSENT"}),
        )
