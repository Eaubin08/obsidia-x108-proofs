from periphery.language.action_meaning_validator import (
    validate_action_meaning,
)


def _halo(
    *,
    uncertainty=False,
    intent="action_request",
):
    return {
        "stage": "C277",
        "name": "final_sense_halo",
        "node_signal": (
            "FINAL_SENSE_WITH_UNCERTAINTY"
            if uncertainty
            else "FINAL_SENSE_CONSOLIDATED"
        ),
        "calibration_result": {
            "uncertainty_present": uncertainty,
            "unresolved_symbols": (
                ["florvaxium"]
                if uncertainty
                else []
            ),
        },
        "integration_trace": {
            "source_stages": [
                "C274",
                "C275",
                "C276",
            ],
            "memory_refs": [],
            "symbolic_context": {
                "intent": intent,
            },
        },
        "readonly": True,
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
    }


def _repair_request(
    objective="corrige ce code",
):
    return {
        "request_id": "rr_test",
        "origin": "BRODY",
        "objective": objective,
        "failure_mode": "ROUTE_INCAPABLE",
        "summary": "",
        "error_contexts": [],
        "repo_targets": [],
        "target_excerpts": {},
        "attempts_spent": 0,
        "sandbox_dir": "",
        "tests_hint": [],
        "boundary": {
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "emits_verdict": False,
            "kernel_mutation": False,
            "memory_write": False,
            "canonical_write": False,
            "auto_apply": False,
            "auto_commit": False,
            "auto_push": False,
            "sandbox_mode": "HUMAN_APPROVED_WRITE",
            "external_engine_role": "PROPOSE_ONLY",
        },
    }


def test_c278_schema_matches_declared_outputs():
    result = validate_action_meaning(
        calibration_context={
            "final_sense_halo": _halo(),
            "action_projection": (
                _repair_request()
            ),
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
            "source_objective": (
                "corrige ce code"
            ),
        },
    )

    assert result["stage"] == "C278"
    assert (
        result["name"]
        == "action_meaning_validator"
    )

    assert "node_signal" in result
    assert "calibration_result" in result
    assert "integration_trace" in result


def test_c278_aligned_repair_request():
    result = validate_action_meaning(
        calibration_context={
            "final_sense_halo": _halo(),
            "action_projection": (
                _repair_request(
                    "corrige ce code"
                )
            ),
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
            "source_objective": (
                "corrige ce code"
            ),
        },
    )

    assert (
        result["node_signal"]
        == "ACTION_MEANING_ALIGNED"
    )

    calibration = result[
        "calibration_result"
    ]

    assert (
        calibration[
            "action_meaning_status"
        ]
        == "ALIGNED"
    )

    assert (
        calibration[
            "objective_continuity"
        ]
        is True
    )

    assert (
        calibration[
            "intent_alignment"
        ]
        is True
    )


def test_c278_detects_objective_divergence():
    result = validate_action_meaning(
        calibration_context={
            "final_sense_halo": _halo(),
            "action_projection": (
                _repair_request(
                    "supprime tout le repo"
                )
            ),
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
            "source_objective": (
                "corrige ce code"
            ),
        },
    )

    assert (
        result["node_signal"]
        == "ACTION_MEANING_DIVERGENCE"
    )

    calibration = result[
        "calibration_result"
    ]

    assert (
        calibration[
            "action_meaning_status"
        ]
        == "DIVERGENT"
    )

    assert (
        calibration[
            "objective_continuity"
        ]
        is False
    )

    # Advisory semantic signal only.
    assert (
        "candidate_valid"
        not in result
    )

    assert (
        "execution_authorized"
        not in result
    )


def test_c278_preserves_c277_uncertainty():
    result = validate_action_meaning(
        calibration_context={
            "final_sense_halo": _halo(
                uncertainty=True
            ),
            "action_projection": (
                _repair_request()
            ),
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
            "source_objective": (
                "corrige ce code"
            ),
        },
    )

    assert (
        result["node_signal"]
        == "ACTION_MEANING_WITH_UNCERTAINTY"
    )

    assert (
        result[
            "calibration_result"
        ][
            "action_meaning_status"
        ]
        == "UNRESOLVED"
    )


def test_c278_no_projection_is_not_applicable():
    result = validate_action_meaning(
        calibration_context={
            "final_sense_halo": _halo(),
            "action_projection": None,
        },
        memory_refs=[],
        symbolic_context={
            "intent": "pure_response",
            "source_objective": (
                "explique x108"
            ),
        },
    )

    assert (
        result["node_signal"]
        == "NO_ACTION_MEANING_TO_VALIDATE"
    )

    assert (
        result[
            "calibration_result"
        ][
            "action_meaning_status"
        ]
        == "NOT_APPLICABLE"
    )


def test_c278_memory_refs_are_pass_through_only():
    refs = [
        "memory-ref-001",
        "memory-ref-002",
    ]

    result = validate_action_meaning(
        calibration_context={
            "final_sense_halo": _halo(),
            "action_projection": (
                _repair_request()
            ),
        },
        memory_refs=refs,
        symbolic_context={
            "intent": "action_request",
            "source_objective": (
                "corrige ce code"
            ),
        },
    )

    assert (
        result[
            "integration_trace"
        ][
            "memory_refs"
        ]
        == refs
    )


def test_c278_kx108_readonly_boundary():
    result = validate_action_meaning(
        calibration_context={
            "final_sense_halo": _halo(),
            "action_projection": (
                _repair_request()
            ),
        },
        memory_refs=[],
        symbolic_context={
            "intent": "action_request",
            "source_objective": (
                "corrige ce code"
            ),
        },
    )

    assert result["readonly"] is True

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        result["allowed_to_decide"]
        is False
    )

    assert (
        result["allowed_to_act"]
        is False
    )

    assert result["emits_act"] is False
    assert result["emits_verdict"] is False

    assert result["memory_write"] is False
    assert result["canonical_write"] is False

    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False

    assert result["auto_apply"] is False
    assert result["auto_commit"] is False
    assert result["auto_push"] is False


def test_c278_does_not_duplicate_downstream_validation():
    import inspect
    import periphery.language.action_meaning_validator as mod

    source = inspect.getsource(
        mod
    ).lower()

    forbidden = (
        "validate_action_candidate",
        "validate_repair_proposal",
        "test_repair_proposal",
        "candidate_valid",
        "execution_authorized",
        "subprocess",
        "pytest",
        "graphiti",
        "neo4j",
        "query_neo4j",
        "native_memory",
        "memory_response_chain",
        "requests.",
        "urlopen",
    )

    for token in forbidden:
        assert token not in source
