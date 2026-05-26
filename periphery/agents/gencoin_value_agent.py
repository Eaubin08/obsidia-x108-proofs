from __future__ import annotations

from typing import Any

from ..common import ActionCandidate, PeripheralSignalPacket
from ..agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from ..gencoin import compute_gencoin

SPEC = NonSovereignAgentSpec(
    agent_id="gencoin_value_agent_v1",
    layer=AgentLayer.GENCOIN,
    description="Computes Gencoin candidate post-proof signal. Never authorizes or executes.",
    can_emit_act=False,
    can_authorize=False,
    can_mutate_kernel=False,
    can_write_memory=False,
)


def compute(action: Any, packet: Any, ticket: Any):
    SPEC.assert_safe()
    return compute_gencoin(action, packet, ticket)


def _run(action: ActionCandidate) -> PeripheralSignalPacket:
    pkt = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    pkt.extra_metrics["gencoin_agent_status"] = "CANDIDATE_PENDING_OS3"
    pkt.extra_metrics["mint_allowed"] = False
    pkt.extra_metrics["gencoin_agent_dry_run"] = True
    return pkt


def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, _run, action)
