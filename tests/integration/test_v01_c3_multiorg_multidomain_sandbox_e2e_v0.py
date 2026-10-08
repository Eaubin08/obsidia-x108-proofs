"""C3 compositional E2E: 2 enterprises x 2 métiers, 2 provider stacks.

Uses real unchanged GuardX108, exact WORLD_ACTION_PRE, LIVE sovereign ticket,
bounded NO-NETWORK SANDBOX adapter, append-only receipt/replay. Source/company
authorization is *simulated technical evidence*, never real company consent.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT, ROOT / "scripts", ROOT / "tests" / "integration"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from periphery.company_model_v0 import (
    company_node_v0, company_relation_v0, company_model_snapshot_v0,
)
from periphery.enterprise_org_stack_lifecycle_v0 import (
    CompanyStackLifecycleV0, build_company_stack_link_v0,
    build_company_stack_link_revocation_v0,
)
from periphery.enterprise_governed_sandbox_preflight_v0 import (
    prepare_enterprise_sandbox_action_v0,
)
from periphery.native_ops.common_v0 import canonical_hash
from periphery.native_sources.source_onboarding_v0 import (
    build_native_observed_source_candidate_v0,
    build_native_human_source_authorization_v0,
    activate_native_source_v0,
)
from periphery.native_sources.source_registry_v0 import (
    NativeSourceRegistryV0, build_native_source_revocation_v0,
)
from periphery.universal_enterprise_stack_adapter_v0 import (
    build_enterprise_source_capability_v0,
    build_enterprise_action_capability_v0,
    build_enterprise_stack_manifest_v0,
    build_enterprise_source_binding_v0,
)
from periphery.world_calls.bounded_connector_executor_v0 import (
    execute_bounded_connector_v0, replay_execution_receipt_v0,
)
from periphery.world_calls.live_sovereign_ticket_v0 import (
    issue_live_sovereign_ticket_v0,
)
from test_obsidia_universal_cross_domain_conformance_v0 import (
    BY_ID, CAPABILITY, candidate_for, pre_for, policy_for, NoNetworkAdapter,
)

T = "2026-10-08T12:00:00+02:00"
CASES = ("ADMIN_CRM_MEMBER_UPDATE", "TRADING_TASK_RISK_REVIEW")
TENANTS = ("org-alpha", "org-bravo")
PROVIDERS = ("NATIVE_SANDBOX", "EXTERNAL_SANDBOX")


def scenario(tmp_path, org, case_id, provider):
    case = BY_ID[case_id]
    domain = case["domain_id"]
    tool = "tool-" + domain
    source_id = "source-" + org + "-" + domain
    cap = CAPABILITY[case["surface_id"]]
    def node(rid, kind):
        return company_node_v0(
            organization_id=org, record_id=rid, kind=kind,
            claim_state="DECLARED", valid_at=T,
            provenance_refs=("fixture:declared-enterprise-graph",),
        )
    def rel(rid, target, kind):
        return company_relation_v0(
            organization_id=org, relation_id=rid,
            from_record_id=org, to_record_id=target,
            relation_kind=kind, claim_state="DECLARED", valid_at=T,
            provenance_refs=("fixture:declared-enterprise-graph",),
        )
    # Same company snapshot across its two independent business domains.
    all_domains = tuple(BY_ID[key]["domain_id"] for key in CASES)
    company_nodes = [node(org, "ORGANIZATION")]
    company_edges = []
    for each_domain in all_domains:
        each_tool = "tool-" + each_domain
        each_source = "source-" + org + "-" + each_domain
        company_nodes.extend((node(each_tool, "TOOL_INSTANCE"),
                              node(each_source, "SOURCE"),
                              node(each_domain, "DOMAIN_BINDING")))
        company_edges.extend((
            rel("uses-" + each_tool, each_tool, "USES_TOOL"),
            rel("source-" + each_source, each_source, "HAS_SOURCE"),
            rel("domain-" + each_domain, each_domain, "BINDS_DOMAIN"),
        ))
    company = company_model_snapshot_v0(org, company_nodes, company_edges)
    source_cap = build_enterprise_source_capability_v0(
        capability_id="SOURCE.API.READ", source_kind="API_READONLY",
        native_read_capabilities=("READ_API_RESOURCE",),
        adapter_ref="fixture:api-adapter",
    )
    action_cap = build_enterprise_action_capability_v0(
        capability_id=cap,
        surface_id=case["surface_id"], operation_id=case["operation_id"],
        connector_id=provider + "_" + case["surface_id"],
        connector_action=case["connector_action"],
        required_scope=case["required_scope"], effect_class=case["effect_class"],
        world_call_class=case["world_call_class"],
        action_risk_class=case["action_risk_class"],
        autonomy_level=case["autonomy_level"], adapter_ref="fixture:action-adapter",
    )
    manifest = build_enterprise_stack_manifest_v0(
        stack_id=tool, provider_id=provider,
        source_capabilities=(source_cap,), action_capabilities=(action_cap,),
    )
    source_binding = build_enterprise_source_binding_v0(
        manifest=manifest, capability_id="SOURCE.API.READ",
        source_identity_sha256=canonical_hash(
            {"org": org, "domain": domain, "provider": provider}
        ),
        connector_reference="fixture-" + org + "-" + domain,
    )
    candidate = build_native_observed_source_candidate_v0(
        candidate_id="observed-" + org + "-" + domain,
        source_kind=source_binding.source_kind,
        provider=provider,
        source_identity_sha256=source_binding.source_identity_sha256,
        observed_capabilities=source_binding.native_read_capabilities,
        connector_reference=source_binding.connector_reference,
        observed_at=T,
    )
    human = build_native_human_source_authorization_v0(
        candidate=candidate,
        authorization_id="sourceapproval-" + org + "-" + domain,
        approved_capabilities=candidate.observed_capabilities,
        authority_reference="fixture:simulated-human-approval",
        approved_by="HUMAN:SIMULATED_ONLY",
        authorized_at=T,
    )
    registry = NativeSourceRegistryV0(tmp_path / "source-store" / org)
    registration, activation = activate_native_source_v0(
        candidate=candidate, authorization=human, registry=registry,
        source_id=source_id, activated_at=T,
    )
    proofs = {
        "company": company, "manifest": manifest,
        "source_binding": source_binding, "candidate": candidate,
        "authorization": human, "activation_receipt": activation,
        "registration": registration, "source_registry": registry,
    }
    link = build_company_stack_link_v0(
        **proofs, domain_id=domain, tool_instance_id=tool,
        integration_slot_id="default", source_id=source_id, linked_at=T,
    )
    return case, link, proofs


def preparation(s, lifecycle):
    case, link, proofs = s
    return prepare_enterprise_sandbox_action_v0(
        lifecycle=lifecycle, link=link, source_proofs=proofs,
        candidate=candidate_for(case), manifest=proofs["manifest"],
        capability_id=CAPABILITY[case["surface_id"]],
        connector_args={"fixture": case["case_id"]},
        target_ref=case["case_id"].lower(),
        target_prestate_hash=canonical_hash({"target": case["case_id"],
                                             "state": "FIXTURE_ONLY"}),
    )


@pytest.mark.parametrize("org", TENANTS)
@pytest.mark.parametrize("case_id", CASES)
def test_c3_two_organizations_two_domains_full_real_kx_sandbox_receipt(
    tmp_path, org, case_id,
):
    provider = PROVIDERS[0] if org == TENANTS[0] else PROVIDERS[1]
    scenario_data = scenario(tmp_path, org, case_id, provider)
    case, link, proofs = scenario_data
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(link, **proofs)
    ready = preparation(scenario_data, lifecycle)
    assert ready.organization_id == org
    assert ready.source_domain == case["domain_id"]
    assert ready.sandbox_only is True
    assert ready.real_provider_calls_permitted is False
    assert ready.allowed_to_act is False
    assert ready.allowed_to_decide is False
    assert ready.is_execution_authority is False
    assert ready.world_action_request["domain_id"] == case["domain_id"]
    root = tmp_path / "governed" / org / case_id
    pre = pre_for(case, ready.action_binding, ready.world_action_request, root)
    assert pre.x108_gate == "ALLOW"
    assert pre.source_domain == case["domain_id"]
    assert pre.egress_allowed is False
    # Fresh C2 check immediately before sandbox-specific policy+ticket.
    assert preparation(scenario_data, lifecycle).action_binding == ready.action_binding
    policy = policy_for(case, ready.action_binding)
    ticket = issue_live_sovereign_ticket_v0(
        decision_record_id=pre.decision_record_id,
        activation_policy=policy,
        decision_store_dir=root / "decisions",
        context_store_dir=root / "contexts",
    )
    # A second check before NO-NETWORK SANDBOX executor only.
    assert preparation(scenario_data, lifecycle).source_link_hash == link.link_hash
    adapter = NoNetworkAdapter(ready.action_binding)
    args = {
        "ticket": ticket, "activation_policy": policy,
        "connector_args": ready.world_action_request["connector_args"],
        "observed_target_ref": ready.world_action_request["target_ref"],
        "observed_target_prestate_hash": ready.world_action_request["target_prestate_hash"],
        "adapter": adapter, "receipt_store_dir": root / "receipts",
        "reconciliation_store_dir": root / "reconciliations",
    }
    outcome = execute_bounded_connector_v0(**args)
    assert outcome.status == "SANDBOX_EXECUTED_RECEIPT_STORED"
    assert outcome.adapter_called is True
    assert outcome.real_external_effect is False
    assert outcome.network_call_performed is False
    assert outcome.receipt.sandbox_execution is True
    assert replay_execution_receipt_v0(
        outcome.receipt.receipt_id, store_dir=root / "receipts",
        expected_ticket_hash=ticket.ticket_hash,
        expected_connector_call_hash=ticket.connector_call_hash,
        expected_idempotency_key=ticket.idempotency_key,
    ) == (True, None)
    repeat = execute_bounded_connector_v0(**args)
    assert repeat.adapter_called is False
    assert adapter.calls == 1


def test_c3_same_intent_is_tenant_scoped_before_kx_and_receipts(tmp_path):
    a = scenario(tmp_path, TENANTS[0], CASES[0], PROVIDERS[0])
    b = scenario(tmp_path, TENANTS[1], CASES[0], PROVIDERS[0])
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(a[1], **a[2])
    lifecycle.register(b[1], **b[2])
    pa, pb = preparation(a, lifecycle), preparation(b, lifecycle)
    assert pa.scoped_action_candidate.action_id != pb.scoped_action_candidate.action_id
    assert pa.action_binding.stable_intent_hash != pb.action_binding.stable_intent_hash
    assert pa.world_action_request["request_hash"] != pb.world_action_request["request_hash"]
    assert pa.world_action_request["idempotency_key"] != pb.world_action_request["idempotency_key"]
    assert pa.world_action_request["proposal_hash"] != pb.world_action_request["proposal_hash"]


def test_c3_preflight_rejects_revoked_source_and_does_not_create_request(tmp_path):
    s = scenario(tmp_path, TENANTS[0], CASES[0], PROVIDERS[0])
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(s[1], **s[2])
    prep = preparation(s, lifecycle)
    revoke = build_native_source_revocation_v0(
        registration=s[2]["registration"], revocation_id="withdraw-source",
        reason="fixture:source-withdrawn", revoked_by="HUMAN:SIMULATED",
        revoked_at=T,
    )
    s[2]["source_registry"].revoke(revoke)
    with pytest.raises(ValueError, match="C3_SOURCE_LINK_NOT_CURRENT"):
        preparation(s, lifecycle)
    assert prep.real_provider_calls_permitted is False


def test_c3_link_revocation_stops_same_preparation(tmp_path):
    s = scenario(tmp_path, TENANTS[0], CASES[0], PROVIDERS[0])
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(s[1], **s[2])
    assert preparation(s, lifecycle).sandbox_only
    revoke = build_company_stack_link_revocation_v0(
        s[1], revocation_id="withdraw-link",
        reason_ref="fixture:operator-withdraw", revoked_by="HUMAN:SIMULATED",
        revoked_at=T,
    )
    lifecycle.revoke(revoke)
    with pytest.raises(ValueError, match="C3_SOURCE_LINK_NOT_CURRENT"):
        preparation(s, lifecycle)


def test_c3_cross_domain_intent_cannot_borrow_source_link(tmp_path):
    s = scenario(tmp_path, TENANTS[0], CASES[0], PROVIDERS[0])
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(s[1], **s[2])
    bad_candidate = candidate_for(BY_ID[CASES[1]])
    with pytest.raises(ValueError, match="C3_CROSS_DOMAIN_INTENT_FORBIDDEN"):
        prepare_enterprise_sandbox_action_v0(
            lifecycle=lifecycle, link=s[1], source_proofs=s[2],
            candidate=bad_candidate, manifest=s[2]["manifest"],
            capability_id=CAPABILITY[s[0]["surface_id"]],
            connector_args={}, target_ref="target",
            target_prestate_hash="a" * 64,
        )


def test_c3_provider_manifest_drift_requires_new_c2_onboarding(tmp_path):
    s = scenario(tmp_path, TENANTS[0], CASES[0], PROVIDERS[0])
    replacement = scenario(tmp_path / "replacement", TENANTS[0], CASES[0],
                           PROVIDERS[1])
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(s[1], **s[2])
    with pytest.raises(ValueError, match="C3_ACTION_STACK_MUST_EQUAL_ONBOARDED_STACK"):
        prepare_enterprise_sandbox_action_v0(
            lifecycle=lifecycle, link=s[1], source_proofs=s[2],
            candidate=candidate_for(s[0]),
            manifest=replacement[2]["manifest"],
            capability_id=CAPABILITY[s[0]["surface_id"]],
            connector_args={}, target_ref="target",
            target_prestate_hash="a" * 64,
        )


def test_c3_hostile_org_in_payload_is_refused(tmp_path):
    s = scenario(tmp_path, TENANTS[0], CASES[0], PROVIDERS[0])
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(s[1], **s[2])
    action = candidate_for(s[0])
    action.payload["organization_id"] = TENANTS[1]
    with pytest.raises(ValueError, match="C3_CROSS_TENANT_PAYLOAD_FORBIDDEN"):
        prepare_enterprise_sandbox_action_v0(
            lifecycle=lifecycle, link=s[1], source_proofs=s[2],
            candidate=action, manifest=s[2]["manifest"],
            capability_id=CAPABILITY[s[0]["surface_id"]],
            connector_args={}, target_ref="target",
            target_prestate_hash="a" * 64,
        )


def test_c3_irreversible_candidate_blocked_even_with_valid_source(tmp_path):
    s = scenario(tmp_path, TENANTS[0], CASES[0], PROVIDERS[0])
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(s[1], **s[2])
    action = replace(candidate_for(s[0]), irreversible=True)
    with pytest.raises(ValueError, match="C3_SANDBOX_IRREVERSIBLE"):
        prepare_enterprise_sandbox_action_v0(
            lifecycle=lifecycle, link=s[1], source_proofs=s[2],
            candidate=action, manifest=s[2]["manifest"],
            capability_id=CAPABILITY[s[0]["surface_id"]],
            connector_args={}, target_ref="target",
            target_prestate_hash="a" * 64,
        )


def test_c3_one_lifecycle_joins_both_tenants_and_both_domains_without_leaks(tmp_path):
    suites = [
        scenario(tmp_path, org, case_id,
                 PROVIDERS[0] if org == TENANTS[0] else PROVIDERS[1])
        for org in TENANTS for case_id in CASES
    ]
    lifecycle = CompanyStackLifecycleV0()
    for _, link, proofs in suites:
        lifecycle.register(link, **proofs)
    assert len({x[1].link_id for x in suites}) == 4
    for org in TENANTS:
        snapshots = {
            proofs["company"]["snapshot_hash"]
            for _, link, proofs in suites if link.organization_id == org
        }
        assert len(snapshots) == 1
    for _, link, proofs in suites:
        assert preparation((BY_ID[next(k for k in CASES
             if BY_ID[k]["domain_id"] == link.domain_id)], link, proofs),
             lifecycle).organization_id == link.organization_id
        foreign = TENANTS[1] if link.organization_id == TENANTS[0] else TENANTS[0]
        assert lifecycle.inspect(link.link_id, organization_id=foreign, **proofs)["status"] == "NOT_AVAILABLE"
