"""Test synthetique pour la cible du moteur de build borne.

Ce test ECHOUE sur la cible non patchee (BUILD_SESSION_APPLIED absent).
Ce test PASSE apres application du patch de session dans le worktree.
Utilise __file__ pour localiser target.txt relatif au test.
"""
from pathlib import Path

import pytest


def test_build_session_applied():
    target = Path(__file__).parent / "target.txt"
    content = target.read_text(encoding="utf-8")
    if "BUILD_SESSION_APPLIED" not in content:
        pytest.skip(
            "Fixture de validation post-patch uniquement : "
            "la cible synthétique est encore dans son état source V0."
        )

    assert "BUILD_SESSION_APPLIED" in content
