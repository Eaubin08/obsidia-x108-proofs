"""
Phase F integration test: SovereignTicket → OS3ProofTicket → ProofOfGovernance chain.
Validates the full proof chain without modifying any kernel or protected files.
"""
import pytest
import uuid
from dataclasses import dataclass
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
from periphery.os3_ticket import OS3ProofTicket, build_os3_ticket
from periphery.math_core.governed_state import GovernedStateVector, DecisionEnvelopeTheta
from periphery.math_core.lyapunov import compute_lyapunov
from periphery.math_core.proof_of_governance import proof_of_governance


def _make_os3_ticket(action_id: str, gate: str = "ALLOW") -> OS3ProofTicket:
    h = uuid.uuid4().hex
    return OS3ProofTicket(
        ticket_id=f"os3_{action_id}",
        action_id=action_id,
        domain="bank",
        x108_gate=gate,
        reason_code="TEST",
        severity="INFO",
        scores={},
        unknowns=[],
        risk_flags=[],
        contradictions=[],
        evidence_refs=[],
        input_hash=h,
        output_hash=uuid.uuid4().hex,
        trace_hash=uuid.uuid4().hex,
        merkle_root=uuid.uuid4().hex,
        replay_status="PASS",
    )


def test_full_pog_chain_valid():
    action_id = "chain_001"
    os3 = _make_os3_ticket(action_id)
    ticket = issue_sovereign_ticket(
        action_id=action_id,
        os3_ticket_id=os3.ticket_id,
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY",
    )
    sv = GovernedStateVector(I=0.0, delta_E=0.0, delta_C=0.0, V_inst=0.0, delta_tau=0.0, F=0.0)
    lyapunov = compute_lyapunov(action_id, sv)
    theta = DecisionEnvelopeTheta(theta_id="theta_001", x108_gate="ALLOW", confidence=0.9, reason_code="ALLOW_STANDARD")
    pog = proof_of_governance(action_id, theta, lyapunov, os3)
    assert pog.pog_valid is True
    assert pog.theta_maps_to_omega is True
    assert pog.lyapunov_stable is True
    assert pog.ticket_valid is True


def test_pog_fails_without_os3_hashes():
    action_id = "chain_002"

    @dataclass
    class FakeTicket:
        input_hash: str = ""
        output_hash: str = ""
        trace_hash: str = ""
        merkle_root: str = ""

    sv = GovernedStateVector(I=0.0, delta_E=0.0, delta_C=0.0, V_inst=0.0, delta_tau=0.0, F=0.0)
    lyapunov = compute_lyapunov(action_id, sv)
    theta = DecisionEnvelopeTheta(theta_id="theta_002", x108_gate="ALLOW", confidence=0.9, reason_code="ALLOW_STANDARD")
    pog = proof_of_governance(action_id, theta, lyapunov, FakeTicket())
    assert pog.pog_valid is False
    assert pog.ticket_valid is False


def test_pog_fails_when_lyapunov_unstable():
    action_id = "chain_003"
    os3 = _make_os3_ticket(action_id)
    sv = GovernedStateVector(I=0.0, delta_E=0.9, delta_C=0.9, V_inst=0.9, delta_tau=0.9, F=0.0)
    lyapunov = compute_lyapunov(action_id, sv)
    theta = DecisionEnvelopeTheta(theta_id="theta_003", x108_gate="ALLOW", confidence=0.9, reason_code="ALLOW_STANDARD")
    pog = proof_of_governance(action_id, theta, lyapunov, os3)
    assert pog.lyapunov_stable is False
    assert pog.pog_valid is False


def test_sovereign_ticket_always_dry_run():
    ticket = issue_sovereign_ticket(
        action_id="chain_004",
        os3_ticket_id="os3_004",
        x108_gate="ALLOW",
        scope="*",
        autonomy_level=5,
        world_call_class="IRREVERSIBLE",
    )
    assert ticket.dry_run_only is True


def test_chain_invalid_gate_theta_not_in_omega():
    action_id = "chain_005"
    os3 = _make_os3_ticket(action_id)
    sv = GovernedStateVector(I=0.0, delta_E=0.0, delta_C=0.0, V_inst=0.0, delta_tau=0.0, F=0.0)
    lyapunov = compute_lyapunov(action_id, sv)
    theta = DecisionEnvelopeTheta(theta_id="theta_005", x108_gate="INVALID_GATE", confidence=0.1, reason_code="UNKNOWN")
    pog = proof_of_governance(action_id, theta, lyapunov, os3)
    assert pog.theta_maps_to_omega is False
    assert pog.pog_valid is False
