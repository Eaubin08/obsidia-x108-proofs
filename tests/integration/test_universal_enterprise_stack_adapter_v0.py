import datetime
import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
for candidate_path in (ROOT, SCRIPTS):
    if str(candidate_path) not in sys.path:
        sys.path.insert(0, str(candidate_path))

from obsidia_world_action_pre_execution_v0 import run_world_action_pre_execution_v0
from periphery.common import ActionCandidate
from periphery.native_ops.common_v0 import NativeEntityStoreV0, canonical_hash
from periphery.native_ops.native_work_to_action_projection_v0 import (
    project_native_work_to_action_v0,
)
from periphery.native_ops.world_action_bridge_v0 import (
    build_native_human_approval_v0,
)
from periphery.native_sources.common_v0 import SOURCE_API_READONLY, SOURCE_MAILBOX
from periphery.native_sources.enterprise_office_interpreted_e2e_v0 import (
    run_interpreted_autonomous_office_e2e_v0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    materialize_enterprise_source_sandbox_v0,
)
from periphery.native_sources.source_onboarding_v0 import (
    verify_native_observed_source_candidate_v0,
)
from periphery.universal_enterprise_stack_adapter_v0 import (
    build_enterprise_action_binding_v0,
    build_enterprise_action_capability_v0,
    build_enterprise_source_binding_v0,
    build_enterprise_source_capability_v0,
    build_enterprise_stack_manifest_v0,
    build_native_source_candidate_from_enterprise_binding_v0,
    build_world_action_request_from_enterprise_binding_v0,
    provider_swap_invariant_v0,
    stable_business_intent_hash_v0,
    verify_enterprise_action_binding_v0,
    verify_enterprise_stack_manifest_v0,
)
import periphery.universal_enterprise_stack_adapter_v0 as stack_module
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
)

CAPABILITY = "CALENDAR.EVENT.CREATE"


def make_manifest(provider_id):
    configs = {
        "GOOGLE_LIKE": (
            "GOOGLE_LIKE_CALENDAR", "EVENTS_INSERT",
            "calendar:event:create", "adapter:google-like:calendar",
        ),
        "MICROSOFT_LIKE": (
            "MICROSOFT_LIKE_CALENDAR", "GRAPH_EVENT_CREATE",
            "calendar:event:create", "adapter:microsoft-like:calendar",
        ),
        "CUSTOM_LIKE": (
            "CUSTOM_LIKE_CALDAV", "CALDAV_PUT_EVENT",
            "calendar:event:create", "adapter:custom-like:calendar",
        ),
    }
    connector_id, action, scope, adapter_ref = configs[provider_id]
    source_mail = build_enterprise_source_capability_v0(
        capability_id="SOURCE.MAIL.READ",
        source_kind=SOURCE_MAILBOX,
        native_read_capabilities=("SEARCH", "READ_MESSAGE"),
        adapter_ref=f"adapter:{provider_id.lower()}:mail",
    )
    source_api = build_enterprise_source_capability_v0(
        capability_id="SOURCE.API.READ",
        source_kind=SOURCE_API_READONLY,
        native_read_capabilities=("READ_API_RESOURCE",),
        adapter_ref=f"adapter:{provider_id.lower()}:api",
    )
    calendar = build_enterprise_action_capability_v0(
        capability_id=CAPABILITY,
        surface_id="CALENDAR",
        operation_id="CREATE_EVENT",
        connector_id=connector_id,
        connector_action=action,
        required_scope=scope,
        effect_class="EXTERNAL_DATA_MUTATION",
        world_call_class="REVERSIBLE_WORLD_CALL",
        action_risk_class="ACTION_PLAN",
        autonomy_level=3,
        adapter_ref=adapter_ref,
    )
    return build_enterprise_stack_manifest_v0(
        stack_id=f"stack:{provider_id.lower()}",
        provider_id=provider_id,
        source_capabilities=(source_mail, source_api),
        action_capabilities=(calendar,),
    )


def native_calendar_candidate(tmp_path):
    paths = materialize_enterprise_source_sandbox_v0(tmp_path / "enterprise")
    office = run_interpreted_autonomous_office_e2e_v0(
        paths=paths,
        runtime_root=tmp_path / "runtime",
        native_store_root=tmp_path / "native",
        governance_root=tmp_path / "governance",
    )
    work = office["results"]["mail-action-001"]
    projection = project_native_work_to_action_v0(
        store=NativeEntityStoreV0(tmp_path / "native"),
        case_id=work["case_id"],
        task_id=work["task_id"],
        followup_id=work["followup_id"],
    )
    assert projection.action_candidate is not None
    return projection.action_candidate


def bind(candidate, manifest):
    return build_enterprise_action_binding_v0(
        candidate=candidate,
        capability_id=CAPABILITY,
        manifest=manifest,
        connector_args={
            "title": candidate.payload["title"],
            "due_at": candidate.payload["due_at"],
            "canonical_capability": CAPABILITY,
        },
        target_ref=f"sim:{manifest.provider_id.lower()}:calendar:event",
        target_prestate_hash=canonical_hash({
            "provider": manifest.provider_id,
            "target": "calendar:event",
            "state": "ABSENT",
        }),
    )


class ProviderNeutralSandboxAdapter:
    execution_mode = "SANDBOX_DETERMINISTIC"
    external_network_capable = False
    side_effect_free = True
    retry_after_confirmed_no_effect = False

    def __init__(self, manifest, binding):
        self.connector_id = binding.connector_id
        self.connector_action = binding.connector_action
        self.required_scope = binding.required_scope
        self.provider_id = f"SANDBOX:{manifest.provider_id}"
        self.call_count = 0

    def execute(self, connector_args):
        self.call_count += 1
        digest = canonical_hash({
            "provider_id": self.provider_id,
            "args": dict(connector_args),
        })
        return ConnectorProviderOutcomeV0(
            status=OUTCOME_CONFIRMED_SUCCESS,
            provider_receipt_ref=f"provider-receipt:{digest[:24]}",
            provider_state_ref=f"provider-state:{digest[24:48]}",
            detail_digest=digest,
            observed_at="2026-10-07T12:00:01+00:00",
        )


def test_manifests_are_provider_specific_but_non_sovereign():
    manifests = [make_manifest(x) for x in (
        "GOOGLE_LIKE", "MICROSOFT_LIKE", "CUSTOM_LIKE"
    )]
    assert len({x.manifest_hash for x in manifests}) == 3
    for manifest in manifests:
        assert verify_enterprise_stack_manifest_v0(manifest) == (True, None)
        assert manifest.allowed_to_decide is False
        assert manifest.allowed_to_act is False
        assert manifest.emits_act is False
        assert manifest.raw_credentials_persisted is False
        assert manifest.decision_authority == "KX108_ONLY"


def test_provider_swap_keeps_business_intent_stable(tmp_path):
    candidate = native_calendar_candidate(tmp_path)
    manifests = [make_manifest(x) for x in (
        "GOOGLE_LIKE", "MICROSOFT_LIKE", "CUSTOM_LIKE"
    )]
    bindings = tuple(bind(candidate, manifest) for manifest in manifests)
    stable = stable_business_intent_hash_v0(
        candidate, capability_id=CAPABILITY
    )
    assert {x.stable_intent_hash for x in bindings} == {stable}
    assert len({x.binding_hash for x in bindings}) == 3
    assert provider_swap_invariant_v0(
        candidate=candidate,
        capability_id=CAPABILITY,
        bindings=bindings,
    ) == (True, None)

    requests = [
        build_world_action_request_from_enterprise_binding_v0(
            candidate=candidate, manifest=manifest, binding=binding
        )
        for manifest, binding in zip(manifests, bindings)
    ]
    assert len({x["proposal_hash"] for x in requests}) == 1
    assert len({x["request_hash"] for x in requests}) == 3
    assert {x["surface_id"] for x in requests} == {"CALENDAR"}
    assert {x["operation_id"] for x in requests} == {"CREATE_EVENT"}


def test_each_provider_binding_reaches_same_kx108_gate_and_replay(tmp_path):
    candidate = native_calendar_candidate(tmp_path / "office")
    manifests = [make_manifest(x) for x in (
        "GOOGLE_LIKE", "MICROSOFT_LIKE", "CUSTOM_LIKE"
    )]
    gates = []

    for manifest in manifests:
        binding = bind(candidate, manifest)
        assert verify_enterprise_action_binding_v0(
            binding, candidate=candidate, manifest=manifest
        ) == (True, None)
        request = build_world_action_request_from_enterprise_binding_v0(
            candidate=candidate, manifest=manifest, binding=binding
        )
        approval = build_native_human_approval_v0(
            request,
            approval_id=f"approval:{binding.binding_id}",
            approved_by="HUMAN:SANDBOX_OPERATOR",
            approval_reference=f"provider-swap:{manifest.provider_id}",
        )
        root = tmp_path / manifest.provider_id.lower()
        pre = run_world_action_pre_execution_v0(
            request=request,
            human_approval=approval,
            evidence_refs=[
                f"stable-intent:{binding.stable_intent_hash}",
                f"provider-binding:{binding.binding_hash}",
            ],
            context_store_dir=root / "contexts",
            decision_store_dir=root / "decisions",
        )
        gates.append(pre.x108_gate)

        now = datetime.datetime.fromisoformat("2026-10-07T12:00:00+00:00")
        policy = build_activation_policy_v0(
            policy_id=f"policy:{manifest.provider_id.lower()}",
            environment="UNIVERSAL_ENTERPRISE_STACK_SANDBOX",
            enabled=True,
            allowed_operations=[(
                binding.connector_id,
                binding.connector_action,
                binding.required_scope,
            )],
            allowed_world_call_classes=(binding.world_call_class,),
            allowed_action_risk_classes=(binding.action_risk_class,),
            max_autonomy_level=binding.autonomy_level,
            created_at="2026-10-01T00:00:00+00:00",
            expires_at="2099-01-01T00:00:00+00:00",
            operator_approval_ref=f"HUMAN:STACK:{manifest.provider_id}",
        )
        ticket = issue_live_sovereign_ticket_v0(
            decision_record_id=pre.decision_record_id,
            activation_policy=policy,
            decision_store_dir=root / "decisions",
            context_store_dir=root / "contexts",
            now=now.isoformat(),
        )
        adapter = ProviderNeutralSandboxAdapter(manifest, binding)
        result = execute_bounded_connector_v0(
            ticket=ticket,
            activation_policy=policy,
            connector_args=request["connector_args"],
            observed_target_ref=request["target_ref"],
            observed_target_prestate_hash=request["target_prestate_hash"],
            adapter=adapter,
            receipt_store_dir=root / "receipts",
            reconciliation_store_dir=root / "reconciliations",
            now=now.isoformat(),
        )
        assert result.status == "SANDBOX_EXECUTED_RECEIPT_STORED"
        assert result.network_call_performed is False
        assert result.real_external_effect is False
        assert result.receipt is not None
        assert replay_execution_receipt_v0(
            result.receipt.receipt_id,
            store_dir=root / "receipts",
            expected_ticket_hash=ticket.ticket_hash,
            expected_connector_call_hash=ticket.connector_call_hash,
            expected_idempotency_key=ticket.idempotency_key,
        ) == (True, None)

    assert gates == ["ALLOW", "ALLOW", "ALLOW"]


def test_source_binding_enters_existing_native_source_contract():
    manifest = make_manifest("CUSTOM_LIKE")
    binding = build_enterprise_source_binding_v0(
        manifest=manifest,
        capability_id="SOURCE.MAIL.READ",
        source_identity_sha256=canonical_hash({"mailbox": "support"}),
        connector_reference="connector:custom-like:mailbox",
    )
    candidate = build_native_source_candidate_from_enterprise_binding_v0(
        binding=binding,
        candidate_id="candidate:custom-like:mailbox",
        observed_at="2026-10-07T12:00:00+00:00",
    )
    assert verify_native_observed_source_candidate_v0(candidate) == (True, None)
    assert candidate.provider == "CUSTOM_LIKE"
    assert candidate.source_kind == SOURCE_MAILBOX
    assert set(candidate.observed_capabilities) == {"SEARCH", "READ_MESSAGE"}
    assert candidate.allowed_to_decide is False
    assert candidate.allowed_to_act is False
    assert candidate.raw_credentials_persisted is False


def test_generic_api_read_source_accepts_custom_enterprise_tool():
    manifest = make_manifest("CUSTOM_LIKE")
    binding = build_enterprise_source_binding_v0(
        manifest=manifest,
        capability_id="SOURCE.API.READ",
        source_identity_sha256=canonical_hash({"service": "erp-house"}),
        connector_reference="connector:custom-like:erp-house",
    )
    candidate = build_native_source_candidate_from_enterprise_binding_v0(
        binding=binding,
        candidate_id="candidate:custom-like:erp-house",
        observed_at="2026-10-07T12:00:00+00:00",
    )
    assert candidate.source_kind == SOURCE_API_READONLY
    assert candidate.observed_capabilities == ("READ_API_RESOURCE",)


def test_non_calendar_capability_uses_same_binding_contract():
    candidate = ActionCandidate(
        action_id="action:crm:001",
        domain="native_operations",
        actor_id="OBSIDIA_TEST",
        intent="UPDATE_CUSTOMER_CASE",
        action_type="CRM_UPDATE_RECORD",
        irreversible=False,
        timestamp_plan="2026-10-07T12:00:00+00:00",
        payload={
            "surface_id": "CRM",
            "operation_id": "UPDATE_RECORD",
            "record_id": "case-001",
        },
    )
    capability = build_enterprise_action_capability_v0(
        capability_id="CRM.RECORD.UPDATE",
        surface_id="CRM",
        operation_id="UPDATE_RECORD",
        connector_id="CUSTOM_CRM",
        connector_action="PATCH_RECORD",
        required_scope="crm:record:update",
        effect_class="EXTERNAL_DATA_MUTATION",
        world_call_class="REVERSIBLE_WORLD_CALL",
        action_risk_class="ACTION_EXTERNAL_API",
        autonomy_level=3,
        adapter_ref="adapter:custom:crm",
    )
    manifest = build_enterprise_stack_manifest_v0(
        stack_id="stack:custom-crm",
        provider_id="CUSTOM_CRM_PROVIDER",
        action_capabilities=(capability,),
    )
    binding = build_enterprise_action_binding_v0(
        candidate=candidate,
        capability_id="CRM.RECORD.UPDATE",
        manifest=manifest,
        connector_args={"record_id": "case-001", "status": "OPEN"},
        target_ref="sim:crm:case-001",
        target_prestate_hash=canonical_hash({"status": "NEW"}),
    )
    request = build_world_action_request_from_enterprise_binding_v0(
        candidate=candidate, manifest=manifest, binding=binding
    )
    assert request["surface_id"] == "CRM"
    assert request["operation_id"] == "UPDATE_RECORD"
    assert request["connector_id"] == "CUSTOM_CRM"


def test_missing_capability_and_secret_args_fail_closed(tmp_path):
    candidate = native_calendar_candidate(tmp_path)
    manifest = make_manifest("GOOGLE_LIKE")
    with pytest.raises(ValueError, match="ENTERPRISE_ACTION_CAPABILITY_UNAVAILABLE"):
        build_enterprise_action_binding_v0(
            candidate=candidate,
            capability_id="MAIL.SEND",
            manifest=manifest,
            connector_args={},
            target_ref="sim:mail",
            target_prestate_hash=canonical_hash({"state": "ABSENT"}),
        )
    with pytest.raises(ValueError, match="ENTERPRISE_STACK_SECRET_FIELD_FORBIDDEN"):
        build_enterprise_action_binding_v0(
            candidate=candidate,
            capability_id=CAPABILITY,
            manifest=manifest,
            connector_args={"access_token": "forbidden"},
            target_ref="sim:calendar:event",
            target_prestate_hash=canonical_hash({"state": "ABSENT"}),
        )


def test_core_adapter_has_no_named_vendor_logic():
    source = inspect.getsource(stack_module)
    for vendor in ("GoogleCalendar", "Microsoft365", "Salesforce", "HubSpot", "Odoo"):
        assert vendor not in source
    assert "KX108_ONLY" in source
    assert "allowed_to_decide: bool = False" in source
    assert "allowed_to_act: bool = False" in source
    assert "emits_act: bool = False" in source
