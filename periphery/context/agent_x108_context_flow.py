"""
Canonical runtime flow: registered agent -> AgentResult -> ContextPacket -> X108.

This module closes the historical runtime gap identified by CG93/CG97:

    run_registered_agent(...)
      -> AgentResult
      -> agent_result_to_context_packet(...)      (canonical binder)
      -> context_packet_validation_projection(...)
      -> validate_context_packet(...)
      -> check_x108_context_boundary(...)
      -> runtime_wiring.x108_admission_stub.evaluate_dry_run(...)
      -> observable dry-run flow result

It is an orchestration layer only. It:
- does not decide;
- does not emit ACT;
- does not authorize execution;
- does not mutate the kernel;
- does not write memory;
- does not enable runtime execution;
- does not introduce a third ContextPacket model.

Pre-gate failure (validator or X108 context boundary) is fail-closed: the
flow reports BLOCK and never reaches admission. Refusing admission is not
a peripheral decision -- no ALLOW can ever originate here.

decision_authority remains KX108_ONLY.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from periphery.agent_registry import run_registered_agent
from periphery.common import ActionCandidate
from periphery.agent_contracts import AgentResult
from periphery.context.agent_result_context_adapter import (
    agent_result_to_context_packet,
    context_packet_validation_projection,
)
from periphery.context.context_packet_validator import validate_context_packet
from periphery.x108_ingress.x108_context_boundary import check_x108_context_boundary
from runtime_wiring.packet_types import ContextPacket
from runtime_wiring.x108_admission_stub import evaluate_dry_run

FLOW_BOUNDARY = "AGENT_TO_X108_CONTEXT_DRY_RUN_ONLY"
PREGATE_FAIL_CLOSED = "PREGATE_FAIL_CLOSED"

ADMISSIBLE_DECISIONS = frozenset({"BLOCK", "HOLD", "ALLOW_CONTEXT_ONLY"})

CRITICAL_GATE_HINTS = frozenset({"HOLD", "BLOCK_CANDIDATE"})


@dataclass
class AgentX108ContextFlowResult:
    """Observable, bounded proof object for one agent -> X108 dry-run pass."""

    agent_id: str
    agent_layer: str
    action_id: str
    context_id: str
    x108_decision: str
    x108_gate_status: str
    x108_ticket_id: str
    critical_action_requested: bool
    context_validation: dict[str, Any] = field(default_factory=dict)
    context_boundary: dict[str, Any] = field(default_factory=dict)
    context_projection: dict[str, Any] = field(default_factory=dict)
    reason_codes: list[str] = field(default_factory=list)
    context_packet_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    agent_notes: list[str] = field(default_factory=list)
    recommended_gate: str = "NONE"
    # Locked non-sovereignty invariants
    advisory_only: bool = True
    readonly: bool = True
    runtime_allowed_now: bool = False
    emits_act: bool = False
    emits_decision: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    decision_authority: str = "KX108_ONLY"
    dry_run: bool = True
    boundary: str = FLOW_BOUNDARY

    @property
    def context_admitted(self) -> bool:
        return self.x108_decision == "ALLOW_CONTEXT_ONLY"

    def assert_non_sovereign(self) -> None:
        if self.emits_act:
            raise AssertionError("FLOW_VIOLATION: emits_act must be False")
        if self.emits_decision:
            raise AssertionError("FLOW_VIOLATION: emits_decision must be False")
        if self.memory_write:
            raise AssertionError("FLOW_VIOLATION: memory_write must be False")
        if self.kernel_mutation:
            raise AssertionError("FLOW_VIOLATION: kernel_mutation must be False")
        if self.runtime_allowed_now:
            raise AssertionError("FLOW_VIOLATION: runtime_allowed_now must be False")
        if not self.readonly or not self.advisory_only:
            raise AssertionError("FLOW_VIOLATION: flow result must stay readonly advisory")
        if self.decision_authority != "KX108_ONLY":
            raise AssertionError("FLOW_VIOLATION: decision_authority must be KX108_ONLY")
        if not self.dry_run:
            raise AssertionError("FLOW_VIOLATION: dry_run must be True")
        if self.x108_decision not in ADMISSIBLE_DECISIONS:
            raise AssertionError(
                "FLOW_VIOLATION: decision outside BLOCK/HOLD/ALLOW_CONTEXT_ONLY: "
                + str(self.x108_decision)
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_layer": self.agent_layer,
            "action_id": self.action_id,
            "context_id": self.context_id,
            "context_admitted": self.context_admitted,
            "x108_decision": self.x108_decision,
            "x108_gate_status": self.x108_gate_status,
            "x108_ticket_id": self.x108_ticket_id,
            "critical_action_requested": self.critical_action_requested,
            "context_validation": self.context_validation,
            "context_boundary": self.context_boundary,
            "context_projection": self.context_projection,
            "reason_codes": self.reason_codes,
            "context_packet_refs": self.context_packet_refs,
            "evidence_refs": self.evidence_refs,
            "agent_notes": self.agent_notes,
            "recommended_gate": self.recommended_gate,
            "advisory_only": self.advisory_only,
            "readonly": self.readonly,
            "runtime_allowed_now": self.runtime_allowed_now,
            "emits_act": self.emits_act,
            "emits_decision": self.emits_decision,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "decision_authority": self.decision_authority,
            "dry_run": self.dry_run,
            "boundary": self.boundary,
        }


def is_critical_action(action: ActionCandidate, result: AgentResult) -> bool:
    """
    Conservative criticality read used to request an X108 HOLD.

    Criticality is only ever an input to X108; it never produces a decision.
    """
    if action.irreversible:
        return True
    if result.packet.recommended_gate in CRITICAL_GATE_HINTS:
        return True
    if result.packet.contradictions:
        return True
    return False


def admit_agent_context(
    context: ContextPacket,
    agent_result: AgentResult,
    critical_action_requested: bool,
) -> AgentX108ContextFlowResult:
    """
    Run the pre-gate + X108 dry-run admission for one already-bound ContextPacket.

    Fail-closed: if the canonical validator or the X108 context boundary
    rejects the projection, admission is never reached and BLOCK is reported.
    """
    projection = context_packet_validation_projection(context)

    validation = validate_context_packet(projection)
    boundary = check_x108_context_boundary(projection)

    packet = agent_result.packet

    common = {
        "agent_id": agent_result.agent_id,
        "agent_layer": agent_result.layer.value,
        "action_id": packet.action_id,
        "context_id": context.context_id,
        "critical_action_requested": critical_action_requested,
        "context_validation": validation.to_dict(),
        "context_boundary": boundary.to_dict(),
        "context_projection": projection,
        "evidence_refs": list(packet.evidence_refs),
        "agent_notes": list(agent_result.notes),
        "recommended_gate": packet.recommended_gate,
    }

    if not validation.valid or not boundary.passed:
        flow = AgentX108ContextFlowResult(
            x108_decision="BLOCK",
            x108_gate_status="X108_FAIL_CLOSED",
            x108_ticket_id="NO_TICKET_PREGATE_FAIL_CLOSED",
            reason_codes=[PREGATE_FAIL_CLOSED, *validation.violations, *boundary.violations],
            context_packet_refs=[],
            **common,
        )
        flow.assert_non_sovereign()
        return flow

    ticket = evaluate_dry_run(
        [context],
        critical_action_requested=critical_action_requested,
    )
    ticket.validate_invariants()

    flow = AgentX108ContextFlowResult(
        x108_decision=ticket.decision,
        x108_gate_status=ticket.x108_gate_status,
        x108_ticket_id=ticket.ticket_id,
        reason_codes=list(ticket.reason_codes),
        context_packet_refs=list(ticket.context_packet_refs),
        **common,
    )
    flow.assert_non_sovereign()
    return flow


def run_agent_x108_context_flow(
    agent_id: str,
    action: ActionCandidate,
) -> AgentX108ContextFlowResult:
    """
    Full canonical path: registered agent -> AgentResult -> ContextPacket -> X108.

    Raises KeyError for an unknown agent and fails closed on any sovereignty
    violation raised upstream by the agent contracts or the canonical binder.
    """
    result = run_registered_agent(agent_id, action)
    result.assert_non_sovereign()

    context = agent_result_to_context_packet(result)

    return admit_agent_context(
        context,
        result,
        critical_action_requested=is_critical_action(action, result),
    )
