"""
Runtime proof: registered agent -> AgentResult -> ContextPacket -> X108 dry-run.

Covers the canonical path closed after CG100. No placeholder assertions:
every test inspects real objects and real values produced by the real
registry, the real binder, the real validator, the real X108 context
boundary and the real X108 admission stub.
"""

from __future__ import annotations

import pytest

from periphery.agent_contracts import AgentLayer, AgentResult
from periphery.agent_registry import list_agents, run_registered_agent
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.context import agent_x108_context_flow as flow_mod
from periphery.context.agent_result_context_adapter import (
    BOUNDARY,
    agent_result_to_context_packet,
)
from periphery.context.agent_x108_context_flow import (
    ADMISSIBLE_DECISIONS,
    FLOW_BOUNDARY,
    PREGATE_FAIL_CLOSED,
    AgentX108ContextFlowResult,
    admit_agent_context,
    is_critical_action,
    run_agent_x108_context_flow,
)

AGENT_ID = "DATA_PURITY_AGENT"


def _action(action_id: str = "flow_action_001", irreversible: bool = False) -> ActionCandidate:
    return ActionCandidate(
        action_id=action_id,
        domain="bank",
        actor_id="runtime-test",
        intent="inspect",
        action_type="query",
        irreversible=irreversible,
        timestamp_plan="2026-09-03T00:00:00+00:00",
        payload={"amount": 10},
    )


def _agent_result(
    action_id: str = "flow_action_001",
    recommended_gate: str = "NONE",
    contradictions: list[str] | None = None,
) -> AgentResult:
    packet = PeripheralSignalPacket(
        action_id=action_id,
        domain="bank",
        extra_metrics={"purity": 0.91},
        unknowns=["UNKNOWN_SOURCE"],
        risk_flags=["RISK_FRESHNESS"],
        contradictions=list(contradictions or []),
        evidence_refs=["proof:flow", "agent:DATA_PURITY_AGENT"],
        recommended_gate=recommended_gate,
        can_emit_act=False,
    )
    return AgentResult(
        agent_id=AGENT_ID,
        layer=AgentLayer.DATA,
        packet=packet,
        notes=["flow provenance note"],
    )


# ── 1. API-level path: real agent -> AgentResult -> ContextPacket ─────────────


def test_registered_agent_produces_context_packet_through_flow():
    action = _action("flow_bind_001")

    agent_result = run_registered_agent(AGENT_ID, action)
    assert isinstance(agent_result, AgentResult)
    assert agent_result.packet.action_id == "flow_bind_001"

    flow = run_agent_x108_context_flow(AGENT_ID, action)

    assert isinstance(flow, AgentX108ContextFlowResult)
    assert flow.agent_id == AGENT_ID
    assert flow.action_id == "flow_bind_001"
    assert flow.context_id.startswith("cp-agent-")
    assert flow.boundary == FLOW_BOUNDARY


def test_flow_context_id_matches_binder_output_for_same_agent_result():
    """The ContextPacket really derives from THIS AgentResult, not a rebuild."""
    action = _action("flow_bind_002")

    agent_result = run_registered_agent(AGENT_ID, action)
    expected = agent_result_to_context_packet(agent_result)

    flow = run_agent_x108_context_flow(AGENT_ID, action)

    assert flow.context_id == expected.context_id
    assert expected.boundary == BOUNDARY
    assert flow.context_packet_refs == [expected.context_id]


# ── 2. Provenance ─────────────────────────────────────────────────────────────


def test_agent_provenance_is_preserved_end_to_end():
    action = _action("flow_prov_001")
    agent_result = run_registered_agent(AGENT_ID, action)

    flow = run_agent_x108_context_flow(AGENT_ID, action)

    assert flow.agent_id == agent_result.agent_id
    assert flow.agent_layer == agent_result.layer.value
    assert flow.evidence_refs == list(agent_result.packet.evidence_refs)
    assert f"agent:{AGENT_ID}" in flow.evidence_refs
    assert flow.recommended_gate == agent_result.packet.recommended_gate
    assert flow.context_projection["action_id"] == "flow_prov_001"
    assert flow.context_projection["source"] == f"agent:{AGENT_ID}"


# ── 3-8. Locked non-sovereignty invariants ───────────────────────────────────


def test_flow_result_locks_non_sovereignty_invariants():
    flow = run_agent_x108_context_flow(AGENT_ID, _action("flow_inv_001"))

    assert flow.readonly is True
    assert flow.advisory_only is True
    assert flow.emits_act is False
    assert flow.emits_decision is False
    assert flow.runtime_allowed_now is False
    assert flow.memory_write is False
    assert flow.kernel_mutation is False
    assert flow.decision_authority == "KX108_ONLY"
    assert flow.dry_run is True

    flow.assert_non_sovereign()


def test_flow_dict_exposes_the_same_locked_invariants():
    data = run_agent_x108_context_flow(AGENT_ID, _action("flow_inv_002")).to_dict()

    assert data["readonly"] is True
    assert data["advisory_only"] is True
    assert data["emits_act"] is False
    assert data["emits_decision"] is False
    assert data["runtime_allowed_now"] is False
    assert data["memory_write"] is False
    assert data["kernel_mutation"] is False
    assert data["decision_authority"] == "KX108_ONLY"
    assert data["dry_run"] is True


def test_flow_result_rejects_any_sovereign_mutation():
    flow = run_agent_x108_context_flow(AGENT_ID, _action("flow_inv_003"))

    flow.emits_act = True
    with pytest.raises(AssertionError, match="emits_act must be False"):
        flow.assert_non_sovereign()

    flow.emits_act = False
    flow.memory_write = True
    with pytest.raises(AssertionError, match="memory_write must be False"):
        flow.assert_non_sovereign()

    flow.memory_write = False
    flow.kernel_mutation = True
    with pytest.raises(AssertionError, match="kernel_mutation must be False"):
        flow.assert_non_sovereign()

    flow.kernel_mutation = False
    flow.runtime_allowed_now = True
    with pytest.raises(AssertionError, match="runtime_allowed_now must be False"):
        flow.assert_non_sovereign()

    flow.runtime_allowed_now = False
    flow.decision_authority = "PERIPHERY"
    with pytest.raises(AssertionError, match="decision_authority must be KX108_ONLY"):
        flow.assert_non_sovereign()


# ── 9-10. Canonical validator + X108 context boundary ────────────────────────


def test_canonical_validator_and_x108_boundary_accept_the_flow_context():
    flow = run_agent_x108_context_flow(AGENT_ID, _action("flow_gate_001"))

    assert flow.context_validation["valid"] is True
    assert flow.context_validation["violations"] == []
    assert flow.context_validation["packet_id"] == flow.context_id

    assert flow.context_boundary["passed"] is True
    assert flow.context_boundary["violations"] == []
    assert flow.context_boundary["decision_authority"] == "KX108_ONLY"
    assert flow.context_boundary["readonly"] is True


def test_flow_projection_carries_no_decision_or_act_capability():
    projection = run_agent_x108_context_flow(
        AGENT_ID, _action("flow_gate_002")
    ).context_projection

    assert projection["allowed_to_decide"] is False
    assert projection["allowed_to_act"] is False
    assert projection["memory_write"] is False
    assert projection["kernel_mutation"] is False
    assert projection["emits_act"] is False
    assert projection["emits_decision"] is False
    assert projection["runtime_allowed_now"] is False
    assert projection["context_signal_only"] is True
    assert projection["decision_authority"] == "KX108_ONLY"


# ── 11-12. X108 admission decisions ──────────────────────────────────────────


def test_normal_context_is_admitted_as_allow_context_only():
    flow = run_agent_x108_context_flow(AGENT_ID, _action("flow_dec_001"))

    assert flow.critical_action_requested is False
    assert flow.x108_decision == "ALLOW_CONTEXT_ONLY"
    assert flow.x108_gate_status == "X108_EVALUATED_DRY_RUN"
    assert flow.x108_ticket_id.startswith("dt-dryrun-")
    assert flow.context_admitted is True
    assert "CONTEXT_ADVISORY_ONLY" in flow.reason_codes


def test_irreversible_action_is_held_not_acted():
    flow = run_agent_x108_context_flow(
        AGENT_ID, _action("flow_dec_002", irreversible=True)
    )

    assert flow.critical_action_requested is True
    assert flow.x108_decision == "HOLD"
    assert flow.context_admitted is False
    assert "CRITICAL_ACTION_REQUIRES_HOLD" in flow.reason_codes
    assert flow.x108_gate_status == "X108_EVALUATED_DRY_RUN"


def test_criticality_is_read_from_action_and_agent_signal_only():
    reversible = _action("flow_crit_001")

    assert is_critical_action(reversible, _agent_result()) is False
    assert is_critical_action(reversible, _agent_result(recommended_gate="HOLD")) is True
    assert (
        is_critical_action(reversible, _agent_result(recommended_gate="BLOCK_CANDIDATE"))
        is True
    )
    assert (
        is_critical_action(reversible, _agent_result(contradictions=["CONTRA_X"])) is True
    )
    assert is_critical_action(_action("flow_crit_002", irreversible=True), _agent_result()) is True


def test_decision_is_always_inside_the_bounded_set():
    for irreversible in (False, True):
        for agent_id in list_agents():
            flow = run_agent_x108_context_flow(
                agent_id, _action("flow_bounded_001", irreversible=irreversible)
            )
            assert flow.x108_decision in ADMISSIBLE_DECISIONS
            assert flow.x108_decision != "ACT"
            assert flow.x108_decision != "ALLOW"
            flow.assert_non_sovereign()


# ── 13-14. Fail closed ───────────────────────────────────────────────────────


def test_pregate_failure_blocks_and_never_reaches_admission(monkeypatch):
    """A corrupted projection must BLOCK before X108 admission — never ALLOW."""
    agent_result = run_registered_agent(AGENT_ID, _action("flow_fail_001"))
    context = agent_result_to_context_packet(agent_result)

    def _corrupted_projection(_context):
        return {
            "packet_id": _context.context_id,
            "action_id": "flow_fail_001",
            "readonly": False,
            "context_signal_only": True,
            "decision_authority": "PERIPHERY",
            "allowed_to_decide": True,
            "allowed_to_act": True,
            "kernel_mutation": True,
            "memory_write": True,
            "emits_act": True,
            "emits_decision": True,
            "runtime_allowed_now": True,
            "boundary": "CORRUPTED",
            "source": "agent:DATA_PURITY_AGENT",
        }

    def _must_not_be_called(*args, **kwargs):
        raise AssertionError("X108 admission reached with an invalid context")

    monkeypatch.setattr(
        flow_mod, "context_packet_validation_projection", _corrupted_projection
    )
    monkeypatch.setattr(flow_mod, "evaluate_dry_run", _must_not_be_called)

    flow = admit_agent_context(context, agent_result, critical_action_requested=False)

    assert flow.x108_decision == "BLOCK"
    assert flow.x108_gate_status == "X108_FAIL_CLOSED"
    assert flow.x108_ticket_id == "NO_TICKET_PREGATE_FAIL_CLOSED"
    assert flow.context_admitted is False
    assert flow.reason_codes[0] == PREGATE_FAIL_CLOSED
    assert any("readonly" in code for code in flow.reason_codes)
    assert flow.context_packet_refs == []
    flow.assert_non_sovereign()


def test_mutated_context_packet_fails_closed_hard():
    agent_result = run_registered_agent(AGENT_ID, _action("flow_fail_002"))
    context = agent_result_to_context_packet(agent_result)
    context.readonly = False

    with pytest.raises(AssertionError, match="readonly must be True"):
        admit_agent_context(context, agent_result, critical_action_requested=False)


def test_sovereign_agent_result_is_rejected_before_any_context_exists():
    agent_result = _agent_result("flow_fail_003")
    agent_result.packet.can_emit_act = True

    with pytest.raises(AssertionError, match="PERIPHERY_CANNOT_EMIT_ACT"):
        agent_result_to_context_packet(agent_result)


def test_unknown_agent_is_rejected_by_the_flow():
    with pytest.raises(KeyError, match="UNKNOWN_AGENT"):
        run_agent_x108_context_flow("NOT_A_REAL_AGENT_XYZ", _action("flow_fail_004"))


def test_malformed_agent_result_is_rejected_by_the_binder():
    with pytest.raises(TypeError, match="AGENT_RESULT_REQUIRED"):
        agent_result_to_context_packet(object())


# ── 15-17. No memory write, no ACT, no X108 bypass ───────────────────────────


def test_flow_writes_no_memory_and_touches_no_bus(tmp_path, monkeypatch):
    """The flow must be pure: no file written anywhere while it runs."""
    monkeypatch.chdir(tmp_path)

    flow = run_agent_x108_context_flow(AGENT_ID, _action("flow_pure_001"))

    assert flow.memory_write is False
    assert list(tmp_path.iterdir()) == []


def test_no_act_token_anywhere_in_the_observable_flow_output():
    data = run_agent_x108_context_flow(
        AGENT_ID, _action("flow_noact_001", irreversible=True)
    ).to_dict()

    assert data["x108_decision"] != "ACT"
    assert data["emits_act"] is False
    for key in ("context_validation", "context_boundary", "context_projection"):
        assert data[key].get("emits_act", False) is False
        assert data[key].get("allowed_to_act", False) is False


def test_flow_cannot_bypass_x108_admission():
    """Every non-blocked decision must carry a real X108 ticket reference."""
    flow = run_agent_x108_context_flow(AGENT_ID, _action("flow_bypass_001"))

    assert flow.x108_ticket_id != "NO_TICKET_PREGATE_FAIL_CLOSED"
    assert flow.x108_gate_status == "X108_EVALUATED_DRY_RUN"
    assert flow.context_id in flow.context_packet_refs
    assert flow.reason_codes  # X108 always states why


# ── 18. Real binding to action_id / agent_id / evidence_refs ─────────────────


def test_context_is_bound_to_the_exact_action_and_agent():
    first = run_agent_x108_context_flow(AGENT_ID, _action("flow_bound_A"))
    second = run_agent_x108_context_flow(AGENT_ID, _action("flow_bound_B"))
    other_agent = run_agent_x108_context_flow("PROVENANCE_ANTI_MIMETIC_AGENT", _action("flow_bound_A"))

    assert first.action_id == "flow_bound_A"
    assert second.action_id == "flow_bound_B"
    assert first.context_id != second.context_id

    assert other_agent.agent_id == "PROVENANCE_ANTI_MIMETIC_AGENT"
    assert other_agent.context_id != first.context_id
    assert "agent:PROVENANCE_ANTI_MIMETIC_AGENT" in other_agent.evidence_refs
