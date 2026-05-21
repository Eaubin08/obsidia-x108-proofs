from __future__ import annotations

from ..common import ActionCandidate, PeripheralSignalPacket
from ..agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely

SPEC = NonSovereignAgentSpec(
    agent_id="feedback_memory_agent_v3",
    layer=AgentLayer.FEEDBACK_MEMORY,
    description="Read-only feedback/memory candidate signal. Never writes to memory. Peripheral only.",
    can_emit_act=False,
    can_authorize=False,
    can_mutate_kernel=False,
    can_write_memory=False,
)


def _run(action: ActionCandidate) -> PeripheralSignalPacket:
    pkt = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    memory_status = action.payload.get("memory_status", "STABLE")

    if memory_status == "UNSTABLE":
        pkt.add_risk("MEMORY_UNSTABLE_CANDIDATE_FROZEN")
        pkt.extra_metrics["memory_candidate_frozen"] = True
        pkt.extra_metrics["memory_write_allowed"] = False
        pkt.recommended_gate = "HOLD"
    else:
        pkt.extra_metrics["memory_candidate_frozen"] = False
        pkt.extra_metrics["memory_write_allowed"] = False

    pkt.extra_metrics["memory_status"] = memory_status
    pkt.extra_metrics["memory_readonly"] = True
    pkt.extra_metrics["memory_candidate_only"] = True
    return pkt


def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, _run, action)
