from __future__ import annotations

from periphery.common import ActionCandidate
from periphery.agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from periphery.operational_constance import run_operational_constance

SPEC = NonSovereignAgentSpec(
    agent_id="OPERATIONAL_CONSTANCE_AGENT",
    layer=AgentLayer.OPERATIONAL_CONSTANCE,
    description="Wrapper non souverain autour de run_operational_constance",
)

def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, run_operational_constance, action)
