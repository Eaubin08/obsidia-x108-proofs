from periphery.common import ActionCandidate
from periphery.control_plane import run_control_plane


def test_control_plane_cannot_emit_act():
    action = ActionCandidate(
        action_id="nsov_control_plane",
        domain="bank",
        actor_id="tester",
        intent="readonly_test",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={"gross_value": 100.0},
    )

    packet = run_control_plane(action)

    assert packet.can_emit_act is False
    packet.assert_non_sovereign()
