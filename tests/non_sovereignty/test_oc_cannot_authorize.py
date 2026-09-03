from periphery.common import ActionCandidate
from periphery.agents import operational_constance_agent


def test_operational_constance_cannot_authorize():
    spec = operational_constance_agent.SPEC

    assert spec.can_emit_act is False
    assert spec.can_authorize is False
    assert spec.can_mutate_kernel is False
    assert spec.can_write_memory is False

    action = ActionCandidate(
        action_id="nsov_oc",
        domain="bank",
        actor_id="tester",
        intent="stability_check",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={
            "flip": 0.0,
            "osc": 0.0,
            "tens": 0.0,
        },
    )

    result = operational_constance_agent.run(action)

    assert result.packet.can_emit_act is False
    result.assert_non_sovereign()
