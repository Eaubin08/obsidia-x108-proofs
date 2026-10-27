from __future__ import annotations

from typing import Callable

from .common import ActionCandidate
from .agent_contracts import AgentResult
from .agents import (
    data_purity_agent,
    provenance_agent,
    brody_memory_agent,
    eml_symbolic_agent,
    energy_thermo_agent,
    timeverse_agent,
    ocs_generation_agent,
    operational_constance_agent,
    permission_economic_agent,
    gencoin_value_agent,
    os3_proof_agent,
    action_sequence_agent,
    feedback_memory_agent,
    world_action_agent,
)

AGENT_REGISTRY: dict[str, Callable[[ActionCandidate], AgentResult]] = {
    data_purity_agent.SPEC.agent_id: data_purity_agent.run,
    provenance_agent.SPEC.agent_id: provenance_agent.run,
    brody_memory_agent.SPEC.agent_id: brody_memory_agent.run,
    eml_symbolic_agent.SPEC.agent_id: eml_symbolic_agent.run,
    energy_thermo_agent.SPEC.agent_id: energy_thermo_agent.run,
    timeverse_agent.SPEC.agent_id: timeverse_agent.run,
    ocs_generation_agent.SPEC.agent_id: ocs_generation_agent.run,
    operational_constance_agent.SPEC.agent_id: operational_constance_agent.run,
    permission_economic_agent.SPEC.agent_id: permission_economic_agent.run,
    gencoin_value_agent.SPEC.agent_id: gencoin_value_agent.run,
    os3_proof_agent.SPEC.agent_id: os3_proof_agent.run,
    action_sequence_agent.SPEC.agent_id: action_sequence_agent.run,
    feedback_memory_agent.SPEC.agent_id: feedback_memory_agent.run,
    world_action_agent.SPEC.agent_id: world_action_agent.run,
}

def list_agents() -> list[str]:
    return sorted(AGENT_REGISTRY)

def run_registered_agent(agent_id: str, action: ActionCandidate) -> AgentResult:
    if agent_id not in AGENT_REGISTRY:
        raise KeyError(f"UNKNOWN_AGENT:{agent_id}")
    result = AGENT_REGISTRY[agent_id](action)
    result.assert_non_sovereign()
    return result
