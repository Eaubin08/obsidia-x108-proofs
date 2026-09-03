from periphery.common import ActionCandidate
from periphery.agents import energy_thermo_agent


def test_energy_cannot_authorize():
    spec = energy_thermo_agent.SPEC

    assert spec.can_emit_act is False
    assert spec.can_authorize is False
    assert spec.can_mutate_kernel is False
    assert spec.can_write_memory is False

    action = ActionCandidate(
        action_id="nsov_energy",
        domain="bank",
        actor_id="tester",
        intent="energy_check",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={
            "pin": 1.0,
            "pout": 1.0,
            "truth_score": 1.0,
            "sigma_score": 1.0,
        },
    )

    result = energy_thermo_agent.run(action)

    assert result.packet.can_emit_act is False
    result.assert_non_sovereign()
