from periphery.agent_registry import list_agents, run_registered_agent
from periphery.common import ActionCandidate

def test_registry_lists_agents():
    agents = list_agents()
    assert "DATA_PURITY_AGENT" in agents
    assert "PERMISSION_ECONOMIC_AGENT" in agents

def test_registered_agent_runs_non_sovereign():
    action = ActionCandidate("a", "bank", "actor", "intent", "act", True, "", payload={})
    result = run_registered_agent("DATA_PURITY_AGENT", action)
    result.assert_non_sovereign()
