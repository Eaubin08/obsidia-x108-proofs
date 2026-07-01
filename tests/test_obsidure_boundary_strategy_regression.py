"""
test_obsidure_boundary_strategy_regression.py
Matrice de non-regression — strategie BOUNDARY_NON_SOVEREIGNTY.

Verifie que BOUNDARY_NON_SOVEREIGNTY est activee uniquement pour les
objectifs Boundary/NonSovereignty et n'interfere pas avec les autres
classes Lean (MEMORY_INVARIANT, DOMAIN_KERNEL_INVARIANT, CODE_SURVEILLANCE,
ARITHMETIC, UNKNOWN).

Scope : OBSIDURE_BOUNDARY_STRATEGY_REGRESSION_MATRIX_V1
Commit ref : d75d509
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from periphery.agents.agent_obsidure import (
    LeanMutationEngine,
    _build_lean_variant,
    _classify_lean_capability,
    _is_boundary_objective,
)

# ---------------------------------------------------------------------------
# Objectifs de test — un par classe Lean
# ---------------------------------------------------------------------------

_OBJ_BOUNDARY = (
    "LEAN_SANDBOX. Fichier cible : periphery/lean_sandbox/P_ObsidureBoundary_NonDecision.lean. "
    "Theoreme cible : P_ObsidureBoundary_NonDecision. "
    "Termes critiques : Boundary, NonDecision, allowed_to_decide=false, "
    "emits_act=false, kernel_mutation=false, KX108_ONLY."
)

_OBJ_MEMORY_INVARIANT = (
    "Verifier l'invariant memory_write=false sur Graphiti readonly. "
    "MEMORY_READONLY absolu — aucune exception connue."
)

_OBJ_DOMAIN_KERNEL = (
    "Verifier entropy HOLD path_fidelity coherence trajectory "
    "signed_decision_receipt sur le kernel."
)

_OBJ_CODE_SURVEILLANCE = (
    "code surveillance correction_candidate protected infix "
    "runtime mutation dans periphery."
)

_OBJ_ARITHMETIC = (
    "Nat arithmetic rfl — propriete sur Nat.add_zero."
)

_OBJ_UNKNOWN = (
    "Reorganiser les sessions SRL par anciennete."
)

_FORBIDDEN_KEYWORDS = ("sorry", "admit", "axiom", "unsafe")
_P38_MARKERS = ("P38", "Nat.add_comm", "1 + 1 = 2", "n + m = m + n")


# ===========================================================================
# Cas 1 — NON_SOVEREIGNTY / BOUNDARY
# ===========================================================================

def test_boundary_is_boundary_objective() -> None:
    """_is_boundary_objective doit retourner True pour un objectif Boundary."""
    assert _is_boundary_objective(_OBJ_BOUNDARY) is True


def test_boundary_classify_non_sovereignty() -> None:
    """La classe Lean doit etre NON_SOVEREIGNTY ou BOUNDARY."""
    cap = _classify_lean_capability(_OBJ_BOUNDARY)
    assert cap["lean_capability_class"] in ("NON_SOVEREIGNTY", "BOUNDARY"), (
        f"Classe inattendue : {cap['lean_capability_class']}"
    )


def test_boundary_generates_correct_theorem_name() -> None:
    """Le moteur doit generer theorem P_ObsidureBoundary_NonDecision."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_ObsidureBoundary_NonDecision" in content, (
        "Le nom du theoreme doit etre exactement P_ObsidureBoundary_NonDecision"
    )


def test_boundary_generates_boundary_state() -> None:
    """Le contenu doit contenir BoundaryState."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    assert "BoundaryState" in content


def test_boundary_generates_non_sovereign_predicate() -> None:
    """Le contenu doit contenir la definition nonSovereign."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    assert "nonSovereign" in content


def test_boundary_generates_correct_namespace() -> None:
    """Le contenu doit utiliser namespace ObsidureBoundary, pas namespace P38."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    assert "namespace ObsidureBoundary" in content
    assert "namespace P38" not in content


def test_boundary_no_forbidden_keywords() -> None:
    """Le contenu ne doit contenir aucun mot-cle interdit."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    cl = content.lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in cl, f"Mot-cle interdit '{kw}' trouve dans le contenu Lean"


def test_boundary_no_p38_markers() -> None:
    """Le contenu ne doit contenir aucun marqueur P38."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    for marker in _P38_MARKERS:
        assert marker not in content, (
            f"Marqueur P38 '{marker}' trouve dans le contenu Lean"
        )


def test_boundary_can_generate_false() -> None:
    """can_generate_with_current_engine doit etre False pour NON_SOVEREIGNTY."""
    cap = _classify_lean_capability(_OBJ_BOUNDARY)
    assert cap["can_generate_with_current_engine"] is False


# ===========================================================================
# Cas 2 — MEMORY_INVARIANT
# ===========================================================================

def test_memory_invariant_classify() -> None:
    """La classe Lean doit etre MEMORY_INVARIANT."""
    cap = _classify_lean_capability(_OBJ_MEMORY_INVARIANT)
    assert cap["lean_capability_class"] == "MEMORY_INVARIANT", (
        f"Attendu MEMORY_INVARIANT, obtenu {cap['lean_capability_class']}"
    )


def test_memory_invariant_not_boundary_objective() -> None:
    """_is_boundary_objective doit retourner False pour MEMORY_INVARIANT."""
    assert _is_boundary_objective(_OBJ_MEMORY_INVARIANT) is False


def test_memory_invariant_no_boundary_theorem() -> None:
    """LeanMutationEngine ne doit pas generer P_ObsidureBoundary_NonDecision."""
    content = _build_lean_variant(
        theorem_id="P_MemInvariant",
        objective=_OBJ_MEMORY_INVARIANT,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_ObsidureBoundary_NonDecision" not in content


# ===========================================================================
# Cas 3 — DOMAIN_KERNEL_INVARIANT
# ===========================================================================

def test_domain_kernel_classify() -> None:
    """La classe Lean doit etre DOMAIN_KERNEL_INVARIANT."""
    cap = _classify_lean_capability(_OBJ_DOMAIN_KERNEL)
    assert cap["lean_capability_class"] == "DOMAIN_KERNEL_INVARIANT", (
        f"Attendu DOMAIN_KERNEL_INVARIANT, obtenu {cap['lean_capability_class']}"
    )


def test_domain_kernel_not_boundary_objective() -> None:
    """_is_boundary_objective doit retourner False pour DOMAIN_KERNEL_INVARIANT."""
    assert _is_boundary_objective(_OBJ_DOMAIN_KERNEL) is False


def test_domain_kernel_no_boundary_theorem() -> None:
    """LeanMutationEngine ne doit pas generer P_ObsidureBoundary_NonDecision."""
    content = _build_lean_variant(
        theorem_id="P_DomainKernel",
        objective=_OBJ_DOMAIN_KERNEL,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_ObsidureBoundary_NonDecision" not in content


# ===========================================================================
# Cas 4 — CODE_SURVEILLANCE
# ===========================================================================

def test_code_surveillance_classify() -> None:
    """La classe Lean doit etre CODE_SURVEILLANCE."""
    cap = _classify_lean_capability(_OBJ_CODE_SURVEILLANCE)
    assert cap["lean_capability_class"] == "CODE_SURVEILLANCE", (
        f"Attendu CODE_SURVEILLANCE, obtenu {cap['lean_capability_class']}"
    )


def test_code_surveillance_not_boundary_objective() -> None:
    """_is_boundary_objective doit retourner False pour CODE_SURVEILLANCE."""
    assert _is_boundary_objective(_OBJ_CODE_SURVEILLANCE) is False


def test_code_surveillance_no_boundary_theorem() -> None:
    """LeanMutationEngine ne doit pas generer P_ObsidureBoundary_NonDecision."""
    content = _build_lean_variant(
        theorem_id="P_CodeSurv",
        objective=_OBJ_CODE_SURVEILLANCE,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_ObsidureBoundary_NonDecision" not in content


# ===========================================================================
# Cas 5 — ARITHMETIC
# ===========================================================================

def test_arithmetic_classify() -> None:
    """La classe Lean doit etre ARITHMETIC."""
    cap = _classify_lean_capability(_OBJ_ARITHMETIC)
    assert cap["lean_capability_class"] == "ARITHMETIC", (
        f"Attendu ARITHMETIC, obtenu {cap['lean_capability_class']}"
    )


def test_arithmetic_can_generate_true() -> None:
    """ARITHMETIC peut etre genere par le moteur actuel."""
    cap = _classify_lean_capability(_OBJ_ARITHMETIC)
    assert cap["can_generate_with_current_engine"] is True


def test_arithmetic_requires_template_false() -> None:
    """ARITHMETIC ne necessite pas de template engine."""
    cap = _classify_lean_capability(_OBJ_ARITHMETIC)
    assert cap["requires_template_engine"] is False


def test_arithmetic_not_boundary_objective() -> None:
    """_is_boundary_objective doit retourner False pour ARITHMETIC."""
    assert _is_boundary_objective(_OBJ_ARITHMETIC) is False


def test_arithmetic_no_boundary_theorem() -> None:
    """LeanMutationEngine ne doit pas generer P_ObsidureBoundary_NonDecision."""
    content = _build_lean_variant(
        theorem_id="P_Arith",
        objective=_OBJ_ARITHMETIC,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_ObsidureBoundary_NonDecision" not in content


# ===========================================================================
# Cas 6 — UNKNOWN
# ===========================================================================

def test_unknown_classify() -> None:
    """La classe Lean doit etre UNKNOWN pour un objectif vague."""
    cap = _classify_lean_capability(_OBJ_UNKNOWN)
    assert cap["lean_capability_class"] == "UNKNOWN", (
        f"Attendu UNKNOWN, obtenu {cap['lean_capability_class']}"
    )


def test_unknown_not_boundary_objective() -> None:
    """_is_boundary_objective doit retourner False pour UNKNOWN."""
    assert _is_boundary_objective(_OBJ_UNKNOWN) is False


def test_unknown_no_boundary_theorem() -> None:
    """LeanMutationEngine ne doit pas generer P_ObsidureBoundary_NonDecision."""
    content = _build_lean_variant(
        theorem_id="P_Unknown",
        objective=_OBJ_UNKNOWN,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_ObsidureBoundary_NonDecision" not in content


# ===========================================================================
# Securite globale — sorry guard actif sur LeanMutationEngine
# ===========================================================================

def test_sorry_pattern_present_in_engine() -> None:
    """LeanMutationEngine doit avoir un SORRY_PATTERN de garde."""
    import re
    engine = LeanMutationEngine()
    assert hasattr(engine, "SORRY_PATTERN"), "SORRY_PATTERN absent de LeanMutationEngine"
    assert isinstance(engine.SORRY_PATTERN, type(re.compile("")))


def test_boundary_content_sorry_guard() -> None:
    """Le contenu BOUNDARY genere ne doit jamais passer le sorry guard."""
    engine = LeanMutationEngine()
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    assert not engine.SORRY_PATTERN.search(content), (
        "SORRY detecte dans le contenu BOUNDARY_NON_SOVEREIGNTY"
    )


# ===========================================================================
# Lean compile check (si lake disponible)
# ===========================================================================

def test_boundary_lean_compiles() -> None:
    """Le contenu BOUNDARY_NON_SOVEREIGNTY doit compiler avec lake env lean."""
    lake_path = shutil.which("lake")
    if not lake_path:
        return  # lake absent — skip silencieux

    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )

    lean_cwd = _REPO_ROOT / "proofs" / "lean"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_lean = Path(tmpdir) / "P_ObsidureBoundary_NonDecision_regtest.lean"
        tmp_lean.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [lake_path, "env", "lean", str(tmp_lean)],
            cwd=str(lean_cwd),
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0, (
            f"lake env lean a echoue (rc={result.returncode}):\n"
            f"stderr: {result.stderr[:400]}\n"
            f"stdout: {result.stdout[:200]}"
        )
