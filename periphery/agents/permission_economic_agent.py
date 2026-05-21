from __future__ import annotations

from periphery.common import ActionCandidate
from periphery.agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from periphery.permission_economic import run_permission_economic

SPEC = NonSovereignAgentSpec(
    agent_id="PERMISSION_ECONOMIC_AGENT",
    layer=AgentLayer.PERMISSION_ECONOMIC,
    description="Wrapper non souverain autour de run_permission_economic",
)

def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, run_permission_economic, action)
