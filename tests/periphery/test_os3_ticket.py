from periphery.adapters.bank_adapter import build_bank_action, build_bank_state
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_bank_with_periphery
from periphery.os3_ticket import build_os3_ticket, ticket_is_valid


def test_os3_ticket_valid_real_bank_state():
    payload = {"action_id":"a", "amount":10, "policy_limit":1000, "elapsed_s":108}
    a = build_bank_action(payload)
    state = build_bank_state(payload)
    p = run_control_plane(a)
    e = run_bank_with_periphery(state, p)
    assert ticket_is_valid(build_os3_ticket(a, p, e))
