from app.gates.gates import evaluate
from app.ir.unified_ir import build_ir
from app.router.decision import decide


def test_greeting_is_local_conversation():
    ir = build_ir("bonjour")

    assert ir["intent_type"] == "conversation"
    assert ir["target_layer"] == "brody"
    assert ir["risk_level"] == "low"
    assert ir["missing"] == []
    assert ir["needs"]["brody"] is True
    assert ir["needs"]["remote_model"] is False


def test_thanks_is_local_conversation():
    ir = build_ir("merci")

    assert ir["intent_type"] == "conversation"
    assert ir["target_layer"] == "brody"
    assert ir["missing"] == []


def test_english_social_surface_is_local():
    for raw in (
        "hello",
        "hi",
        "thank you",
    ):
        ir = build_ir(raw)

        assert ir["intent_type"] == "conversation"
        assert ir["target_layer"] == "brody"
        assert ir["missing"] == []


def test_greeting_gate_is_allow():
    verdict = evaluate(
        build_ir("bonjour")
    )

    assert verdict["verdict"] == "ALLOW"


def test_conversation_routes_to_brody_without_model():
    for raw in (
        "bonjour",
        "salut",
        "merci",
        "hello",
    ):
        decision = decide(raw)

        assert decision["route"] == "brody"
        assert decision["level"] == 1
        assert decision["model"] is None


def test_ambiguous_ok_vas_y_still_clarifies():
    ir = build_ir("ok vas-y")
    verdict = evaluate(ir)
    decision = decide("ok vas-y")

    assert ir["intent_type"] == "unknown"
    assert "intent" in ir["missing"]

    assert verdict["verdict"] == "CLARIFY"

    assert (
        decision["route"]
        == "clarification_needed"
    )


def test_explicit_action_still_beats_social_language():
    ir = build_ir(
        "bonjour execute ce script"
    )

    decision = decide(
        "bonjour execute ce script"
    )

    assert ir["intent_type"] == "world_action"
    assert ir["risk_level"] == "high"

    assert (
        decision["route"]
        == "hold_commands_only"
    )


def test_real_question_still_beats_greeting():
    ir = build_ir(
        "bonjour explique le contexte"
    )

    assert ir["intent_type"] == "question"
    assert ir["target_layer"] == "brody"



def test_conversation_modifiers_alone_remain_ambiguous():
    for raw in (
        "you",
        "beaucoup",
    ):
        ir = build_ir(raw)

        assert ir["intent_type"] == "unknown"
        assert "intent" in ir["missing"]

        decision = decide(raw)

        assert (
            decision["route"]
            == "clarification_needed"
        )


def test_conversation_marker_with_modifier_is_local():
    for raw in (
        "merci beaucoup",
        "thank you",
    ):
        ir = build_ir(raw)

        assert ir["intent_type"] == "conversation"
        assert ir["target_layer"] == "brody"
        assert ir["missing"] == []

        decision = decide(raw)

        assert decision["route"] == "brody"
        assert decision["model"] is None
