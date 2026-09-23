import pytest
from periphery.agent_registry import AGENT_REGISTRY, list_agents
from periphery.common import ActionCandidate


def _make_action():
    return ActionCandidate(
        action_id="nsov_test",
        domain="bank",
        actor_id="tester",
        intent="test",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={},
    )


def test_no_agent_can_emit_act():
    action = _make_action()
    for agent_id, fn in AGENT_REGISTRY.items():
        result = fn(action)
        assert not result.packet.can_emit_act, f"Agent {agent_id} must not emit ACT"


def test_no_agent_can_authorize():
    from periphery.agents import (
        action_sequence_agent,
        feedback_memory_agent,
        world_action_agent,
    )
    for agent in [action_sequence_agent, feedback_memory_agent, world_action_agent]:
        assert not agent.SPEC.can_authorize
        assert not agent.SPEC.can_emit_act
        assert not agent.SPEC.can_mutate_kernel
        assert not agent.SPEC.can_write_memory


def test_world_action_agent_cannot_emit_real_action():
    from periphery.agents import world_action_agent
    action = _make_action()
    result = world_action_agent.run(action)
    assert result.packet.extra_metrics.get("world_action_allowed") is False
    assert result.packet.extra_metrics.get("dry_run_only") is True


def test_feedback_memory_agent_cannot_write():
    from periphery.agents import feedback_memory_agent
    action = _make_action()
    result = feedback_memory_agent.run(action)
    assert result.packet.extra_metrics.get("memory_write_allowed") is False


def test_control_plane_cannot_emit_act_v3():
    from periphery.control_plane import run_control_plane
    action = _make_action().__class__(
        action_id="cp_nsov",
        domain="bank",
        actor_id="tester",
        intent="test",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={"gross_value": 100.0},
    )
    packet = run_control_plane(action)
    assert not packet.can_emit_act
