from apps.obsidia_api import brody_real_response_pipeline as pipeline
from apps.obsidia_api import brody_repair_request_router as repair_router


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
        "risk_flags": kwargs.get(
            "ir_candidate",
            {},
        ).get(
            "risk_flags",
            [],
        ),
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


def _blocked_c276(**kwargs):
    return {
        "stage": "C276",
        "action_candidate_readiness": (
            "REQUIRES_SEMANTIC_RESOLUTION"
        ),
        "candidate_projection_ready": False,
        "execution_authorized": False,
        "requires_downstream_governance": True,
        "risk_flags": kwargs.get(
            "ir_candidate",
            {},
        ).get(
            "risk_flags",
            [],
        ),
        "unresolved_symbols": [
            "florvaxium",
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


def test_c276_snapshot_is_exposed_in_runtime(
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
        raising=False,
    )

    result = (
        pipeline.run_brody_real_response_pipeline(
            "corrige ce code",
            language="fr",
        )
    )

    assert (
        result["pre_action_calibration"][
            "stage"
        ]
        == "C276"
    )

    assert (
        result["pre_action_calibration"][
            "candidate_projection_ready"
        ]
        is True
    )


def test_c276_ready_allows_candidate_builder_to_run(
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
        raising=False,
    )

    calls = {
        "attach": 0,
    }

    def fake_attach(
        result,
        message,
        ir_intent="",
        risk_flags=None,
    ):
        calls["attach"] += 1

        result["repair_request"] = {
            "status": "CANDIDATE_CREATED",
            "message": message,
        }

        return result

    monkeypatch.setattr(
        repair_router,
        "attach_repair_request",
        fake_attach,
    )

    result = (
        pipeline.run_brody_real_response_pipeline(
            "corrige ce code",
            language="fr",
        )
    )

    assert calls["attach"] == 1

    assert result[
        "repair_request"
    ] == {
        "status": "CANDIDATE_CREATED",
        "message": "corrige ce code",
    }

    assert (
        result["pre_action_calibration"][
            "execution_authorized"
        ]
        is False
    )


def test_c276_not_ready_prevents_candidate_builder(
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
        _blocked_c276,
        raising=False,
    )

    calls = {
        "attach": 0,
    }

    def fake_attach(
        result,
        message,
        ir_intent="",
        risk_flags=None,
    ):
        calls["attach"] += 1

        result["repair_request"] = {
            "status": "SHOULD_NOT_EXIST",
        }

        return result

    monkeypatch.setattr(
        repair_router,
        "attach_repair_request",
        fake_attach,
    )

    result = (
        pipeline.run_brody_real_response_pipeline(
            "corrige florvaxium dans ce code",
            language="fr",
        )
    )

    assert calls["attach"] == 0

    assert (
        result["repair_request"]
        is None
    )

    assert (
        result["repair_route_status"]
        == "C276_CANDIDATE_NOT_READY"
    )

    assert (
        result["pre_action_calibration"][
            "action_candidate_readiness"
        ]
        == "REQUIRES_SEMANTIC_RESOLUTION"
    )


def test_c276_runtime_never_authorizes_execution(
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
        raising=False,
    )

    result = (
        pipeline.run_brody_real_response_pipeline(
            "corrige ce code",
            language="fr",
        )
    )

    c276 = result[
        "pre_action_calibration"
    ]

    assert (
        c276["execution_authorized"]
        is False
    )

    assert (
        c276["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        c276["allowed_to_act"]
        is False
    )

    assert (
        c276["emits_act"]
        is False
    )


def test_c276_integration_does_not_touch_memory_boundary():
    import inspect

    source = inspect.getsource(
        pipeline
    ).lower()

    c276_lines = "\n".join(
        line
        for line in source.splitlines()
        if (
            "c276" in line
            or "pre_action_calibration"
            in line
            or "calibrate_pre_action"
            in line
        )
    )

    forbidden = (
        "graphiti",
        "neo4j",
        "native_memory",
        "memory_response_chain",
    )

    for token in forbidden:
        assert token not in c276_lines
