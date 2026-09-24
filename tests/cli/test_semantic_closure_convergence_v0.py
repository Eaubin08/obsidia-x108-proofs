from __future__ import annotations

from scripts import obsidia_gateway_route_decision_v0 as route_gate
from scripts import obsidia_cognitive_ingress_v0 as ingress


def _rich_router_result() -> dict:
    return {
        "route": "brody",
        "level": 1,
        "reason": "SEMANTIC_TEST_ROUTE",
        "model": None,
        "gate": {
            "verdict": "ALLOW",
        },
        "ir": {
            "raw": "explique le contexte",
            "normalized": "explique le contexte",
            "intent_type": "question",
            "target_layer": "brody",
            "action_type": "answer",
            "risk_level": "low",
            "needs": {
                "local_structure": True,
                "memory": False,
                "brody": True,
                "remote_model": False,
                "gate": False,
            },
            "constraints": [
                "router_non_sovereign",
                "no_auto_act",
                "no_auto_commit",
                "no_auto_push",
                "bounded_output",
            ],
            "missing": [],
        },
    }


def test_route_decision_preserves_canonical_semantic_ir(
    monkeypatch,
):
    def fake_router_decide(
        raw,
        memory_index=None,
    ):
        return (
            _rich_router_result(),
            "ROUTER_OK",
        )

    monkeypatch.setattr(
        route_gate,
        "router_decide",
        fake_router_decide,
    )

    result = route_gate.build_route_decision(
        "explique le contexte",
        {},
    )

    ir = result["ir"]

    assert ir.get("intent_type") == "question"
    assert ir.get("target_layer") == "brody"

    # Canonical router field names must survive the gateway.
    assert ir.get("action_type") == "answer"
    assert ir.get("risk_level") == "low"

    assert ir.get("needs") == {
        "local_structure": True,
        "memory": False,
        "brody": True,
        "remote_model": False,
        "gate": False,
    }

    assert "no_auto_act" in ir.get(
        "constraints",
        [],
    )

    assert ir.get("missing") == []


def _sufficiency(
    *,
    route: str,
    structural_missing=None,
    resolution_required: bool = False,
    resolution_targets=None,
    candidate_available: bool = True,
):
    if structural_missing is None:
        structural_missing = []

    if resolution_targets is None:
        resolution_targets = []

    route_decision = {
        "router_route": route,
        "level": 1 if route == "brody" else 0,
        "ir": {
            "intent_type": (
                "question"
                if route == "brody"
                else "status"
            ),
            "target_layer": (
                "brody"
                if route == "brody"
                else "local"
            ),
            "action_type": (
                "answer"
                if route == "brody"
                else "status"
            ),
            "risk_level": "low",
            "needs": {},
            "constraints": [
                "router_non_sovereign",
                "no_auto_act",
            ],
            "missing": list(
                structural_missing
            ),
        },
    }

    authority_snapshot = {
        "requires_kx108_decision": False,
    }

    brody_stage = {
        "attempted": candidate_available,
        "candidate_available": (
            candidate_available
        ),
        "boundary_ok": True,
        "boundary_violation": False,
        "source": (
            "REAL_BRODY_RUNTIME_NO_GRAPHITI"
        ),
    }

    brody_runtime = {
        "response_md": (
            "R?ponse Brody born?e."
        ),
        "pre_reasoning_snapshot": {
            "reasoning_directive": {
                "resolution_required": (
                    resolution_required
                ),
                "resolution_targets": list(
                    resolution_targets
                ),
            },
            "unknown_qualification": {
                "unresolved_unknowns": list(
                    resolution_targets
                ),
            },
            "decision_authority": (
                "KX108_ONLY"
            ),
            "readonly": True,
            "allowed_to_act": False,
            "memory_write": False,
            "kernel_mutation": False,
        },
    }

    cognitive_join = {
        "components": {
            "W3_BRODY": (
                "READY:REAL_RUNTIME_ADAPTER"
            ),
        },
        "context_packet_v2": {
            "contradictions": [],
            "risk_flags": [],
            "unknowns": [],
        },
        "errors": [],
    }

    llm_activation = {
        "required": False,
    }

    return ingress._evaluate_brody_sufficiency(
        route_decision=route_decision,
        authority_snapshot=authority_snapshot,
        brody_stage=brody_stage,
        brody_runtime=brody_runtime,
        cognitive_join=cognitive_join,
        llm_activation=llm_activation,
    )


def test_unresolved_semantic_target_cannot_close_brody():
    result = _sufficiency(
        route="brody",
        resolution_required=True,
        resolution_targets=[
            "florvaxium",
        ],
    )

    # OUTPUT_EXISTS != SEMANTIC_CLOSURE.
    assert result["sufficient"] is False

    # Unknown meaning is not a reason to invoke a model blindly.
    assert result["model_required"] is False

    assert (
        result["next_stage"]
        != "LOCAL_STACK_RESULT"
    )

    assert (
        result.get(
            "semantic_resolution_required"
        )
        is True
    )

    assert result.get(
        "semantic_resolution_targets"
    ) == [
        "florvaxium",
    ]


def test_resolved_brody_path_still_closes_locally():
    result = _sufficiency(
        route="brody",
        resolution_required=False,
        resolution_targets=[],
    )

    assert (
        result["status"]
        == "BRODY_SUFFICIENT"
    )

    assert result["sufficient"] is True
    assert result["model_required"] is False

    assert (
        result["next_stage"]
        == "LOCAL_STACK_RESULT"
    )


def test_structural_missing_cannot_be_local_route_sufficient():
    result = _sufficiency(
        route="no_model_needed",
        structural_missing=[
            "intent",
        ],
        resolution_required=False,
        candidate_available=False,
    )

    assert result["sufficient"] is False
    assert result["model_required"] is False

    assert (
        result["next_stage"]
        != "LOCAL_STACK_RESULT"
    )

    assert result.get(
        "structural_missing"
    ) == [
        "intent",
    ]


def test_clean_local_route_can_remain_sufficient():
    result = _sufficiency(
        route="no_model_needed",
        structural_missing=[],
        resolution_required=False,
        candidate_available=False,
    )

    assert (
        result["status"]
        == "LOCAL_ROUTE_SUFFICIENT"
    )

    assert result["sufficient"] is True
    assert result["model_required"] is False

    assert (
        result["next_stage"]
        == "LOCAL_STACK_RESULT"
    )



def _model_route_semantic_debt(
    *,
    source="REAL_BRODY_RUNTIME_NO_GRAPHITI",
    structural_missing=None,
):
    if structural_missing is None:
        structural_missing = [
            "target_scope",
            "target_layer",
        ]

    return ingress._evaluate_brody_sufficiency(
        route_decision={
            "router_route": "fireworks",
            "level": 3,
            "ir": {
                "intent_type": "code_request",
                "target_layer": "unknown",
                "action_type": "commands",
                "risk_level": "medium",
                "needs": {
                    "local_structure": True,
                    "memory": False,
                    "brody": False,
                    "remote_model": True,
                    "gate": True,
                },
                "constraints": [
                    "router_non_sovereign",
                    "no_auto_act",
                    "no_auto_commit",
                    "no_auto_push",
                    "bounded_output",
                ],
                "missing": list(
                    structural_missing
                ),
            },
        },
        authority_snapshot={
            "requires_kx108_decision": False,
        },
        brody_stage={
            "attempted": True,
            "candidate_available": True,
            "boundary_ok": True,
            "boundary_violation": False,
            "source": source,
        },
        brody_runtime={
            "response_md": (
                "Brody bounded context."
            ),
            "pre_reasoning_snapshot": {
                "reasoning_directive": {
                    "resolution_required": True,
                    "resolution_targets": [
                        "python",
                    ],
                },
                "unknown_qualification": {
                    "unresolved_unknowns": [
                        "python",
                    ],
                },
                "decision_authority":
                    "KX108_ONLY",
                "readonly": True,
                "allowed_to_act": False,
                "memory_write": False,
                "kernel_mutation": False,
            },
        },
        cognitive_join={
            "components": {
                "W3_BRODY":
                    "READY:REAL_RUNTIME_ADAPTER",
            },
            "context_packet_v2": {
                "contradictions": [],
                "risk_flags": [],
                "unknowns": [],
            },
            "errors": [],
        },
        llm_activation={
            "required": True,
        },
    )


def test_model_eligible_semantic_debt_uses_local_model_gate():
    result = _model_route_semantic_debt()

    assert (
        result["status"]
        == "BRODY_INSUFFICIENT"
    )

    assert result["sufficient"] is False
    assert result["model_required"] is True

    assert (
        result["next_stage"]
        == "LOCAL_MODEL_GATE"
    )

    assert (
        result[
            "semantic_resolution_required"
        ]
        is True
    )

    assert (
        result[
            "semantic_resolution_targets"
        ]
        == ["python"]
    )

    assert (
        "target_layer"
        in result[
            "closure_critical_missing"
        ]
    )


def test_strong_brody_cannot_close_l3_with_semantic_debt():
    result = _model_route_semantic_debt(
        source="REAL_BRODY_GRAPHITI_LIVE",
        structural_missing=[],
    )

    assert (
        result["status"]
        == "BRODY_INSUFFICIENT"
    )

    assert result["sufficient"] is False
    assert result["model_required"] is True

    assert (
        result["next_stage"]
        == "LOCAL_MODEL_GATE"
    )

    assert (
        result[
            "semantic_resolution_required"
        ]
        is True
    )
