"""C2 universal company/stack scope: source onboarding, revocation, provider swap."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from periphery.company_model_v0 import (
    company_model_snapshot_v0, company_node_v0, company_relation_v0,
)
from periphery.enterprise_org_stack_lifecycle_v0 import (
    CompanyStackLifecycleV0, LINK_STATUS, REFUSED_STATUS,
    build_company_stack_link_v0, verify_company_stack_link_v0,
    build_company_stack_link_revocation_v0,
    verify_company_stack_link_revocation_v0,
)
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
    build_enterprise_stack_manifest_v0,
    build_enterprise_source_binding_v0,
)

TIME = "2026-10-08T10:00:00+02:00"
C1_SOURCE_PROV = ("fixture:source-declared",)


def model(org: str, source_ids=("mail-1", "mail-2")):
    def n(rec_id, kind):
        return company_node_v0(
            organization_id=org, record_id=rec_id, kind=kind,
            claim_state="DECLARED", valid_at=TIME,
            provenance_refs=("fixture:company-declared-map",),
        )

    def r(ref, target, kind):
        return company_relation_v0(
            organization_id=org, relation_id=ref,
            from_record_id=org, to_record_id=target,
            relation_kind=kind, claim_state="DECLARED", valid_at=TIME,
            provenance_refs=("fixture:company-declared-map",),
        )

    return company_model_snapshot_v0(
        org,
        [n(org, "ORGANIZATION"), n("erp", "TOOL_INSTANCE"),
         n("trading", "DOMAIN_BINDING")]
        + [n(i, "SOURCE") for i in source_ids],
        [r("tool", "erp", "USES_TOOL"),
         r("domain", "trading", "BINDS_DOMAIN")]
        + [r("source-" + i, i, "HAS_SOURCE") for i in source_ids],
    )


def rig(tmp_path, org="company-a", provider="provider-alpha",
        source_id="mail-1", company=None, registry=None, stack="erp", slot=None):
    company = company if company is not None else model(org)
    registry = registry if registry is not None else NativeSourceRegistryV0(tmp_path / org)
    capability = build_enterprise_source_capability_v0(
        capability_id="SOURCE.MAIL.READ",
        source_kind="MAILBOX",
        native_read_capabilities=("SEARCH", "READ_MESSAGE"),
        adapter_ref="mail-adapter",
    )
    manifest = build_enterprise_stack_manifest_v0(
        stack_id=stack, provider_id=provider,
        source_capabilities=(capability,),
    )
    binding = build_enterprise_source_binding_v0(
        manifest=manifest,
        capability_id="SOURCE.MAIL.READ",
        source_identity_sha256=("a" if source_id == "mail-1" else "b") * 64,
        connector_reference=f"connector-{source_id}",
    )
    candidate = build_native_observed_source_candidate_v0(
        candidate_id=f"{org}-{provider}-{source_id}",
        source_kind=binding.source_kind,
        provider=provider,
        source_identity_sha256=binding.source_identity_sha256,
        observed_capabilities=binding.native_read_capabilities,
        connector_reference=binding.connector_reference,
        observed_at=TIME,
    )
    authorization = build_native_human_source_authorization_v0(
        candidate=candidate,
        authorization_id=f"approval-{org}-{provider}-{source_id}",
        approved_capabilities=binding.native_read_capabilities,
        authority_reference=f"fixture:unverified-operator-claim-{org}",
        approved_by="fixture-human",
        authorized_at=TIME,
    )
    registration, receipt = activate_native_source_v0(
        candidate=candidate, authorization=authorization,
        registry=registry, source_id=source_id, activated_at=TIME,
    )
    context = {
        "company": company, "manifest": manifest, "source_binding": binding,
        "candidate": candidate, "authorization": authorization,
        "activation_receipt": receipt, "registration": registration,
        "source_registry": registry,
    }
    link = build_company_stack_link_v0(
        **context, domain_id="trading", tool_instance_id=stack,
        integration_slot_id=slot or source_id,
        source_id=source_id, linked_at=TIME,
    )
    return link, context


def test_c2_one_company_multiple_sources_same_domain_and_no_right_to_act(tmp_path):
    org_map = model("company-a")
    registry = NativeSourceRegistryV0(tmp_path / "sources")
    a, ap = rig(tmp_path, company=org_map, registry=registry)
    b, bp = rig(tmp_path, company=org_map, registry=registry, source_id="mail-2")
    assert verify_company_stack_link_v0(a, **ap) == (True, None)
    assert verify_company_stack_link_v0(b, **bp) == (True, None)
    assert a.link_hash != b.link_hash
    assert a.organization_authority_verified is False
    assert a.has_runtime_permission is False
    assert a.allows_provider_calls is False
    assert a.allowed_to_act is False
    assert a.allowed_to_decide is False
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(a, **ap)
    lifecycle.register(b, **bp)
    result = lifecycle.inspect(a.link_id, organization_id="company-a", **ap)
    assert result["status"] == LINK_STATUS
    assert result["runtime_permission_granted"] is False
    assert result["provider_call_allowed"] is False


def test_c2_identical_vendor_domains_across_companies_are_separated(tmp_path):
    a, ap = rig(tmp_path, org="company-a", source_id="mail-1")
    b, bp = rig(tmp_path, org="company-b", source_id="mail-2")
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(a, **ap)
    lifecycle.register(b, **bp)
    assert lifecycle.inspect(b.link_id, organization_id="company-a", **bp) == {
        "status": REFUSED_STATUS, "reason": "C2_LINK_NOT_IN_ORGANIZATION"
    }
    assert lifecycle.inspect(a.link_id, organization_id="company-b", **ap) == {
        "status": REFUSED_STATUS, "reason": "C2_LINK_NOT_IN_ORGANIZATION"
    }


def test_c2_same_source_id_cannot_be_reassigned_to_different_org(tmp_path):
    a, ap = rig(tmp_path, org="company-a", source_id="mail-1")
    b, bp = rig(tmp_path, org="company-b", source_id="mail-1")
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(a, **ap)
    with pytest.raises(ValueError, match="ALREADY_SCOPED"):
        lifecycle.register(b, **bp)


def test_c2_native_source_revocation_is_checked_on_each_read(tmp_path):
    a, ap = rig(tmp_path)
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(a, **ap)
    revocation = build_native_source_revocation_v0(
        registration=ap["registration"], revocation_id="revoke-mail",
        reason="fixture:source-owner-withdrawal", revoked_by="fixture-human",
        revoked_at="2026-10-08T11:00:00+02:00",
    )
    ap["source_registry"].revoke(revocation)
    state = lifecycle.inspect(a.link_id, organization_id="company-a", **ap)
    assert state["status"] == REFUSED_STATUS
    assert "SOURCE_REVOKED" in state["reason"]
    with pytest.raises(ValueError, match="SOURCE_REVOKED"):
        build_company_stack_link_v0(
            **ap, domain_id="trading", tool_instance_id="erp",
            integration_slot_id="mail-1",
            source_id="mail-1", linked_at=TIME,
        )


def test_c2_provider_swap_requires_explicit_link_revocation_and_fresh_onboarding(tmp_path):
    org_map = model("company-a")
    registry = NativeSourceRegistryV0(tmp_path / "company-a")
    a, ap = rig(tmp_path, company=org_map, registry=registry)
    b, bp = rig(tmp_path, company=org_map, registry=registry,
                source_id="mail-2", provider="provider-beta", slot="mail-1")
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(a, **ap)
    with pytest.raises(ValueError, match="BINDING_MUST_BE_REVOKED"):
        lifecycle.register(b, **bp)
    revocation = build_company_stack_link_revocation_v0(
        a, revocation_id="revoke-provider-alpha",
        reason_ref="fixture:operator-change-of-provider",
        revoked_by="fixture-human",
        revoked_at="2026-10-08T12:00:00+02:00",
    )
    assert verify_company_stack_link_revocation_v0(
        revocation, link=a
    ) == (True, None)
    lifecycle.revoke(revocation)
    lifecycle.register(b, **bp)
    assert lifecycle.inspect(a.link_id, organization_id="company-a", **ap)["reason"] == "C2_LINK_REVOKED"
    assert lifecycle.inspect(b.link_id, organization_id="company-a", **bp)["status"] == LINK_STATUS
    assert b.provider_id != a.provider_id
    assert b.manifest_hash != a.manifest_hash
    assert b.has_runtime_permission is False


def test_c2_revoked_link_cannot_reactivate_and_revocation_immutable(tmp_path):
    a, ap = rig(tmp_path)
    lifecycle = CompanyStackLifecycleV0()
    lifecycle.register(a, **ap)
    rev = build_company_stack_link_revocation_v0(
        a, revocation_id="revoke-1", reason_ref="fixture:close",
        revoked_by="fixture-human", revoked_at=TIME,
    )
    lifecycle.revoke(rev)
    with pytest.raises(ValueError, match="CANNOT_REACTIVATE"):
        lifecycle.register(a, **ap)
    revised = build_company_stack_link_revocation_v0(
        a, revocation_id="revoke-2", reason_ref="fixture:new-reason",
        revoked_by="fixture-human", revoked_at=TIME,
    )
    with pytest.raises(ValueError, match="REVOCATION_IMMUTABLE"):
        lifecycle.revoke(revised)
    assert verify_company_stack_link_revocation_v0(
        replace(rev, is_execution_authority=True), link=a
    )[0] is False


def test_c2_org_model_cannot_be_substituted_by_other_company(tmp_path):
    a, ap = rig(tmp_path)
    ap["company"] = model("company-b")
    ok, reason = verify_company_stack_link_v0(a, **ap)
    assert not ok
    assert "SCOPE" in reason or "COMPANY_MODEL" in reason


def test_c2_manifest_provider_drift_blocks_link_and_lookups(tmp_path):
    a, ap = rig(tmp_path)
    bad_cap = build_enterprise_source_capability_v0(
        capability_id="SOURCE.MAIL.READ", source_kind="MAILBOX",
        native_read_capabilities=("SEARCH",), adapter_ref="mail-adapter",
    )
    ap["manifest"] = build_enterprise_stack_manifest_v0(
        stack_id="erp", provider_id="provider-beta",
        source_capabilities=(bad_cap,),
    )
    ok, reason = verify_company_stack_link_v0(a, **ap)
    assert not ok
    assert "SOURCE_BINDING" in reason or "SOURCE_PROOF" in reason or "STACK" in reason


def test_c2_source_binding_forgery_blocks_promotion(tmp_path):
    a, ap = rig(tmp_path)
    ap["source_binding"] = replace(ap["source_binding"], provider_id="forged")
    ok, reason = verify_company_stack_link_v0(a, **ap)
    assert not ok
    assert "BINDING_DRIFT" in reason


def test_c2_human_source_approval_is_required_and_tamper_fails(tmp_path):
    a, ap = rig(tmp_path)
    ap["authorization"] = replace(ap["authorization"], approved_by="MACHINE")
    ok, reason = verify_company_stack_link_v0(a, **ap)
    assert not ok
    assert "AUTHORIZATION_INVALID" in reason


def test_c2_receipt_and_source_identity_match_exact_registration(tmp_path):
    a, ap = rig(tmp_path)
    ap["activation_receipt"] = replace(
        ap["activation_receipt"], registration_hash="a" * 64
    )
    assert verify_company_stack_link_v0(a, **ap)[0] is False


def test_c2_company_graph_requires_declared_edges_not_only_nodes(tmp_path):
    a, ap = rig(tmp_path)
    company = dict(ap["company"])
    company["relations"] = []
    # C1 snapshot verifier must fail rather than silently accepting modified graph.
    ap["company"] = company
    assert verify_company_stack_link_v0(a, **ap)[0] is False


def test_c2_hash_and_authority_tampering_rejected(tmp_path):
    a, ap = rig(tmp_path)
    assert verify_company_stack_link_v0(
        replace(a, allowed_to_act=True), **ap
    )[0] is False
    assert verify_company_stack_link_v0(
        replace(a, has_runtime_permission=True), **ap
    )[0] is False
    assert verify_company_stack_link_v0(
        replace(a, organization_authority_verified=True), **ap
    )[0] is False
    assert verify_company_stack_link_v0(
        replace(a, link_hash="0" * 64), **ap
    )[0] is False
    with pytest.raises(FrozenInstanceError):
        a.allows_provider_calls = True


def test_c2_snapshot_change_requires_relink_not_implicit_permissions(tmp_path):
    a, ap = rig(tmp_path)
    updated = dict(ap["company"])
    # A new declaration requires a fresh canonical C1 model and a new C2 link.
    updated["truth_scope"] = "NEW_UNVERIFIED_CLAIM"
    ap["company"] = updated
    assert verify_company_stack_link_v0(a, **ap)[0] is False


def test_c2_unknown_link_or_wrong_organization_fails_closed(tmp_path):
    a, ap = rig(tmp_path)
    registry = CompanyStackLifecycleV0()
    registry.register(a, **ap)
    assert registry.inspect("unknown", organization_id="company-a", **ap)["status"] == REFUSED_STATUS
    assert registry.inspect(a.link_id, organization_id="another-company", **ap)["status"] == REFUSED_STATUS
