from __future__ import annotations

from periphery.common import ActionCandidate
from periphery.agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from periphery.ocs_generation import run_ocs_generation

SPEC = NonSovereignAgentSpec(
    agent_id="OCS_GENERATION_COST_AGENT",
    layer=AgentLayer.OCS,
    description="Wrapper non souverain autour de run_ocs_generation",
)

def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, run_ocs_generation, action)
