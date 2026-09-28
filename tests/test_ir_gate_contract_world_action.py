"""IR -> gate contract for canonical world-action requests.

If the canonical IR has already classified an input as a requested world action,
the gate layer must not let it fall through to ALLOW just because the exact
surface is absent from HOLD_KEYWORDS.
"""

import pytest

from app.gates.gates import evaluate
from app.ir.unified_ir import build_ir
from app.router.decision import decide


MISSING_GATE_CONTRACT_PROBES = [
    "drop the users table",
    "format the disk",
    "rm the build folder",
    "authorize the payment",
]

EXISTING_HOLD_PROBES = [
    "execute the script",
    "run the tests",
    "push the changes",
]


@pytest.mark.parametrize("raw", MISSING_GATE_CONTRACT_PROBES)
def test_world_action_act_request_cannot_allow(raw):
    ir = build_ir(raw)
    gate = evaluate(ir)
    decision = decide(raw)

    assert ir["intent_type"] == "world_action"
    assert ir["action_type"] == "act_request"
    assert gate["verdict"] in {"HOLD", "DENY", "CLARIFY"}
    assert gate["verdict"] != "ALLOW"
    assert decision["route"] in {"hold_commands_only", "denied", "clarification_needed"}


@pytest.mark.parametrize("raw", EXISTING_HOLD_PROBES)
def test_existing_direct_action_holds(raw):
    ir = build_ir(raw)
    gate = evaluate(ir)
    decision = decide(raw)

    assert ir["intent_type"] == "world_action"
    assert ir["action_type"] == "act_request"
    assert gate["verdict"] == "HOLD"
    assert decision["route"] == "hold_commands_only"
