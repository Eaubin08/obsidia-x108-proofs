from apps.obsidia_api.brody_pre_reasoning_adapter import (
    build_brody_pre_reasoning_snapshot,
)


def _build(message):
    return build_brody_pre_reasoning_snapshot(
        user_message=message,
        language="fr",
        intent="pure_response",
        authority_snapshot={
            "request_type": "PURE_RESPONSE",
        },
    )


def test_current_state_keeps_raw_lexical_unknowns_but_c274_gets_none():
    result = _build(
        "Explique moi le statut actuel de Brody."
    )

    lexical = (
        result["ir_candidate"]
        ["lexical_calibration"]
    )

    qualification = result[
        "unknown_qualification"
    ]

    calibration = result[
        "pre_reasoning_calibration"
    ]

    directive = result[
        "reasoning_directive"
    ]

    # Raw diagnostic signal is preserved.
    assert lexical["unknowns"] == [
        "moi",
        "statut",
        "actuel",
        "brody",
    ]

    assert qualification[
        "surface_language_unknowns"
    ] == ["moi"]

    assert qualification[
        "semantically_resolved_unknowns"
    ] == [
        "statut",
        "actuel",
        "brody",
    ]

    assert qualification[
        "unresolved_unknowns"
    ] == []

    # Only genuinely unresolved concepts become causal.
    assert calibration["unknowns"] == []
    assert calibration[
        "reasoning_readiness"
    ] == "CALIBRATED"

    assert directive[
        "reasoning_mode"
    ] == "NORMAL_REASONING"

    assert directive[
        "resolution_targets"
    ] == []


def test_mixed_current_state_preserves_only_real_unknown_for_c274():
    result = _build(
        "Explique moi le statut actuel "
        "de Brody et florvaxium."
    )

    lexical = (
        result["ir_candidate"]
        ["lexical_calibration"]
    )

    qualification = result[
        "unknown_qualification"
    ]

    calibration = result[
        "pre_reasoning_calibration"
    ]

    directive = result[
        "reasoning_directive"
    ]

    assert lexical["unknowns"] == [
        "moi",
        "statut",
        "actuel",
        "brody",
        "florvaxium",
    ]

    assert qualification[
        "unresolved_unknowns"
    ] == [
        "florvaxium",
    ]

    assert calibration[
        "unknowns"
    ] == [
        "florvaxium",
    ]

    assert calibration[
        "reasoning_readiness"
    ] == "CALIBRATED_WITH_UNCERTAINTY"

    assert directive[
        "reasoning_mode"
    ] == "RESOLVE_BEFORE_ASSERT"

    assert directive[
        "resolution_targets"
    ] == [
        "florvaxium",
    ]


def test_general_real_unknown_stays_unresolved():
    result = _build(
        "explique le florvaxium"
    )

    qualification = result[
        "unknown_qualification"
    ]

    assert qualification[
        "unresolved_unknowns"
    ] == [
        "florvaxium",
    ]

    assert result[
        "reasoning_directive"
    ][
        "resolution_targets"
    ] == [
        "florvaxium",
    ]


def test_qualification_boundary_is_preserved():
    result = _build(
        "Explique moi le statut actuel de Brody."
    )

    qualification = result[
        "unknown_qualification"
    ]

    assert qualification[
        "decision_authority"
    ] == "KX108_ONLY"

    assert qualification["readonly"] is True
    assert qualification[
        "allowed_to_decide"
    ] is False
    assert qualification[
        "allowed_to_act"
    ] is False
    assert qualification[
        "emits_act"
    ] is False
    assert qualification[
        "emits_verdict"
    ] is False
    assert qualification[
        "memory_write"
    ] is False
    assert qualification[
        "kernel_mutation"
    ] is False
