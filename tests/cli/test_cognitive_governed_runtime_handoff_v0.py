from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (str(ROOT), str(ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from obsidia_cognitive_governed_runtime_handoff_v0 import (  # noqa: E402
    CognitiveGovernedHandoffError,
    prepare_cognitive_governed_handoff,
    run_cognitive_governed_handoff,
    verify_cognitive_governed_handoff,
)
from runtime_wiring.packet_types import DecisionTicketDryRun  # noqa: E402
from scripts.obsidia_governed_runtime_cycle_v1 import (  # noqa: E402
    EXECUTION_AUTHORIZED,
    REFUSED_GATE_NOT_ALLOW,
)
from scripts.providers.canonical_runtime_receipt_flow_v1 import (  # noqa: E402
    CanonicalRuntimeReceiptFlow,
)
from sigma.contracts import BankState  # noqa: E402


PROVIDER_ID = "j3_provider"


class CountingProvider:
    def __init__(self):
        self.calls = 0
        self.last_kwargs = None

    def __call__(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        return {"runtime_id": "j3-runtime-001", "provider": PROVIDER_ID}


@pytest.fixture
def surface():
    provider = CountingProvider()
    flow = CanonicalRuntimeReceiptFlow()
    flow.register_provider(PROVIDER_ID, provider)
    return flow, provider


def _bank_state(**over):
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


def _allow_state():
    return _bank_state()


def _hold_state():
    return _bank_state(amount=99999.0, available_cash=1.0, account_balance=1.0)


def _block_state():
    return _bank_state(
        fraud_score=0.99,
        identity_mismatch_score=0.9,
        narrative_conflict_score=0.9,
        recent_failed_attempts=9,
    )


def _dry_ticket(decision="ALLOW_CONTEXT_ONLY"):
    return DecisionTicketDryRun(
        ticket_id=f"dt-j3-{decision.lower()}",
        intent_envelope_ref="ie-j3-cognitive",
        decision=decision,
        reason_codes=["J3_TEST_PROVENANCE_ONLY"],
        x108_gate_status="X108_EVALUATED_DRY_RUN",
        timestamp_or_tick="2026-09-23T00:00:00Z",
        context_packet_refs=["cp-c1-j3"],
    )


def _proposal(**over):
    params = dict(
        mission_id="mission-j3-001",
        provider_id=PROVIDER_ID,
        capability="analysis",
        payload={"scope": "bounded", "value": 42},
        domain="bank",
        action_id="j3-action-001",
        intent="transfer_review",
        action_type="transfer",
        context_packet_ref="cp-c1-j3",
        c1_provenance={"context_packet_v2_ref": "cpv2-j3", "c1": "audit"},
        dry_run_ticket=_dry_ticket(),
    )
    params.update(over)
    return prepare_cognitive_governed_handoff(**params)


def test_t1_prepare_only_does_not_execute(surface):
    _flow, provider = surface
    proposal = _proposal()

    ok, reason = verify_cognitive_governed_handoff(proposal)

    assert ok is True, reason
    assert provider.calls == 0
    assert proposal["provider_called"] is False
    assert proposal["execution_started"] is False
    assert proposal["authority_boundary"]["decision_authority"] == "KX108_ONLY"
    assert proposal["authority_boundary"]["emits_act"] is False


def test_t2_dry_run_ticket_is_not_authority(surface, tmp_path):
    flow, provider = surface
    proposal = _proposal(dry_run_ticket=_dry_ticket("ALLOW_CONTEXT_ONLY"))

    result = run_cognitive_governed_handoff(
        proposal,
        domain_state=_block_state(),
        execution_surface=flow,
        agent_context_store_dir=tmp_path / "ctx",
        decision_store_dir=tmp_path / "dec",
    )

    assert proposal["dry_run_ticket_audit"]["decision"] == "ALLOW_CONTEXT_ONLY"
    assert proposal["dry_run_ticket_audit"]["used_as_authority"] is False
    assert result.decision_engine == "sigma.guard.GuardX108.decide"
    assert result.x108_gate == "BLOCK"
    assert provider.calls == 0


def test_t3_block_refuses_provider(surface, tmp_path):
    flow, provider = surface

    result = run_cognitive_governed_handoff(
        _proposal(action_id="j3-block"),
        domain_state=_block_state(),
        execution_surface=flow,
        agent_context_store_dir=tmp_path / "ctx",
        decision_store_dir=tmp_path / "dec",
    )

    assert result.x108_gate == "BLOCK"
    assert result.execution_authorization_reason == REFUSED_GATE_NOT_ALLOW
    assert result.provider_invoked is False
    assert provider.calls == 0
    assert result.receipt is None
    assert result.decision_record_verified is True


def test_t4_hold_refuses_provider(surface, tmp_path):
    flow, provider = surface

    result = run_cognitive_governed_handoff(
        _proposal(action_id="j3-hold"),
        domain_state=_hold_state(),
        execution_surface=flow,
        agent_context_store_dir=tmp_path / "ctx",
        decision_store_dir=tmp_path / "dec",
    )

    assert result.x108_gate == "HOLD"
    assert result.execution_authorization_reason == REFUSED_GATE_NOT_ALLOW
    assert result.provider_invoked is False
    assert provider.calls == 0


def test_t5_real_allow_invokes_provider_once_with_same_plan(surface, tmp_path):
    flow, provider = surface
    proposal = _proposal(action_id="j3-allow")

    result = run_cognitive_governed_handoff(
        proposal,
        domain_state=_allow_state(),
        execution_surface=flow,
        agent_context_store_dir=tmp_path / "ctx",
        decision_store_dir=tmp_path / "dec",
    )

    assert result.x108_gate == "ALLOW"
    assert result.execution_authorization_reason == EXECUTION_AUTHORIZED
    assert result.provider_invoked is True
    assert provider.calls == 1
    assert provider.last_kwargs["mission_id"] == proposal["mission_id"]
    assert provider.last_kwargs["capability"] == proposal["capability"]
    assert provider.last_kwargs["payload"] == proposal["payload"]
    assert result.receipt["status"] == "COMPLETED"
    assert result.receipt["provider_id"] == PROVIDER_ID


def test_t6_capability_substitution_is_refused(surface, tmp_path):
    flow, _provider = surface
    proposal = _proposal(action_id="j3-substitution")
    proposal["capability"] = "mutated-capability"

    with pytest.raises(CognitiveGovernedHandoffError) as exc:
        run_cognitive_governed_handoff(
            proposal,
            domain_state=_allow_state(),
            execution_surface=flow,
            agent_context_store_dir=tmp_path / "ctx",
            decision_store_dir=tmp_path / "dec",
        )

    assert "HANDOFF_PLAN_HASH_MISMATCH" in str(exc.value)


def test_t7_provenance_stays_audit_context():
    proposal = _proposal()

    assert proposal["context_packet_ref"] == "cp-c1-j3"
    assert proposal["c1_provenance"]["context_packet_v2_ref"] == "cpv2-j3"
    assert proposal["dry_run_ticket_audit"]["execution_authorization"] is False
    assert proposal["dry_run_ticket_used_as_authority"] is False
    assert proposal["execution_authorization"] is False


def test_t8_handoff_alone_never_self_authorizes():
    proposal = _proposal()

    assert proposal["authority_boundary"]["handoff_authority"] == "NONE"
    assert proposal["authority_boundary"]["allowed_to_act"] is False
    assert proposal["authority_boundary"]["allowed_to_decide"] is False
    assert proposal["execution_authorization"] is False
    assert proposal["provider_called"] is False
