from __future__ import annotations

import pytest

from app.ir.unified_ir import build_ir
from app.gates.gates import evaluate
from app.router.decision import decide


PREPARE_NO_EXECUTE_CASES = [
    "pr\u00e9pare le sans rien lancer",

    (
        "pr\u00e9pare le script mais "
        "ne l'ex\u00e9cute pas"
    ),

    (
        "prepare the script but "
        "do not execute it"
    ),
]


@pytest.mark.parametrize(
    "prompt",
    PREPARE_NO_EXECUTE_CASES,
)
def test_prepare_with_explicit_no_execute_preserves_both_meanings(
    prompt,
):
    ir = build_ir(prompt)

    # Positive requested operation survives.
    assert (
        ir["action_type"]
        == "prepare"
    )

    # The execution verb is explicitly negated.
    assert (
        "no_execute"
        in ir["constraints"]
    )

    # Negated execution is NOT an execution request.
    assert (
        ir["intent_type"]
        != "world_action"
    )

    assert (
        ir["risk_level"]
        != "high"
    )

    assert (
        ir["needs"].get(
            "current_world_evidence",
            False,
        )
        is False
    )

    gate = evaluate(ir)

    # It may still need clarification/context,
    # especially for the anaphoric "le",
    # but it must NOT be treated as requested execution.
    assert (
        gate["verdict"]
        != "HOLD"
    )

    decision = decide(
        prompt,
        memory_index={},
    )

    assert (
        decision["route"]
        != "hold_commands_only"
    )

    assert (
        decision["gate"]["verdict"]
        != "HOLD"
    )


def test_direct_execute_remains_world_action_hold():
    prompt = "vas y execute"

    ir = build_ir(prompt)
    gate = evaluate(ir)
    decision = decide(
        prompt,
        memory_index={},
    )

    assert (
        ir["intent_type"]
        == "world_action"
    )

    assert (
        ir["action_type"]
        == "act_request"
    )

    assert (
        "no_execute"
        not in ir["constraints"]
    )

    assert (
        gate["verdict"]
        == "HOLD"
    )

    assert (
        decision["route"]
        == "hold_commands_only"
    )


def test_explicit_execute_script_remains_hold():
    prompt = "execute le script"

    ir = build_ir(prompt)
    gate = evaluate(ir)
    decision = decide(
        prompt,
        memory_index={},
    )

    assert (
        ir["intent_type"]
        == "world_action"
    )

    assert (
        ir["action_type"]
        == "act_request"
    )

    assert (
        "no_execute"
        not in ir["constraints"]
    )

    assert (
        gate["verdict"]
        == "HOLD"
    )

    assert (
        decision["route"]
        == "hold_commands_only"
    )


def test_current_world_contract_remains_independent():
    prompt = (
        "est-ce qu'il pleut dehors ?"
    )

    ir = build_ir(prompt)
    decision = decide(
        prompt,
        memory_index={},
    )

    assert (
        ir["needs"][
            "current_world_evidence"
        ]
        is True
    )

    assert (
        "no_execute"
        not in ir["constraints"]
    )

    assert (
        decision["route"]
        == "evidence_required"
    )


def test_negated_execute_does_not_hide_later_positive_execution():
    prompt = (
        "prepare the script, "
        "do not execute it, "
        "then run it"
    )

    ir = build_ir(prompt)
    gate = evaluate(ir)
    decision = decide(
        prompt,
        memory_index={},
    )

    # One execution occurrence is negated...
    assert (
        "no_execute"
        in ir["constraints"]
    )

    # ...but a later positive RUN still requests world action.
    assert (
        ir["intent_type"]
        == "world_action"
    )

    assert (
        ir["action_type"]
        == "act_request"
    )

    assert (
        gate["verdict"]
        == "HOLD"
    )

    assert (
        decision["route"]
        == "hold_commands_only"
    )

