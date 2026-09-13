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


def _fake_c277(**kwargs):
    calibration_context = kwargs[
        "calibration_context"
    ]

    return {
        "stage": "C277",
        "name": "final_sense_halo",
        "node_signal": (
            "FINAL_SENSE_CONSOLIDATED"
        ),
        "calibration_result": {
            "uncertainty_present": False,
        },
        "integration_trace": {
            "source_stages": [
                calibration_context[
                    "pre_reasoning"
                ].get(
                    "stage",
                    "C274",
                ),
                calibration_context[
                    "pre_response"
                ].get(
                    "stage",
                    "C275",
                ),
                calibration_context[
                    "pre_action"
                ]["stage"],
            ],
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


def test_c277_snapshot_is_exposed_after_c276(
    monkeypatch,
):
    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        FakeTerminal(),
    )

    monkeypatch.setattr(
        pipeline,
        "calibrate_pre_action",
        _ready_c276,
    )

    monkeypatch.setattr(
        pipeline,
        "build_final_sense_halo",
        _fake_c277,
        raising=False,
    )

    result = (
        pipeline.run_brody_real_response_pipeline(
            "corrige ce code",
            language="fr",
        )
    )

    assert (
        result["final_sense_halo"][
            "stage"
        ]
        == "C277"
    )

    assert (
        result["final_sense_halo"][
            "integration_trace"
        ][
            "source_stages"
        ][-1]
        == "C276"
    )


def test_c277_receives_c274_c275_c276_context(
    monkeypatch,
):
    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        FakeTerminal(),
    )

    monkeypatch.setattr(
        pipeline,
        "calibrate_pre_action",
        _ready_c276,
    )

    captured = {}

    def fake_builder(**kwargs):
        captured.update(
            kwargs
        )

        return _fake_c277(
            **kwargs
        )

    monkeypatch.setattr(
        pipeline,
        "build_final_sense_halo",
        fake_builder,
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
        "pre_reasoning"
        in context
    )

    assert (
        "pre_response"
        in context
    )

    assert (
        context[
            "pre_action"
        ][
            "stage"
        ]
        == "C276"
    )


def test_c277_runtime_does_not_query_memory(
    monkeypatch,
):
    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        FakeTerminal(),
    )

    monkeypatch.setattr(
        pipeline,
        "calibrate_pre_action",
        _ready_c276,
    )

    captured = {}

    def fake_builder(**kwargs):
        captured.update(
            kwargs
        )

        return _fake_c277(
            **kwargs
        )

    monkeypatch.setattr(
        pipeline,
        "build_final_sense_halo",
        fake_builder,
        raising=False,
    )

    pipeline.run_brody_real_response_pipeline(
        "corrige ce code",
        language="fr",
    )

    # Harness branch does not resolve or query memory here.
    assert (
        captured[
            "memory_refs"
        ]
        == []
    )


def test_c277_receives_symbolic_intent(
    monkeypatch,
):
    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        FakeTerminal(),
    )

    monkeypatch.setattr(
        pipeline,
        "calibrate_pre_action",
        _ready_c276,
    )

    captured = {}

    def fake_builder(**kwargs):
        captured.update(
            kwargs
        )

        return _fake_c277(
            **kwargs
        )

    monkeypatch.setattr(
        pipeline,
        "build_final_sense_halo",
        fake_builder,
        raising=False,
    )

    pipeline.run_brody_real_response_pipeline(
        "corrige ce code",
        language="fr",
    )

    assert (
        captured[
            "symbolic_context"
        ][
            "intent"
        ]
        == "action_request"
    )


def test_c277_runtime_preserves_non_sovereignty(
    monkeypatch,
):
    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        FakeTerminal(),
    )

    monkeypatch.setattr(
        pipeline,
        "calibrate_pre_action",
        _ready_c276,
    )

    monkeypatch.setattr(
        pipeline,
        "build_final_sense_halo",
        _fake_c277,
        raising=False,
    )

    result = (
        pipeline.run_brody_real_response_pipeline(
            "corrige ce code",
            language="fr",
        )
    )

    c277 = result[
        "final_sense_halo"
    ]

    assert (
        c277["decision_authority"]
        == "KX108_ONLY"
    )

    assert c277["allowed_to_decide"] is False
    assert c277["allowed_to_act"] is False
    assert c277["emits_act"] is False
    assert c277["emits_verdict"] is False


def test_c277_integration_has_no_memory_coupling():
    import inspect

    source = inspect.getsource(
        pipeline
    ).lower()

    c277_lines = "\n".join(
        line
        for line in source.splitlines()
        if (
            "c277" in line
            or "final_sense_halo"
            in line
            or "build_final_sense_halo"
            in line
        )
    )

    forbidden = (
        "graphiti",
        "neo4j",
        "query_neo4j",
        "native_memory",
        "memory_response_chain",
    )

    for token in forbidden:
        assert token not in c277_lines
