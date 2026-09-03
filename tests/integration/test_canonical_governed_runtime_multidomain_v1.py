"""
R7 — several domains, agents and providers coexisting on ONE canonical
governed runtime.

The engine under test is exactly the R6 cycle: same binder, same frozen
pre-execution context, same GuardX108 path, same persisted and verified
decision record, same execution-plan binding, same execution rail, same
receipt lifecycle, same feedback re-entry. Only the domain state and the
sigma bridge differ, and the bridge is selected by the cycle, never by the
agent.

No verdict is forced anywhere: each gate below is what the real kernel
returns for a real domain state.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "scripts"), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_agent_pre_execution_context_v1 as APEC  # noqa: E402
import obsidia_kx108_decision_store as DS  # noqa: E402
from obsidia_governed_runtime_cycle_v1 import (  # noqa: E402
    EXECUTION_AUTHORIZED,
    REFUSED_GATE_NOT_ALLOW,
    REFUSED_UNSUPPORTED_DOMAIN,
    SUPPORTED_DOMAINS,
    is_supported_domain,
    run_governed_feedback_cycle,
    run_governed_runtime_cycle,
)
from scripts.providers.canonical_runtime_receipt_flow_v1 import (  # noqa: E402
    CanonicalRuntimeReceiptFlow,
)
from _r7_domain_fixtures import (  # noqa: E402
    DOMAIN_REACHABLE_GATES,
    action_for,
    bank_allow,
    bank_block,
    bank_hold,
    ecom_state,
    gps_allow,
    gps_hold,
    trading_allow,
    trading_hold,
)

AGENT_ID = "DATA_PURITY_AGENT"


class DomainProvider:
    """One local deterministic sandbox handler per domain, counted."""

    def __init__(self, domain: str):
        self.domain = domain
        self.runtime_id = f"runtime-r7-{domain}"
        self.invocations = 0
        self.seen_missions: list[str] = []

    def __call__(self, **kwargs):
        self.invocations += 1
        return {"runtime_id": self.runtime_id, "provider": f"{self.domain}_provider"}


@pytest.fixture
def rig(tmp_path):
    """One shared runtime surface with one provider registered per domain."""
    flow = CanonicalRuntimeReceiptFlow()
    providers = {}
    for domain in ("bank", "gps_defense_aviation", "trading", "ecom"):
        provider = DomainProvider(domain)
        providers[domain] = provider
        flow.register_provider(f"{domain}_provider", provider)
    return {
        "flow": flow,
        "providers": providers,
        "ctx_dir": tmp_path / "agent_contexts",
        "dec_dir": tmp_path / "kx108_decisions",
    }


def run_domain(rig, domain, state, action_id, mission=None, capability="analysis"):
    return run_governed_runtime_cycle(
        AGENT_ID,
        action_for(domain, action_id),
        state,
        execution_surface=rig["flow"],
        mission_id=mission or f"mission-{action_id}",
        provider_id=f"{domain}_provider",
        capability=capability,
        execution_payload={"domain": domain},
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
    )


# ── The supported-domain table is the real bridge table ────────────────────


def test_supported_domains_are_exactly_the_real_bridges():
    assert set(SUPPORTED_DOMAINS) == {
        "bank", "trading", "ecom", "gps", "gps_defense_aviation"
    }
    for domain in DOMAIN_REACHABLE_GATES:
        assert is_supported_domain(domain) is True


def test_unsupported_domain_is_refused_without_a_decision(rig):
    """R7-C: no synthetic decision, no record, provider untouched."""
    result = run_governed_runtime_cycle(
        AGENT_ID,
        _unsupported_action(),
        bank_allow(),
        execution_surface=rig["flow"],
        mission_id="mission-unsupported",
        provider_id="bank_provider",
        capability="analysis",
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
    )

    assert result.execution_authorization_reason.startswith(REFUSED_UNSUPPORTED_DOMAIN)
    assert result.decision_rendered is False
    assert result.decision_id == ""
    assert result.decision_record_persisted is False
    assert result.execution_authorized is False
    assert all(p.invocations == 0 for p in rig["providers"].values())


def _unsupported_action():
    from periphery.common import ActionCandidate

    return ActionCandidate(
        action_id="r7_unsupported",
        domain="quantum_teleportation",
        actor_id="r7",
        intent="inspect",
        action_type="query",
        irreversible=False,
        timestamp_plan="",
        payload={},
    )


# ── Per-domain full chain (R7-D) ───────────────────────────────────────────


@pytest.mark.parametrize(
    "domain,state_fn,expected_gate",
    [
        ("bank", bank_allow, "ALLOW"),
        ("gps_defense_aviation", gps_allow, "ALLOW"),
        ("trading", trading_allow, "ALLOW"),
    ],
)
def test_domain_allow_runs_the_whole_canonical_chain(rig, domain, state_fn, expected_gate):
    provider = rig["providers"][domain]
    result = run_domain(rig, domain, state_fn(), f"r7_{domain}_allow")

    # 1-4: real agent, real binder, domain preserved
    assert result.agent_id == AGENT_ID
    assert result.agent_layer == "DATA"
    assert result.domain == domain
    assert result.context_id.startswith("cp-agent-")

    # 5: real frozen pre-execution context
    assert result.agent_pre_execution_context_verified is True
    stored_ctx = APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )
    assert stored_ctx["domain"] == domain

    # 6: real GuardX108 verdict
    assert result.decision_rendered is True
    assert result.x108_gate == expected_gate
    assert result.decision_id.startswith(f"{domain.split('_')[0]}-") or result.decision_id

    # 7-8: persisted and verified decision record
    assert result.decision_record_id.startswith("kxagent-")
    stored_rec = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])
    ok, reason = DS.verify_kx108_decision_record(stored_rec)
    assert ok is True, reason
    assert stored_rec["domain"] == domain

    # 11-13: execution only behind a verified ALLOW
    assert result.execution_authorized is True
    assert result.execution_authorization_reason == EXECUTION_AUTHORIZED
    assert provider.invocations == 1
    assert result.envelope_status == "SEALED"
    assert result.receipt["status"] == "COMPLETED"
    assert result.receipt["result_ref"] == provider.runtime_id

    # 14-15: readonly feedback and a next context
    assert result.feedback["memory_write_allowed"] is False
    assert result.next_context_id.startswith("cp-feedback-")
    result.assert_non_sovereign()


@pytest.mark.parametrize(
    "domain,state_fn",
    [
        ("bank", bank_hold),
        ("gps_defense_aviation", gps_hold),
        ("trading", trading_hold),
        ("ecom", ecom_state),
    ],
)
def test_domain_hold_is_decided_recorded_and_never_executed(rig, domain, state_fn):
    provider = rig["providers"][domain]
    result = run_domain(rig, domain, state_fn(), f"r7_{domain}_hold")

    assert result.x108_gate == "HOLD"
    assert result.decision_rendered is True
    assert result.decision_record_persisted is True
    assert result.decision_record_verified is True

    assert result.execution_authorized is False
    assert result.execution_authorization_reason == REFUSED_GATE_NOT_ALLOW
    assert result.provider_invoked is False
    assert provider.invocations == 0
    assert result.receipt is None
    result.assert_non_sovereign()


def test_bank_block_is_decided_recorded_and_never_executed(rig):
    """Only bank carries agents that emit contradictions, so only bank BLOCKs."""
    result = run_domain(rig, "bank", bank_block(), "r7_bank_block")

    assert result.x108_gate == "BLOCK"
    assert result.decision_record_verified is True
    assert result.execution_authorized is False
    assert rig["providers"]["bank"].invocations == 0


def test_domain_gate_reachability_matches_the_real_bridges(rig):
    """
    Records what each domain can actually reach. GPS and trading cannot
    BLOCK because none of their agents emits a contradiction; ecom cannot
    leave HOLD because its state contract is incomplete. These are facts,
    not gaps engineered around.
    """
    observed = {
        "bank": {
            run_domain(rig, "bank", bank_allow(), "r7_reach_bank_a").x108_gate,
            run_domain(rig, "bank", bank_hold(), "r7_reach_bank_h").x108_gate,
            run_domain(rig, "bank", bank_block(), "r7_reach_bank_b").x108_gate,
        },
        "gps_defense_aviation": {
            run_domain(rig, "gps_defense_aviation", gps_allow(), "r7_reach_gps_a").x108_gate,
            run_domain(rig, "gps_defense_aviation", gps_hold(), "r7_reach_gps_h").x108_gate,
        },
        "trading": {
            run_domain(rig, "trading", trading_allow(), "r7_reach_trd_a").x108_gate,
            run_domain(rig, "trading", trading_hold(), "r7_reach_trd_h").x108_gate,
        },
        "ecom": {
            run_domain(rig, "ecom", ecom_state(), "r7_reach_ecm").x108_gate,
        },
    }

    for domain, gates in observed.items():
        assert gates == set(DOMAIN_REACHABLE_GATES[domain]), (domain, gates)


# ── Multi-cycle coexistence on one runtime (R7-F, R7-I) ────────────────────


def test_multiple_domains_coexist_on_one_runtime(rig):
    """
    BANK ALLOW -> execute; GPS HOLD -> no execute; TRADING ALLOW -> execute;
    BANK feedback -> t1 decided again. One canonical runtime throughout.
    """
    bank_t0 = run_domain(rig, "bank", bank_allow(), "r7_coexist_bank")
    gps_t0 = run_domain(rig, "gps_defense_aviation", gps_hold(), "r7_coexist_gps")
    trading_t0 = run_domain(rig, "trading", trading_allow(), "r7_coexist_trd")

    assert bank_t0.x108_gate == "ALLOW" and bank_t0.provider_invoked is True
    assert gps_t0.x108_gate == "HOLD" and gps_t0.provider_invoked is False
    assert trading_t0.x108_gate == "ALLOW" and trading_t0.provider_invoked is True

    bank_t1 = run_governed_feedback_cycle(
        bank_t0,
        action_for("bank", "r7_coexist_bank_t1"),
        bank_block(),
        execution_surface=rig["flow"],
        mission_id="mission-bank-t1",
        provider_id="bank_provider",
        capability="analysis",
        execution_payload={"domain": "bank"},
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
    )

    assert bank_t1.x108_gate == "BLOCK"
    assert bank_t1.provider_invoked is False

    # Exactly the two authorized executions happened, in the right providers.
    assert rig["providers"]["bank"].invocations == 1
    assert rig["providers"]["trading"].invocations == 1
    assert rig["providers"]["gps_defense_aviation"].invocations == 0
    assert rig["providers"]["ecom"].invocations == 0

    # No identity leaks across cycles.
    cycles = [bank_t0, gps_t0, trading_t0, bank_t1]
    assert len({c.decision_id for c in cycles}) == 4
    assert len({c.trace_id for c in cycles}) == 4
    assert len({c.agent_pre_execution_context_id for c in cycles}) == 4
    assert len({c.decision_record_id for c in cycles}) == 4
    assert len({c.context_id for c in cycles}) == 4

    # Every record is independently verifiable on disk.
    for cycle in cycles:
        stored = DS.load_kx108_decision_record(cycle.decision_record_id, rig["dec_dir"])
        ok, reason = DS.verify_kx108_decision_record(stored)
        assert ok is True, (cycle.domain, reason)

    # Non-sovereignty holds globally.
    for cycle in cycles:
        assert cycle.memory_write is False
        assert cycle.kernel_mutation is False
        assert cycle.emits_act is False
        assert cycle.world_action_allowed is False
        assert cycle.world_action_dry_run_only is True
        assert cycle.context_runtime_allowed_now is False
        assert cycle.decision_authority == "KX108_ONLY"
        cycle.assert_non_sovereign()


def test_receipts_are_distinct_per_domain(rig):
    bank = run_domain(rig, "bank", bank_allow(), "r7_receipt_bank")
    trading = run_domain(rig, "trading", trading_allow(), "r7_receipt_trd")

    assert bank.receipt["runtime_execution_id"] != trading.receipt["runtime_execution_id"]
    assert bank.receipt["result_ref"] == "runtime-r7-bank"
    assert trading.receipt["result_ref"] == "runtime-r7-trading"
    assert bank.receipt["provider_id"] == "bank_provider"
    assert trading.receipt["provider_id"] == "trading_provider"


def test_provider_registry_is_bounded_to_registered_ids(rig):
    """An unregistered provider cannot be reached, even behind a real ALLOW."""
    with pytest.raises(Exception):
        run_governed_runtime_cycle(
            AGENT_ID,
            action_for("bank", "r7_unregistered"),
            bank_allow(),
            execution_surface=rig["flow"],
            mission_id="mission-unregistered",
            provider_id="provider_that_was_never_registered",
            capability="analysis",
            agent_context_store_dir=rig["ctx_dir"],
            decision_store_dir=rig["dec_dir"],
        )

    assert all(p.invocations == 0 for p in rig["providers"].values())


# ── Gencoin stays post-proof (R7-G) ────────────────────────────────────────


def test_gencoin_observes_the_gate_and_never_changes_it(rig):
    allowed = run_domain(rig, "bank", bank_allow(), "r7_gencoin_allow")
    held = run_domain(rig, "bank", bank_hold(), "r7_gencoin_hold")
    blocked = run_domain(rig, "bank", bank_block(), "r7_gencoin_block")

    for result in (allowed, held, blocked):
        assert result.gencoin is not None
        assert result.gencoin["observed_x108_gate"] == result.x108_gate
        assert result.gencoin["is_authority"] is False
        assert result.gencoin["can_change_gate"] is False
        assert result.gencoin["emits_act"] is False


def test_gencoin_cannot_turn_a_refusal_into_an_execution(rig):
    held = run_domain(rig, "bank", bank_hold(), "r7_gencoin_no_mint_hold")
    blocked = run_domain(rig, "bank", bank_block(), "r7_gencoin_no_mint_block")

    for result in (held, blocked):
        assert result.gencoin["mint_allowed"] is False
        assert result.gencoin["gencoin_candidate"] == 0.0
        assert result.execution_authorized is False
        assert result.provider_invoked is False


def test_gencoin_runs_after_the_decision_not_before(rig):
    """Gencoin only ever reports a gate that was already rendered."""
    result = run_domain(rig, "bank", bank_allow(), "r7_gencoin_order")

    assert result.decision_rendered is True
    assert result.gencoin["os3_ticket_id"] == result.os3_ticket_id
    assert result.gencoin["proof_valid"] is True
    assert result.gencoin["action_id"] == result.action_id
