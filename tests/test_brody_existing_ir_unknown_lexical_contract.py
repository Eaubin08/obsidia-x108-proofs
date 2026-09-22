from apps.obsidia_api.brody_existing_reverse_os_bridge import (
    build_existing_ir_candidate,
)


def _build(message: str) -> dict:
    return build_existing_ir_candidate(
        user_message=message,
        intent="unknown",
        semantic_query_snapshot={},
        authority_snapshot={},
        reverse_flow={},
    )


def test_existing_ir_surfaces_unknown_lexical_term():
    ir = _build(
        "explique le florvaxium"
    )

    assert "unknowns" in ir
    assert ir["unknowns"] == [
        "florvaxium"
    ]

    assert "lexical_calibration" in ir

    calibration = ir[
        "lexical_calibration"
    ]

    assert calibration["status"] == "CALIBRATED"
    assert calibration["readonly"] is True
    assert (
        calibration["decision_authority"]
        == "KX108_ONLY"
    )

    assert ir["readonly"] is True
    assert ir["memory_write"] is False
    assert ir["kernel_mutation"] is False
    assert (
        ir["decision_authority"]
        == "KX108_ONLY"
    )


def test_existing_ir_recognizes_reverse_os():
    ir = _build(
        "explique le reverse os"
    )

    assert "unknowns" in ir
    assert ir["unknowns"] == []

    calibration = ir[
        "lexical_calibration"
    ]

    assert (
        calibration["status"]
        == "CALIBRATED"
    )

    assert (
        "reverse_os"
        in calibration[
            "known_concept_ids"
        ]
    )
