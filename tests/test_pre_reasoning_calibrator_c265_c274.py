from periphery.language.lexical_calibrator import (
    calibrate_lexical_knownness,
)

from periphery.language.pre_reasoning_calibrator import (
    calibrate_pre_reasoning,
)


EXPECTED_STAGE_ORDER = [
    "C265",
    "C266",
    "C273",
    "C274",
]


def test_pre_reasoning_known_x108_is_bounded_and_aligned():
    lexical = calibrate_lexical_knownness(
        "explique x108",
        "fr",
    )

    result = calibrate_pre_reasoning(
        user_message="explique x108",
        language="fr",
        lexical_calibration=lexical,
        ir_candidate={
            "unknowns": [],
            "contradictions": [],
            "risk_flags": [],
        },
    )

    assert result["status"] == "PRE_REASONING_CALIBRATION_PASS"

    assert result["stage_order"] == EXPECTED_STAGE_ORDER

    assert result["unknowns"] == []
    assert "x108" in result["known_concept_ids"]

    assert result["symbolic_alignment"] == "ALIGNED"
    assert result["divergences"] == []
    assert result["reasoning_readiness"] == "CALIBRATED"

    assert result["readonly"] is True
    assert result["decision_authority"] == "KX108_ONLY"

    assert result["allowed_to_decide"] is False
    assert result["allowed_to_act"] is False
    assert result["emits_act"] is False
    assert result["emits_verdict"] is False

    assert result["memory_write"] is False
    assert result["canonical_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False


def test_pre_reasoning_unknown_is_preserved_without_verdict():
    lexical = calibrate_lexical_knownness(
        "explique le florvaxium",
        "fr",
    )

    result = calibrate_pre_reasoning(
        user_message="explique le florvaxium",
        language="fr",
        lexical_calibration=lexical,
        ir_candidate={
            "unknowns": ["florvaxium"],
            "contradictions": [],
            "risk_flags": [],
        },
    )

    assert result["status"] == "PRE_REASONING_CALIBRATION_PASS"

    assert result["stage_order"] == EXPECTED_STAGE_ORDER

    assert result["unknowns"] == ["florvaxium"]

    assert result["symbolic_alignment"] == "PARTIAL"
    assert result["divergence_tokens"] == ["florvaxium"]

    assert result["reasoning_readiness"] == (
        "CALIBRATED_WITH_UNCERTAINTY"
    )

    # The cognitive calibrator reports uncertainty.
    # It NEVER decides HOLD/BLOCK/ALLOW itself.
    assert result.get("verdict") is None
    assert result.get("decision") is None

    assert result["readonly"] is True
    assert result["decision_authority"] == "KX108_ONLY"

    assert result["allowed_to_decide"] is False
    assert result["allowed_to_act"] is False
    assert result["emits_act"] is False
    assert result["emits_verdict"] is False

    assert result["memory_write"] is False
    assert result["canonical_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False


def test_pre_reasoning_keeps_single_logical_unknown():
    lexical = calibrate_lexical_knownness(
        "florvaxium",
        "fr",
    )

    result = calibrate_pre_reasoning(
        user_message="florvaxium",
        language="fr",
        lexical_calibration=lexical,
        ir_candidate={
            "unknowns": [
                "florvaxium",
                "florvaxium",
            ],
            "contradictions": [],
            "risk_flags": [],
        },
    )

    assert result["unknowns"] == ["florvaxium"]
    assert result["unknowns"].count("florvaxium") == 1


def test_pre_reasoning_has_no_memory_or_provider_dependency():
    import inspect
    import periphery.language.pre_reasoning_calibrator as mod

    source = inspect.getsource(mod).lower()

    forbidden = (
        "brody_obsidia_native_memory",
        "brody_native_memory_response_adapter",
        "brody_memory_response_chain_adapter",
        "graphiti_v20_readonly_client",
        "neo4j_brody_guide_bridge",
        "bolt://",
        "localhost:7688",
        "localhost:8011",
    )

    for token in forbidden:
        assert token not in source
