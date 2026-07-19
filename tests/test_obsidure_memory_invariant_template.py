"""
test_obsidure_memory_invariant_template.py
Matrice de tests — strategie MEMORY_INVARIANT_TEMPLATE.

Verifie :
  - Detection correcte des objectifs memory invariant readonly
  - Generation des 3 theoremes V1 (P_MemoryWriteInvariant_Readonly,
    P_GraphitiReadonly_NoWrite, P_CanonicalMemoryWrite_Blocked)
  - Isolation stricte de la strategie (ne capture pas boundary / code surveillance
    / arithmetic / unknown)
  - Absence de sorry/admit/axiom/unsafe dans le contenu genere
  - Absence de marqueurs P38
  - Namespace correct (ObsidureMemoryInvariant)
  - Classifier MEMORY_INVARIANT / HIGH / MEMORY_INVARIANT_TEMPLATE

Scope : OBSIDURE_MEMORY_INVARIANT_TEMPLATE_V1
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
    _is_memory_invariant_objective,
)

# ---------------------------------------------------------------------------
# Objectifs de test
# ---------------------------------------------------------------------------

_OBJ_MI_A = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_MemoryWriteInvariant_Readonly.lean. "
    "Theoreme cible : P_MemoryWriteInvariant_Readonly. "
    "Objectif : invariant memoire readonly, memory_write=false et readonly=true. "
    "Termes critiques : MEMORY_READONLY, Graphiti readonly, memory_write=false, "
    "canonical_memory_write=false, attestation only. "
    "Aucun apply. Aucun commit. Aucun sorry/admit/axiom/unsafe."
)

_OBJ_MI_B = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_GraphitiReadonly_NoWrite.lean. "
    "Theoreme cible : P_GraphitiReadonly_NoWrite. "
    "Objectif : Graphiti readonly interdit toute ecriture Graphiti. "
    "Termes critiques : Graphiti, readonly, graphiti_write=false, "
    "memory_write=false, MEMORY_READONLY. "
    "Aucun apply. Aucun commit. Aucun sorry/admit/axiom/unsafe."
)

_OBJ_MI_C = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_CanonicalMemoryWrite_Blocked.lean. "
    "Theoreme cible : P_CanonicalMemoryWrite_Blocked. "
    "Objectif : canonical_memory_write=false, ecriture memoire canonique bloquee. "
    "Termes critiques : canonical_memory_write=false, memory_write=false, "
    "readonly, attestation only, no canonical memory write. "
    "Aucun apply. Aucun commit. Aucun sorry/admit/axiom/unsafe."
)

_OBJ_BOUNDARY = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_ObsidureBoundary_NonDecision.lean. "
    "Theoreme cible : P_ObsidureBoundary_NonDecision. "
    "Termes critiques : Boundary, NonDecision, allowed_to_decide=false, "
    "emits_act=false, kernel_mutation=false, KX108_ONLY."
)

_OBJ_CS = (
    "LEAN_SANDBOX. Fichier cible : "
    "periphery/lean_sandbox/P_ObsidureCodeSurveillance_NonSovereign.lean. "
    "Theoreme cible : P_ObsidureCodeSurveillance_NonSovereign. "
    "Termes : code surveillance, applies_patch=false, HUMAN_APPROVED_WRITE."
)

_OBJ_ARITHMETIC = "Nat arithmetic rfl — propriete sur Nat.add_zero."
_OBJ_UNKNOWN = "Reorganiser les sessions SRL par anciennete."

_FORBIDDEN_KEYWORDS = ("sorry", "admit", "axiom", "unsafe")
_P38_MARKERS = ("P38", "Nat.add_comm", "1 + 1 = 2", "n + m = m + n")


# ===========================================================================
# Groupe 1 — Detection _is_memory_invariant_objective
# ===========================================================================

def test_mi_detection_explicit_a() -> None:
    """Detection via nom explicite P_MemoryWriteInvariant_Readonly."""
    assert _is_memory_invariant_objective(_OBJ_MI_A) is True


def test_mi_detection_explicit_b() -> None:
    """Detection via nom explicite P_GraphitiReadonly_NoWrite."""
    assert _is_memory_invariant_objective(_OBJ_MI_B) is True


def test_mi_detection_explicit_c() -> None:
    """Detection via nom explicite P_CanonicalMemoryWrite_Blocked."""
    assert _is_memory_invariant_objective(_OBJ_MI_C) is True


def test_mi_detection_term_count() -> None:
    """Detection via count >= 2 sans nom explicite."""
    obj = "memory_write=false, readonly invariant absolu."
    assert _is_memory_invariant_objective(obj) is True


def test_mi_no_false_positive_boundary() -> None:
    """_is_memory_invariant_objective doit retourner False pour BOUNDARY."""
    assert _is_memory_invariant_objective(_OBJ_BOUNDARY) is False


def test_mi_no_false_positive_cs() -> None:
    """_is_memory_invariant_objective doit retourner False pour CODE_SURVEILLANCE."""
    assert _is_memory_invariant_objective(_OBJ_CS) is False


def test_mi_no_false_positive_arithmetic() -> None:
    """_is_memory_invariant_objective doit retourner False pour ARITHMETIC."""
    assert _is_memory_invariant_objective(_OBJ_ARITHMETIC) is False


def test_mi_no_false_positive_unknown() -> None:
    """_is_memory_invariant_objective doit retourner False pour UNKNOWN."""
    assert _is_memory_invariant_objective(_OBJ_UNKNOWN) is False


# ===========================================================================
# Groupe 2 — Classification Lean
# ===========================================================================

def test_mi_classify_a() -> None:
    """Objectif A doit etre classe MEMORY_INVARIANT / HIGH / MEMORY_INVARIANT_TEMPLATE."""
    cap = _classify_lean_capability(_OBJ_MI_A)
    assert cap["lean_capability_class"] == "MEMORY_INVARIANT", (
        f"Attendu MEMORY_INVARIANT, obtenu {cap['lean_capability_class']}"
    )
    assert cap["confidence"] == "HIGH"
    assert cap["recommended_strategy_family"] == "MEMORY_INVARIANT_TEMPLATE"


def test_mi_classify_b() -> None:
    """Objectif B doit etre classe MEMORY_INVARIANT / HIGH / MEMORY_INVARIANT_TEMPLATE."""
    cap = _classify_lean_capability(_OBJ_MI_B)
    assert cap["lean_capability_class"] == "MEMORY_INVARIANT"
    assert cap["confidence"] == "HIGH"
    assert cap["recommended_strategy_family"] == "MEMORY_INVARIANT_TEMPLATE"


def test_mi_classify_c() -> None:
    """Objectif C doit etre classe MEMORY_INVARIANT / HIGH / MEMORY_INVARIANT_TEMPLATE."""
    cap = _classify_lean_capability(_OBJ_MI_C)
    assert cap["lean_capability_class"] == "MEMORY_INVARIANT"
    assert cap["confidence"] == "HIGH"
    assert cap["recommended_strategy_family"] == "MEMORY_INVARIANT_TEMPLATE"


# ===========================================================================
# Groupe 3 — Contenu genere : theoreme A
# ===========================================================================

def test_mi_a_theorem_name() -> None:
    """Le moteur doit generer theorem P_MemoryWriteInvariant_Readonly."""
    content = _build_lean_variant(
        theorem_id="P_MemoryWriteInvariant_Readonly",
        objective=_OBJ_MI_A,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_MemoryWriteInvariant_Readonly" in content


def test_mi_a_memory_boundary_state() -> None:
    """Le contenu A doit contenir MemoryBoundaryState."""
    content = _build_lean_variant(
        theorem_id="P_MemoryWriteInvariant_Readonly",
        objective=_OBJ_MI_A,
        attempt=1,
        error_contexts=[],
    )
    assert "MemoryBoundaryState" in content


def test_mi_a_namespace() -> None:
    """Le contenu A doit utiliser namespace ObsidureMemoryInvariant."""
    content = _build_lean_variant(
        theorem_id="P_MemoryWriteInvariant_Readonly",
        objective=_OBJ_MI_A,
        attempt=1,
        error_contexts=[],
    )
    assert "namespace ObsidureMemoryInvariant" in content
    assert "namespace P38" not in content


def test_mi_a_memory_readonly_predicate() -> None:
    """Le contenu A doit contenir memoryReadonly."""
    content = _build_lean_variant(
        theorem_id="P_MemoryWriteInvariant_Readonly",
        objective=_OBJ_MI_A,
        attempt=1,
        error_contexts=[],
    )
    assert "memoryReadonly" in content


def test_mi_a_no_forbidden() -> None:
    """Le contenu A ne doit contenir aucun mot-cle interdit."""
    content = _build_lean_variant(
        theorem_id="P_MemoryWriteInvariant_Readonly",
        objective=_OBJ_MI_A,
        attempt=1,
        error_contexts=[],
    )
    cl = content.lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in cl, f"Mot-cle interdit '{kw}' dans le contenu A"


def test_mi_a_no_p38() -> None:
    """Le contenu A ne doit pas contenir de marqueur P38."""
    content = _build_lean_variant(
        theorem_id="P_MemoryWriteInvariant_Readonly",
        objective=_OBJ_MI_A,
        attempt=1,
        error_contexts=[],
    )
    for marker in _P38_MARKERS:
        assert marker not in content, f"Marqueur P38 '{marker}' dans le contenu A"


# ===========================================================================
# Groupe 4 — Contenu genere : theoreme B
# ===========================================================================

def test_mi_b_theorem_name() -> None:
    """Le moteur doit generer theorem P_GraphitiReadonly_NoWrite."""
    content = _build_lean_variant(
        theorem_id="P_GraphitiReadonly_NoWrite",
        objective=_OBJ_MI_B,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_GraphitiReadonly_NoWrite" in content


def test_mi_b_graphiti_readonly_predicate() -> None:
    """Le contenu B doit contenir graphitiReadonly."""
    content = _build_lean_variant(
        theorem_id="P_GraphitiReadonly_NoWrite",
        objective=_OBJ_MI_B,
        attempt=1,
        error_contexts=[],
    )
    assert "graphitiReadonly" in content


def test_mi_b_no_forbidden() -> None:
    """Le contenu B ne doit contenir aucun mot-cle interdit."""
    content = _build_lean_variant(
        theorem_id="P_GraphitiReadonly_NoWrite",
        objective=_OBJ_MI_B,
        attempt=1,
        error_contexts=[],
    )
    cl = content.lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in cl, f"Mot-cle interdit '{kw}' dans le contenu B"


def test_mi_b_no_p38() -> None:
    """Le contenu B ne doit pas contenir de marqueur P38."""
    content = _build_lean_variant(
        theorem_id="P_GraphitiReadonly_NoWrite",
        objective=_OBJ_MI_B,
        attempt=1,
        error_contexts=[],
    )
    for marker in _P38_MARKERS:
        assert marker not in content, f"Marqueur P38 '{marker}' dans le contenu B"


# ===========================================================================
# Groupe 5 — Contenu genere : theoreme C
# ===========================================================================

def test_mi_c_theorem_name() -> None:
    """Le moteur doit generer theorem P_CanonicalMemoryWrite_Blocked."""
    content = _build_lean_variant(
        theorem_id="P_CanonicalMemoryWrite_Blocked",
        objective=_OBJ_MI_C,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_CanonicalMemoryWrite_Blocked" in content


def test_mi_c_no_memory_write_predicate() -> None:
    """Le contenu C doit contenir noMemoryWrite."""
    content = _build_lean_variant(
        theorem_id="P_CanonicalMemoryWrite_Blocked",
        objective=_OBJ_MI_C,
        attempt=1,
        error_contexts=[],
    )
    assert "noMemoryWrite" in content


def test_mi_c_no_forbidden() -> None:
    """Le contenu C ne doit contenir aucun mot-cle interdit."""
    content = _build_lean_variant(
        theorem_id="P_CanonicalMemoryWrite_Blocked",
        objective=_OBJ_MI_C,
        attempt=1,
        error_contexts=[],
    )
    cl = content.lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in cl, f"Mot-cle interdit '{kw}' dans le contenu C"


def test_mi_c_no_p38() -> None:
    """Le contenu C ne doit pas contenir de marqueur P38."""
    content = _build_lean_variant(
        theorem_id="P_CanonicalMemoryWrite_Blocked",
        objective=_OBJ_MI_C,
        attempt=1,
        error_contexts=[],
    )
    for marker in _P38_MARKERS:
        assert marker not in content, f"Marqueur P38 '{marker}' dans le contenu C"


# ===========================================================================
# Groupe 6 — Isolation strategie
# ===========================================================================

def test_mi_boundary_not_captured() -> None:
    """_is_memory_invariant_objective ne doit pas capturer l'objectif boundary."""
    assert _is_memory_invariant_objective(_OBJ_BOUNDARY) is False


def test_mi_boundary_theorem_absent() -> None:
    """BOUNDARY genere ObsidureBoundary, pas ObsidureMemoryInvariant."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    assert "ObsidureMemoryInvariant" not in content
    assert "ObsidureBoundary" in content


def test_mi_cs_not_captured() -> None:
    """_is_memory_invariant_objective ne doit pas capturer CODE_SURVEILLANCE."""
    assert _is_memory_invariant_objective(_OBJ_CS) is False


def test_mi_cs_theorem_absent() -> None:
    """CODE_SURVEILLANCE genere ObsidureCodeSurveillance, pas ObsidureMemoryInvariant."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureCodeSurveillance_NonSovereign",
        objective=_OBJ_CS,
        attempt=1,
        error_contexts=[],
    )
    assert "ObsidureMemoryInvariant" not in content
    assert "ObsidureCodeSurveillance" in content


def test_mi_not_generated_for_arithmetic() -> None:
    """ARITHMETIC ne doit pas generer ObsidureMemoryInvariant."""
    content = _build_lean_variant(
        theorem_id="P_Arith",
        objective=_OBJ_ARITHMETIC,
        attempt=1,
        error_contexts=[],
    )
    assert "ObsidureMemoryInvariant" not in content


def test_mi_not_generated_for_unknown() -> None:
    """UNKNOWN ne doit pas generer ObsidureMemoryInvariant."""
    content = _build_lean_variant(
        theorem_id="P_Unknown",
        objective=_OBJ_UNKNOWN,
        attempt=1,
        error_contexts=[],
    )
    assert "ObsidureMemoryInvariant" not in content


# ===========================================================================
# Groupe 7 — Sorry guard actif
# ===========================================================================

def test_sorry_guard_mi_a() -> None:
    """Le contenu A ne doit pas passer le sorry guard."""
    engine = LeanMutationEngine()
    content = _build_lean_variant(
        theorem_id="P_MemoryWriteInvariant_Readonly",
        objective=_OBJ_MI_A,
        attempt=1,
        error_contexts=[],
    )
    assert not engine.SORRY_PATTERN.search(content)


def test_sorry_guard_mi_b() -> None:
    """Le contenu B ne doit pas passer le sorry guard."""
    engine = LeanMutationEngine()
    content = _build_lean_variant(
        theorem_id="P_GraphitiReadonly_NoWrite",
        objective=_OBJ_MI_B,
        attempt=1,
        error_contexts=[],
    )
    assert not engine.SORRY_PATTERN.search(content)


def test_sorry_guard_mi_c() -> None:
    """Le contenu C ne doit pas passer le sorry guard."""
    engine = LeanMutationEngine()
    content = _build_lean_variant(
        theorem_id="P_CanonicalMemoryWrite_Blocked",
        objective=_OBJ_MI_C,
        attempt=1,
        error_contexts=[],
    )
    assert not engine.SORRY_PATTERN.search(content)


# ===========================================================================
# Groupe 8 — BOUNDARY_NON_SOVEREIGNTY non affaibli
# ===========================================================================

def test_boundary_non_regression() -> None:
    """P_ObsidureBoundary_NonDecision doit rester NON_SOVEREIGNTY ou BOUNDARY."""
    cap = _classify_lean_capability(_OBJ_BOUNDARY)
    assert cap["lean_capability_class"] in ("NON_SOVEREIGNTY", "BOUNDARY")
    assert cap["recommended_strategy_family"] == "BOUNDARY_NON_SOVEREIGNTY"


def test_boundary_strategy_not_overridden_by_mi() -> None:
    """BOUNDARY_NON_SOVEREIGNTY ne doit pas etre remplace par MEMORY_INVARIANT_TEMPLATE."""
    content = _build_lean_variant(
        theorem_id="P_ObsidureBoundary_NonDecision",
        objective=_OBJ_BOUNDARY,
        attempt=1,
        error_contexts=[],
    )
    assert "BoundaryState" in content
    assert "MemoryBoundaryState" not in content


# ===========================================================================
# Groupe 9 — Lean compile check (si lake disponible)
# ===========================================================================

def _run_lake_lean(content: str, filename: str) -> subprocess.CompletedProcess:
    lake_path = shutil.which("lake")
    lean_cwd = _REPO_ROOT / "proofs" / "lean"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_lean = Path(tmpdir) / filename
        tmp_lean.write_text(content, encoding="utf-8")
        return subprocess.run(
            [lake_path, "env", "lean", str(tmp_lean)],
            cwd=str(lean_cwd),
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace",
        )


def test_mi_a_lean_compiles() -> None:
    """P_MemoryWriteInvariant_Readonly doit compiler avec lake env lean."""
    if not shutil.which("lake"):
        return
    content = _build_lean_variant(
        theorem_id="P_MemoryWriteInvariant_Readonly",
        objective=_OBJ_MI_A,
        attempt=1,
        error_contexts=[],
    )
    result = _run_lake_lean(content, "P_MemoryWriteInvariant_Readonly_test.lean")
    assert result.returncode == 0, (
        f"lake env lean A echec (rc={result.returncode}):\n"
        f"stderr: {result.stderr[:400]}"
    )


def test_mi_b_lean_compiles() -> None:
    """P_GraphitiReadonly_NoWrite doit compiler avec lake env lean."""
    if not shutil.which("lake"):
        return
    content = _build_lean_variant(
        theorem_id="P_GraphitiReadonly_NoWrite",
        objective=_OBJ_MI_B,
        attempt=1,
        error_contexts=[],
    )
    result = _run_lake_lean(content, "P_GraphitiReadonly_NoWrite_test.lean")
    assert result.returncode == 0, (
        f"lake env lean B echec (rc={result.returncode}):\n"
        f"stderr: {result.stderr[:400]}"
    )


def test_mi_c_lean_compiles() -> None:
    """P_CanonicalMemoryWrite_Blocked doit compiler avec lake env lean."""
    if not shutil.which("lake"):
        return
    content = _build_lean_variant(
        theorem_id="P_CanonicalMemoryWrite_Blocked",
        objective=_OBJ_MI_C,
        attempt=1,
        error_contexts=[],
    )
    result = _run_lake_lean(content, "P_CanonicalMemoryWrite_Blocked_test.lean")
    assert result.returncode == 0, (
        f"lake env lean C echec (rc={result.returncode}):\n"
        f"stderr: {result.stderr[:400]}"
    )
