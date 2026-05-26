from __future__ import annotations

from periphery.common import ActionCandidate
from periphery.agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from periphery.timeverse import run_timeverse

SPEC = NonSovereignAgentSpec(
    agent_id="TIMEVERSE_TRAJECTORY_AGENT",
    layer=AgentLayer.TIMEVERSE,
    description="Wrapper non souverain autour de run_timeverse",
)

def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, run_timeverse, action)
