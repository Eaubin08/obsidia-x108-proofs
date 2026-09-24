from __future__ import annotations

import pytest

from app.ir.unified_ir import build_ir
from app.router.decision import decide


CURRENT_WORLD_CASES = [
    # Presence of a real person now.
    "maman est l\u00e0 ?",

    # Current physical/environmental state.
    "est-ce qu'il pleut dehors ?",
]


@pytest.mark.parametrize(
    "prompt",
    CURRENT_WORLD_CASES,
)
def test_current_world_question_requires_evidence_not_model(
    prompt,
):
    ir = build_ir(prompt)

    # Semantic meaning is understood.
    assert ir["intent_type"] == "question"
    assert ir["action_type"] == "answer"
    assert ir["target_layer"] == "world"

    # The missing dimension is evidence, not intent.
    assert "intent" not in ir["missing"]

    assert (
        ir["needs"].get(
            "current_world_evidence"
        )
        is True
    )

    # A language model cannot substitute for a current-world
    # observation/source.
    assert (
        ir["needs"].get(
            "remote_model"
        )
        is False
    )

    decision = decide(
        prompt,
        memory_index={},
    )

    # Evidence is a distinct next need:
    # neither CLARIFY nor remote/model inference.
    assert (
        decision["route"]
        == "evidence_required"
    )

    assert decision["level"] == 0
    assert decision["model"] is None

    # This is not an authority violation and not semantic ambiguity.
    assert (
        decision["gate"]["verdict"]
        == "ALLOW"
    )


@pytest.mark.parametrize(
    "prompt, expected_route",
    [
        (
            "The capital city of germany is?",
            "fireworks",
        ),
        (
            "explique le contexte",
            "brody",
        ),
        (
            "fais le",
            "clarification_needed",
        ),
        (
            "vas y execute",
            "hold_commands_only",
        ),
        (
            (
                "\u00c9cris une fonction Python "
                "qui inverse une cha\u00eene."
            ),
            "fireworks",
        ),
    ],
)
def test_current_world_contract_does_not_reclassify_existing_routes(
    prompt,
    expected_route,
):
    ir = build_ir(prompt)

    assert (
        ir["needs"].get(
            "current_world_evidence",
            False,
        )
        is False
    )

    decision = decide(
        prompt,
        memory_index={},
    )

    assert (
        decision["route"]
        == expected_route
    )
