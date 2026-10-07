import json

from periphery.cognition.semantic_role_interpreter_v0 import (
    interpret_semantic_roles_v0,
    semantic_role_prompt_v0,
)
from periphery.cognition.semantic_roles_v0 import SemanticRoleKindV0


def _payload_memory_focus():
    return {
        "schema": "OBSIDIA_SEMANTIC_ROLE_INTERPRETATION_V0",
        "producer": "BRODY",
        "producer_version": "R6-C1-TEST",
        "roles": {
            "FOCUS": {
                "status": "RESOLVED",
                "candidates": [{"value": "MEMORY", "surface": "mémoire"}],
            },
            "SCOPE": {
                "status": "RESOLVED",
                "candidates": [{"value": "OBSIDIA", "surface": "Obsidia"}],
            },
            "OPERATION": {
                "status": "RESOLVED",
                "candidates": [{"value": "EXPLAIN", "surface": "Explique"}],
            },
            "QUALIFIER": {
                "status": "RESOLVED",
                "candidates": [{"value": "DETAILED", "surface": "détaille"}],
            },
            "SOURCE_OR_INSTRUMENT": {
                "status": "UNKNOWN",
                "candidates": [],
            },
        },
    }


def test_r6_c1_accepts_grounded_memory_focus_projection():
    raw = "Explique ce que tu sais en mémoire sur Obsidia, et détaille."
    result = interpret_semantic_roles_v0(
        raw_utterance=raw,
        structured_output=json.dumps(_payload_memory_focus(), ensure_ascii=False),
        source_refs=("brody:test",),
    )

    assert result.status == "SEMANTIC_ROLE_INTERPRETATION_ACCEPTED"
    assert result.projection is not None
    assert result.projection.resolved(SemanticRoleKindV0.FOCUS) == "MEMORY"
    assert result.projection.resolved(SemanticRoleKindV0.SCOPE) == "OBSIDIA"
    assert result.projection.resolved(SemanticRoleKindV0.OPERATION) == "EXPLAIN"
    assert result.projection.resolved(SemanticRoleKindV0.QUALIFIER) == "DETAILED"
    assert result.projection.resolved(SemanticRoleKindV0.SOURCE_OR_INSTRUMENT) is None
    focus = result.projection.binding(SemanticRoleKindV0.FOCUS)
    assert focus.candidates[0].source_span == (
        raw.index("mémoire"),
        raw.index("mémoire") + len("mémoire"),
    )


def test_r6_c1_accepts_memory_as_source_not_focus():
    raw = "Explique Obsidia en utilisant ta mémoire."
    payload = {
        "schema": "OBSIDIA_SEMANTIC_ROLE_INTERPRETATION_V0",
        "producer": "BRODY",
        "producer_version": "R6-C1-TEST",
        "roles": {
            "FOCUS": {
                "status": "RESOLVED",
                "candidates": [{"value": "OBSIDIA", "surface": "Obsidia"}],
            },
            "OPERATION": {
                "status": "RESOLVED",
                "candidates": [{"value": "EXPLAIN", "surface": "Explique"}],
            },
            "SOURCE_OR_INSTRUMENT": {
                "status": "RESOLVED",
                "candidates": [{"value": "MEMORY", "surface": "mémoire"}],
            },
        },
    }

    result = interpret_semantic_roles_v0(
        raw_utterance=raw,
        structured_output=payload,
    )

    assert result.status == "SEMANTIC_ROLE_INTERPRETATION_ACCEPTED"
    assert result.projection.resolved(SemanticRoleKindV0.FOCUS) == "OBSIDIA"
    assert result.projection.resolved(
        SemanticRoleKindV0.SOURCE_OR_INSTRUMENT
    ) == "MEMORY"


def test_r6_c1_rejects_candidate_not_grounded_in_raw():
    payload = _payload_memory_focus()
    payload["roles"]["FOCUS"]["candidates"][0]["surface"] = "Graphiti"

    result = interpret_semantic_roles_v0(
        raw_utterance="Explique ce que tu sais en mémoire sur Obsidia, et détaille.",
        structured_output=payload,
    )

    assert result.status == "SEMANTIC_ROLE_INTERPRETATION_REJECTED"
    assert result.projection is None
    assert "CANDIDATE_SURFACE_NOT_IN_RAW" in result.errors[0]


def test_r6_c1_rejects_authority_language_in_model_output():
    payload = _payload_memory_focus()
    payload["roles"]["OPERATION"]["candidates"][0]["value"] = "ACT"

    result = interpret_semantic_roles_v0(
        raw_utterance="Explique ce que tu sais en mémoire sur Obsidia, et détaille.",
        structured_output=payload,
    )

    assert result.status == "SEMANTIC_ROLE_INTERPRETATION_REJECTED"
    assert result.projection is None
    assert "AUTHORITY_WORD_FORBIDDEN:ACT" in result.errors[0]


def test_r6_c1_rejects_non_unique_surface_provenance():
    raw = "mémoire puis mémoire"
    payload = {
        "schema": "OBSIDIA_SEMANTIC_ROLE_INTERPRETATION_V0",
        "producer": "BRODY",
        "producer_version": "R6-C1-TEST",
        "roles": {
            "FOCUS": {
                "status": "RESOLVED",
                "candidates": [{"value": "MEMORY", "surface": "mémoire"}],
            }
        },
    }

    result = interpret_semantic_roles_v0(
        raw_utterance=raw,
        structured_output=payload,
    )

    assert result.status == "SEMANTIC_ROLE_INTERPRETATION_REJECTED"
    assert "CANDIDATE_SURFACE_NOT_UNIQUE" in result.errors[0]


def test_r6_c1_missing_roles_are_unknown_not_invented():
    raw = "Explique Obsidia."
    payload = {
        "schema": "OBSIDIA_SEMANTIC_ROLE_INTERPRETATION_V0",
        "producer": "BRODY",
        "producer_version": "R6-C1-TEST",
        "roles": {
            "FOCUS": {
                "status": "RESOLVED",
                "candidates": [{"value": "OBSIDIA", "surface": "Obsidia"}],
            }
        },
    }

    result = interpret_semantic_roles_v0(
        raw_utterance=raw,
        structured_output=payload,
    )

    assert result.status == "SEMANTIC_ROLE_INTERPRETATION_ACCEPTED"
    for role in (
        SemanticRoleKindV0.SCOPE,
        SemanticRoleKindV0.OPERATION,
        SemanticRoleKindV0.QUALIFIER,
        SemanticRoleKindV0.SOURCE_OR_INSTRUMENT,
    ):
        binding = result.projection.binding(role)
        assert binding.status.value == "UNKNOWN"
        assert binding.candidates == ()


def test_r6_c1_prompt_is_bounded_and_non_sovereign():
    prompt = semantic_role_prompt_v0("Explique Obsidia.")
    assert "Return JSON only" in prompt
    assert "FOCUS" in prompt
    assert "SOURCE_OR_INSTRUMENT" in prompt
    assert "Do not decide" in prompt
    assert "User utterance:" in prompt
