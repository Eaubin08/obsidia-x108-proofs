from __future__ import annotations

from apps.obsidia_api.brody_v1_4_12a_final_answer_adapter import (
    run_brody_v1_4_12a_final_answer,
)


CODE = (
    "def add(a, b):\n"
    "    return a + b"
)


def _ready_projection():
    return {
        "status": "READY",
        "reason": None,
        "content": CODE,
        "source": "VALIDATED_MODEL_EVIDENCE",
        "source_ref": "model-evidence:qwen:test",
        "projection_hash": "projection-hash",
        "readonly": True,
        "advisory_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "kernel_mutation": False,
        "decision_authority": "KX108_ONLY",
        "raw_model_direct_surface": False,
    }


def test_ready_projection_is_final_human_material():
    result = run_brody_v1_4_12a_final_answer(
        user_message=(
            "?cris uniquement ce code Python, "
            "sans explication et sans markdown :\n\n"
            "def add(a, b):\n"
            "    return a + b"
        ),
        language="fr",
        governed_model_projection=(
            _ready_projection()
        ),
    )

    assert result["final_answer"] == CODE

    assert (
        result[
            "governed_model_projection_selected"
        ]
        is True
    )

    assert result[
        "v1_4_12a_status_tag"
    ].startswith(
        "GOVERNED_MODEL_PROJECTION_"
    )

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )

    assert result["emits_act"] is False
    assert result["emits_verdict"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False


def test_blocked_projection_preserves_code_guard():
    projection = _ready_projection()
    projection["status"] = "BLOCKED"
    projection["content"] = ""

    result = run_brody_v1_4_12a_final_answer(
        user_message=(
            "def add(a, b):\n"
            "    return a + b"
        ),
        language="fr",
        governed_model_projection=projection,
    )

    assert (
        result[
            "governed_model_projection_selected"
        ]
        is False
    )

    assert (
        result["v1_4_12a_status_tag"]
        == "CODE_PASTE_GUARD"
    )


def test_projection_cannot_bypass_action_risk():
    result = run_brody_v1_4_12a_final_answer(
        user_message=(
            "Ex?cute cette op?ration maintenant."
        ),
        language="fr",
        risk=True,
        governed_model_projection=(
            _ready_projection()
        ),
    )

    assert (
        result[
            "governed_model_projection_selected"
        ]
        is False
    )

    assert result["final_answer"] != CODE

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )


def test_projection_requires_full_boundary_contract():
    projection = _ready_projection()
    projection["allowed_to_act"] = True

    result = run_brody_v1_4_12a_final_answer(
        user_message="Analyse cette fonction.",
        language="fr",
        governed_model_projection=projection,
    )

    assert (
        result[
            "governed_model_projection_selected"
        ]
        is False
    )

    assert result["final_answer"] != CODE
