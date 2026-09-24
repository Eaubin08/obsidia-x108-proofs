from __future__ import annotations

import os

os.environ[
    "OBSIDIA_ROUTER_ROOT"
] = (
    r"C:\Users\User\Desktop\OBSIDIA_R&D"
    r"\zone tampon obsidia"
    r"\08_HACKATHON_AMD"
    r"\obsidia-track3-final"
)

import pytest

from scripts import (
    obsidia_gateway_route_decision_v0
    as ROUTER_GATE,
)

from scripts.obsidia_cognitive_ingress_v0 import (
    run_cognitive_ingress,
)


CURRENT_WORLD_CASES = [
    "maman est l\u00e0 ?",
    "est-ce qu'il pleut dehors ?",
]


@pytest.mark.parametrize(
    "prompt",
    CURRENT_WORLD_CASES,
)
def test_gateway_preserves_current_world_evidence_route(
    prompt,
):
    d = ROUTER_GATE.build_route_decision(
        prompt,
        {},
    )

    assert (
        d["router_status"]
        == ROUTER_GATE.ROUTER_OK
    )

    assert (
        d["router_route"]
        == "evidence_required"
    )

    assert (
        d["gate_verdict"]
        == "ALLOW"
    )

    # A known deterministic semantic route,
    # but NOT a claim that evidence is locally available.
    assert (
        d["route_class"]
        == ROUTER_GATE.ROUTE_STACK_NATIVE
    )

    assert (
        d["human_authority_required"]
        is False
    )

    assert (
        d["unknown"]
        is False
    )

    ir = d["ir"]

    assert (
        ir["intent_type"]
        == "question"
    )

    assert (
        ir["target_layer"]
        == "world"
    )

    assert (
        ir["action_type"]
        == "answer"
    )

    assert (
        ir["missing"]
        == []
    )

    assert (
        ir["needs"][
            "current_world_evidence"
        ]
        is True
    )

    assert (
        ir["needs"][
            "remote_model"
        ]
        is False
    )


@pytest.mark.parametrize(
    "prompt",
    CURRENT_WORLD_CASES,
)
def test_ingress_keeps_current_world_evidence_open(
    prompt,
):
    result = run_cognitive_ingress(
        text=prompt,
        session_id="current-world-red",
        memory_index={},
        allow_local_model=False,
        readonly_pc_context={},
    )

    assert (
        result["route_decision"][
            "router_route"
        ]
        == "evidence_required"
    )

    suff = result[
        "brody_sufficiency"
    ]

    assert (
        suff["status"]
        == "EVIDENCE_REQUIRED"
    )

    assert (
        suff["sufficient"]
        is False
    )

    assert (
        suff["model_required"]
        is False
    )

    assert (
        suff["next_stage"]
        == "EVIDENCE_REQUIRED"
    )

    assert (
        suff["reason"]
        == "CURRENT_WORLD_EVIDENCE_REQUIRED"
    )

    assert (
        result["next_stage"]
        == "EVIDENCE_REQUIRED"
    )

    model = result[
        "local_model_stage"
    ]

    assert (
        model["eligible"]
        is False
    )

    assert (
        model["attempted"]
        is False
    )

    assert (
        model["model_call_used"]
        is False
    )

    assert (
        model["tokens_remote"]
        == 0
    )

    receipt = result[
        "route_receipt"
    ]

    assert (
        receipt["selected_route"]
        == "evidence_required"
    )

    assert (
        receipt["result_status"]
        == "CURRENT_WORLD_EVIDENCE_REQUIRED"
    )

    assert (
        receipt["model_call_used"]
        is False
    )

    assert (
        receipt["model_call_avoided"]
        is True
    )

    assert (
        result["allowed_to_act"]
        is False
    )

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )


def test_existing_model_route_still_reaches_model_gate():
    result = run_cognitive_ingress(
        text=(
            "\u00c9cris une fonction Python "
            "qui inverse une cha\u00eene."
        ),
        session_id="current-world-control-model",
        memory_index={},
        allow_local_model=False,
        readonly_pc_context={},
    )

    assert (
        result["route_decision"][
            "router_route"
        ]
        == "fireworks"
    )

    assert (
        result["next_stage"]
        == "LOCAL_MODEL_GATE"
    )


def test_existing_ambiguous_action_still_requires_human_review():
    result = run_cognitive_ingress(
        text="fais le",
        session_id="current-world-control-ambiguous",
        memory_index={},
        allow_local_model=False,
        readonly_pc_context={},
    )

    assert (
        result["route_decision"][
            "router_route"
        ]
        == "clarification_needed"
    )

    assert (
        result["next_stage"]
        == "HUMAN_REVIEW"
    )


def test_existing_world_action_still_hits_governance():
    result = run_cognitive_ingress(
        text="vas y execute",
        session_id="current-world-control-action",
        memory_index={},
        allow_local_model=False,
        readonly_pc_context={},
    )

    assert (
        result["route_decision"][
            "router_route"
        ]
        == "hold_commands_only"
    )

    assert (
        result["next_stage"]
        == "KX108_GOVERNANCE"
    )

    assert (
        result["allowed_to_act"]
        is False
    )
