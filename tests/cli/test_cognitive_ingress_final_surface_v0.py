from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


from obsidia_cognitive_ingress_v0 import (
    run_cognitive_ingress,
)

import obsidia_openjarvis_native_cli_bridge_v0 as bridge


def test_cognitive_ingress_exposes_governed_final_surface():
    result = run_cognitive_ingress(
        text="bonjour",
        session_id=(
            "jws-11111111111111111111"
        ),
        allow_local_model=False,
    )

    surface = result.get(
        "surface_response"
    )

    snap = result.get(
        "final_answer_snapshot"
    )

    assert isinstance(surface, str)
    assert surface.strip()

    assert isinstance(snap, dict)

    assert surface == str(
        snap.get("final_answer")
        or ""
    ).strip()

    assert (
        snap.get(
            "decision_authority"
        )
        == "KX108_ONLY"
    )

    assert (
        snap.get(
            "emits_act"
        )
        is False
    )

    assert (
        snap.get(
            "allowed_to_decide"
        )
        is False
    )


def test_native_bridge_prefers_governed_surface_over_brody_debug():
    turn = {
        "surface_text": (
            "RÉPONSE FINALE GOUVERNÉE"
        ),
        "cognitive_result": {
            "cognitive_join": {
                "brody_cognitive_response": {
                    "response_text": (
                        "RÉPONSE STRUCTURELLE."
                    )
                }
            }
        },
    }

    assert (
        bridge._surface_turn(turn)
        == "RÉPONSE FINALE GOUVERNÉE"
    )


def test_raw_local_model_evidence_is_never_surface_priority():
    turn = {
        "surface_text": (
            "RÉPONSE FINALE ADMISE"
        ),
        "cognitive_result": {
            "cognitive_join": {
                "local_model_evidence_snapshot": {
                    "content": (
                        "RAW_QWEN_EVIDENCE"
                    )
                },
                "brody_cognitive_response": {
                    "response_text": (
                        "RÉPONSE STRUCTURELLE."
                    )
                },
            }
        },
    }

    rendered = bridge._surface_turn(
        turn
    )

    assert (
        rendered
        == "RÉPONSE FINALE ADMISE"
    )

    assert (
        "RAW_QWEN_EVIDENCE"
        not in rendered
    )
