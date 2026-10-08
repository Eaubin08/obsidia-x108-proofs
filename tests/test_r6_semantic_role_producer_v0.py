import json

from periphery.cognition.semantic_role_producer_v0 import (
    _validate_loopback,
    resolve_semantic_role_projection_v0,
)
from periphery.cognition.semantic_roles_v0 import SemanticRoleKindV0


def _good_payload(producer):
    return {
        "schema": "OBSIDIA_SEMANTIC_ROLE_INTERPRETATION_V0",
        "producer": producer,
        "producer_version": "TEST",
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


def test_r6_c2_brody_valid_wins_without_qwen_call():
    called = {"qwen": 0}

    def qwen(_raw):
        called["qwen"] += 1
        return {"success": True, "text": json.dumps(_good_payload("QWEN_LOCAL"))}

    raw = "Explique Obsidia en utilisant ta mémoire."
    result = resolve_semantic_role_projection_v0(
        raw_utterance=raw,
        brody_structured_output=_good_payload("BRODY"),
        qwen_available=True,
        qwen_caller=qwen,
    )

    assert result.status == "SEMANTIC_ROLE_PROJECTION_RESOLVED"
    assert result.selected_producer == "BRODY"
    assert result.brody_attempted is True
    assert result.qwen_attempted is False
    assert called["qwen"] == 0
    assert result.interpretation.projection.resolved(
        SemanticRoleKindV0.FOCUS
    ) == "OBSIDIA"


def test_r6_c2_invalid_brody_uses_brody_sens_before_qwen():
    called = {"qwen": 0}

    def qwen(_raw):
        called["qwen"] += 1
        return {
            "success": True,
            "status": "ok",
            "text": json.dumps(_good_payload("QWEN_LOCAL"), ensure_ascii=False),
        }

    bad_brody = _good_payload("BRODY")
    bad_brody["roles"]["FOCUS"]["candidates"][0]["surface"] = "Graphiti"

    result = resolve_semantic_role_projection_v0(
        raw_utterance="Explique Obsidia en utilisant ta mémoire.",
        brody_structured_output=bad_brody,
        qwen_available=True,
        qwen_caller=qwen,
    )

    assert result.status == "SEMANTIC_ROLE_PROJECTION_RESOLVED"
    assert result.selected_producer == "BRODY_SENS_V1"
    assert result.brody_attempted is True
    assert result.qwen_attempted is False
    assert called["qwen"] == 0
    assert any(x.startswith("BRODY:") for x in result.errors)


def test_r6_c2_invalid_qwen_output_stays_unresolved_when_brody_sens_is_insufficient():
    def qwen(_raw):
        return {
            "success": True,
            "status": "ok",
            "text": json.dumps(
                {
                    "schema": "OBSIDIA_SEMANTIC_ROLE_INTERPRETATION_V0",
                    "producer": "QWEN_LOCAL",
                    "producer_version": "TEST",
                    "roles": {
                        "FOCUS": {
                            "status": "RESOLVED",
                            "candidates": [
                                {"value": "UNKNOWN_ENTITY", "surface": "NOT_IN_INPUT"}
                            ],
                        }
                    },
                }
            ),
        }

    result = resolve_semantic_role_projection_v0(
        raw_utterance="Analyse le florvaxium.",
        brody_structured_output=None,
        qwen_available=True,
        qwen_caller=qwen,
    )

    assert result.status == "SEMANTIC_ROLE_PROJECTION_UNRESOLVED"
    assert result.selected_producer is None
    assert result.qwen_attempted is True
    assert result.interpretation is not None
    assert result.interpretation.projection is None
    assert any("CANDIDATE_SURFACE_NOT_IN_RAW" in x for x in result.errors)


def test_r6_c2_no_qwen_available_stays_unresolved_without_attempt():
    result = resolve_semantic_role_projection_v0(
        raw_utterance="Analyse le florvaxium.",
        brody_structured_output=None,
        qwen_available=False,
    )

    assert result.status == "SEMANTIC_ROLE_PROJECTION_UNRESOLVED"
    assert result.qwen_attempted is False
    assert result.qwen_available is False
    assert "QWEN_LOCAL_NOT_AVAILABLE" in result.errors


def test_r6_c2_non_loopback_endpoint_is_rejected():
    import pytest

    with pytest.raises(ValueError, match="QWEN_ENDPOINT_NOT_LOOPBACK"):
        _validate_loopback("https://api.example.com/v1")


def test_r6_c2_result_is_non_sovereign():
    result = resolve_semantic_role_projection_v0(
        raw_utterance="Explique Obsidia en utilisant ta mémoire.",
        brody_structured_output=_good_payload("BRODY"),
        qwen_available=False,
    )

    assert result.readonly is True
    assert result.non_sovereign is True
    assert result.decision_authority == "KX108_ONLY"
    assert result.allowed_to_decide is False
    assert result.allowed_to_act is False
    assert result.emits_act is False
    assert result.emits_verdict is False
    assert result.memory_write is False
    assert result.kernel_mutation is False

def test_r6_c2_brody_sens_resolves_contrastive_memory_roles_without_qwen():
    called = {"qwen": 0}

    def qwen(_raw):
        called["qwen"] += 1
        raise AssertionError("Qwen must not be called when Brody/SENS resolves")

    first = resolve_semantic_role_projection_v0(
        raw_utterance="Explique ce que tu sais en mémoire sur Obsidia, et détaille.",
        qwen_available=True,
        qwen_caller=qwen,
    )
    second = resolve_semantic_role_projection_v0(
        raw_utterance="Explique Obsidia en utilisant ta mémoire.",
        qwen_available=True,
        qwen_caller=qwen,
    )

    assert first.selected_producer == "BRODY_SENS_V1"
    assert second.selected_producer == "BRODY_SENS_V1"
    assert first.interpretation.projection.resolved(
        SemanticRoleKindV0.FOCUS
    ) == "MEMORY"
    assert second.interpretation.projection.resolved(
        SemanticRoleKindV0.FOCUS
    ) == "OBSIDIA"
    assert second.interpretation.projection.resolved(
        SemanticRoleKindV0.SOURCE_OR_INSTRUMENT
    ) == "MEMORY"
    assert first.qwen_attempted is False
    assert second.qwen_attempted is False
    assert called["qwen"] == 0
