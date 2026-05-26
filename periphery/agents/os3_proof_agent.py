from __future__ import annotations

from typing import Any

from ..common import ActionCandidate, PeripheralSignalPacket
from ..agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from ..os3_ticket import build_os3_ticket, ticket_is_valid

SPEC = NonSovereignAgentSpec(
    agent_id="os3_proof_agent_v1",
    layer=AgentLayer.OS3,
    description="OS3 proof ticket signal agent. Never authorizes the action.",
    can_emit_act=False,
    can_authorize=False,
    can_mutate_kernel=False,
    can_write_memory=False,
)


def build(action: Any, packet: Any, envelope: Any):
    SPEC.assert_safe()
    ticket = build_os3_ticket(action, packet, envelope)
    return ticket, ticket_is_valid(ticket)


def _run(action: ActionCandidate) -> PeripheralSignalPacket:
    pkt = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    pkt.extra_metrics["os3_agent_status"] = "READY_PENDING_ENVELOPE"
    pkt.extra_metrics["os3_ticket_pending"] = True
    return pkt


def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, _run, action)
