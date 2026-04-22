import pytest
from entrypoint import run_obsidia

def _W_zero(n=3):
    return [[0.0 for _ in range(n)] for _ in range(n)]

def _W_one(n=3, v=1.0):
    return [[(0.0 if i==j else v) for j in range(n)] for i in range(n)]

def test_F01_order_invariance_act_calls_os1():
    # OS2 ACT => OS1 executed => os1 payload present
    res = run_obsidia({
        "raw_input": "x=1\nprint(x)",
        "W_full": _W_one(3, 1.0),
        "core_nodes": [0,1,2],
        "theta_S": 0.25,
        "irreversible": False,
        "elapsed_s": 999.0,
        "min_wait_s": 108.0,
    })
    assert res.os2 is not None
    assert res.os2.get("decision") == "ACT"
    assert res.os1 is not None  # proves OS1 executed after OS2 ACT

def test_F02_irreversible_refusal_registry_reject():
    # Registry gate happens before OS2/OS1 => both must be None
    res = run_obsidia({
        "raw_input": "x=1",
        "agent_id": "NOT_ALLOWED_AGENT",
    })
    assert res.decision == "REJECT"
    assert res.registry_ok is False
    assert res.os2 is None
    assert res.os1 is None

def test_F03_valid_non_action_hold_skips_os1():
    # OS2 HOLD => OS1 not executed
    res = run_obsidia({
        "raw_input": "x=1\nprint(x)",
        "W_full": _W_zero(3),
        "core_nodes": [0,1,2],
        "theta_S": 0.25,
        "irreversible": False,
        "elapsed_s": 999.0,
        "min_wait_s": 108.0,
    })
    assert res.decision == "HOLD"
    assert res.os2 is not None
    assert res.os2.get("decision") == "HOLD"
    assert res.os1 is None

def test_F04_authorized_action_act_audited():
    # Ensure OS1 returns a structured payload and decision is not REJECT
    res = run_obsidia({
        "raw_input": "x=2\nprint(x)",
        "W_full": _W_one(3, 1.0),
        "core_nodes": [0,1,2],
        "theta_S": 0.25,
        "irreversible": False,
        "elapsed_s": 999.0,
        "min_wait_s": 108.0,
    })
    assert res.os1 is not None
    assert res.decision in ("ACT", "HOLD")  # depending on OS1 contract/X108; should not be REJECT here
    assert isinstance(res.ssr, str) and len(res.ssr) > 0
