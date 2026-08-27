"""
obsidia_governed_write_guard_v0.py
==================================
C2_D_ATOMIC_PRODUCTION_ACTIVATION_V1 — garde d'écriture partagée.

Source de vérité UNIQUE pour :

  - le refus fail-closed de toute mutation du dépôt CANONIQUE par les
    entrypoints d'apply legacy (`AgentObsidure.apply_proposal`,
    `obsidure_bounded_apply.run_bounded_apply`, `obsidure_synth_session`) ;
  - la sûreté lien symbolique / point de reparse Windows d'un chemin et de
    chacun de ses composants parents (source ET cible), réutilisée par
    l'orchestrateur gouverné C2 et par le durcissement de
    `obsidia_content_apply`.

Doctrine gelée (CORRECT_AND_FREEZE_C2_D_ATOMIC_DESIGN_V1 §2, §4) :

    OBSIDIA_GOVERNED_TEST_MODE == "1"  est NÉCESSAIRE mais JAMAIS SUFFISANT.

    LEGACY_TEST_ONLY_CAN_MUTATE_CANONICAL_REPO = FALSE

Aucune variable d'environnement ne peut lever le refus canonique : si la
racine d'écriture EST / contient / est contenue par / est un worktree lié
du dépôt canonique, l'écriture est refusée DUR — même avec
`OBSIDIA_GOVERNED_TEST_MODE=1`.

Ce module ne mute rien. Il n'a AUCUNE capacité d'écriture.
"""
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path
from typing import Iterable, Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Ancres structurelles — jamais dérivées d'un argument d'appelant.
#  * dépôt canonique  : parent de scripts/ (ce fichier vit dans scripts/)
#  * stores canoniques: %LOCALAPPDATA%\Obsidia  (batch_execution / approvals /
#    kx108_decisions / content_apply / test_contract_results / rollback_results
#    / sealed_receipts / sealed_rollback_evidence …)
_CANONICAL_REPO_ROOT = _SCRIPTS_DIR.parent
_CANONICAL_STORES_ROOT = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia"

_TEST_MODE_ENV = "OBSIDIA_GOVERNED_TEST_MODE"

_REPARSE_ATTR = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class LegacyDirectApplyDisabled(RuntimeError):
    """Levée quand un entrypoint d'apply legacy vise le dépôt canonique
    (ou un magasin canonique), ou quand le mode test isolé n'est pas
    intégralement satisfait. Fail-closed : jamais rattrapée en interne
    pour poursuivre l'écriture."""


# ── Sûreté lien / reparse (portable Windows : os.lstat + attribut reparse) ──

def _is_unsafe_link_or_reparse(path: "str | Path") -> bool:
    """True si `path` existe ET est un lien symbolique ou porte l'attribut
    FILE_ATTRIBUTE_REPARSE_POINT (jonction, montage…). Un chemin inexistant
    n'est pas « unsafe » ici — l'existence est gérée séparément par
    l'appelant."""
    try:
        st = os.lstat(str(path))
    except OSError:
        return False
    if stat.S_ISLNK(st.st_mode):
        return True
    return bool(getattr(st, "st_file_attributes", 0) & _REPARSE_ATTR)


def _verify_no_reparse_on_path(
    repo_root: "str | Path", inner_path: "str | Path",
) -> "tuple[bool, Optional[str]]":
    """Chaque composant EXISTANT entre `repo_root` (inclus) et
    `inner_path.parent` (inclus) : aucun lien symbolique / point de reparse.
    `inner_path` doit être sous `repo_root` (littéralement, sans resolve)."""
    root = Path(repo_root).resolve()
    parent = Path(inner_path).parent
    try:
        rel_parts = parent.relative_to(root).parts
    except ValueError:
        return False, "INNER_PATH_PARENT_OUTSIDE_ROOT"
    if _is_unsafe_link_or_reparse(root):
        return False, "ROOT_IS_LINK_OR_REPARSE"
    cur = root
    for part in rel_parts:
        cur = cur / part
        if cur.exists() and _is_unsafe_link_or_reparse(cur):
            return False, f"PARENT_COMPONENT_REPARSE:{cur.name}"
    return True, None


def verify_path_reparse_safe(
    repo_root: "str | Path", inner_path: "str | Path", *, kind: str = "PATH",
) -> "tuple[bool, Optional[str]]":
    """`inner_path` lui-même + tous ses composants parents (jusqu'à
    `repo_root`) doivent être exempts de lien symbolique / reparse.
    `kind` ("SOURCE" | "TARGET" | "PATH") préfixe la raison d'échec."""
    if _is_unsafe_link_or_reparse(inner_path):
        return False, f"{kind}_IS_LINK_OR_REPARSE"
    ok, reason = _verify_no_reparse_on_path(repo_root, inner_path)
    if not ok:
        return False, f"{kind}_{reason}"
    return True, None


# ── Confinement structurel ─────────────────────────────────────────────────

def _is_relative_to(child: Path, ancestor: Path) -> bool:
    try:
        Path(child).resolve().relative_to(Path(ancestor).resolve())
        return True
    except (ValueError, OSError):
        return False


def _same_git_repository(path_a: "str | Path", path_b: "str | Path") -> bool:
    """Délègue à obsidia_content_apply.same_git_repository (git-common-dir).
    Import paresseux pour éviter un cycle au chargement du module."""
    try:
        import obsidia_content_apply as _C
        return bool(_C.same_git_repository(path_a, path_b))
    except Exception:
        # Fail-closed : si on ne peut pas prouver que ce sont des dépôts
        # DISTINCTS, on ne renvoie pas False par défaut ici — l'appelant
        # traite None/erreur comme « ne peut pas garantir l'isolation ».
        return True


def canonical_repo_root() -> Path:
    return _CANONICAL_REPO_ROOT


def is_canonical_write_root(effective_root: "str | Path") -> bool:
    """True si `effective_root` est, contient, est contenu par, ou est un
    worktree Git lié du dépôt canonique Obsidia."""
    canonical = _CANONICAL_REPO_ROOT.resolve()
    try:
        root = Path(effective_root).resolve()
    except OSError:
        return True  # illisible -> fail-closed (traité comme canonique)
    if root == canonical or _is_relative_to(root, canonical) or _is_relative_to(canonical, root):
        return True
    if _same_git_repository(root, canonical):
        return True
    return False


def assert_isolated_non_canonical_write_root(
    effective_root: "str | Path",
    effective_proposals: "str | Path | None" = None,
    *,
    evidence_dir: "str | Path | None" = None,
    results_dir: "str | Path | None" = None,
    execution_dir: "str | Path | None" = None,
    kx108_decision_dir: "str | Path | None" = None,
    extra_store_dirs: Optional[Iterable["str | Path"]] = None,
) -> bool:
    """
    Autorise une écriture legacy UNIQUEMENT vers une racine prouvée
    NON-canonique et isolée. Lève LegacyDirectApplyDisabled sinon.

    TOUTES les conditions requises :
      (a) OBSIDIA_GOVERNED_TEST_MODE == "1"                (nécessaire, jamais suffisant)
      (b) effective_root n'est ni égal, ni sous, ni sur le dépôt canonique
      (c) effective_root n'est pas un worktree Git lié du dépôt canonique
      (d) effective_proposals (si fourni) hors du dépôt canonique ET des stores canoniques
      (e) aucun répertoire d'évidence/résultats/exécution/décision (ni extra) ne résout
          dans le dépôt canonique ou dans les stores canoniques
    """
    if os.environ.get(_TEST_MODE_ENV) != "1":
        raise LegacyDirectApplyDisabled("LEGACY_DIRECT_APPLY_DISABLED")

    canonical = _CANONICAL_REPO_ROOT.resolve()
    try:
        root = Path(effective_root).resolve()
    except OSError as exc:
        raise LegacyDirectApplyDisabled(f"WRITE_ROOT_UNRESOLVABLE:{exc}") from exc

    if root == canonical or _is_relative_to(root, canonical) or _is_relative_to(canonical, root):
        raise LegacyDirectApplyDisabled("REFUSED_CANONICAL_REPO_ROOT")

    if _same_git_repository(root, canonical):
        raise LegacyDirectApplyDisabled("REFUSED_CANONICAL_WORKTREE")

    def _reject_if_canonical(label: str, p: "str | Path | None") -> None:
        if p is None:
            return
        rp = Path(p)
        if _is_relative_to(rp, canonical):
            raise LegacyDirectApplyDisabled(f"REFUSED_CANONICAL_DIR:{label}")
        try:
            if str(_CANONICAL_STORES_ROOT) and _is_relative_to(rp, _CANONICAL_STORES_ROOT):
                raise LegacyDirectApplyDisabled(f"REFUSED_CANONICAL_STORE_DIR:{label}")
        except LegacyDirectApplyDisabled:
            raise
        except Exception:
            pass

    _reject_if_canonical("proposals", effective_proposals)
    _reject_if_canonical("evidence", evidence_dir)
    _reject_if_canonical("results", results_dir)
    _reject_if_canonical("execution", execution_dir)
    _reject_if_canonical("kx108_decision", kx108_decision_dir)
    for d in (extra_store_dirs or ()):
        _reject_if_canonical("extra_store", d)

    return True


def assert_destination_confined(
    effective_root: "str | Path", rel_path: str,
) -> Path:
    """Résout `effective_root / rel_path`, exige le confinement littéral
    sous `effective_root`, et rejette tout composant lien/reparse. Retourne
    le chemin de destination confiné. Lève LegacyDirectApplyDisabled sinon.
    À appeler PAR FICHIER, juste avant la copie."""
    root = Path(effective_root).resolve()
    norm = str(rel_path).replace("\\", "/").strip()
    if not norm or norm.startswith("/") or (len(norm) > 1 and norm[1] == ":") \
            or "*" in norm or "?" in norm:
        raise LegacyDirectApplyDisabled(f"DESTINATION_REJECTED:{rel_path}")
    dst = (root / norm)
    try:
        dst.resolve().relative_to(root)
    except (ValueError, OSError):
        raise LegacyDirectApplyDisabled(f"DESTINATION_ESCAPE:{rel_path}")
    if dst.exists() and dst.is_dir():
        raise LegacyDirectApplyDisabled(f"DESTINATION_IS_DIR:{rel_path}")
    ok, reason = verify_path_reparse_safe(root, dst, kind="DESTINATION")
    if not ok:
        raise LegacyDirectApplyDisabled(f"DESTINATION_PATH_UNSAFE:{reason}")
    return dst
