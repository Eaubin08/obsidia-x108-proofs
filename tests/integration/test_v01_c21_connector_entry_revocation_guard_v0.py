"""C2.1 deny-only boundary tests: no connector invocation or authority creation."""
from dataclasses import replace

from periphery.enterprise_connector_entry_revocation_guard_v0 import (
    ConnectorEntryContextV0, ConnectorEntryGuardV0,
)


def context(**kwargs):
    data = dict(
        organization_id="company-a", principal_id="human-a",
        delegate_id="delegate-a", connector_id="calendar-a",
        capability_id="CALENDAR.EVENT.CREATE",
        action_request_hash="a" * 64,
        world_action_decision_hash="b" * 64,
        ticket_hash="c" * 64, delegation_hash="d" * 64,
        generation=0, organization_verified=True,
        delegation_verified=True, ticket_verified=True,
        kx108_allow_verified=True,
    )
    data.update(kwargs)
    return ConnectorEntryContextV0(**data)


def inspect(guard, ctx, **kwargs):
    args = dict(
        expected_organization_id="company-a",
        expected_connector_id="calendar-a",
        expected_capability_id="CALENDAR.EVENT.CREATE",
    )
    args.update(kwargs)
    return guard.inspect_before_dispatch(ctx, **args)


def test_fully_attested_only_passes_checks_not_execution():
    assert inspect(ConnectorEntryGuardV0(), context()) == (
        "BLOCK:C21_INDEPENDENT_ATTESTATION_VERIFIER_NOT_BOUND"
    )


def test_missing_attestation_is_never_a_grant():
    for field in ("organization_verified", "delegation_verified",
                  "ticket_verified", "kx108_allow_verified"):
        ctx = replace(context(), **{field: False})
        assert inspect(ConnectorEntryGuardV0(), ctx).startswith("BLOCK:")


def test_wrong_organization_or_connector_or_capability_denied():
    g = ConnectorEntryGuardV0()
    assert inspect(g, context(organization_id="company-b")) == "BLOCK:C21_SCOPE_MISMATCH"
    assert inspect(g, context(connector_id="other")) == "BLOCK:C21_SCOPE_MISMATCH"
    assert inspect(g, context(capability_id="MAIL.SEND")) == "BLOCK:C21_SCOPE_MISMATCH"


def test_revocation_after_prior_check_denies_at_connector_entry():
    g = ConnectorEntryGuardV0()
    ctx = context()
    assert inspect(g, ctx) == "BLOCK:C21_INDEPENDENT_ATTESTATION_VERIFIER_NOT_BOUND"
    assert g.revoke(
        organization_id="company-a", delegate_id="delegate-a",
        connector_id="calendar-a", capability_id="CALENDAR.EVENT.CREATE"
    ) == 1
    assert inspect(g, ctx) == "BLOCK:C21_DELEGATION_REVOKED"


def test_revocation_does_not_cross_tenants():
    g = ConnectorEntryGuardV0()
    g.revoke(organization_id="company-b", delegate_id="delegate-a",
             connector_id="calendar-a", capability_id="CALENDAR.EVENT.CREATE")
    assert inspect(g, context()) == "BLOCK:C21_INDEPENDENT_ATTESTATION_VERIFIER_NOT_BOUND"


def test_stale_generation_fails_closed_even_without_revocation():
    g = ConnectorEntryGuardV0()
    assert inspect(g, context(generation=1)) == "BLOCK:C21_GENERATION_STALE"


def test_missing_identity_or_hash_rejected():
    g = ConnectorEntryGuardV0()
    assert inspect(g, context(principal_id="")) == "BLOCK:C21_IDENTITY_OR_PROOF_ABSENT"
    assert inspect(g, context(ticket_hash="")) == "BLOCK:C21_IDENTITY_OR_PROOF_ABSENT"


def test_caller_forged_all_true_flags_still_fail_closed():
    # The untrusted caller can populate all four booleans. This does not
    # authenticate the organization, delegation, ticket or KX108 decision.
    ctx = context(organization_verified=True, delegation_verified=True,
                  ticket_verified=True, kx108_allow_verified=True)
    assert inspect(ConnectorEntryGuardV0(), ctx) == (
        "BLOCK:C21_INDEPENDENT_ATTESTATION_VERIFIER_NOT_BOUND"
    )
