from periphery.language.final_sense_halo import (
    build_final_sense_halo,
)


def _c274():
    return {
        "stage": "C274",
        "readiness": "CALIBRATED",
        "unknowns": [],
        "contradictions": [],
        "risk_flags": [],
    }


def _c275():
    return {
        "stage": "C275",
        "response_readiness": "READY",
        "calibration_required": False,
        "calibration_flags": [],
    }


def _c276():
    return {
        "stage": "C276",
        "action_candidate_readiness": (
            "READY_FOR_GOVERNANCE_CANDIDATE"
        ),
        "candidate_projection_ready": True,
        "risk_flags": [
            "action_request",
        ],
        "unresolved_symbols": [],
    }


def test_c277_schema_matches_declared_spec_outputs():
    result = build_final_sense_halo(
        calibration_context={
            "pre_reasoning": _c274(),
            "pre_response": _c275(),
            "pre_action": _c276(),
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
        },
    )

    assert result["stage"] == "C277"
    assert result["name"] == "final_sense_halo"

    assert "node_signal" in result
    assert "calibration_result" in result
    assert "integration_trace" in result


def test_c277_consolidates_c274_c275_c276_in_order():
    result = build_final_sense_halo(
        calibration_context={
            "pre_reasoning": _c274(),
            "pre_response": _c275(),
            "pre_action": _c276(),
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
        },
    )

    trace = result[
        "integration_trace"
    ]

    assert trace[
        "source_stages"
    ] == [
        "C274",
        "C275",
        "C276",
    ]


def test_c277_preserves_uncertainty_without_resolving_it():
    result = build_final_sense_halo(
        calibration_context={
            "pre_reasoning": {
                "stage": "C274",
                "readiness": (
                    "CALIBRATED_WITH_UNCERTAINTY"
                ),
                "unknowns": [
                    "florvaxium",
                ],
                "contradictions": [],
                "risk_flags": [],
            },
            "pre_response": {
                "stage": "C275",
                "response_readiness": (
                    "READY_WITH_UNCERTAINTY"
                ),
                "calibration_required": False,
                "calibration_flags": [],
            },
            "pre_action": {
                "stage": "C276",
                "action_candidate_readiness": (
                    "REQUIRES_SEMANTIC_RESOLUTION"
                ),
                "candidate_projection_ready": False,
                "risk_flags": [
                    "action_request",
                ],
                "unresolved_symbols": [
                    "florvaxium",
                ],
            },
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
        },
    )

    calibration = result[
        "calibration_result"
    ]

    assert calibration[
        "unresolved_symbols"
    ] == [
        "florvaxium",
    ]

    assert calibration[
        "uncertainty_present"
    ] is True

    # C277 consolidates. It does not magically
    # convert unresolved meaning into readiness.
    assert result[
        "node_signal"
    ] == "FINAL_SENSE_WITH_UNCERTAINTY"


def test_c277_memory_refs_are_pass_through_only():
    refs = [
        "memory-ref-001",
        "memory-ref-002",
    ]

    result = build_final_sense_halo(
        calibration_context={
            "pre_reasoning": _c274(),
            "pre_response": _c275(),
            "pre_action": _c276(),
        },
        memory_refs=refs,
        symbolic_context={
            "intent": "action_request",
        },
    )

    assert result[
        "integration_trace"
    ][
        "memory_refs"
    ] == refs


def test_c277_does_not_duplicate_c276_or_c278():
    result = build_final_sense_halo(
        calibration_context={
            "pre_reasoning": _c274(),
            "pre_response": _c275(),
            "pre_action": _c276(),
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
        },
    )

    # No action validation / authorization belongs here.
    assert (
        "execution_authorized"
        not in result
    )

    assert (
        "action_meaning_valid"
        not in result
    )

    assert (
        "candidate_projection_ready"
        not in result
    )


def test_c277_kx108_readonly_boundary():
    result = build_final_sense_halo(
        calibration_context={
            "pre_reasoning": _c274(),
            "pre_response": _c275(),
            "pre_action": _c276(),
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
        },
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


def test_c277_source_has_no_memory_or_execution_coupling():
    import inspect
    import periphery.language.final_sense_halo as mod

    source = inspect.getsource(mod).lower()

    forbidden = (
        "graphiti",
        "neo4j",
        "query_neo4j",
        "native_memory",
        "memory_response_chain",
        "urlopen",
        "requests.",
        "/kernel/ragnarok",
        "subprocess",
    )

    for token in forbidden:
        assert token not in source
