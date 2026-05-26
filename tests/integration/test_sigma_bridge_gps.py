from periphery.adapters.gps_adapter import build_gps_action, build_gps_state
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_gps_with_periphery


def test_gps_bridge_real_sigma():
    payload = {"action_id": "g1"}
    a = build_gps_action(payload)
    state = build_gps_state(payload)
    p = run_control_plane(a)
    e = run_gps_with_periphery(state, p)
    assert e.x108_gate in {"ALLOW", "HOLD", "BLOCK"}
