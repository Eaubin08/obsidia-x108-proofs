import pytest

from periphery.agent_contracts import (
    AgentLayer,
    AgentResult,
)
from periphery.common import PeripheralSignalPacket
from periphery.context.agent_result_context_adapter import (
    BOUNDARY,
    agent_result_to_context_packet,
    context_packet_validation_projection,
)
from periphery.context.context_packet_validator import (
    validate_context_packet,
)
from periphery.x108_ingress.x108_context_boundary import (
    check_x108_context_boundary,
)
from runtime_wiring.x108_admission_stub import evaluate_dry_run


def _result() -> AgentResult:
    packet = PeripheralSignalPacket(
        action_id="agent_bind_001",
        domain="bank",
        extra_metrics={
            "score": 0.75,
        },
        unknowns=[
            "UNKNOWN_SAMPLE",
        ],
        risk_flags=[
            "RISK_SAMPLE",
        ],
        contradictions=[],
        evidence_refs=[
            "proof:test",
            "agent:TEST_AGENT",
        ],
        recommended_gate="HOLD",
        can_emit_act=False,
    )

    return AgentResult(
        agent_id="TEST_AGENT",
        layer=AgentLayer.DATA,
        packet=packet,
        notes=[
            "test provenance",
        ],
    )


def test_agent_result_binds_to_runtime_context_packet():
    result = _result()

    context = agent_result_to_context_packet(result)

    assert context.source == "agent:TEST_AGENT"
    assert context.boundary == BOUNDARY
    assert context.advisory_only is True
    assert context.readonly is True
    assert context.runtime_allowed_now is False
    assert context.emits_act is False
    assert context.emits_decision is False
    assert context.decision_authority == "KX108_ONLY"

    context.validate_invariants()


def test_agent_result_provenance_is_preserved():
    context = agent_result_to_context_packet(
        _result()
    )

    payload = context.payload

    assert payload["agent_id"] == "TEST_AGENT"
    assert payload["agent_layer"] == "DATA"
    assert payload["action_id"] == "agent_bind_001"
    assert payload["domain"] == "bank"

    assert payload["extra_metrics"]["score"] == 0.75

    assert payload["unknowns"] == [
        "UNKNOWN_SAMPLE",
    ]

    assert payload["risk_flags"] == [
        "RISK_SAMPLE",
    ]

    assert payload["evidence_refs"] == [
        "proof:test",
        "agent:TEST_AGENT",
    ]

    assert payload["recommended_gate"] == "HOLD"

    assert payload["agent_notes"] == [
        "test provenance",
    ]


def test_context_id_is_deterministically_bound_to_agent_result():
    first = agent_result_to_context_packet(
        _result()
    )

    second = agent_result_to_context_packet(
        _result()
    )

    assert first.context_id == second.context_id
    assert first.context_id.startswith(
        "cp-agent-"
    )


def test_malformed_agent_result_fails_closed():
    with pytest.raises(
        TypeError,
        match="AGENT_RESULT_REQUIRED",
    ):
        agent_result_to_context_packet(
            object()
        )


def test_sovereign_agent_packet_is_rejected():
    result = _result()
    result.packet.can_emit_act = True

    with pytest.raises(
        AssertionError,
        match="PERIPHERY_CANNOT_EMIT_ACT",
    ):
        agent_result_to_context_packet(
            result
        )


def test_existing_context_validator_accepts_projection():
    context = agent_result_to_context_packet(
        _result()
    )

    projection = context_packet_validation_projection(
        context
    )

    validation = validate_context_packet(
        projection
    )

    assert validation.valid is True
    assert validation.violations == []


def test_existing_x108_context_boundary_accepts_projection():
    context = agent_result_to_context_packet(
        _result()
    )

    projection = context_packet_validation_projection(
        context
    )

    boundary = check_x108_context_boundary(
        projection
    )

    assert boundary.passed is True
    assert boundary.violations == []
    assert boundary.readonly is True
    assert (
        boundary.decision_authority
        == "KX108_ONLY"
    )


def test_agent_context_enters_existing_x108_dry_run_only():
    context = agent_result_to_context_packet(
        _result()
    )

    ticket = evaluate_dry_run(
        [context],
        critical_action_requested=False,
    )

    assert (
        ticket.decision
        == "ALLOW_CONTEXT_ONLY"
    )

    assert (
        ticket.x108_gate_status
        == "X108_EVALUATED_DRY_RUN"
    )

    assert context.context_id in (
        ticket.context_packet_refs
    )

    assert ticket.decision != "ACT"


def test_critical_agent_context_can_only_hold_not_act():
    context = agent_result_to_context_packet(
        _result()
    )

    ticket = evaluate_dry_run(
        [context],
        critical_action_requested=True,
    )

    assert ticket.decision == "HOLD"
    assert ticket.decision != "ACT"
