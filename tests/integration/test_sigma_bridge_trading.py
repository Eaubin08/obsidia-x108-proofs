from periphery.adapters.trading_adapter import build_trading_action, build_trading_state
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_trading_with_periphery


def test_trading_bridge_real_sigma():
    payload = {"action_id": "t1"}
    a = build_trading_action(payload)
    state = build_trading_state(payload)
    p = run_control_plane(a)
    e = run_trading_with_periphery(state, p)
    assert e.x108_gate in {"ALLOW", "HOLD", "BLOCK"}
