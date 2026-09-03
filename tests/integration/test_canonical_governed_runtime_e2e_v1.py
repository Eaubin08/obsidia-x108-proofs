"""
E2E proof of the governed INTERNAL runtime cycle (R5).

Real chain, no mock of the core:

    run_registered_agent            -> real AgentResult
    agent_result_to_context_packet  -> real ContextPacket (R4 binder)
    validate_context_packet / check_x108_context_boundary
    sigma_bridge.run_bank_with_periphery -> real GuardX108.decide()
    build_os3_ticket + run_replay   -> cryptographic verification
    [GATE] verified ALLOW only      -> CanonicalRuntimeReceiptFlow
                                    -> CanonicalExecutionFlow
                                    -> CanonicalExecutionOrchestrator
                                    -> MissionExecutionRouter
                                    -> bounded local handler
                                    -> sealed envelope + terminal receipt
    build_memory_candidate          -> readonly feedback

The only test double is a LOCAL, DETERMINISTIC, SANDBOXED provider handler
whose invocations are counted. Nothing in the decision, verification or
execution rail is patched: a HOLD or a BLOCK is a real kernel verdict
produced by a real degraded domain state, never a forced value.

No world action. No memory write. No kernel mutation. No ACT.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from obsidia_governed_runtime_cycle_v1 import (  # noqa: E402
    CYCLE_BOUNDARY,
    DECISION_RECORD_PERSISTENCE_BLOCKER,
    EXECUTION_AUTHORIZED,
    REFUSED_GATE_NOT_ALLOW,
    REFUSED_NO_EXECUTION_SURFACE,
    REFUSED_REPLAY_NOT_PASS,
    REFUSED_TICKET_INVALID,
    REFUSED_UNSUPPORTED_DOMAIN,
    GovernedRuntimeCycleError,
    authorize_execution_from_verified_kx108,
    is_supported_domain,
    resolve_domain_pipeline,
    run_governed_runtime_cycle,
)

from periphery.agent_registry import run_registered_agent  # noqa: E402
from periphery.common import ActionCandidate  # noqa: E402
from periphery.context.agent_result_context_adapter import (  # noqa: E402
    agent_result_to_context_packet,
)
from periphery.os3_ticket import build_os3_ticket  # noqa: E402
from periphery.os3_replay_runner import run_replay  # noqa: E402
from periphery.sigma_bridge import run_bank_with_periphery  # noqa: E402
from scripts.providers.canonical_runtime_receipt_flow_v1 import (  # noqa: E402
    CanonicalRuntimeReceiptFlow,
)
from sigma.contracts import BankState  # noqa: E402

AGENT_ID = "DATA_PURITY_AGENT"
PROVIDER_ID = "r5_sandbox_provider"
RUNTIME_ID = "runtime-r5-governed-001"


class BoundedSandboxProvider:
    """Local, deterministic, side-effect-free handler. Counts its invocations."""

    def __init__(self, runtime_id: str = RUNTIME_ID):
        self.runtime_id = runtime_id
        self.invocations = 0
        self.seen_payloads: list[dict] = []

    def __call__(self, **kwargs):
        self.invocations += 1
        self.seen_payloads.append(dict(kwargs.get("payload") or {}))
        return {"runtime_id": self.runtime_id, "provider": PROVIDER_ID}


def _action(action_id: str = "r5_gov_001", irreversible: bool = False) -> ActionCandidate:
    return ActionCandidate(
        action_id=action_id,
        domain="bank",
        actor_id="r5-integration",
        intent="transfer_review",
        action_type="transfer",
        irreversible=irreversible,
        timestamp_plan="2026-09-03T00:00:00Z",
        payload={"gross_value": 500.0, "amount": 200.0},
    )


def _bank_state(**over) -> BankState:
    base = dict(
        transaction_type="TRANSFER",
        amount=200.0,
        channel="web",
        counterparty_known=True,
        counterparty_age_days=90,
        account_balance=1000.0,
        available_cash=800.0,
        historical_avg_amount=150.0,
        behavior_shift_score=0.1,
        fraud_score=0.05,
        policy_limit=5000.0,
        affordability_score=0.85,
        urgency_score=0.2,
        identity_mismatch_score=0.0,
        narrative_conflict_score=0.0,
        device_trust_score=0.9,
        recent_failed_attempts=0,
        elapsed_s=200.0,
    )
    base.update(over)
    return BankState(**base)


def _blocking_state() -> BankState:
    """Genuinely fraudulent state — the kernel really returns BLOCK."""
    return _bank_state(
        fraud_score=0.99,
        identity_mismatch_score=0.9,
        narrative_conflict_score=0.9,
        recent_failed_attempts=9,
    )


def _holding_state() -> BankState:
    """Genuinely over-committed state — the kernel really returns HOLD."""
    return _bank_state(
        amount=99999.0,
        available_cash=1.0,
        account_balance=1.0,
        affordability_score=0.01,
    )


@pytest.fixture
def surface(tmp_path):
    """Stores are per-test: the canonical rails write outside the repo."""
    provider = BoundedSandboxProvider()
    flow = CanonicalRuntimeReceiptFlow()
    flow.register_provider(PROVIDER_ID, provider)
    return flow, provider, tmp_path


def _run(surface_pair, state=None, action_id="r5_gov_001", with_surface=True):
    flow, provider, tmp_path = surface_pair
    return (
        run_governed_runtime_cycle(
            AGENT_ID,
            _action(action_id),
            state if state is not None else _bank_state(),
            execution_surface=flow if with_surface else None,
            mission_id=f"mission-{action_id}",
            provider_id=PROVIDER_ID,
            capability="analysis",
            execution_payload={"scope": "bounded"},
            agent_context_store_dir=tmp_path / "agent_contexts",
            decision_store_dir=tmp_path / "kx108_decisions",
        ),
        provider,
    )


# ── 1-4. Agent, binder, provenance, validator ────────────────────────────────


def test_01_real_registered_agent_produces_agent_result():
    agent_result = run_registered_agent(AGENT_ID, _action("r5_agent_001"))

    assert agent_result.agent_id == AGENT_ID
    assert agent_result.packet.action_id == "r5_agent_001"
    assert agent_result.packet.domain == "bank"
    assert agent_result.packet.can_emit_act is False


def test_02_binder_produces_context_packet_from_this_agent_result(surface):
    action = _action("r5_bind_001")
    expected = agent_result_to_context_packet(run_registered_agent(AGENT_ID, action))

    result, _ = _run(surface, action_id="r5_bind_001")

    assert result.context_id == expected.context_id
    assert result.context_id.startswith("cp-agent-")
    assert result.boundary == CYCLE_BOUNDARY


def test_03_agent_provenance_survives_the_whole_cycle(surface):
    result, _ = _run(surface, action_id="r5_prov_001")

    assert result.agent_id == AGENT_ID
    assert result.agent_layer == "DATA"
    assert result.action_id == "r5_prov_001"
    assert result.domain == "bank"


def test_04_context_validator_and_boundary_pass(surface):
    result, _ = _run(surface, action_id="r5_valid_001")

    assert result.context_validation["valid"] is True
    assert result.context_validation["violations"] == []
    assert result.context_boundary["passed"] is True
    assert result.context_boundary["violations"] == []
    assert result.context_boundary["decision_authority"] == "KX108_ONLY"


# ── 5-7. Real sovereign KX108 decision ───────────────────────────────────────


def test_05_decision_comes_from_the_real_sovereign_kernel(surface):
    """The gate is produced by GuardX108, reachable through the canonical bridge."""
    action = _action("r5_dec_001")
    packet = run_registered_agent(AGENT_ID, action).packet
    state = _bank_state()

    direct = run_bank_with_periphery(state, packet)

    result, _ = _run(surface, state=state, action_id="r5_dec_001")

    assert result.decision_engine == "sigma.guard.GuardX108.decide"
    assert result.x108_gate == direct.x108_gate
    assert result.x108_gate in ("ALLOW", "HOLD", "BLOCK")
    assert result.reason_code == direct.reason_code


def test_06_decision_carries_real_identifiers(surface):
    result, _ = _run(surface, action_id="r5_dec_002")

    assert result.decision_id
    assert result.decision_id.startswith("bank-")
    assert result.trace_id
    assert result.severity


def test_07_decision_authority_is_kx108_only(surface):
    result, _ = _run(surface, action_id="r5_auth_001")

    assert result.decision_authority == "KX108_ONLY"
    assert result.to_dict()["decision_authority"] == "KX108_ONLY"
    result.assert_non_sovereign()


# ── 8-10. Cryptographic verification, fail closed on tampering ───────────────


def test_08_os3_evidence_is_bound_and_replay_verifies(surface):
    result, _ = _run(surface, action_id="r5_os3_001")

    assert len(result.input_hash) == 64
    assert len(result.output_hash) == 64
    assert len(result.trace_hash) == 64
    assert len(result.merkle_root) == 64
    assert result.replay_status == "PASS"


def test_09_tampered_evidence_fails_closed_and_refuses_authorization():
    """A ticket whose hashes were altered can never authorize execution."""
    action = _action("r5_tamper_001")
    packet = run_registered_agent(AGENT_ID, action).packet
    envelope = run_bank_with_periphery(_bank_state(), packet)
    ticket = build_os3_ticket(action, packet, envelope)
    replay = run_replay(ticket, action, packet, envelope)

    assert envelope.x108_gate == "ALLOW"
    ok, reason = authorize_execution_from_verified_kx108(envelope, ticket, replay)
    assert ok is True and reason == EXECUTION_AUTHORIZED

    ticket.merkle_root = ""
    ok_t, reason_t = authorize_execution_from_verified_kx108(envelope, ticket, replay)
    assert ok_t is False
    assert reason_t == REFUSED_TICKET_INVALID


def test_10_replay_mismatch_fails_closed():
    """A replay that does not reproduce the original hashes refuses execution."""
    action = _action("r5_replay_001")
    packet = run_registered_agent(AGENT_ID, action).packet
    envelope = run_bank_with_periphery(_bank_state(), packet)
    ticket = build_os3_ticket(action, packet, envelope)

    other_envelope = run_bank_with_periphery(_holding_state(), packet)
    mismatched = run_replay(ticket, action, packet, other_envelope)

    assert mismatched.replay_status == "FAIL"

    ok, reason = authorize_execution_from_verified_kx108(envelope, ticket, mismatched)
    assert ok is False
    assert reason == REFUSED_REPLAY_NOT_PASS


# ── 11-14. Fail closed: the handler is the ground truth ──────────────────────


def test_11_block_never_invokes_the_provider(surface):
    result, provider = _run(surface, state=_blocking_state(), action_id="r5_block_001")

    assert result.x108_gate == "BLOCK"
    assert result.execution_authorized is False
    assert result.execution_authorization_reason == REFUSED_GATE_NOT_ALLOW
    assert result.provider_invoked is False
    assert provider.invocations == 0
    assert result.receipt is None
    assert result.runtime_id == ""


def test_12_hold_never_invokes_the_provider(surface):
    result, provider = _run(surface, state=_holding_state(), action_id="r5_hold_001")

    assert result.x108_gate == "HOLD"
    assert result.execution_authorized is False
    assert result.execution_authorization_reason == REFUSED_GATE_NOT_ALLOW
    assert result.provider_invoked is False
    assert provider.invocations == 0
    assert result.receipt is None


def test_13_allow_without_a_bound_execution_surface_invokes_nothing(surface):
    result, provider = _run(surface, action_id="r5_nosurface_001", with_surface=False)

    assert result.x108_gate == "ALLOW"
    assert result.execution_authorized is False
    assert result.execution_authorization_reason == REFUSED_NO_EXECUTION_SURFACE
    assert result.provider_invoked is False
    assert provider.invocations == 0


def test_14_verified_allow_invokes_the_provider_exactly_once(surface):
    result, provider = _run(surface, action_id="r5_allow_001")

    assert result.x108_gate == "ALLOW"
    assert result.execution_authorized is True
    assert result.execution_authorization_reason == EXECUTION_AUTHORIZED
    assert result.provider_invoked is True
    assert provider.invocations == 1
    assert provider.seen_payloads == [{"scope": "bounded"}]


# ── 15-18. Real execution rail, sealed envelope, terminal receipt ────────────


def test_15_execution_traverses_the_real_canonical_flow(surface):
    """The router really dispatched to the registered provider."""
    flow, provider, _tmp = surface
    result, _ = _run(surface, action_id="r5_flow_001")

    assert result.flow_status == "COMPLETED"
    assert PROVIDER_ID in flow.flow.orchestrator.router.routes
    assert provider.invocations == 1


def test_16_execution_envelope_is_really_sealed(surface):
    result, _ = _run(surface, action_id="r5_seal_001")

    assert result.envelope_status == "SEALED"
    assert result.runtime_id == RUNTIME_ID
    assert result.runtime_id != "runtime-unknown"


def test_17_terminal_receipt_is_completed_only_on_a_real_sealed_result(surface):
    result, _ = _run(surface, action_id="r5_receipt_001")
    receipt = result.receipt

    assert receipt is not None
    assert receipt["status"] == "COMPLETED"
    assert receipt["completed_at"] != ""
    assert receipt["started_at"] != ""


def test_18_receipt_result_ref_matches_the_runtime_id(surface):
    result, _ = _run(surface, action_id="r5_receipt_002")

    assert result.receipt["result_ref"] == result.runtime_id
    assert result.receipt["invocation_id"] == "mission-r5_receipt_002"
    assert result.receipt["decision_authority"] is False
    assert result.receipt["execution_authority"] is False


def test_18b_no_false_completed_receipt_on_refused_paths(surface):
    for state, action_id in (
        (_blocking_state(), "r5_noreceipt_block"),
        (_holding_state(), "r5_noreceipt_hold"),
    ):
        result, provider = _run(surface, state=state, action_id=action_id)
        assert result.receipt is None
        assert result.envelope_status == ""
        assert result.flow_status == ""
    assert provider.invocations == 0


# ── 19-22. Readonly feedback, no authority leak ─────────────────────────────


def test_19_feedback_candidate_is_readonly(surface):
    result, _ = _run(surface, action_id="r5_feedback_001")
    feedback = result.feedback

    assert feedback is not None
    assert feedback["status"] == "CANDIDATE_ONLY"
    assert feedback["os3_ticket_id"] == result.os3_ticket_id
    assert feedback["action_id"] == "r5_feedback_001"


def test_20_feedback_never_allows_a_memory_write(surface):
    for state in (_bank_state(), _holding_state(), _blocking_state()):
        result, _ = _run(surface, state=state, action_id="r5_feedback_002")
        assert result.feedback["memory_write_allowed"] is False
        assert result.memory_write is False
        assert result.kernel_mutation is False


def test_21_source_context_packet_runtime_allowed_now_stays_false(surface):
    action = _action("r5_ctx_001")
    context = agent_result_to_context_packet(run_registered_agent(AGENT_ID, action))
    result, _ = _run(surface, action_id="r5_ctx_001")

    assert context.runtime_allowed_now is False
    assert result.context_runtime_allowed_now is False
    assert result.to_dict()["context_runtime_allowed_now"] is False


def test_22_no_peripheral_authority_emerges_from_the_cycle(surface):
    result, _ = _run(surface, action_id="r5_noauth_001")

    assert result.emits_act is False
    assert result.memory_write is False
    assert result.kernel_mutation is False
    assert result.world_action_allowed is False
    assert result.world_action_dry_run_only is True
    result.assert_non_sovereign()

    result.provider_invoked = True
    result.execution_authorized = False
    with pytest.raises(AssertionError, match="provider invoked without authorization"):
        result.assert_non_sovereign()


# ── 23-24. Determinism, and no inheritance of a previous ALLOW ──────────────


def test_23_context_identity_is_deterministic_across_cycles(surface):
    first, _ = _run(surface, action_id="r5_det_001")
    second, provider = _run(surface, action_id="r5_det_001")

    assert first.context_id == second.context_id
    assert first.input_hash == second.input_hash
    assert provider.invocations == 2

    other, _ = _run(surface, action_id="r5_det_002")
    assert other.context_id != first.context_id
    assert other.input_hash != first.input_hash


def test_24_a_new_cycle_never_inherits_the_previous_allow(surface):
    """A t0 ALLOW confers nothing at t1: the new cycle is decided again."""
    allowed, provider = _run(surface, action_id="r5_next_001")
    assert allowed.x108_gate == "ALLOW"
    assert provider.invocations == 1

    blocked, provider2 = _run(
        surface, state=_blocking_state(), action_id="r5_next_002"
    )

    assert blocked.x108_gate == "BLOCK"
    assert blocked.execution_authorized is False
    assert blocked.provider_invoked is False
    assert provider2.invocations == 1  # unchanged by the second, refused cycle
    assert blocked.decision_id != allowed.decision_id
    assert blocked.trace_id != allowed.trace_id


# ── Blocker: canonical decision-record persistence is not applicable ────────


def test_25_decision_record_is_persisted_on_the_dedicated_agent_rail(surface):
    """
    R6 closed what R5 had to leave open: the cycle now persists and verifies
    a real KX108 record on its own agent rail, without ever fabricating the
    remediation rail's binding artefacts.
    """
    result, _ = _run(surface, action_id="r5_blocker_001")

    assert result.decision_record_persisted is True
    assert result.decision_record_verified is True
    assert result.decision_record_id.startswith("kxagent-")

    # The remediation rail stays inapplicable and is never diverted.
    assert (
        result.remediation_rail_blocker == DECISION_RECORD_PERSISTENCE_BLOCKER
    )
    assert result.to_dict()["decision_record_verified"] is True


def test_26_unsupported_domain_is_refused_without_any_decision(surface):
    """
    R7-C: an unsupported domain is refused before any verdict is requested.
    The refusal is not a decision: nothing is rendered, nothing is recorded,
    and the provider is never reached.
    """
    flow, provider, tmp_path = surface
    action = ActionCandidate(
        action_id="r5_unknown_domain",
        domain="not_a_canonical_domain",
        actor_id="r5",
        intent="inspect",
        action_type="query",
        irreversible=False,
        timestamp_plan="",
        payload={},
    )

    result = run_governed_runtime_cycle(
        AGENT_ID,
        action,
        _bank_state(),
        execution_surface=flow,
        mission_id="m",
        provider_id=PROVIDER_ID,
        capability="analysis",
        agent_context_store_dir=tmp_path / "agent_contexts",
        decision_store_dir=tmp_path / "kx108_decisions",
    )

    assert result.execution_authorization_reason.startswith(
        REFUSED_UNSUPPORTED_DOMAIN
    )
    assert result.decision_rendered is False
    assert result.decision_id == ""
    assert result.decision_record_persisted is False
    assert result.execution_authorized is False
    assert result.provider_invoked is False
    assert provider.invocations == 0
    result.assert_non_sovereign()


def test_27_resolving_an_unsupported_domain_directly_still_raises():
    """The direct resolver keeps its strict contract for programmatic callers."""
    with pytest.raises(GovernedRuntimeCycleError, match="NO_CANONICAL_DOMAIN_PIPELINE"):
        resolve_domain_pipeline("not_a_canonical_domain")

    assert is_supported_domain("bank") is True
    assert is_supported_domain("not_a_canonical_domain") is False
