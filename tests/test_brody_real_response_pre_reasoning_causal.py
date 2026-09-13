import apps.obsidia_api.brody_real_response_pipeline as pipeline


class FakeTerminal:
    def __init__(self):
        self.build_calls = []

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
        self.build_calls.append(
            {
                "user_text": user_text,
                "memory_query": memory_query,
                "packet": packet,
                "selected": selected,
                "command": command,
            }
        )

        return (
            "TERMINAL_RESPONSE",
            [],
            False,
        )


def test_known_concept_reaches_terminal_after_pre_reasoning(
    monkeypatch,
):
    terminal = FakeTerminal()

    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        terminal,
    )

    result = pipeline.run_brody_real_response_pipeline(
        message="explique x108",
        language="fr",
    )

    pre = result["pre_reasoning_snapshot"]
    directive = pre["reasoning_directive"]

    assert directive[
        "reasoning_mode"
    ] == "NORMAL_REASONING"

    assert directive[
        "resolution_required"
    ] is False

    assert len(
        terminal.build_calls
    ) == 1

    assert result[
        "response_md"
    ] == "TERMINAL_RESPONSE"


def test_unknown_is_causal_before_terminal_assertion(
    monkeypatch,
):
    terminal = FakeTerminal()

    monkeypatch.setattr(
        pipeline,
        "_TERMINAL",
        terminal,
    )

    result = pipeline.run_brody_real_response_pipeline(
        message="explique le florvaxium",
        language="fr",
    )

    pre = result["pre_reasoning_snapshot"]
    directive = pre["reasoning_directive"]

    assert directive[
        "reasoning_mode"
    ] == "RESOLVE_BEFORE_ASSERT"

    assert directive[
        "resolution_required"
    ] is True

    assert directive[
        "resolution_targets"
    ] == [
        "florvaxium",
    ]

    # Causal proof:
    # the old terminal responder must not invent/assert
    # content about an unresolved symbol.
    assert terminal.build_calls == []

    assert result[
        "response_source"
    ] == "PRE_REASONING_UNRESOLVED_SYMBOL"

    assert result[
        "response_md"
    ]

    assert "florvaxium" in result[
        "response_md"
    ].lower()

    assert result[
        "decision_authority"
    ] == "KX108_ONLY"

    assert result[
        "emits_act"
    ] is False

    assert result[
        "emits_verdict"
    ] is False

    assert result[
        "memory_write"
    ] is False

    assert result[
        "kernel_mutation"
    ] is False


def test_runtime_pre_reasoning_remains_provider_free():
    import inspect

    source = inspect.getsource(
        pipeline.run_brody_real_response_pipeline
    ).lower()

    # Pre-reasoning must not acquire a new
    # memory/provider dependency.
    forbidden = (
        "brody_obsidia_native_memory",
        "brody_native_memory_response_adapter",
        "brody_memory_response_chain_adapter",
        "graphiti_v20_readonly_client",
        "neo4j_brody_guide_bridge",
    )

    for token in forbidden:
        assert token not in source
