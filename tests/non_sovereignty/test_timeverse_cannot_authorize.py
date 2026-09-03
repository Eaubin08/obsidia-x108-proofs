from periphery.common import ActionCandidate
from periphery.agents import timeverse_agent


def test_timeverse_cannot_authorize():
    spec = timeverse_agent.SPEC

    assert spec.can_emit_act is False
    assert spec.can_authorize is False
    assert spec.can_mutate_kernel is False
    assert spec.can_write_memory is False

    action = ActionCandidate(
        action_id="nsov_timeverse",
        domain="bank",
        actor_id="tester",
        intent="trajectory_check",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={
            "trajectory_score": 1.0,
            "trajectory_divergence": 0.0,
            "context_drift": 0.0,
            "async_action": False,
        },
    )

    result = timeverse_agent.run(action)

    assert result.packet.can_emit_act is False
    result.assert_non_sovereign()
