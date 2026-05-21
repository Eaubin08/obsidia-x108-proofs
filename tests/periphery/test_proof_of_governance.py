import pytest
from periphery.math_core.governed_state import GovernedStateVector, DecisionEnvelopeTheta
from periphery.math_core.lyapunov import compute_lyapunov
from periphery.math_core.proof_of_governance import proof_of_governance
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket


def _make_ticket():
    action = ActionCandidate(
        action_id="pog_test",
        domain="bank",
        actor_id="t",
        intent="t",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={},
    )
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    class E:
        x108_gate = "ALLOW"
        reason_code = "X"
        severity = "INFO"
        metrics = {}
        unknowns = []
        risk_flags = []
        contradictions = []
        evidence_refs = []
    return build_os3_ticket(action, packet, E())


def test_pog_valid():
    # all-zero state vector → L=0 → lyapunov stable
    sv = GovernedStateVector(I=0.0, delta_E=0.0, delta_C=0.0, V_inst=0.0, delta_tau=0.0, F=0.0)
    lyapunov = compute_lyapunov("pog_test", sv)
    theta = DecisionEnvelopeTheta(theta_id="t", x108_gate="ALLOW", confidence=0.9, reason_code="X")
    ticket = _make_ticket()
    result = proof_of_governance("pog_test", theta, lyapunov, ticket)
    assert result.pog_valid is True


def test_pog_invalid_on_unstable():
    sv = GovernedStateVector(V_inst=0.9)
    lyapunov = compute_lyapunov("x", sv)
    theta = DecisionEnvelopeTheta(theta_id="t", x108_gate="ALLOW", confidence=0.5, reason_code="X")
    ticket = _make_ticket()
    result = proof_of_governance("x", theta, lyapunov, ticket)
    assert result.pog_valid is False


def test_pog_result_not_lean_proof():
    sv = GovernedStateVector()
    lyapunov = compute_lyapunov("x", sv)
    theta = DecisionEnvelopeTheta(theta_id="t", x108_gate="ALLOW", confidence=0.9, reason_code="X")
    ticket = _make_ticket()
    result = proof_of_governance("x", theta, lyapunov, ticket)
    d = result.to_dict()
    assert "pog_valid" in d
    assert "lyapunov_stable" in d
