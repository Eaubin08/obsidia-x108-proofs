from apps.obsidia_api.brody_existing_reverse_os_bridge import (
    build_existing_reverse_os_projection,
)

from periphery.language.pre_reasoning_calibrator import (
    calibrate_pre_reasoning,
)


def _projection(message: str):
    return build_existing_reverse_os_projection(
        user_message=message,
        intent="pure_response",
        semantic_query_snapshot={
            "topic": "GENERAL",
            "semantic_query": message,
            "primary_query": message,
        },
        authority_snapshot={
            "request_type": "PURE_RESPONSE",
        },
        tree_signal_packet={},
        tree_policy_snapshot={},
    )


def test_reverse_os_unknown_reaches_c265_c274_once():
    reverse = _projection(
        "explique le florvaxium"
    )

    ir = reverse["ir_candidate"]

    assert ir["unknowns"] == [
        "florvaxium"
    ]

    result = calibrate_pre_reasoning(
        user_message="explique le florvaxium",
        language="fr",
        lexical_calibration=ir[
            "lexical_calibration"
        ],
        ir_candidate=ir,
    )

    assert result[
        "stage_order"
    ] == [
        "C265",
        "C266",
        "C273",
        "C274",
    ]

    assert result[
        "unknowns"
    ] == [
        "florvaxium"
    ]

    assert result[
        "unknowns"
    ].count(
        "florvaxium"
    ) == 1

    assert result[
        "symbolic_alignment"
    ] == "PARTIAL"

    assert result[
        "divergence_tokens"
    ] == [
        "florvaxium"
    ]

    assert result[
        "reasoning_readiness"
    ] == (
        "CALIBRATED_WITH_UNCERTAINTY"
    )

    assert result[
        "decision_authority"
    ] == "KX108_ONLY"

    assert result[
        "emits_verdict"
    ] is False

    assert result[
        "emits_act"
    ] is False

    assert result[
        "memory_write"
    ] is False

    assert result[
        "canonical_write"
    ] is False

    assert result[
        "kernel_mutation"
    ] is False


def test_reverse_os_known_x108_reaches_aligned_c274():
    reverse = _projection(
        "explique x108"
    )

    ir = reverse["ir_candidate"]

    result = calibrate_pre_reasoning(
        user_message="explique x108",
        language="fr",
        lexical_calibration=ir[
            "lexical_calibration"
        ],
        ir_candidate=ir,
    )

    assert "x108" in result[
        "known_concept_ids"
    ]

    assert result[
        "unknowns"
    ] == []

    assert result[
        "symbolic_alignment"
    ] == "ALIGNED"

    assert result[
        "divergences"
    ] == []

    assert result[
        "reasoning_readiness"
    ] == "CALIBRATED"
