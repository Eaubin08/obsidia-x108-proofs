"""
R7-E — cross-domain isolation.

A decision taken for one domain must never authorize an execution in
another. Every binding that could be substituted is exercised against real
persisted artefacts: domain, agent, context, decision, trace, provider,
capability, payload and the execution-plan digest that ties them together.

Every substitution must fail closed with a provider invocation count of
zero. No core component is mocked; the only doubles are counted local
sandbox handlers.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (
    str(_REPO_ROOT),
    str(_REPO_ROOT / "scripts"),
    str(Path(__file__).resolve().parent),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_agent_pre_execution_context_v1 as APEC  # noqa: E402
import obsidia_kx108_decision_store as DS  # noqa: E402
from obsidia_governed_runtime_cycle_v1 import (  # noqa: E402
    run_governed_feedback_cycle,
    run_governed_runtime_cycle,
)
from scripts.providers.canonical_runtime_receipt_flow_v1 import (  # noqa: E402
    CanonicalRuntimeReceiptFlow,
)
from _r7_domain_fixtures import (  # noqa: E402
    action_for,
    bank_allow,
    gps_allow,
    trading_allow,
)

AGENT_ID = "DATA_PURITY_AGENT"


class DomainProvider:
    def __init__(self, domain: str):
        self.domain = domain
        self.runtime_id = f"runtime-iso-{domain}"
        self.invocations = 0

    def __call__(self, **kwargs):
        self.invocations += 1
        return {"runtime_id": self.runtime_id, "provider": f"{self.domain}_provider"}


@pytest.fixture
def rig(tmp_path):
    flow = CanonicalRuntimeReceiptFlow()
    providers = {}
    for domain in ("bank", "gps_defense_aviation", "trading"):
        provider = DomainProvider(domain)
        providers[domain] = provider
        flow.register_provider(f"{domain}_provider", provider)
    return {
        "flow": flow,
        "providers": providers,
        "ctx_dir": tmp_path / "agent_contexts",
        "dec_dir": tmp_path / "kx108_decisions",
    }


_STATES = {
    "bank": bank_allow,
    "gps_defense_aviation": gps_allow,
    "trading": trading_allow,
}


def _run(rig, domain, action_id):
    return run_governed_runtime_cycle(
        AGENT_ID,
        action_for(domain, action_id),
        _STATES[domain](),
        execution_surface=rig["flow"],
        mission_id=f"mission-{domain}",
        provider_id=f"{domain}_provider",
        capability="analysis",
        execution_payload={"domain": domain},
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
    )


def _ctx(rig, result):
    return APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )


def _plan_binding(record, **over):
    kwargs = dict(
        context_packet_id=record["context_packet_id"],
        mission_id=record["mission_id"],
        provider_id=record["provider_id"],
        capability=record["capability"],
        payload={"domain": record["domain"]},
    )
    kwargs.update(over)
    return APEC.verify_execution_plan_binding(record, **kwargs)


# ── Every domain produces its own distinct artefacts ───────────────────────


def test_each_domain_produces_its_own_bindings(rig):
    bank = _run(rig, "bank", "iso_bank")
    gps = _run(rig, "gps_defense_aviation", "iso_gps")
    trading = _run(rig, "trading", "iso_trading")

    cycles = [bank, gps, trading]
    for attr in (
        "context_id",
        "decision_id",
        "trace_id",
        "agent_pre_execution_context_id",
        "decision_record_id",
        "execution_plan_digest",
        "os3_ticket_id",
    ):
        values = {getattr(c, attr) for c in cycles}
        assert len(values) == 3, (attr, values)

    assert bank.domain == "bank"
    assert gps.domain == "gps_defense_aviation"
    assert trading.domain == "trading"


def test_each_decision_record_names_its_own_domain(rig):
    for domain, action_id in (
        ("bank", "iso_rec_bank"),
        ("gps_defense_aviation", "iso_rec_gps"),
        ("trading", "iso_rec_trading"),
    ):
        result = _run(rig, domain, action_id)
        stored = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])

        assert stored["domain"] == domain
        assert stored["action_id"] == action_id
        assert stored["canonical_envelope"]["domain"] == domain
        ok, reason = DS.verify_kx108_decision_record(stored)
        assert ok is True, reason


# ── A bank context cannot run a GPS plan (R7-E 1) ──────────────────────────


def test_bank_context_cannot_execute_a_gps_execution_plan(rig):
    bank = _run(rig, "bank", "iso_sub_bank")
    gps = _run(rig, "gps_defense_aviation", "iso_sub_gps")

    bank_ctx = _ctx(rig, bank)
    gps_ctx = _ctx(rig, gps)
    before = dict((d, p.invocations) for d, p in rig["providers"].items())

    # GPS provider, capability, mission and payload against the bank context.
    for field, value in (
        ("provider_id", gps_ctx["provider_id"]),
        ("mission_id", gps_ctx["mission_id"]),
        ("context_packet_id", gps_ctx["context_packet_id"]),
        ("payload", {"domain": "gps_defense_aviation"}),
    ):
        ok, reason = _plan_binding(bank_ctx, **{field: value})
        assert ok is False, field
        assert reason in (
            "EXECUTION_PLAN_BINDING_MISMATCH",
            "CONTEXT_PACKET_BINDING_MISMATCH",
        )

    assert {d: p.invocations for d, p in rig["providers"].items()} == before


def test_the_domain_itself_is_bound_into_the_plan_digest(rig):
    """Rewriting only the domain already breaks the digest."""
    bank = _run(rig, "bank", "iso_domain_bank")
    bank_ctx = _ctx(rig, bank)

    forged = dict(bank_ctx)
    forged["domain"] = "gps_defense_aviation"

    recomputed = APEC.compute_execution_plan_digest(forged)
    assert recomputed != bank_ctx["execution_plan_digest"]

    ok, reason = APEC.verify_agent_pre_execution_context_record(forged)
    assert ok is False
    assert reason == "EXECUTION_PLAN_DIGEST_NOT_SELF_CONTAINED"


# ── A GPS decision record cannot authorize a trading provider (R7-E 2) ─────


def test_gps_decision_record_cannot_authorize_a_trading_provider(rig):
    gps = _run(rig, "gps_defense_aviation", "iso_auth_gps")
    trading = _run(rig, "trading", "iso_auth_trading")
    before = rig["providers"]["trading"].invocations

    gps_record = DS.load_kx108_decision_record(gps.decision_record_id, rig["dec_dir"])
    trading_ctx = _ctx(rig, trading)

    # The record is bound to the GPS context, not the trading one.
    assert gps_record["agent_pre_execution_context_id"] == (
        gps.agent_pre_execution_context_id
    )
    assert gps_record["agent_pre_execution_context_id"] != (
        trading.agent_pre_execution_context_id
    )
    assert gps_record["agent_execution_plan_digest"] != (
        trading_ctx["execution_plan_digest"]
    )
    assert gps_record["context_packet_id"] != trading.context_id

    # Repointing the record at the trading context breaks verification.
    forged = dict(gps_record)
    forged["agent_pre_execution_context_id"] = trading.agent_pre_execution_context_id
    forged["agent_execution_plan_digest"] = trading_ctx["execution_plan_digest"]
    ok, reason = DS.verify_kx108_decision_record(forged)
    assert ok is False
    assert reason == "DECISION_RECORD_HASH_MISMATCH"

    assert rig["providers"]["trading"].invocations == before


@pytest.mark.parametrize(
    "field",
    [
        "domain",
        "agent_id",
        "action_id",
        "context_packet_id",
        "decision_id",
        "trace_id",
        "agent_pre_execution_context_id",
        "agent_pre_execution_context_record_hash",
        "agent_execution_plan_digest",
        "agent_execution_scope",
    ],
)
def test_substituting_any_bound_field_breaks_record_verification(rig, field):
    """R7-E: every listed binding is hash-bound and cannot be swapped."""
    bank = _run(rig, "bank", "iso_field_bank")
    gps = _run(rig, "gps_defense_aviation", "iso_field_gps")

    bank_record = DS.load_kx108_decision_record(bank.decision_record_id, rig["dec_dir"])
    gps_record = DS.load_kx108_decision_record(gps.decision_record_id, rig["dec_dir"])

    forged = dict(bank_record)
    substitute = gps_record[field]
    if substitute == bank_record[field]:
        # Shared across domains by nature (e.g. agent_id, execution scope):
        # substitute a distinct value so the binding is still exercised.
        substitute = f"SUBSTITUTED_{field}"
    forged[field] = substitute

    ok, reason = DS.verify_kx108_decision_record(forged)
    assert ok is False
    assert reason == "DECISION_RECORD_HASH_MISMATCH"
    assert rig["providers"]["bank"].invocations == 1


# ── A trading receipt cannot be replayed as bank context (R7-E 3) ──────────


def test_trading_feedback_reenters_as_trading_and_is_decided_again(rig):
    trading = _run(rig, "trading", "iso_feedback_trading")
    assert trading.x108_gate == "ALLOW"
    before_bank = rig["providers"]["bank"].invocations

    reentry = run_governed_feedback_cycle(
        trading,
        action_for("trading", "iso_feedback_trading_t1"),
        trading_allow(),
        execution_surface=rig["flow"],
        mission_id="mission-trading-t1",
        provider_id="trading_provider",
        capability="analysis",
        execution_payload={"domain": "trading"},
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
    )

    # The re-entry stays in its own domain and is decided from scratch.
    assert reentry.domain == "trading"
    assert reentry.decision_id != trading.decision_id
    assert reentry.decision_record_id != trading.decision_record_id
    assert reentry.decision_record_verified is True
    assert rig["providers"]["bank"].invocations == before_bank


def test_a_trading_receipt_cannot_authorize_a_bank_execution(rig):
    """
    Re-entering trading feedback while naming bank providers produces a
    trading-domain cycle whose plan is bound to what was actually named:
    nothing from the trading receipt carries bank authority.
    """
    trading = _run(rig, "trading", "iso_cross_receipt")
    trading_ctx = _ctx(rig, trading)

    ok, reason = _plan_binding(
        trading_ctx,
        provider_id="bank_provider",
        mission_id="mission-bank",
    )
    assert ok is False
    assert reason == "EXECUTION_PLAN_BINDING_MISMATCH"

    # And the previous ALLOW is only ever transported as a fact.
    from periphery.context.feedback_result_context_adapter import (
        feedback_result_to_context_packet,
    )

    next_context = feedback_result_to_context_packet(trading)
    assert next_context.payload["previous_x108_gate"] == "ALLOW"
    assert next_context.payload["_authority_inherited"] is False
    assert next_context.runtime_allowed_now is False
    assert next_context.payload["previous_domain"] == "trading"


# ── Isolation holds while cycles interleave ────────────────────────────────


def test_interleaved_cycles_do_not_leak_state(rig):
    bank_a = _run(rig, "bank", "iso_leak_bank_a")
    gps_a = _run(rig, "gps_defense_aviation", "iso_leak_gps_a")
    bank_b = _run(rig, "bank", "iso_leak_bank_b")
    trading_a = _run(rig, "trading", "iso_leak_trading_a")

    cycles = [bank_a, gps_a, bank_b, trading_a]

    assert len({c.decision_record_id for c in cycles}) == 4
    assert len({c.agent_pre_execution_context_id for c in cycles}) == 4

    # Each provider only ran for its own domain's authorized cycles.
    assert rig["providers"]["bank"].invocations == 2
    assert rig["providers"]["gps_defense_aviation"].invocations == 1
    assert rig["providers"]["trading"].invocations == 1

    for cycle in cycles:
        stored = DS.load_kx108_decision_record(cycle.decision_record_id, rig["dec_dir"])
        assert stored["domain"] == cycle.domain
        assert stored["action_id"] == cycle.action_id
        ok, _ = DS.verify_kx108_decision_record(stored)
        assert ok is True
        cycle.assert_non_sovereign()
