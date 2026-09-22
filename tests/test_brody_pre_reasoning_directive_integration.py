from apps.obsidia_api.brody_pre_reasoning_adapter import (
    build_brody_pre_reasoning_snapshot,
)


def test_adapter_exports_reasoning_directive_for_unknown():
    result = build_brody_pre_reasoning_snapshot(
        user_message="explique le florvaxium",
        language="fr",
        intent="pure_response",
        authority_snapshot={
            "request_type": "PURE_RESPONSE",
        },
    )

    directive = result["reasoning_directive"]

    assert directive[
        "status"
    ] == "PRE_REASONING_DIRECTIVE_PASS"

    assert directive[
        "reasoning_mode"
    ] == "RESOLVE_BEFORE_ASSERT"

    assert directive[
        "resolution_required"
    ] is True

    assert directive[
        "resolution_targets"
    ] == [
        "florvaxium"
    ]

    assert directive[
        "assertion_policy"
    ] == (
        "DO_NOT_ASSERT_UNRESOLVED_SYMBOL_AS_KNOWN"
    )


def test_adapter_exports_normal_reasoning_for_known_concept():
    result = build_brody_pre_reasoning_snapshot(
        user_message="explique x108",
        language="fr",
        intent="pure_response",
        authority_snapshot={
            "request_type": "PURE_RESPONSE",
        },
    )

    directive = result["reasoning_directive"]

    assert directive[
        "reasoning_mode"
    ] == "NORMAL_REASONING"

    assert directive[
        "resolution_required"
    ] is False

    assert directive[
        "resolution_targets"
    ] == []


def test_adapter_and_directive_preserve_same_authority_boundary():
    result = build_brody_pre_reasoning_snapshot(
        user_message="florvaxium",
        language="fr",
        intent="pure_response",
        authority_snapshot={
            "request_type": "PURE_RESPONSE",
        },
    )

    directive = result["reasoning_directive"]

    for obj in (
        result,
        result["pre_reasoning_calibration"],
        directive,
    ):
        assert obj["decision_authority"] == "KX108_ONLY"
        assert obj["readonly"] is True
        assert obj["allowed_to_decide"] is False
        assert obj["allowed_to_act"] is False
        assert obj["emits_act"] is False
        assert obj["emits_verdict"] is False
        assert obj["memory_write"] is False
        assert obj["kernel_mutation"] is False
