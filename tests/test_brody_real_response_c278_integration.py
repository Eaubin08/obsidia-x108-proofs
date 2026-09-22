from apps.obsidia_api import brody_real_response_pipeline as pipeline


class FakeTerminal:
    def extract_memory_query(self, message):
        return message

    def is_action_risk(self, message):
        return False

    def build_response(
        self,
        user_text,
        memory_query,
        packet,
        selected,
        command=None,
    ):
        return (
            "Réponse cognitive normale.",
            [],
            False,
        )


def _ready_c276(**kwargs):
    return {
        "stage": "C276",
        "intent": "action_request",
        "action_candidate_readiness": (
            "READY_FOR_GOVERNANCE_CANDIDATE"
        ),
        "candidate_projection_ready": True,
        "execution_authorized": False,
        "requires_downstream_governance": True,
        "risk_flags": [
            "action_request",
        ],
        "unresolved_symbols": [],
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


def _no_action_c276(**kwargs):
    result = _ready_c276(**kwargs)

    result[
        "action_candidate_readiness"
    ] = "NO_ACTION_CANDIDATE_REQUESTED"

    result[
        "candidate_projection_ready"
    ] = False

    result["intent"] = "pure_response"
    result["risk_flags"] = []

    return result


def _fake_c277(**kwargs):
    intent = kwargs[
        "symbolic_context"
    ][
        "intent"
    ]

    return {
        "stage": "C277",
        "name": "final_sense_halo",
        "node_signal": (
            "FINAL_SENSE_CONSOLIDATED"
        ),
        "calibration_result": {
            "uncertainty_present": False,
            "unresolved_symbols": [],
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


def _attach_repair_request(
    response,
    message,
    ir_intent="",
    risk_flags=None,
    repo_root=None,
):
    response["repair_request"] = {
        "request_id": "rr_runtime_test",
        "origin": "BRODY",
        "objective": message,
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
            "sandbox_mode": (
                "HUMAN_APPROVED_WRITE"
            ),
            "external_engine_role": (
                "PROPOSE_ONLY"
            ),
        },
    }

    response[
        "repair_route_status"
    ] = "REPAIR_REQUEST_EMITTED"

    return response


def _fake_c278(**kwargs):
    calibration_context = kwargs[
        "calibration_context"
    ]

    projection = calibration_context.get(
        "action_projection"
    )

    return {
        "stage": "C278",
        "name": "action_meaning_validator",
        "node_signal": (
            "ACTION_MEANING_ALIGNED"
            if projection
            else "NO_ACTION_MEANING_TO_VALIDATE"
        ),
        "calibration_result": {
            "action_meaning_status": (
                "ALIGNED"
                if projection
                else "NOT_APPLICABLE"
            ),
            "objective_continuity": bool(
                projection
            ),
            "intent_alignment": True,
        },
        "integration_trace": {
            "source_stage": (
                calibration_context[
                    "final_sense_halo"
                ][
                    "stage"
                ]
            ),
            "projection_id": (
                projection.get(
                    "request_id",
                    "",
                )
                if projection
                else ""
            ),
            "memory_refs": kwargs[
                "memory_refs"
            ],
            "symbolic_context": kwargs[
                "symbolic_context"
            ],
        },
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


def _prepare(
    monkeypatch,
    c276=_ready_c276,
):
    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        FakeTerminal(),
    )

    monkeypatch.setattr(
        pipeline,
        "calibrate_pre_action",
        c276,
    )

    monkeypatch.setattr(
        pipeline,
        "build_final_sense_halo",
        _fake_c277,
    )


def test_c278_is_exposed_after_repair_request(
    monkeypatch,
):
    _prepare(monkeypatch)

    monkeypatch.setattr(
        pipeline,
        "attach_repair_request",
        _attach_repair_request,
        raising=False,
    )

    monkeypatch.setattr(
        pipeline,
        "validate_action_meaning",
        _fake_c278,
        raising=False,
    )

    result = (
        pipeline.run_brody_real_response_pipeline(
            "corrige ce code",
            language="fr",
        )
    )

    assert (
        result[
            "action_meaning_validation"
        ][
            "stage"
        ]
        == "C278"
    )

    assert (
        result[
            "action_meaning_validation"
        ][
            "integration_trace"
        ][
            "projection_id"
        ]
        == "rr_runtime_test"
    )


def test_c278_receives_c277_and_repair_request(
    monkeypatch,
):
    _prepare(monkeypatch)

    monkeypatch.setattr(
        pipeline,
        "attach_repair_request",
        _attach_repair_request,
        raising=False,
    )

    captured = {}

    def fake_validator(**kwargs):
        captured.update(kwargs)

        return _fake_c278(
            **kwargs
        )

    monkeypatch.setattr(
        pipeline,
        "validate_action_meaning",
        fake_validator,
        raising=False,
    )

    pipeline.run_brody_real_response_pipeline(
        "corrige ce code",
        language="fr",
    )

    context = captured[
        "calibration_context"
    ]

    assert (
        context[
            "final_sense_halo"
        ][
            "stage"
        ]
        == "C277"
    )

    assert (
        context[
            "action_projection"
        ][
            "request_id"
        ]
        == "rr_runtime_test"
    )


def test_c278_receives_original_objective(
    monkeypatch,
):
    _prepare(monkeypatch)

    monkeypatch.setattr(
        pipeline,
        "attach_repair_request",
        _attach_repair_request,
        raising=False,
    )

    captured = {}

    def fake_validator(**kwargs):
        captured.update(kwargs)

        return _fake_c278(
            **kwargs
        )

    monkeypatch.setattr(
        pipeline,
        "validate_action_meaning",
        fake_validator,
        raising=False,
    )

    message = (
        "corrige ce code sans modifier "
        "le contrat KX108"
    )

    pipeline.run_brody_real_response_pipeline(
        message,
        language="fr",
    )

    assert (
        captured[
            "symbolic_context"
        ][
            "source_objective"
        ]
        == message
    )


def test_c278_memory_refs_remain_empty(
    monkeypatch,
):
    _prepare(monkeypatch)

    monkeypatch.setattr(
        pipeline,
        "attach_repair_request",
        _attach_repair_request,
        raising=False,
    )

    captured = {}

    def fake_validator(**kwargs):
        captured.update(kwargs)

        return _fake_c278(
            **kwargs
        )

    monkeypatch.setattr(
        pipeline,
        "validate_action_meaning",
        fake_validator,
        raising=False,
    )

    pipeline.run_brody_real_response_pipeline(
        "corrige ce code",
        language="fr",
    )

    assert (
        captured[
            "memory_refs"
        ]
        == []
    )


def test_c278_no_candidate_is_not_applicable(
    monkeypatch,
):
    _prepare(
        monkeypatch,
        c276=_no_action_c276,
    )

    monkeypatch.setattr(
        pipeline,
        "validate_action_meaning",
        _fake_c278,
        raising=False,
    )

    result = (
        pipeline.run_brody_real_response_pipeline(
            "explique x108",
            language="fr",
        )
    )

    assert (
        result[
            "action_meaning_validation"
        ][
            "node_signal"
        ]
        == "NO_ACTION_MEANING_TO_VALIDATE"
    )

    assert (
        result[
            "action_meaning_validation"
        ][
            "calibration_result"
        ][
            "action_meaning_status"
        ]
        == "NOT_APPLICABLE"
    )


def test_c278_preserves_non_sovereignty(
    monkeypatch,
):
    _prepare(monkeypatch)

    monkeypatch.setattr(
        pipeline,
        "attach_repair_request",
        _attach_repair_request,
        raising=False,
    )

    monkeypatch.setattr(
        pipeline,
        "validate_action_meaning",
        _fake_c278,
        raising=False,
    )

    result = (
        pipeline.run_brody_real_response_pipeline(
            "corrige ce code",
            language="fr",
        )
    )

    c278 = result[
        "action_meaning_validation"
    ]

    assert (
        c278["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        c278["allowed_to_decide"]
        is False
    )

    assert (
        c278["allowed_to_act"]
        is False
    )

    assert c278["emits_act"] is False
    assert c278["emits_verdict"] is False


def test_c278_pipeline_has_no_downstream_validator_coupling():
    import inspect

    source = inspect.getsource(
        pipeline
    ).lower()

    c278_lines = "\n".join(
        line
        for line in source.splitlines()
        if (
            "c278" in line
            or "action_meaning" in line
        )
    )

    forbidden = (
        "validate_action_candidate",
        "validate_repair_proposal",
        "test_repair_proposal",
        "graphiti",
        "neo4j",
        "query_neo4j",
        "native_memory",
        "memory_response_chain",
    )

    for token in forbidden:
        assert token not in c278_lines
