from __future__ import annotations

from ..common import ActionCandidate, PeripheralSignalPacket
from ..agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely

SPEC = NonSovereignAgentSpec(
    agent_id="world_action_agent_v4",
    layer=AgentLayer.WORLD_ACTION,
    description="Dry-run world action signal. Never emits real action. Requires human takeover for any real execution. Peripheral only.",
    can_emit_act=False,
    can_authorize=False,
    can_mutate_kernel=False,
    can_write_memory=False,
)

_BLOCKED_CAPABILITIES = [
    "PAYMENT",
    "TRADE_EXECUTION",
    "API_MUTATION",
    "POSTING",
    "EMAIL",
    "MEMORY_WRITE",
    "KERNEL_BYPASS",
]


def _run(action: ActionCandidate) -> PeripheralSignalPacket:
    pkt = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    pkt.extra_metrics["dry_run_only"] = True
    pkt.extra_metrics["world_action_allowed"] = False
    pkt.extra_metrics["consent_checkpoint_required"] = True
    pkt.extra_metrics["requires_human_takeover"] = True
    pkt.extra_metrics["blocked_capabilities"] = _BLOCKED_CAPABILITIES

    if action.irreversible:
        pkt.add_unknown("IRREVERSIBLE_WORLD_ACTION_PENDING_HUMAN_GATE")
        pkt.recommended_gate = "HOLD"

    pkt.evidence_refs.append("world_action:dry_run_v4")
    return pkt


def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, _run, action)
