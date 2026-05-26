from periphery.adapters.bank_adapter import build_bank_action, build_bank_state
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_bank_with_periphery


def test_bank_bridge_real_sigma():
    payload = {"action_id": "b1", "amount": 10, "policy_limit": 1000, "elapsed_s": 108}
    a = build_bank_action(payload)
    state = build_bank_state(payload)
    p = run_control_plane(a)
    e = run_bank_with_periphery(state, p)
    assert e.x108_gate in {"ALLOW", "HOLD", "BLOCK"}
