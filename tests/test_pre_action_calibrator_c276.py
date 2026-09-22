from periphery.language.pre_action_calibrator import (
    calibrate_pre_action,
)


def _clean_reasoning():
    return {
        "reasoning_mode": "NORMAL_REASONING",
        "resolution_required": False,
        "resolution_targets": [],
    }


def _clean_c274():
    return {
        "unknowns": [],
        "contradictions": [],
        "risk_flags": [],
    }


def _clean_c275():
    return {
        "stage": "C275",
        "response_readiness": "READY",
        "calibration_required": False,
        "calibration_flags": [],
    }


def test_c276_no_action_intent_produces_no_candidate():
    result = calibrate_pre_action(
        ir_candidate={
            "intent": "question",
            "risk_flags": [],
            "contradictions": [],
            "constraints": [
                "READONLY",
                "NO_ACT",
            ],
        },
        reasoning_directive=_clean_reasoning(),
        pre_reasoning_calibration=_clean_c274(),
        pre_response_calibration=_clean_c275(),
    )

    assert result["stage"] == "C276"

    assert (
        result["action_candidate_readiness"]
        == "NO_ACTION_CANDIDATE_REQUESTED"
    )

    assert (
        result["candidate_projection_ready"]
        is False
    )


def test_c276_clean_action_intent_is_ready_for_candidate_projection():
    result = calibrate_pre_action(
        ir_candidate={
            "intent": "action_request",
            "risk_flags": [
                "action_request",
            ],
            "contradictions": [
                "REQUEST_REQUIRES_ACTION_BUT_ROUTE_IS_READONLY",
            ],
            "constraints": [
                "READONLY",
                "NO_ACT",
                "ACTION_REQUEST_FORCED_TO_READONLY_PROJECTION",
            ],
        },
        reasoning_directive=_clean_reasoning(),
        pre_reasoning_calibration=_clean_c274(),
        pre_response_calibration=_clean_c275(),
    )

    assert (
        result["action_candidate_readiness"]
        == "READY_FOR_GOVERNANCE_CANDIDATE"
    )

    assert (
        result["candidate_projection_ready"]
        is True
    )

    assert result["execution_authorized"] is False

    assert (
        "REQUEST_REQUIRES_ACTION_BUT_ROUTE_IS_READONLY"
        in result["boundary_contradictions"]
    )


def test_c276_unresolved_symbol_blocks_candidate_projection():
    result = calibrate_pre_action(
        ir_candidate={
            "intent": "action_request",
            "risk_flags": [
                "action_request",
            ],
            "contradictions": [],
            "constraints": [],
        },
        reasoning_directive={
            "reasoning_mode": "RESOLVE_BEFORE_ASSERT",
            "resolution_required": True,
            "resolution_targets": [
                "florvaxium",
            ],
        },
        pre_reasoning_calibration={
            "unknowns": [
                "florvaxium",
            ],
            "contradictions": [],
            "risk_flags": [],
        },
        pre_response_calibration={
            "stage": "C275",
            "response_readiness": (
                "READY_WITH_UNCERTAINTY"
            ),
            "calibration_required": False,
            "calibration_flags": [],
        },
    )

    assert (
        result["action_candidate_readiness"]
        == "REQUIRES_SEMANTIC_RESOLUTION"
    )

    assert (
        result["candidate_projection_ready"]
        is False
    )

    assert result[
        "unresolved_symbols"
    ] == ["florvaxium"]


def test_c276_rejected_c275_blocks_candidate_projection():
    result = calibrate_pre_action(
        ir_candidate={
            "intent": "action_request",
            "risk_flags": [
                "action_request",
            ],
            "contradictions": [],
            "constraints": [],
        },
        reasoning_directive=_clean_reasoning(),
        pre_reasoning_calibration=_clean_c274(),
        pre_response_calibration={
            "stage": "C275",
            "response_readiness": (
                "REQUIRES_CALIBRATION"
            ),
            "calibration_required": True,
            "calibration_flags": [
                "UNRESOLVED_SYMBOL_ASSERTED_AS_KNOWN",
            ],
        },
    )

    assert (
        result["action_candidate_readiness"]
        == "REQUIRES_RESPONSE_CALIBRATION"
    )

    assert (
        result["candidate_projection_ready"]
        is False
    )


def test_c276_preserves_existing_ir_risk_and_authority_boundary():
    result = calibrate_pre_action(
        ir_candidate={
            "intent": "action_request",
            "risk_flags": [
                "action_request",
                "mutation_request",
            ],
            "contradictions": [
                "REQUEST_REQUIRES_ACTION_BUT_ROUTE_IS_READONLY",
            ],
            "constraints": [
                "READONLY",
                "NO_ACT",
                "NO_VERDICT",
            ],
        },
        reasoning_directive=_clean_reasoning(),
        pre_reasoning_calibration=_clean_c274(),
        pre_response_calibration=_clean_c275(),
    )

    assert result[
        "risk_flags"
    ] == [
        "action_request",
        "mutation_request",
    ]

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

    assert result[
        "execution_authorized"
    ] is False

    assert result[
        "requires_downstream_governance"
    ] is True

    assert result["memory_write"] is False
    assert result["canonical_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False


def test_c276_source_is_independent_of_memory_and_kernel_execution():
    import inspect
    import periphery.language.pre_action_calibrator as mod

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
    )

    for token in forbidden:
        assert token not in source
