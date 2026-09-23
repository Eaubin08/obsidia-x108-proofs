import pytest
from periphery.agent_registry import AGENT_REGISTRY, list_agents, run_registered_agent
from periphery.common import ActionCandidate


def _make_action(**kwargs) -> ActionCandidate:
    defaults = dict(
        action_id="test_v3",
        domain="bank",
        actor_id="test",
        intent="test_intent",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={},
    )
    defaults.update(kwargs)
    return ActionCandidate(**defaults)


V3_REQUIRED_AGENTS = [
    "action_sequence_agent_v3",
    "feedback_memory_agent_v3",
    "world_action_agent_v4",
    "gencoin_value_agent_v1",
    "os3_proof_agent_v1",
]


def test_v3_agents_registered():
    agents = list_agents()
    for agent_id in V3_REQUIRED_AGENTS:
        assert agent_id in agents, f"Missing agent: {agent_id}"


def test_all_agents_non_sovereign():
    action = _make_action()
    for agent_id in list_agents():
        result = run_registered_agent(agent_id, action)
        assert not result.packet.can_emit_act, f"Agent {agent_id} must not emit ACT"


def test_action_sequence_agent_no_steps():
    action = _make_action(payload={})
    result = run_registered_agent("action_sequence_agent_v3", action)
    assert result.packet.extra_metrics.get("sequence_step_count", 0) == 0
    assert not result.packet.can_emit_act


def test_feedback_memory_agent_no_write():
    action = _make_action(payload={"memory_status": "STABLE"})
    result = run_registered_agent("feedback_memory_agent_v3", action)
    assert result.packet.extra_metrics.get("memory_write_allowed") is False


def test_world_action_agent_dry_run():
    action = _make_action(payload={})
    result = run_registered_agent("world_action_agent_v4", action)
    assert result.packet.extra_metrics.get("dry_run_only") is True
    assert result.packet.extra_metrics.get("world_action_allowed") is False


def test_unknown_agent_raises():
    action = _make_action()
    with pytest.raises(KeyError):
        run_registered_agent("nonexistent_agent_xyz", action)
