from __future__ import annotations

from periphery.common import ActionCandidate
from periphery.agent_contracts import AgentLayer, NonSovereignAgentSpec, AgentResult, run_agent_safely
from periphery.energy_thermo import run_energy_thermo

SPEC = NonSovereignAgentSpec(
    agent_id="ENERGY_THERMO_AGENT",
    layer=AgentLayer.ENERGY,
    description="Wrapper non souverain autour de run_energy_thermo",
)

def run(action: ActionCandidate) -> AgentResult:
    return run_agent_safely(SPEC, run_energy_thermo, action)
