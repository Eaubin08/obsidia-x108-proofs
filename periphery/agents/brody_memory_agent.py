from __future__ import annotations

from periphery.common import ActionCandidate
from periphery.agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from periphery.memory_governor import run_memory_governor

SPEC = NonSovereignAgentSpec(
    agent_id="BRODY_MEMORY_GOVERNOR_AGENT",
    layer=AgentLayer.MEMORY,
    description="Wrapper non souverain autour de run_memory_governor",
)

def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, run_memory_governor, action)
