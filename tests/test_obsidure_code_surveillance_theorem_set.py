"""
test_obsidure_code_surveillance_theorem_set.py
Matrice de tests — strategie CODE_SURVEILLANCE_TEMPLATE.

Verifie :
  - Detection correcte des objectifs code surveillance
  - Generation des 3 theoremes V1 (P_ObsidureCodeSurveillance_NonSovereign,
    P_CandidateCorrection_RequiresValidation, P_ProtectedRuntimeMutation_Blocked)
  - Isolation stricte de la strategie (ne capture pas boundary / arithmetic / unknown)
  - Absence de sorry/admit/axiom/unsafe dans le contenu genere
  - Absence de marqueurs P38 dans le contenu genere
  - Namespace correct (ObsidureCodeSurveillance)
  - Metadonnees strategy_used = CODE_SURVEILLANCE_TEMPLATE

Scope : OBSIDURE_CODE_SURVEILLANCE_THEOREM_SET_V1
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
    _is_code_surveillance_objective,
)

# ---------------------------------------------------------------------------
# Objectifs de test
# ---------------------------------------------------------------------------

_OBJ_CS_A = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_ObsidureCodeSurveillance_NonSovereign.lean. "
    "Theoreme cible : P_ObsidureCodeSurveillance_NonSovereign. "
    "Termes critiques : code surveillance, applies_patch=false, commits_git=false, "
    "runtime mutation=false, kernel mutation=false, memory_write=false, HUMAN_APPROVED_WRITE."
)

_OBJ_CS_B = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_CandidateCorrection_RequiresValidation.lean. "
    "Theoreme cible : P_CandidateCorrection_RequiresValidation. "
    "Termes critiques : correction_candidate, apply proposal, human_validated=true, "
    "HUMAN_APPROVED_WRITE."
)

_OBJ_CS_C = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_ProtectedRuntimeMutation_Blocked.lean. "
    "Theoreme cible : P_ProtectedRuntimeMutation_Blocked. "
    "Termes critiques : protected infix, runtime mutation=false, kernel mutation=false."
)

_OBJ_BOUNDARY = (
    "LEAN_SANDBOX. Fichier cible : periphery/lean_sandbox/P_ObsidureBoundary_NonDecision.lean. "
    "Theoreme cible : P_ObsidureBoundary_NonDecision. "
    "Termes critiques : Boundary, NonDecision, allowed_to_decide=false, "
    "emits_act=false, kernel_mutation=false, KX108_ONLY."
)

_OBJ_ARITHMETIC = "Nat arithmetic rfl — propriete sur Nat.add_zero."
_OBJ_UNKNOWN = "Reorganiser les sessions SRL par anciennete."

_FORBIDDEN_KEYWORDS = ("sorry", "admit", "axiom", "unsafe")
_P38_MARKERS = ("P38", "Nat.add_comm", "1 + 1 = 2", "n + m = m + n")


# ===========================================================================
# Groupe 1 — Detection _is_code_surveillance_objective
# ===========================================================================

def test_cs_detection_explicit_theorem_a() -> None:
    """Detection via nom explicite P_ObsidureCodeSurveillance_NonSovereign."""
    assert _is_code_surveillance_objective(_OBJ_CS_A) is True


def test_cs_detection_explicit_theorem_b() -> None:
    """Detection via nom explicite P_CandidateCorrection_RequiresValidation."""
    assert _is_code_surveillance_objective(_OBJ_CS_B) is True


def test_cs_detection_explicit_theorem_c() -> None:
    """Detection via nom explicite P_ProtectedRuntimeMutation_Blocked."""
    assert _is_code_surveillance_objective(_OBJ_CS_C) is True


def test_cs_detection_term_count() -> None:
    """Detection via count >= 2 sans nom explicite."""
    obj = "code surveillance correction_candidate dans periphery."
    assert _is_code_surveillance_objective(obj) is True


def test_cs_no_false_positive_boundary() -> None:
    """_is_code_surveillance_objective doit retourner False pour un objectif boundary."""
    assert _is_code_surveillance_objective(_OBJ_BOUNDARY) is False


def test_cs_no_false_positive_arithmetic() -> None:
    """_is_code_surveillance_objective doit retourner False pour ARITHMETIC."""
    assert _is_code_surveillance_objective(_OBJ_ARITHMETIC) is False


def test_cs_no_false_positive_unknown() -> None:
    """_is_code_surveillance_objective doit retourner False pour UNKNOWN."""
    assert _is_code_surveillance_objective(_OBJ_UNKNOWN) is False


# ===========================================================================
# Groupe 2 — Classification Lean
# ===========================================================================

def test_cs_classify_a() -> None:
    """Objectif A doit etre classe CODE_SURVEILLANCE."""
    cap = _classify_lean_capability(_OBJ_CS_A)
    assert cap["lean_capability_class"] == "CODE_SURVEILLANCE", (
        f"Attendu CODE_SURVEILLANCE, obtenu {cap['lean_capability_class']}"
    )


def test_cs_classify_b() -> None:
    """Objectif B doit etre classe CODE_SURVEILLANCE."""
    cap = _classify_lean_capability(_OBJ_CS_B)
    assert cap["lean_capability_class"] == "CODE_SURVEILLANCE", (
        f"Attendu CODE_SURVEILLANCE, obtenu {cap['lean_capability_class']}"
    )


def test_cs_classify_c() -> None:
    """Objectif C doit etre classe CODE_SURVEILLANCE."""
    cap = _classify_lean_capability(_OBJ_CS_C)
    assert cap["lean_capability_class"] == "CODE_SURVEILLANCE", (
        f"Attendu CODE_SURVEILLANCE, obtenu {cap['lean_capability_class']}"
    )


# ===========================================================================
# Groupe 3 — Contenu genere : theoreme A
# ===========================================================================

def test_cs_a_theorem_name() -> None:
    """Le moteur doit generer theorem P_ObsidureCodeSurveillance_NonSovereign."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureCodeSurveillance_NonSovereign",
        objective=_OBJ_CS_A,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_ObsidureCodeSurveillance_NonSovereign" in content


def test_cs_a_namespace() -> None:
    """Le contenu A doit utiliser namespace ObsidureCodeSurveillance."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureCodeSurveillance_NonSovereign",
        objective=_OBJ_CS_A,
        attempt=1,
        error_contexts=[],
    )
    assert "namespace ObsidureCodeSurveillance" in content
    assert "namespace P38" not in content


def test_cs_a_structure() -> None:
    """Le contenu A doit contenir CodeSurveillanceOutput."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureCodeSurveillance_NonSovereign",
        objective=_OBJ_CS_A,
        attempt=1,
        error_contexts=[],
    )
    assert "CodeSurveillanceOutput" in content


def test_cs_a_non_sovereign_predicate() -> None:
    """Le contenu A doit contenir la definition nonSovereign."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureCodeSurveillance_NonSovereign",
        objective=_OBJ_CS_A,
        attempt=1,
        error_contexts=[],
    )
    assert "nonSovereign" in content


def test_cs_a_no_forbidden() -> None:
    """Le contenu A ne doit pas contenir de mot-cle interdit."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureCodeSurveillance_NonSovereign",
        objective=_OBJ_CS_A,
        attempt=1,
        error_contexts=[],
    )
    cl = content.lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in cl, f"Mot-cle interdit '{kw}' trouve dans le contenu A"


def test_cs_a_no_p38() -> None:
    """Le contenu A ne doit pas contenir de marqueur P38."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureCodeSurveillance_NonSovereign",
        objective=_OBJ_CS_A,
        attempt=1,
        error_contexts=[],
    )
    for marker in _P38_MARKERS:
        assert marker not in content, f"Marqueur P38 '{marker}' trouve dans le contenu A"


# ===========================================================================
# Groupe 4 — Contenu genere : theoreme B
# ===========================================================================

def test_cs_b_theorem_name() -> None:
    """Le moteur doit generer theorem P_CandidateCorrection_RequiresValidation."""
    content = _build_lean_variant(
        theorem_id="P_CandidateCorrection_RequiresValidation",
        objective=_OBJ_CS_B,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_CandidateCorrection_RequiresValidation" in content


def test_cs_b_requires_validation() -> None:
    """Le contenu B doit contenir requiresValidation."""
    content = _build_lean_variant(
        theorem_id="P_CandidateCorrection_RequiresValidation",
        objective=_OBJ_CS_B,
        attempt=1,
        error_contexts=[],
    )
    assert "requiresValidation" in content


def test_cs_b_no_forbidden() -> None:
    """Le contenu B ne doit pas contenir de mot-cle interdit."""
    content = _build_lean_variant(
        theorem_id="P_CandidateCorrection_RequiresValidation",
        objective=_OBJ_CS_B,
        attempt=1,
        error_contexts=[],
    )
    cl = content.lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in cl, f"Mot-cle interdit '{kw}' trouve dans le contenu B"


def test_cs_b_no_p38() -> None:
    """Le contenu B ne doit pas contenir de marqueur P38."""
    content = _build_lean_variant(
        theorem_id="P_CandidateCorrection_RequiresValidation",
        objective=_OBJ_CS_B,
        attempt=1,
        error_contexts=[],
    )
    for marker in _P38_MARKERS:
        assert marker not in content, f"Marqueur P38 '{marker}' trouve dans le contenu B"


# ===========================================================================
# Groupe 5 — Contenu genere : theoreme C
# ===========================================================================

def test_cs_c_theorem_name() -> None:
    """Le moteur doit generer theorem P_ProtectedRuntimeMutation_Blocked."""
    content = _build_lean_variant(
        theorem_id="P_ProtectedRuntimeMutation_Blocked",
        objective=_OBJ_CS_C,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_ProtectedRuntimeMutation_Blocked" in content


def test_cs_c_protected_mutation_blocked() -> None:
    """Le contenu C doit contenir protectedMutationBlocked."""
    content = _build_lean_variant(
        theorem_id="P_ProtectedRuntimeMutation_Blocked",
        objective=_OBJ_CS_C,
        attempt=1,
        error_contexts=[],
    )
    assert "protectedMutationBlocked" in content


def test_cs_c_no_forbidden() -> None:
    """Le contenu C ne doit pas contenir de mot-cle interdit."""
    content = _build_lean_variant(
        theorem_id="P_ProtectedRuntimeMutation_Blocked",
        objective=_OBJ_CS_C,
        attempt=1,
        error_contexts=[],
    )
    cl = content.lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in cl, f"Mot-cle interdit '{kw}' trouve dans le contenu C"


def test_cs_c_no_p38() -> None:
    """Le contenu C ne doit pas contenir de marqueur P38."""
    content = _build_lean_variant(
        theorem_id="P_ProtectedRuntimeMutation_Blocked",
        objective=_OBJ_CS_C,
        attempt=1,
        error_contexts=[],
    )
    for marker in _P38_MARKERS:
        assert marker not in content, f"Marqueur P38 '{marker}' trouve dans le contenu C"


# ===========================================================================
# Groupe 6 — Isolation strategie (ne capture pas boundary ni autres)
# ===========================================================================

def test_cs_boundary_not_captured_by_cs() -> None:
    """_is_code_surveillance_objective ne doit pas capturer l'objectif boundary."""
    assert _is_code_surveillance_objective(_OBJ_BOUNDARY) is False


def test_cs_boundary_theorem_absent_from_cs() -> None:
    """LeanMutationEngine ne doit pas generer ObsidureCodeSurveillance pour boundary."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    assert "ObsidureCodeSurveillance" not in content


def test_cs_content_not_generated_for_arithmetic() -> None:
    """LeanMutationEngine ne doit pas generer ObsidureCodeSurveillance pour ARITHMETIC."""
    content = _build_lean_variant(
        theorem_id="P_Arith",
        objective=_OBJ_ARITHMETIC,
        attempt=1,
        error_contexts=[],
    )
    assert "ObsidureCodeSurveillance" not in content


def test_cs_content_not_generated_for_unknown() -> None:
    """LeanMutationEngine ne doit pas generer ObsidureCodeSurveillance pour UNKNOWN."""
    content = _build_lean_variant(
        theorem_id="P_Unknown",
        objective=_OBJ_UNKNOWN,
        attempt=1,
        error_contexts=[],
    )
    assert "ObsidureCodeSurveillance" not in content


# ===========================================================================
# Groupe 7 — Sorry guard actif
# ===========================================================================

def test_sorry_guard_cs_a() -> None:
    """Le contenu A ne doit pas passer le sorry guard de LeanMutationEngine."""
    engine = LeanMutationEngine()
    content = _build_lean_variant(
        theorem_id="P_ObsidureCodeSurveillance_NonSovereign",
        objective=_OBJ_CS_A,
        attempt=1,
        error_contexts=[],
    )
    assert not engine.SORRY_PATTERN.search(content), (
        "SORRY detecte dans le contenu CODE_SURVEILLANCE A"
    )


def test_sorry_guard_cs_b() -> None:
    """Le contenu B ne doit pas passer le sorry guard de LeanMutationEngine."""
    engine = LeanMutationEngine()
    content = _build_lean_variant(
        theorem_id="P_CandidateCorrection_RequiresValidation",
        objective=_OBJ_CS_B,
        attempt=1,
        error_contexts=[],
    )
    assert not engine.SORRY_PATTERN.search(content), (
        "SORRY detecte dans le contenu CODE_SURVEILLANCE B"
    )


def test_sorry_guard_cs_c() -> None:
    """Le contenu C ne doit pas passer le sorry guard de LeanMutationEngine."""
    engine = LeanMutationEngine()
    content = _build_lean_variant(
        theorem_id="P_ProtectedRuntimeMutation_Blocked",
        objective=_OBJ_CS_C,
        attempt=1,
        error_contexts=[],
    )
    assert not engine.SORRY_PATTERN.search(content), (
        "SORRY detecte dans le contenu CODE_SURVEILLANCE C"
    )


# ===========================================================================
# Groupe 8 — Lean compile check (si lake disponible)
# ===========================================================================

def _run_lake_lean(content: str, filename: str) -> subprocess.CompletedProcess:
    lean_cwd = _REPO_ROOT / "proofs" / "lean"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_lean = Path(tmpdir) / filename
        tmp_lean.write_text(content, encoding="utf-8")
        return subprocess.run(
            [shutil.which("lake"), "env", "lean", str(tmp_lean)],
            cwd=str(lean_cwd),
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace",
        )


def test_cs_a_lean_compiles() -> None:
    """P_ObsidureCodeSurveillance_NonSovereign doit compiler avec lake env lean."""
    if not shutil.which("lake"):
        return
    content = _build_lean_variant(
        theorem_id="P_ObsidureCodeSurveillance_NonSovereign",
        objective=_OBJ_CS_A,
        attempt=1,
        error_contexts=[],
    )
    result = _run_lake_lean(content, "P_ObsidureCodeSurveillance_NonSovereign_test.lean")
    assert result.returncode == 0, (
        f"lake env lean A echec (rc={result.returncode}):\n"
        f"stderr: {result.stderr[:400]}"
    )


def test_cs_b_lean_compiles() -> None:
    """P_CandidateCorrection_RequiresValidation doit compiler avec lake env lean."""
    if not shutil.which("lake"):
        return
    content = _build_lean_variant(
        theorem_id="P_CandidateCorrection_RequiresValidation",
        objective=_OBJ_CS_B,
        attempt=1,
        error_contexts=[],
    )
    result = _run_lake_lean(content, "P_CandidateCorrection_RequiresValidation_test.lean")
    assert result.returncode == 0, (
        f"lake env lean B echec (rc={result.returncode}):\n"
        f"stderr: {result.stderr[:400]}"
    )


def test_cs_c_lean_compiles() -> None:
    """P_ProtectedRuntimeMutation_Blocked doit compiler avec lake env lean."""
    if not shutil.which("lake"):
        return
    content = _build_lean_variant(
        theorem_id="P_ProtectedRuntimeMutation_Blocked",
        objective=_OBJ_CS_C,
        attempt=1,
        error_contexts=[],
    )
    result = _run_lake_lean(content, "P_ProtectedRuntimeMutation_Blocked_test.lean")
    assert result.returncode == 0, (
        f"lake env lean C echec (rc={result.returncode}):\n"
        f"stderr: {result.stderr[:400]}"
    )


# ===========================================================================
# Groupe 9 — Alignement classifier : CODE_SURVEILLANCE_EXPLICIT > BOUNDARY
# Non-regression BOUNDARY_NON_SOVEREIGNTY
# ===========================================================================

# Objectif C tel qu'utilise dans le proposal reel (contient KX108_ONLY)
_OBJ_CS_C_KX108 = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_ProtectedRuntimeMutation_Blocked.lean. "
    "Theoreme cible : P_ProtectedRuntimeMutation_Blocked. "
    "Objectif : mutation runtime/kernel protegee bloquee par surveillance code. "
    "Termes critiques : protected infix, runtime mutation=false, kernel mutation=false, "
    "KX108_ONLY, no memory write. "
    "Aucun apply. Aucun commit. Aucun sorry/admit/axiom/unsafe."
)

# Objectif BOUNDARY avec KX108 — non-regression
_OBJ_BOUNDARY_FULL = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_ObsidureBoundary_NonDecision.lean. "
    "Theoreme cible : P_ObsidureBoundary_NonDecision. "
    "Termes critiques : Boundary, NonDecision, allowed_to_decide=false, "
    "emits_act=false, kernel_mutation=false, KX108_ONLY."
)


def test_cs_c_kx108_classify_code_surveillance() -> None:
    """P_ProtectedRuntimeMutation_Blocked avec KX108_ONLY doit rester CODE_SURVEILLANCE.

    Regression apres OBSIDURE_CODE_SURVEILLANCE_CLASSIFIER_ALIGNMENT_V1 :
    l'ID explicite doit prendre la priorite sur le terme generique KX108.
    """
    cap = _classify_lean_capability(_OBJ_CS_C_KX108)
    assert cap["lean_capability_class"] == "CODE_SURVEILLANCE", (
        f"Attendu CODE_SURVEILLANCE meme avec KX108_ONLY, "
        f"obtenu {cap['lean_capability_class']}"
    )
    assert cap["confidence"] == "HIGH", (
        f"Attendu HIGH, obtenu {cap['confidence']}"
    )
    assert cap["recommended_strategy_family"] == "CODE_SURVEILLANCE_TEMPLATE", (
        f"Attendu CODE_SURVEILLANCE_TEMPLATE, "
        f"obtenu {cap['recommended_strategy_family']}"
    )


def test_cs_c_kx108_is_code_surveillance_not_boundary() -> None:
    """_is_code_surveillance_objective doit etre True, _is_boundary_objective False."""
    assert _is_code_surveillance_objective(_OBJ_CS_C_KX108) is True
    assert _is_boundary_objective(_OBJ_CS_C_KX108) is False


def test_boundary_non_regression_with_kx108() -> None:
    """P_ObsidureBoundary_NonDecision avec Boundary/KX108/NonDecision doit rester
    NON_SOVEREIGNTY ou BOUNDARY avec strategie BOUNDARY_NON_SOVEREIGNTY.

    Verifie que la correction CLASSIFIER_ALIGNMENT_V1 n'affaiblit pas la detection
    des theoremes boundary existants.
    """
    cap = _classify_lean_capability(_OBJ_BOUNDARY_FULL)
    assert cap["lean_capability_class"] in ("NON_SOVEREIGNTY", "BOUNDARY"), (
        f"Attendu NON_SOVEREIGNTY ou BOUNDARY, "
        f"obtenu {cap['lean_capability_class']}"
    )
    assert cap["recommended_strategy_family"] == "BOUNDARY_NON_SOVEREIGNTY", (
        f"Attendu BOUNDARY_NON_SOVEREIGNTY, "
        f"obtenu {cap['recommended_strategy_family']}"
    )
