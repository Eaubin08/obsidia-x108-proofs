"""Test synthetique pour la cible du moteur de build borne.

Ce test ECHOUE sur la cible non patchee (BUILD_SESSION_APPLIED absent).
Ce test PASSE apres application du patch de session dans le worktree.
Utilise __file__ pour localiser target.txt relatif au test.
"""
from pathlib import Path


def test_build_session_applied():
    target = Path(__file__).parent / "target.txt"
    content = target.read_text(encoding="utf-8")
    assert "BUILD_SESSION_APPLIED" in content, (
        f"Cible non patchee. Contenu actuel: {content!r}\n"
        "Ce test doit etre execute dans le worktree de session apres patch."
    )
