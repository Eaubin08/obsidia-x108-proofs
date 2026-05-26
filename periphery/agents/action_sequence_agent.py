from __future__ import annotations

from ..common import ActionCandidate, PeripheralSignalPacket
from ..agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from ..action_sequence_governor import ActionSequence, ActionStep, govern_action_sequence

SPEC = NonSovereignAgentSpec(
    agent_id="action_sequence_agent_v3",
    layer=AgentLayer.CONTROL,
    description="Governs multi-step, async, and irreversible action sequences. Peripheral only.",
    can_emit_act=False,
    can_authorize=False,
    can_mutate_kernel=False,
    can_write_memory=False,
)


def _run(action: ActionCandidate) -> PeripheralSignalPacket:
    raw_steps = action.payload.get("steps", [])
    if not raw_steps:
        pkt = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
        pkt.extra_metrics["sequence_step_count"] = 0
        return pkt

    steps = [
        ActionStep(
            step_id=s.get("step_id", f"step_{i}"),
            tool=s.get("tool", ""),
            irreversible=s.get("irreversible", False),
            async_step=s.get("async_step", False),
            requires_permission=s.get("requires_permission", True),
            changed_plan=s.get("changed_plan", False),
            payload=s.get("payload", {}),
        )
        for i, s in enumerate(raw_steps)
    ]
    seq = ActionSequence(action_id=action.action_id, steps=steps)
    return govern_action_sequence(action, seq)


def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, _run, action)
