from __future__ import annotations

from periphery.common import ActionCandidate
from periphery.agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from periphery.eml_compression import run_eml_compression

SPEC = NonSovereignAgentSpec(
    agent_id="EML_SYMBOLIC_COMPRESSION_AGENT",
    layer=AgentLayer.EML,
    description="Wrapper non souverain autour de run_eml_compression",
)

def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, run_eml_compression, action)
