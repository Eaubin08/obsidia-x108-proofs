import datetime
import hashlib
import json
import sys
from dataclasses import replace
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
from periphery.world_calls.external_runtime_activation_policy_v0 import (  # noqa: E402
    build_activation_policy_v0,
    verify_activation_policy_v0,
)
from periphery.world_calls.live_sovereign_ticket_v0 import (  # noqa: E402
    LiveSovereignTicketError,
    issue_live_sovereign_ticket_v0,
    verify_live_sovereign_ticket_v0,
)
from periphery.world_calls.obsidia_live_gateway_v0 import (  # noqa: E402
    ObsidiaLiveGatewayV0,
)
from periphery.world_calls.sovereign_ticket import (  # noqa: E402
    issue_sovereign_ticket,
)
from scripts.kernel.kx108_runtime_link_facts_v1 import (  # noqa: E402
    MISSING_RUNTIME_LINK_REAL_EXECUTION,
    MISSING_RUNTIME_LINK_WORLD_ACTUATION,
    runtime_link_facts,
    world_action_live_gateway_capability_present,
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


def build_request(
    *,
    domain="administration",
    connector_id="CRM_TEST",
    connector_action="UPDATE_RECORD",
    required_scope="crm:write:test",
    target_ref="crm:test:customer-001",
    world_call_class="REVERSIBLE_WORLD_CALL",
    action_risk_class="ACTION_EXTERNAL_API",
    autonomy_level=4,
    irreversible=False,
):
    args = {
        "record_id": "customer-001",
        "field": "status",
        "value": "confirmed",
    }
    request = {
        "request_id": f"world-{domain}-live-001",
        "proposal_id": f"proposal-{domain}-live-001",
        "proposal_hash": canonical_hash({"proposal": domain, "live": True}),
        "domain_id": domain,
        "surface_id": "CRM",
        "operation_id": "UPDATE_RECORD",
        "effect_class": "EXTERNAL_DATA_MUTATION",
        "connector_id": connector_id,
        "connector_action": connector_action,
        "connector_args": args,
        "target_ref": target_ref,
        "target_prestate_hash": canonical_hash(
            {"target": target_ref, "status": "pending"}
        ),
        "required_scope": required_scope,
        "world_call_class": world_call_class,
        "action_risk_class": action_risk_class,
        "autonomy_level": autonomy_level,
        "irreversible": irreversible,
        "retry_policy": "NEVER_AUTORETRY_ON_UNKNOWN",
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
    }
    request["connector_call_hash"] = canonical_hash(
        {
            "connector_id": connector_id,
            "connector_action": connector_action,
            "connector_args": args,
        }
    )
    request["idempotency_key"] = canonical_hash(
        {
            "schema": "UNIVERSAL_WORLD_ACTION_IDEMPOTENCY_V0",
            "proposal_hash": request["proposal_hash"],
            "connector_call_hash": request["connector_call_hash"],
            "target_prestate_hash": request["target_prestate_hash"],
            "required_scope": required_scope,
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
        "approval_id": f"approval-{request['request_id']}",
        "approved_by": "HUMAN:TEST_OPERATOR",
        "approval_reference": f"review:{request['request_id']}",
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


def run_pre(tmp_path, request=None, *, unknowns=None, contradictions=None):
    request = request or build_request()
    result = run_world_action_pre_execution_v0(
        request=request,
        human_approval=build_approval(request),
        evidence_refs=["fixture:live-gateway"],
        unknowns=list(unknowns or []),
        contradictions=list(contradictions or []),
        context_store_dir=tmp_path / "contexts",
        decision_store_dir=tmp_path / "decisions",
    )
    return request, result


def active_policy(request, *, enabled=True):
    now = datetime.datetime.now(datetime.timezone.utc)
    return build_activation_policy_v0(
        policy_id="policy-live-test-v0",
        environment="TEST_ONLY",
        enabled=enabled,
        allowed_operations=[
            {
                "connector_id": request["connector_id"],
                "connector_action": request["connector_action"],
                "required_scope": request["required_scope"],
            }
        ],
        created_at=now.isoformat(),
        expires_at=(now + datetime.timedelta(hours=1)).isoformat(),
        operator_approval_ref="TEST_OPERATOR_EXPLICIT_ENABLE",
    )


def gateway_check(gateway, ticket, policy, request, **overrides):
    values = {
        "observed_connector_id": request["connector_id"],
        "observed_connector_action": request["connector_action"],
        "observed_connector_call_hash": request["connector_call_hash"],
        "observed_target_ref": request["target_ref"],
        "observed_target_prestate_hash": request["target_prestate_hash"],
        "observed_required_scope": request["required_scope"],
        "observed_idempotency_key": request["idempotency_key"],
    }
    values.update(overrides)
    return gateway.check(
        ticket=ticket,
        activation_policy=policy,
        **values,
    )


def test_activation_policy_is_disabled_by_default_semantics():
    request = build_request()
    policy = active_policy(request, enabled=False)
    ok, reason = verify_activation_policy_v0(policy)
    assert ok is False
    assert reason == "EXTERNAL_RUNTIME_ACTIVATION_DISABLED"


@pytest.mark.parametrize(
    "unsafe_world,unsafe_risk",
    [
        ("IRREVERSIBLE_WORLD_CALL", "ACTION_EXTERNAL_API"),
        ("CRITICAL_WORLD_CALL", "ACTION_EXTERNAL_API"),
        ("READ_ONLY_WORLD_CALL", "ACTION_FINANCIAL"),
    ],
)
def test_activation_policy_refuses_unsafe_live_classes(
    unsafe_world,
    unsafe_risk,
):
    request = build_request()
    now = datetime.datetime.now(datetime.timezone.utc)
    with pytest.raises(ValueError):
        build_activation_policy_v0(
            policy_id="unsafe-policy",
            environment="TEST_ONLY",
            enabled=True,
            allowed_operations=[
                (
                    request["connector_id"],
                    request["connector_action"],
                    request["required_scope"],
                )
            ],
            allowed_world_call_classes=[unsafe_world],
            allowed_action_risk_classes=[unsafe_risk],
            created_at=now.isoformat(),
            expires_at=(now + datetime.timedelta(hours=1)).isoformat(),
            operator_approval_ref="TEST_OPERATOR",
        )


def test_live_ticket_requires_verified_world_action_pre_allow(tmp_path):
    request, pre = run_pre(tmp_path)
    assert pre.x108_gate == "ALLOW"

    ticket = issue_live_sovereign_ticket_v0(
        decision_record_id=pre.decision_record_id,
        activation_policy=active_policy(request),
        decision_store_dir=tmp_path / "decisions",
        context_store_dir=tmp_path / "contexts",
    )
    ok, reason = verify_live_sovereign_ticket_v0(ticket)
    assert (ok, reason) == (True, None)
    assert ticket.x108_gate == "ALLOW"
    assert ticket.dry_run_only is False
    assert ticket.live_egress_preflight_capable is True
    assert ticket.executor_bound is False


def test_hold_pre_cannot_issue_live_ticket(tmp_path):
    request, pre = run_pre(
        tmp_path,
        unknowns=["OWNER_UNKNOWN", "TARGET_FRESHNESS_UNKNOWN"],
    )
    assert pre.x108_gate == "HOLD"

    with pytest.raises(
        LiveSovereignTicketError,
        match="LIVE_TICKET_KX108_GATE_NOT_ALLOW",
    ):
        issue_live_sovereign_ticket_v0(
            decision_record_id=pre.decision_record_id,
            activation_policy=active_policy(request),
            decision_store_dir=tmp_path / "decisions",
            context_store_dir=tmp_path / "contexts",
        )


def test_disabled_or_tampered_policy_cannot_issue_ticket(tmp_path):
    request, pre = run_pre(tmp_path)

    with pytest.raises(
        LiveSovereignTicketError,
        match="EXTERNAL_RUNTIME_ACTIVATION_DISABLED",
    ):
        issue_live_sovereign_ticket_v0(
            decision_record_id=pre.decision_record_id,
            activation_policy=active_policy(request, enabled=False),
            decision_store_dir=tmp_path / "decisions",
            context_store_dir=tmp_path / "contexts",
        )

    valid = active_policy(request)
    tampered = replace(valid, policy_hash="0" * 64)
    with pytest.raises(
        LiveSovereignTicketError,
        match="ACTIVATION_POLICY_HASH_MISMATCH",
    ):
        issue_live_sovereign_ticket_v0(
            decision_record_id=pre.decision_record_id,
            activation_policy=tampered,
            decision_store_dir=tmp_path / "decisions",
            context_store_dir=tmp_path / "contexts",
        )


def test_policy_operation_scope_must_match_exactly(tmp_path):
    request, pre = run_pre(tmp_path)
    now = datetime.datetime.now(datetime.timezone.utc)
    wrong = build_activation_policy_v0(
        policy_id="wrong-scope",
        environment="TEST_ONLY",
        enabled=True,
        allowed_operations=[
            (
                request["connector_id"],
                request["connector_action"],
                "crm:read:test",
            )
        ],
        created_at=now.isoformat(),
        expires_at=(now + datetime.timedelta(hours=1)).isoformat(),
        operator_approval_ref="TEST_OPERATOR",
    )
    with pytest.raises(
        LiveSovereignTicketError,
        match="ACTIVATION_POLICY_OPERATION_NOT_ALLOWED",
    ):
        issue_live_sovereign_ticket_v0(
            decision_record_id=pre.decision_record_id,
            activation_policy=wrong,
            decision_store_dir=tmp_path / "decisions",
            context_store_dir=tmp_path / "contexts",
        )


def test_live_gateway_exact_preflight_ready_but_no_egress(tmp_path):
    request, pre = run_pre(tmp_path)
    policy = active_policy(request)
    ticket = issue_live_sovereign_ticket_v0(
        decision_record_id=pre.decision_record_id,
        activation_policy=policy,
        decision_store_dir=tmp_path / "decisions",
        context_store_dir=tmp_path / "contexts",
    )

    decision = gateway_check(
        ObsidiaLiveGatewayV0(),
        ticket,
        policy,
        request,
    )
    assert decision.gate_result == "LIVE_PREFLIGHT_READY"
    assert decision.egress_preflight_allowed is True
    assert decision.egress_allowed is False
    assert decision.executor_bound is False
    assert decision.network_call_performed is False
    assert decision.decision_authority == "KX108_ONLY"


@pytest.mark.parametrize(
    "field,value",
    [
        ("observed_connector_id", "OTHER_CONNECTOR"),
        ("observed_connector_action", "OTHER_ACTION"),
        ("observed_connector_call_hash", "1" * 64),
        ("observed_target_ref", "crm:test:other"),
        ("observed_target_prestate_hash", "2" * 64),
        ("observed_required_scope", "crm:admin"),
        ("observed_idempotency_key", "3" * 64),
    ],
)
def test_live_gateway_blocks_any_exact_binding_change(
    tmp_path,
    field,
    value,
):
    request, pre = run_pre(tmp_path)
    policy = active_policy(request)
    ticket = issue_live_sovereign_ticket_v0(
        decision_record_id=pre.decision_record_id,
        activation_policy=policy,
        decision_store_dir=tmp_path / "decisions",
        context_store_dir=tmp_path / "contexts",
    )

    decision = gateway_check(
        ObsidiaLiveGatewayV0(),
        ticket,
        policy,
        request,
        **{field: value},
    )
    assert decision.gate_result == "BLOCK"
    assert decision.egress_preflight_allowed is False
    assert decision.egress_allowed is False
    assert decision.network_call_performed is False


def test_legacy_dry_run_ticket_is_rejected_by_live_gateway():
    legacy = issue_sovereign_ticket(
        action_id="legacy",
        os3_ticket_id="os3-legacy",
        x108_gate="ALLOW",
        scope="crm:write:test",
        autonomy_level=4,
        world_call_class="REVERSIBLE_WORLD_CALL",
    )
    request = build_request()
    policy = active_policy(request)
    decision = gateway_check(
        ObsidiaLiveGatewayV0(),
        legacy,
        policy,
        request,
    )
    assert decision.gate_result == "BLOCK"
    assert decision.reason == "NON_LIVE_TICKET_REJECTED"


def test_expired_live_ticket_is_blocked(tmp_path):
    request, pre = run_pre(tmp_path)
    policy = active_policy(request)
    issued = datetime.datetime.now(datetime.timezone.utc)
    ticket = issue_live_sovereign_ticket_v0(
        decision_record_id=pre.decision_record_id,
        activation_policy=policy,
        decision_store_dir=tmp_path / "decisions",
        context_store_dir=tmp_path / "contexts",
        ttl_seconds=1,
        now=issued.isoformat(),
    )
    decision = gateway_check(
        ObsidiaLiveGatewayV0(),
        ticket,
        policy,
        request,
        now=(issued + datetime.timedelta(seconds=2)).isoformat(),
    )
    assert decision.gate_result == "BLOCK"
    assert "LIVE_TICKET_EXPIRED" in decision.reason
    assert decision.egress_allowed is False



def test_runtime_facts_show_live_capability_without_activation():
    facts = runtime_link_facts()
    assert world_action_live_gateway_capability_present() is True
    assert facts["world_action_live_gateway_capability_present"] is True
    assert facts["world_action_runtime_activated"] is False
    assert facts["execution_authority"] is False
    assert facts["emits_act"] is False
    assert MISSING_RUNTIME_LINK_WORLD_ACTUATION in facts["missing_runtime_links"]
    assert MISSING_RUNTIME_LINK_REAL_EXECUTION in facts["missing_runtime_links"]
