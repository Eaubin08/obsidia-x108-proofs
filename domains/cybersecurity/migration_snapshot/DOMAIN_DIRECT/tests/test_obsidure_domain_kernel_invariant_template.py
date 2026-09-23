"""
test_obsidure_domain_kernel_invariant_template.py
Suite de tests — stratégie DOMAIN_KERNEL_INVARIANT_TEMPLATE (4e stratégie générative).

Vérifie :
- Classifieur retourne DOMAIN_KERNEL_INVARIANT / HIGH / DOMAIN_KERNEL_INVARIANT_TEMPLATE
  pour les 3 IDs explicites.
- Le contenu généré contient DomainKernelState, le nom exact de chaque théorème.
- Aucun mot-clé interdit (sorry/admit/axiom/unsafe).
- Aucun marqueur P38.
- Isolation : boundary/code-surveillance/memory-invariant/arithmetic/unknown
  ne capturent pas un objectif DK.
- Sorry guard actif (LeanMutationEngine.SORRY_PATTERN).
- Lake env lean disponible ou skip silencieux.

Scope  : OBSIDURE_DOMAIN_KERNEL_INVARIANT_TEMPLATE_V1
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
    _is_domain_kernel_invariant_objective,
    _is_memory_invariant_objective,
)

# ---------------------------------------------------------------------------
# Objectifs de test
# ---------------------------------------------------------------------------

_OBJ_DK_A = (
    "LEAN_SANDBOX. Fichier cible : periphery/lean_sandbox/P_DomainKernel_EntropyRisk_RequiresHold.lean. "
    "Theoreme cible : P_DomainKernel_EntropyRisk_RequiresHold. "
    "Termes critiques : entropy_risk, HOLD, hold_required, domain kernel invariant."
)
_OBJ_DK_B = (
    "LEAN_SANDBOX. Fichier cible : periphery/lean_sandbox/P_DomainKernel_PathFidelity_RequiresCoherence.lean. "
    "Theoreme cible : P_DomainKernel_PathFidelity_RequiresCoherence. "
    "Termes critiques : path_fidelity_ok, coherence_ok, trajectory_admissible."
)
_OBJ_DK_C = (
    "LEAN_SANDBOX. Fichier cible : periphery/lean_sandbox/P_DomainKernel_SignedReceipt_KX108Only.lean. "
    "Theoreme cible : P_DomainKernel_SignedReceipt_KX108Only. "
    "Termes critiques : signed_decision_receipt, kx108_only, KX108_ONLY, decision_receipt."
)

_FORBIDDEN_KEYWORDS = ("sorry", "admit", "axiom", "unsafe")
_P38_MARKERS = ("P38", "Nat.add_comm", "1 + 1 = 2", "n + m = m + n")


# ===========================================================================
# Groupe 1 — détecteur _is_domain_kernel_invariant_objective
# ===========================================================================

def test_dk_detector_a() -> None:
    assert _is_domain_kernel_invariant_objective(_OBJ_DK_A) is True


def test_dk_detector_b() -> None:
    assert _is_domain_kernel_invariant_objective(_OBJ_DK_B) is True


def test_dk_detector_c() -> None:
    assert _is_domain_kernel_invariant_objective(_OBJ_DK_C) is True


# ===========================================================================
# Groupe 2 — classifieur retourne DOMAIN_KERNEL_INVARIANT / HIGH / DOMAIN_KERNEL_INVARIANT_TEMPLATE
# ===========================================================================

def test_dk_classify_a() -> None:
    cap = _classify_lean_capability(_OBJ_DK_A)
    assert cap["lean_capability_class"] == "DOMAIN_KERNEL_INVARIANT", (
        f"Attendu DOMAIN_KERNEL_INVARIANT, obtenu {cap['lean_capability_class']}"
    )
    assert cap["confidence"] == "HIGH"
    assert cap["recommended_strategy_family"] == "DOMAIN_KERNEL_INVARIANT_TEMPLATE"


def test_dk_classify_b() -> None:
    cap = _classify_lean_capability(_OBJ_DK_B)
    assert cap["lean_capability_class"] == "DOMAIN_KERNEL_INVARIANT"
    assert cap["confidence"] == "HIGH"
    assert cap["recommended_strategy_family"] == "DOMAIN_KERNEL_INVARIANT_TEMPLATE"


def test_dk_classify_c_kx108_not_boundary() -> None:
    """KX108_ONLY dans l'objectif C ne doit pas déclencher BOUNDARY."""
    cap = _classify_lean_capability(_OBJ_DK_C)
    assert cap["lean_capability_class"] == "DOMAIN_KERNEL_INVARIANT", (
        f"P_DomainKernel_SignedReceipt_KX108Only doit être DOMAIN_KERNEL_INVARIANT, "
        f"obtenu {cap['lean_capability_class']}"
    )
    assert cap["confidence"] == "HIGH"
    assert cap["recommended_strategy_family"] == "DOMAIN_KERNEL_INVARIANT_TEMPLATE"


def test_dk_classify_requires_human_false() -> None:
    cap = _classify_lean_capability(_OBJ_DK_A)
    assert cap["requires_human_authorized_template"] is False


# ===========================================================================
# Groupe 3 — contenu généré : DomainKernelState présent
# ===========================================================================

def test_dk_content_domain_kernel_state_a() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_EntropyRisk_RequiresHold",
        objective=_OBJ_DK_A,
        attempt=1,
        error_contexts=[],
    )
    assert "DomainKernelState" in content


def test_dk_content_domain_kernel_state_b() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_PathFidelity_RequiresCoherence",
        objective=_OBJ_DK_B,
        attempt=1,
        error_contexts=[],
    )
    assert "DomainKernelState" in content


def test_dk_content_domain_kernel_state_c() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_SignedReceipt_KX108Only",
        objective=_OBJ_DK_C,
        attempt=1,
        error_contexts=[],
    )
    assert "DomainKernelState" in content


# ===========================================================================
# Groupe 4 — nom exact du théorème présent dans le contenu
# ===========================================================================

def test_dk_theorem_name_a() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_EntropyRisk_RequiresHold",
        objective=_OBJ_DK_A,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_DomainKernel_EntropyRisk_RequiresHold" in content


def test_dk_theorem_name_b() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_PathFidelity_RequiresCoherence",
        objective=_OBJ_DK_B,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_DomainKernel_PathFidelity_RequiresCoherence" in content


def test_dk_theorem_name_c() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_SignedReceipt_KX108Only",
        objective=_OBJ_DK_C,
        attempt=1,
        error_contexts=[],
    )
    assert "theorem P_DomainKernel_SignedReceipt_KX108Only" in content


# ===========================================================================
# Groupe 5 — mots-clés interdits absents
# ===========================================================================

def test_dk_no_forbidden_a() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_EntropyRisk_RequiresHold",
        objective=_OBJ_DK_A,
        attempt=1,
        error_contexts=[],
    ).lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in content, f"Mot-clé interdit '{kw}' trouvé (théorème A)"


def test_dk_no_forbidden_b() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_PathFidelity_RequiresCoherence",
        objective=_OBJ_DK_B,
        attempt=1,
        error_contexts=[],
    ).lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in content, f"Mot-clé interdit '{kw}' trouvé (théorème B)"


def test_dk_no_forbidden_c() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_SignedReceipt_KX108Only",
        objective=_OBJ_DK_C,
        attempt=1,
        error_contexts=[],
    ).lower()
    for kw in _FORBIDDEN_KEYWORDS:
        assert kw not in content, f"Mot-clé interdit '{kw}' trouvé (théorème C)"


# ===========================================================================
# Groupe 6 — marqueurs P38 absents
# ===========================================================================

def test_dk_no_p38_a() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_EntropyRisk_RequiresHold",
        objective=_OBJ_DK_A,
        attempt=1,
        error_contexts=[],
    )
    for m in _P38_MARKERS:
        assert m not in content, f"Marqueur P38 '{m}' trouvé (théorème A)"


def test_dk_no_p38_c() -> None:
    content = _build_lean_variant(
        theorem_id="P_DomainKernel_SignedReceipt_KX108Only",
        objective=_OBJ_DK_C,
        attempt=1,
        error_contexts=[],
    )
    for m in _P38_MARKERS:
        assert m not in content, f"Marqueur P38 '{m}' trouvé (théorème C)"


# ===========================================================================
# Groupe 7 — isolation : les autres stratégies ne capturent pas un objectif DK
# ===========================================================================

def test_dk_isolation_not_boundary() -> None:
    assert _is_boundary_objective(_OBJ_DK_A) is False
    assert _is_boundary_objective(_OBJ_DK_B) is False


def test_dk_isolation_c_not_boundary() -> None:
    """Objectif C contient KX108_ONLY — ne doit pas être boundary."""
    assert _is_boundary_objective(_OBJ_DK_C) is False


def test_dk_isolation_not_code_surveillance() -> None:
    assert _is_code_surveillance_objective(_OBJ_DK_A) is False
    assert _is_code_surveillance_objective(_OBJ_DK_B) is False
    assert _is_code_surveillance_objective(_OBJ_DK_C) is False


def test_dk_isolation_not_memory_invariant() -> None:
    assert _is_memory_invariant_objective(_OBJ_DK_A) is False
    assert _is_memory_invariant_objective(_OBJ_DK_B) is False
    assert _is_memory_invariant_objective(_OBJ_DK_C) is False


# ===========================================================================
# Groupe 8 — sorry guard actif
# ===========================================================================

def test_dk_sorry_guard() -> None:
    engine = LeanMutationEngine()
    for tid, obj in [
        ("P_DomainKernel_EntropyRisk_RequiresHold", _OBJ_DK_A),
        ("P_DomainKernel_PathFidelity_RequiresCoherence", _OBJ_DK_B),
        ("P_DomainKernel_SignedReceipt_KX108Only", _OBJ_DK_C),
    ]:
        content = _build_lean_variant(theorem_id=tid, objective=obj, attempt=1, error_contexts=[])
        assert not engine.SORRY_PATTERN.search(content), (
            f"SORRY détecté dans le contenu DK pour {tid}"
        )


# ===========================================================================
# Groupe 9 — lake env lean (si disponible)
# ===========================================================================

def _lean_check(theorem_id: str, objective: str) -> None:
    lake_path = shutil.which("lake")
    if not lake_path:
        return  # skip silencieux si lake absent

    content = _build_lean_variant(
        theorem_id=theorem_id,
        objective=objective,
        attempt=1,
        error_contexts=[],
    )
    lean_cwd = _REPO_ROOT / "proofs" / "lean"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_lean = Path(tmpdir) / f"{theorem_id}_dktest.lean"
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
            f"lake env lean a échoué pour {theorem_id} (rc={result.returncode}):\n"
            f"stderr: {result.stderr[:400]}\nstdout: {result.stdout[:200]}"
        )


def test_dk_lean_a() -> None:
    _lean_check("P_DomainKernel_EntropyRisk_RequiresHold", _OBJ_DK_A)


def test_dk_lean_b() -> None:
    _lean_check("P_DomainKernel_PathFidelity_RequiresCoherence", _OBJ_DK_B)


def test_dk_lean_c() -> None:
    _lean_check("P_DomainKernel_SignedReceipt_KX108Only", _OBJ_DK_C)
