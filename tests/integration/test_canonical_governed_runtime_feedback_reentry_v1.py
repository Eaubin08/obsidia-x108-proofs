"""
Proof that a finished governed cycle re-enters as read-only context and
that nothing about the previous verdict carries over.

t0: agent -> context -> KX108 -> verified record -> execution -> receipt
    -> feedback -> Context1
t1: Context1 -> fresh KX108 decision -> its own verified record -> its own gate

A previous ALLOW is transported as evidence, never as permission. All core
components are real; the only double is a counted local sandbox provider.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_kx108_decision_store as DS  # noqa: E402
from obsidia_governed_runtime_cycle_v1 import (  # noqa: E402
    EXECUTION_AUTHORIZED,
    run_governed_feedback_cycle,
    run_governed_runtime_cycle,
)
from periphery.common import ActionCandidate  # noqa: E402
from periphery.context.feedback_result_context_adapter import (  # noqa: E402
    BOUNDARY,
    SIGNAL_EXECUTION_FAILED,
    SIGNAL_EXECUTION_REFUSED,
    FeedbackContextAdapterError,
    context_packet_validation_projection,
    feedback_result_to_context_packet,
    feedback_result_to_peripheral_signal,
)
from periphery.context.context_packet_validator import validate_context_packet  # noqa: E402
from periphery.x108_ingress.x108_context_boundary import (  # noqa: E402
    check_x108_context_boundary,
)
from scripts.providers.canonical_runtime_receipt_flow_v1 import (  # noqa: E402
    CanonicalRuntimeReceiptFlow,
)
from sigma.contracts import BankState  # noqa: E402

AGENT_ID = "DATA_PURITY_AGENT"
PROVIDER_ID = "r6_reentry_provider"


class CountingProvider:
    def __init__(self, runtime_id="runtime-r6-reentry"):
        self.runtime_id = runtime_id
        self.invocations = 0

    def __call__(self, **kwargs):
        self.invocations += 1
        return {"runtime_id": self.runtime_id, "provider": PROVIDER_ID}


class ResultlessProvider:
    """Runs, but yields no runtime_id — the receipt fails closed."""

    def __init__(self):
        self.invocations = 0

    def __call__(self, **kwargs):
        self.invocations += 1
        return {"provider": PROVIDER_ID}


def _action(action_id="r6_re_t0") -> ActionCandidate:
    return ActionCandidate(
        action_id=action_id,
        domain="bank",
        actor_id="r6-reentry",
        intent="transfer_review",
        action_type="transfer",
        irreversible=False,
        timestamp_plan="2026-09-03T00:00:00Z",
        payload={"gross_value": 500.0, "amount": 200.0},
    )


def _bank_state(**over) -> BankState:
    base = dict(
        transaction_type="TRANSFER", amount=200.0, channel="web",
        counterparty_known=True, counterparty_age_days=90,
        account_balance=1000.0, available_cash=800.0,
        historical_avg_amount=150.0, behavior_shift_score=0.1,
        fraud_score=0.05, policy_limit=5000.0, affordability_score=0.85,
        urgency_score=0.2, identity_mismatch_score=0.0,
        narrative_conflict_score=0.0, device_trust_score=0.9,
        recent_failed_attempts=0, elapsed_s=200.0,
    )
    base.update(over)
    return BankState(**base)


def _one_contradiction_state() -> BankState:
    """Real state that the kernel ALLOWs while already carrying one contradiction."""
    return _bank_state(identity_mismatch_score=0.9)


def _blocking_state() -> BankState:
    return _bank_state(
        fraud_score=0.99, identity_mismatch_score=0.9,
        narrative_conflict_score=0.9, recent_failed_attempts=9,
    )


@pytest.fixture
def rig(tmp_path):
    provider = CountingProvider()
    flow = CanonicalRuntimeReceiptFlow()
    flow.register_provider(PROVIDER_ID, provider)
    return {
        "flow": flow,
        "provider": provider,
        "ctx_dir": tmp_path / "agent_contexts",
        "dec_dir": tmp_path / "kx108_decisions",
    }


def _stores(rig):
    return dict(
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
    )


def _t0(rig, state=None, mission="mission-t0", action_id="r6_re_t0"):
    return run_governed_runtime_cycle(
        AGENT_ID,
        _action(action_id),
        state if state is not None else _bank_state(),
        execution_surface=rig["flow"],
        mission_id=mission,
        provider_id=PROVIDER_ID,
        capability="analysis",
        execution_payload={"scope": "bounded"},
        **_stores(rig),
    )


def _t1(rig, previous, state=None, mission="mission-t1", action_id="r6_re_t1"):
    return run_governed_feedback_cycle(
        previous,
        _action(action_id),
        state if state is not None else _bank_state(),
        execution_surface=rig["flow"],
        mission_id=mission,
        provider_id=PROVIDER_ID,
        capability="analysis",
        execution_payload={"scope": "bounded"},
        **_stores(rig),
    )


# ── The next context is produced from observed facts ────────────────────────


def test_finished_cycle_produces_a_next_context(rig):
    t0 = _t0(rig)

    assert t0.x108_gate == "ALLOW"
    assert t0.next_context_id.startswith("cp-feedback-")
    assert t0.next_context_inherits_authority is False


def test_next_context_records_the_previous_cycle_facts(rig):
    t0 = _t0(rig)
    context = feedback_result_to_context_packet(t0)
    payload = context.payload

    assert payload["previous_action_id"] == "r6_re_t0"
    assert payload["previous_context_packet_id"] == t0.context_id
    assert payload["previous_decision_id"] == t0.decision_id
    assert payload["previous_decision_record_id"] == t0.decision_record_id
    assert payload["previous_decision_record_verified"] is True
    assert payload["previous_os3_ticket_id"] == t0.os3_ticket_id
    assert payload["previous_receipt_status"] == "COMPLETED"
    assert payload["previous_receipt_result_ref"] == t0.runtime_id
    assert payload["previous_envelope_status"] == "SEALED"


def test_previous_gate_is_a_fact_never_a_permission(rig):
    t0 = _t0(rig)
    context = feedback_result_to_context_packet(t0)

    assert context.payload["previous_x108_gate"] == "ALLOW"
    assert context.payload["_authority_inherited"] is False
    assert "NO_INHERITED_AUTHORITY" in context.labels

    # The packet itself grants nothing.
    assert context.runtime_allowed_now is False
    assert context.emits_act is False
    assert context.emits_decision is False
    assert context.advisory_only is True
    assert context.readonly is True
    assert context.decision_authority == "KX108_ONLY"
    assert context.boundary == BOUNDARY


def test_next_context_passes_validator_and_x108_boundary(rig):
    t0 = _t0(rig)
    projection = context_packet_validation_projection(
        feedback_result_to_context_packet(t0)
    )

    validation = validate_context_packet(projection)
    boundary = check_x108_context_boundary(projection)

    assert validation.valid is True
    assert validation.violations == []
    assert boundary.passed is True
    assert boundary.violations == []


def test_reentry_signal_is_non_sovereign_and_carries_evidence(rig):
    t0 = _t0(rig)
    packet = feedback_result_to_peripheral_signal(t0)

    assert packet.can_emit_act is False
    assert packet.action_id == "r6_re_t0"
    assert packet.domain == "bank"
    assert f"os3:{t0.os3_ticket_id}" in packet.evidence_refs
    assert f"kx108:{t0.decision_record_id}" in packet.evidence_refs
    assert f"apec:{t0.agent_pre_execution_context_id}" in packet.evidence_refs
    assert packet.extra_metrics["previous_x108_gate"] == "ALLOW"


def test_adapter_fails_closed_on_a_cycle_without_identity():
    class Empty:
        context_id = ""
        action_id = ""

    with pytest.raises(FeedbackContextAdapterError):
        feedback_result_to_context_packet(Empty())


# ── t0 -> t1: a fresh decision every time ──────────────────────────────────


def test_t1_is_decided_again_and_never_inherits_t0(rig):
    t0 = _t0(rig)
    assert t0.x108_gate == "ALLOW"
    assert rig["provider"].invocations == 1

    t1 = _t1(rig, t0)

    assert t1.agent_id == "FEEDBACK_REENTRY"
    assert t1.agent_layer == "FEEDBACK_MEMORY"
    assert t1.context_id == t0.next_context_id
    assert t1.context_id != t0.context_id

    # Its own decision, its own record, its own frozen context.
    assert t1.decision_id != t0.decision_id
    assert t1.trace_id != t0.trace_id
    assert t1.decision_record_id != t0.decision_record_id
    assert t1.agent_pre_execution_context_id != t0.agent_pre_execution_context_id
    assert t1.decision_record_verified is True


def test_t1_execution_requires_its_own_verified_record(rig):
    t0 = _t0(rig)
    t1 = _t1(rig, t0)

    assert t1.execution_authorized is True
    assert t1.execution_authorization_reason == EXECUTION_AUTHORIZED
    assert t1.decision_record_verified is True
    assert t1.execution_plan_binding_verified is True
    assert rig["provider"].invocations == 2

    stored = DS.load_kx108_decision_record(t1.decision_record_id, rig["dec_dir"])
    ok, reason = DS.verify_kx108_decision_record(stored)
    assert ok is True, reason
    assert stored["context_packet_id"] == t1.context_id


def test_t1_records_are_distinct_documents_on_disk(rig):
    t0 = _t0(rig)
    t1 = _t1(rig, t0)

    rec0 = DS.load_kx108_decision_record(t0.decision_record_id, rig["dec_dir"])
    rec1 = DS.load_kx108_decision_record(t1.decision_record_id, rig["dec_dir"])

    assert rec0 is not None and rec1 is not None
    assert rec0["decision_record_hash"] != rec1["decision_record_hash"]
    assert rec0["agent_execution_plan_digest"] != rec1["agent_execution_plan_digest"]


def test_a_blocked_t1_stops_even_after_an_allowed_t0(rig):
    """R6-J: a t0 ALLOW grants nothing when t1 is genuinely blocked."""
    t0 = _t0(rig)
    assert t0.x108_gate == "ALLOW"
    invocations_after_t0 = rig["provider"].invocations

    t1 = _t1(rig, t0, state=_blocking_state())

    assert t1.x108_gate == "BLOCK"
    assert t1.execution_authorized is False
    assert t1.provider_invoked is False
    assert rig["provider"].invocations == invocations_after_t0
    assert t1.receipt is None


# ── Degraded feedback really changes the next verdict ──────────────────────


def test_failed_execution_feedback_raises_a_real_block_candidate(tmp_path):
    """
    A genuinely failed execution is reported as a peripheral risk, and on a
    domain state that already carries one contradiction the kernel really
    flips ALLOW -> BLOCK. The verdict is never forced.
    """
    failing = ResultlessProvider()
    flow = CanonicalRuntimeReceiptFlow()
    flow.register_provider(PROVIDER_ID, failing)
    rig = {
        "flow": flow,
        "provider": failing,
        "ctx_dir": tmp_path / "agent_contexts",
        "dec_dir": tmp_path / "kx108_decisions",
    }

    t0 = _t0(rig, state=_one_contradiction_state())
    assert t0.x108_gate == "ALLOW"
    assert t0.provider_invoked is True
    assert t0.receipt["status"] == "FAILED"
    assert t0.next_context_recommended_gate == "BLOCK_CANDIDATE"

    signal = feedback_result_to_peripheral_signal(t0)
    assert SIGNAL_EXECUTION_FAILED in signal.risk_flags

    t1 = _t1(rig, t0, state=_one_contradiction_state())

    assert t1.x108_gate == "BLOCK"
    assert t1.execution_authorized is False
    assert t1.provider_invoked is False
    assert failing.invocations == 1  # only t0 ran


def test_healthy_feedback_leaves_the_same_state_allowed(rig):
    """Control: with the same domain state, a healthy feedback stays ALLOW."""
    t0 = _t0(rig, state=_one_contradiction_state())
    assert t0.receipt["status"] == "COMPLETED"
    assert t0.next_context_recommended_gate == "NONE"

    t1 = _t1(rig, t0, state=_one_contradiction_state())

    assert t1.x108_gate == "ALLOW"
    assert t1.provider_invoked is True


def test_refused_cycle_feedback_reports_the_refusal(rig):
    t0 = _t0(rig, state=_blocking_state())
    assert t0.x108_gate == "BLOCK"
    assert t0.provider_invoked is False

    signal = feedback_result_to_peripheral_signal(t0)
    assert SIGNAL_EXECUTION_REFUSED in signal.risk_flags
    assert t0.next_context_recommended_gate == "HOLD"


def test_reentry_never_writes_memory_or_mutates_anything(rig):
    t0 = _t0(rig)
    t1 = _t1(rig, t0)

    for result in (t0, t1):
        assert result.memory_write is False
        assert result.kernel_mutation is False
        assert result.emits_act is False
        assert result.world_action_allowed is False
        assert result.world_action_dry_run_only is True
        assert result.context_runtime_allowed_now is False
        assert result.feedback["memory_write_allowed"] is False
        result.assert_non_sovereign()


def test_a_cycle_claiming_inherited_authority_is_rejected(rig):
    t0 = _t0(rig)

    t0.next_context_inherits_authority = True
    with pytest.raises(AssertionError, match="never inherit authority"):
        t0.assert_non_sovereign()
