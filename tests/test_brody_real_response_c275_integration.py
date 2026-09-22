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
            "X108 est le noyau décisionnel.",
            [],
            False,
        )


def test_c275_snapshot_is_attached_after_normal_response(monkeypatch):
    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        FakeTerminal(),
    )

    result = pipeline.run_brody_real_response_pipeline(
        "explique x108",
        language="fr",
    )

    c275 = result[
        "pre_response_calibration"
    ]

    assert c275["stage"] == "C275"

    assert (
        c275["response_candidate"]
        == result["response_md"]
    )

    assert (
        c275["response_readiness"]
        == "READY"
    )

    assert (
        c275["calibration_required"]
        is False
    )


def test_c275_sees_bounded_unknown_response_as_ready_with_uncertainty(
    monkeypatch,
):
    fake = FakeTerminal()

    calls = {"build_response": 0}

    original = fake.build_response

    def counted(*args, **kwargs):
        calls["build_response"] += 1
        return original(*args, **kwargs)

    fake.build_response = counted

    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        fake,
    )

    result = pipeline.run_brody_real_response_pipeline(
        "explique le florvaxium",
        language="fr",
    )

    assert calls["build_response"] == 0

    c275 = result[
        "pre_response_calibration"
    ]

    assert (
        c275["response_readiness"]
        == "READY_WITH_UNCERTAINTY"
    )

    assert (
        c275["calibration_required"]
        is False
    )

    assert (
        "florvaxium"
        in c275["unresolved_symbols"]
    )


def test_runtime_does_not_surface_candidate_rejected_by_c275(
    monkeypatch,
):
    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        FakeTerminal(),
    )

    def forced_rejection(**kwargs):
        candidate = kwargs[
            "candidate_response"
        ]

        return {
            "stage": "C275",
            "response_candidate": candidate,
            "response_readiness": (
                "REQUIRES_CALIBRATION"
            ),
            "calibration_required": True,
            "calibration_flags": [
                "UNRESOLVED_SYMBOL_ASSERTED_AS_KNOWN",
            ],
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

    monkeypatch.setattr(
        pipeline,
        "calibrate_pre_response",
        forced_rejection,
        raising=False,
    )

    result = pipeline.run_brody_real_response_pipeline(
        "explique x108",
        language="fr",
    )

    assert (
        result[
            "pre_response_calibration"
        ][
            "response_readiness"
        ]
        == "REQUIRES_CALIBRATION"
    )

    # Candidate rejected by C275 must not be surfaced unchanged.
    assert (
        result["response_md"]
        != "X108 est le noyau décisionnel."
    )

    assert (
        result["response_source"]
        == "C275_RESPONSE_CALIBRATION_REQUIRED"
    )


def test_c275_runtime_source_has_no_memory_provider_dependency():
    import inspect

    source = inspect.getsource(
        pipeline
    ).lower()

    # Only inspect the future C275-specific symbols/lines,
    # not legacy content already present elsewhere in this pipeline.
    c275_lines = "\n".join(
        line
        for line in source.splitlines()
        if (
            "c275" in line
            or "pre_response_calibration" in line
            or "calibrate_pre_response" in line
        )
    )

    forbidden = (
        "graphiti",
        "neo4j",
        "native_memory",
        "memory_response_chain",
    )

    for token in forbidden:
        assert token not in c275_lines
