from periphery.language.reasoning_directive import (
    build_reasoning_directive,
)


def _base_calibration(**overrides):
    payload = {
        "status": "PRE_REASONING_CALIBRATION_PASS",
        "stage_order": [
            "C265",
            "C266",
            "C273",
            "C274",
        ],
        "known_concept_ids": [],
        "unknowns": [],
        "contradictions": [],
        "risk_flags": [],
        "symbolic_alignment": "ALIGNED",
        "divergences": [],
        "reasoning_readiness": "CALIBRATED",
        "readonly": True,
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "canonical_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
    }

    payload.update(overrides)
    return payload


def test_known_state_allows_normal_reasoning():
    result = build_reasoning_directive(
        _base_calibration(
            known_concept_ids=["x108"],
        )
    )

    assert result[
        "status"
    ] == "PRE_REASONING_DIRECTIVE_PASS"

    assert result[
        "reasoning_mode"
    ] == "NORMAL_REASONING"

    assert result[
        "resolution_required"
    ] is False

    assert result[
        "resolution_targets"
    ] == []

    assert result[
        "assertion_policy"
    ] == "NORMAL_ASSERTION_WITH_EVIDENCE"


def test_unknown_requires_resolution_before_assertion():
    result = build_reasoning_directive(
        _base_calibration(
            unknowns=["florvaxium"],
            symbolic_alignment="PARTIAL",
            divergences=[
                {
                    "kind": "UNRESOLVED_SYMBOL",
                    "token": "florvaxium",
                    "source": "LEXICAL_OR_IR_UNKNOWN",
                }
            ],
            reasoning_readiness=(
                "CALIBRATED_WITH_UNCERTAINTY"
            ),
        )
    )

    assert result[
        "reasoning_mode"
    ] == "RESOLVE_BEFORE_ASSERT"

    assert result[
        "resolution_required"
    ] is True

    assert result[
        "resolution_targets"
    ] == [
        "florvaxium"
    ]

    assert result[
        "assertion_policy"
    ] == (
        "DO_NOT_ASSERT_UNRESOLVED_SYMBOL_AS_KNOWN"
    )

    # This is cognitive guidance, never a sovereign gate.
    assert result.get("verdict") is None
    assert result.get("decision") is None

    assert result["emits_verdict"] is False
    assert result["emits_act"] is False


def test_contradiction_also_forces_uncertainty_aware_reasoning():
    result = build_reasoning_directive(
        _base_calibration(
            contradictions=[
                "SEMANTIC_CONTRADICTION"
            ],
            reasoning_readiness=(
                "CALIBRATED_WITH_UNCERTAINTY"
            ),
        )
    )

    assert result[
        "reasoning_mode"
    ] == "RESOLVE_BEFORE_ASSERT"

    assert result[
        "resolution_required"
    ] is True

    assert result[
        "contradictions"
    ] == [
        "SEMANTIC_CONTRADICTION"
    ]


def test_reasoning_directive_boundary():
    result = build_reasoning_directive(
        _base_calibration()
    )

    assert result["readonly"] is True
    assert result[
        "decision_authority"
    ] == "KX108_ONLY"

    assert result["allowed_to_decide"] is False
    assert result["allowed_to_act"] is False
    assert result["emits_act"] is False
    assert result["emits_verdict"] is False

    assert result["memory_write"] is False
    assert result["canonical_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False


def test_reasoning_directive_has_no_memory_provider_dependency():
    import inspect
    import periphery.language.reasoning_directive as mod

    source = inspect.getsource(mod).lower()

    forbidden = (
        "brody_obsidia_native_memory",
        "brody_native_memory_response_adapter",
        "brody_memory_response_chain_adapter",
        "graphiti",
        "neo4j",
        "hydrate_packet",
        "query_neo4j",
        "localhost:8011",
        "localhost:7688",
    )

    for token in forbidden:
        assert token not in source
