"""
periphery/tests/test_obsidure_python_route.py
=============================================
Tests smoke — route PYTHON_PATCH_PROPOSAL d'Obsidure.

Critères :
  1. Objectif Python → intent = PYTHON_PATCH_PROPOSAL
  2. Objectif Python → aucun patch .lean généré
  3. Chemins protégés bloqués (proofs/, sealed, V18, kernel)
  4. Fichiers proposés toujours sous periphery/
  5. Lean trigger neutralisé quand intent = PYTHON_PATCH_PROPOSAL

Contraintes absolues :
  kernel_mutation = False
  P107 = A_PROUVER (ne pas présenter comme prouvé)
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

# Résolution du repo root depuis ce fichier
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from periphery.agents.agent_obsidure import (
    _local_intent,
    _local_risk_flags,
    _generate_python_peripheral_patches,
    _test_patches_conformity,
    _is_protected,
    PROTECTED_INFIXES,
)


# ===========================================================================
# Test 1 — Détection de l'intent PYTHON_PATCH_PROPOSAL
# ===========================================================================

def test_intent_python_detected_by_py_extension():
    """'.py' dans l'objectif → PYTHON_PATCH_PROPOSAL."""
    assert _local_intent("Cree un module test_route_python.py dans periphery/math_core") == "PYTHON_PATCH_PROPOSAL"


def test_intent_python_detected_by_math_core():
    """'periphery/math_core' → PYTHON_PATCH_PROPOSAL."""
    assert _local_intent("module Python dans periphery/math_core avec tests smoke") == "PYTHON_PATCH_PROPOSAL"


def test_intent_python_detected_by_branch_registry():
    """'BRANCH_REGISTRY' → PYTHON_PATCH_PROPOSAL."""
    assert _local_intent("genere BRANCH_REGISTRY.json") == "PYTHON_PATCH_PROPOSAL"


def test_intent_python_detected_by_tests_smoke():
    """'tests smoke' → PYTHON_PATCH_PROPOSAL."""
    assert _local_intent("ajoute des tests smoke dans periphery/tests") == "PYTHON_PATCH_PROPOSAL"


def test_intent_python_priority_over_lean():
    """Objectif contenant 'Lean' ET '.py' → Python gagne."""
    intent = _local_intent("Cree test.py sans toucher kernel Lean V18")
    assert intent == "PYTHON_PATCH_PROPOSAL", f"Attendu PYTHON_PATCH_PROPOSAL, obtenu {intent}"


def test_intent_lean_not_triggered_by_sans_lean():
    """'rapport markdown' + 'sans toucher Lean' → PYTHON_PATCH_PROPOSAL (pas LEAN_SANDBOX).
    'rapport markdown' contient '.md' implicitement via le keyword RAPPORT MARKDOWN.
    """
    intent = _local_intent("cree un rapport markdown sans toucher Lean")
    assert intent != "LEAN_SANDBOX", f"LEAN_SANDBOX ne devrait pas être déclenché ici, obtenu {intent}"


# ===========================================================================
# Test 2 — Génération de patches : aucun .lean quand route Python
# ===========================================================================

def test_python_route_generates_no_lean_patch():
    """Route PYTHON_PATCH_PROPOSAL → aucun patch avec action CREATE_LEAN_PERIPHERAL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        patches = _generate_python_peripheral_patches(
            "Cree test_route_python.py dans periphery/math_core", sandbox, attempt=1
        )
    lean_patches = [p for p in patches if p.get("action") == "CREATE_LEAN_PERIPHERAL"]
    assert lean_patches == [], f"Patches Lean inattendus : {lean_patches}"


def test_python_route_generates_python_patch():
    """Route PYTHON_PATCH_PROPOSAL → au moins un patch action CREATE_PYTHON_PERIPHERAL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        patches = _generate_python_peripheral_patches(
            "Cree test_route_python.py dans periphery/math_core", sandbox, attempt=1
        )
    py_patches = [p for p in patches if p.get("action") == "CREATE_PYTHON_PERIPHERAL"]
    assert py_patches, "Aucun patch Python généré"


def test_python_route_file_content_is_python():
    """Le stub généré contient du code Python valide (pas du Lean)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        patches = _generate_python_peripheral_patches(
            "Cree test_route_python.py dans periphery/math_core", sandbox, attempt=1
        )
        for p in patches:
            sp = Path(p["sandbox_path"])
            if sp.exists() and sp.suffix == ".py":
                content = sp.read_text(encoding="utf-8")
                assert "theorem" not in content.lower(), "Contenu Lean détecté dans un stub Python"
                assert "def " in content or '"""' in content, "Stub Python ne ressemble pas à du Python"


# ===========================================================================
# Test 3 — Chemins protégés bloqués
# ===========================================================================

def test_protected_paths_are_blocked():
    """Les chemins protégés ne doivent pas apparaître dans les patches Python."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        # Objectif tentant de cibler un fichier protégé
        patches = _generate_python_peripheral_patches(
            "Modifie server.kernel.sealed.cjs et proofs/V18_test.py", sandbox, attempt=1
        )
    for p in patches:
        path = p.get("path", "")
        for infx in PROTECTED_INFIXES:
            assert infx not in path, f"Chemin protégé '{infx}' dans le patch : {path}"


def test_is_protected_kernel():
    assert _is_protected("server.kernel.sealed.cjs") is True


def test_is_protected_v18():
    assert _is_protected("proofs/V18_bundle/P01.lean") is True


def test_is_protected_merkle():
    assert _is_protected("merkle_seal.json") is True


def test_is_protected_periphery_math_core():
    """periphery/math_core/ n'est PAS protégé."""
    assert _is_protected("periphery/math_core/omega_space.py") is False


# ===========================================================================
# Test 4 — Fichiers proposés sous periphery/ uniquement
# ===========================================================================

def test_python_patches_under_periphery():
    """Tous les patches Python ont un path commençant par periphery/."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        patches = _generate_python_peripheral_patches(
            "Cree omega_space.py et BRANCH_REGISTRY.json dans periphery/math_core", sandbox, attempt=1
        )
    for p in patches:
        path = p.get("path", "")
        assert path.startswith("periphery/"), (
            f"Patch Python hors de periphery/ : '{path}'"
        )


def test_conformity_check_rejects_outside_periphery():
    """_test_patches_conformity détecte un patch Python hors periphery/."""
    bad_patch = [{
        "path": "proofs/lean/peripheral/hacked.py",
        "action": "CREATE_PYTHON_PERIPHERAL",
        "sandbox_path": "",
    }]
    errors = _test_patches_conformity(bad_patch, None, Path("."))
    types = [e["type"] for e in errors]
    assert "PYTHON_OUTPUT_OUTSIDE_PERIPHERY" in types


def test_conformity_check_rejects_bad_extension():
    """_test_patches_conformity détecte une extension non autorisée."""
    bad_patch = [{
        "path": "periphery/math_core/hack.lean",
        "action": "CREATE_PYTHON_PERIPHERAL",
        "sandbox_path": "",
    }]
    errors = _test_patches_conformity(bad_patch, None, Path("."))
    types = [e["type"] for e in errors]
    assert "PYTHON_INVALID_EXTENSION" in types


def test_conformity_check_accepts_valid_python():
    """_test_patches_conformity accepte un patch .py sous periphery/."""
    with tempfile.TemporaryDirectory() as tmpdir:
        f = Path(tmpdir) / "periphery" / "math_core" / "test.py"
        f.parent.mkdir(parents=True)
        f.write_text("def init(): return {}\n", encoding="utf-8")
        patch = [{
            "path": "periphery/math_core/test.py",
            "action": "CREATE_PYTHON_PERIPHERAL",
            "sandbox_path": str(f),
        }]
        errors = _test_patches_conformity(patch, None, Path(tmpdir))
    assert errors == [], f"Erreurs inattendues : {errors}"


# ===========================================================================
# Test 5 — Boundaries kernel_mutation=False
# ===========================================================================

def test_boundary_kernel_mutation_false():
    """kernel_mutation doit toujours être False dans AGENT_OBSIDURE_BOUNDARY."""
    from periphery.agents.agent_obsidure import AGENT_OBSIDURE_BOUNDARY
    assert AGENT_OBSIDURE_BOUNDARY["kernel_mutation"] is False


def test_boundary_emits_act_false():
    from periphery.agents.agent_obsidure import AGENT_OBSIDURE_BOUNDARY
    assert AGENT_OBSIDURE_BOUNDARY["emits_act"] is False


# ===========================================================================
# Runner autonome
# ===========================================================================

if __name__ == "__main__":
    tests = [
        test_intent_python_detected_by_py_extension,
        test_intent_python_detected_by_math_core,
        test_intent_python_detected_by_branch_registry,
        test_intent_python_detected_by_tests_smoke,
        test_intent_python_priority_over_lean,
        test_intent_lean_not_triggered_by_sans_lean,
        test_python_route_generates_no_lean_patch,
        test_python_route_generates_python_patch,
        test_python_route_file_content_is_python,
        test_protected_paths_are_blocked,
        test_is_protected_kernel,
        test_is_protected_v18,
        test_is_protected_merkle,
        test_is_protected_periphery_math_core,
        test_python_patches_under_periphery,
        test_conformity_check_rejects_outside_periphery,
        test_conformity_check_rejects_bad_extension,
        test_conformity_check_accepts_valid_python,
        test_boundary_kernel_mutation_false,
        test_boundary_emits_act_false,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {t.__name__} — {exc}")
            failed += 1
    print(f"\n{passed}/{passed+failed} tests passés.")
    sys.exit(0 if failed == 0 else 1)
