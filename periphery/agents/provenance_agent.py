from __future__ import annotations

from periphery.common import ActionCandidate
from periphery.agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from periphery.provenance_gate import run_provenance_gate

SPEC = NonSovereignAgentSpec(
    agent_id="PROVENANCE_ANTI_MIMETIC_AGENT",
    layer=AgentLayer.PROVENANCE,
    description="Wrapper non souverain autour de run_provenance_gate",
)

def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, run_provenance_gate, action)
