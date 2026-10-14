from apps.obsidia_api import brody_pre_reasoning_adapter as adapter
from periphery.cognition.brody_semantic_focus_v1 import (
    build_brody_semantic_focus_projection_v1,
)


def _patch_pre_reasoning(monkeypatch):
    monkeypatch.setattr(
        adapter,
        "build_semantic_query",
        lambda _message: {
            "route": "FALLBACK_WORD_EXTRACTION",
            "is_canonical": False,
            "topic": "UNKNOWN",
        },
    )
    monkeypatch.setattr(
        adapter,
        "build_existing_reverse_os_projection",
        lambda **kwargs: {
            "ir_candidate": {
                "unknowns": ["memoire", "obsidia", "florvaxium"],
                "lexical_calibration": {
                    "unknowns": ["memoire", "obsidia", "florvaxium"],
                },
            }
        },
    )

    def calibrate(**kwargs):
        unknowns = list(kwargs["lexical_calibration"].get("unknowns", []))
        return {
            "unknowns": unknowns,
            "reasoning_readiness": (
                "REQUIRES_RESOLUTION" if unknowns else "READY"
            ),
        }

    monkeypatch.setattr(adapter, "calibrate_pre_reasoning", calibrate)
    monkeypatch.setattr(
        adapter,
        "build_reasoning_directive",
        lambda calibration: {
            "resolution_required": bool(calibration.get("unknowns")),
            "resolution_targets": list(calibration.get("unknowns", [])),
        },
    )


def test_brody_sens_terms_resolve_only_their_grounded_lexical_units(monkeypatch):
    _patch_pre_reasoning(monkeypatch)
    raw = "Explique ce que tu sais en mémoire sur Obsidia, et détaille."
    projection = build_brody_semantic_focus_projection_v1(raw)

    result = adapter.build_brody_pre_reasoning_snapshot(
        user_message=raw,
        language="fr",
        semantic_role_projection=projection,
    )

    qualified = result["unknown_qualification"]
    assert "memoire" in qualified["semantically_resolved_unknowns"]
    assert "obsidia" in qualified["semantically_resolved_unknowns"]
    assert "florvaxium" in qualified["unresolved_unknowns"]
    assert "florvaxium" in result["reasoning_directive"]["resolution_targets"]
    assert "memoire" not in result["reasoning_directive"]["resolution_targets"]
    assert "obsidia" not in result["reasoning_directive"]["resolution_targets"]


def test_without_brody_sens_projection_terms_remain_unresolved(monkeypatch):
    _patch_pre_reasoning(monkeypatch)

    result = adapter.build_brody_pre_reasoning_snapshot(
        user_message="Analyse le florvaxium.",
        language="fr",
        semantic_role_projection=None,
    )

    qualified = result["unknown_qualification"]
    assert "florvaxium" in qualified["unresolved_unknowns"]
    assert result["reasoning_directive"]["resolution_required"] is True


def test_pre_reasoning_role_context_keeps_kx108_boundary(monkeypatch):
    _patch_pre_reasoning(monkeypatch)
    raw = "Explique Obsidia en utilisant ta mémoire."
    projection = build_brody_semantic_focus_projection_v1(raw)

    result = adapter.build_brody_pre_reasoning_snapshot(
        user_message=raw,
        language="fr",
        semantic_role_projection=projection,
    )

    ctx = result["semantic_role_context"]
    assert ctx["readonly"] is True
    assert ctx["non_sovereign"] is True
    assert ctx["decision_authority"] == "KX108_ONLY"
    assert ctx["allowed_to_decide"] is False
    assert ctx["allowed_to_act"] is False
    assert result["decision_authority"] == "KX108_ONLY"
