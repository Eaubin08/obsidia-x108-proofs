from periphery.language.pre_response_calibrator import (
    calibrate_pre_response,
)


def _directive_normal():
    return {
        "reasoning_mode": "NORMAL_REASONING",
        "resolution_required": False,
        "resolution_targets": [],
        "assertion_policy": (
            "NORMAL_ASSERTION_WITH_EVIDENCE"
        ),
    }


def _directive_unresolved():
    return {
        "reasoning_mode": "RESOLVE_BEFORE_ASSERT",
        "resolution_required": True,
        "resolution_targets": [
            "florvaxium",
        ],
        "assertion_policy": (
            "DO_NOT_ASSERT_UNRESOLVED_SYMBOL_AS_KNOWN"
        ),
    }


def test_c275_normal_candidate_is_response_ready():
    result = calibrate_pre_response(
        candidate_response=(
            "X108 est le noyau décisionnel."
        ),
        reasoning_directive=_directive_normal(),
        pre_reasoning_calibration={
            "unknowns": [],
            "contradictions": [],
            "risk_flags": [],
        },
        language="fr",
    )

    assert result[
        "stage"
    ] == "C275"

    assert result[
        "response_readiness"
    ] == "READY"

    assert result[
        "calibration_required"
    ] is False

    assert result[
        "response_candidate"
    ] == (
        "X108 est le noyau décisionnel."
    )


def test_c275_unresolved_symbol_cannot_be_asserted_as_known():
    result = calibrate_pre_response(
        candidate_response=(
            "Le florvaxium est un composant "
            "connu du système."
        ),
        reasoning_directive=_directive_unresolved(),
        pre_reasoning_calibration={
            "unknowns": [
                "florvaxium",
            ],
            "contradictions": [],
            "risk_flags": [],
        },
        language="fr",
    )

    assert result[
        "response_readiness"
    ] == "REQUIRES_CALIBRATION"

    assert result[
        "calibration_required"
    ] is True

    assert (
        "UNRESOLVED_SYMBOL_ASSERTED_AS_KNOWN"
        in result["calibration_flags"]
    )


def test_c275_bounded_uncertainty_response_is_acceptable():
    result = calibrate_pre_response(
        candidate_response=(
            "Je ne peux pas traiter "
            "« florvaxium » comme un concept "
            "connu : il reste non résolu."
        ),
        reasoning_directive=_directive_unresolved(),
        pre_reasoning_calibration={
            "unknowns": [
                "florvaxium",
            ],
            "contradictions": [],
            "risk_flags": [],
        },
        language="fr",
    )

    assert result[
        "response_readiness"
    ] == "READY_WITH_UNCERTAINTY"

    assert result[
        "calibration_required"
    ] is False


def test_c275_does_not_generate_or_rewrite_response():
    candidate = (
        "Réponse candidate strictement intacte."
    )

    result = calibrate_pre_response(
        candidate_response=candidate,
        reasoning_directive=_directive_normal(),
        pre_reasoning_calibration={},
        language="fr",
    )

    assert result[
        "response_candidate"
    ] == candidate

    assert "rewritten_response" not in result
    assert "final_answer" not in result


def test_c275_is_non_sovereign_provider_free():
    result = calibrate_pre_response(
        candidate_response="test",
        reasoning_directive=_directive_normal(),
        pre_reasoning_calibration={},
        language="fr",
    )

    assert result["readonly"] is True

    assert result[
        "decision_authority"
    ] == "KX108_ONLY"

    assert result[
        "allowed_to_decide"
    ] is False

    assert result[
        "allowed_to_act"
    ] is False

    assert result["emits_act"] is False
    assert result["emits_verdict"] is False
    assert result["memory_write"] is False
    assert result["canonical_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False

    import inspect
    import periphery.language.pre_response_calibrator as mod

    source = inspect.getsource(mod).lower()

    forbidden = (
        "graphiti",
        "neo4j",
        "query_neo4j",
        "native_memory",
        "memory_response_chain",
        "provider",
    )

    for token in forbidden:
        assert token not in source
