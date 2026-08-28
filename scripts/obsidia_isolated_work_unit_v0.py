"""
obsidia_isolated_work_unit_v0.py
================================
MINIMAL_AUTONOMOUS_WORK_WIRING_CHECKPOINT_1 — pont stack-natif le PLUS PETIT
entre « action gouvernée unique PROUVÉE » et « unité de travail isolée
stack-native ». Ce module :

  * NE DÉFINIT AUCUNE nouvelle autorité — ni « BoundedMissionAuthority »,
    ni pré-approbation multi-actions, ni sémantique de mission ;
  * NE SÉQUENCE RIEN — une seule action mono-enfant, forme déjà prouvée
    (UPDATE_TARGET_FROM_SOURCE / REPLACE, source GIT_BLOB, cible existante) ;
  * N'IMPLÉMENTE AUCUNE boucle de réparation, AUCUN retry automatique ;
  * N'ÉCRIT JAMAIS une cible de remédiation (aucun open/write/replace/copy) —
    la seule voie de remédiation reste
    `obsidia_governed_execution_driver_v0` -> `run_governed_content_apply` ;
  * NE DUPLIQUE PAS la logique du driver générique (ni Ledger, ni
    BatchProposal, ni PEC hashing, ni ExecutionEnvelope, ni calcul d'EAH,
    ni HumanApproval, ni KX108 PRE/POST, ni C1/C2, ni D1/D2) — il en est
    seulement le PREMIER APPELANT réel ;
  * NE FAIT AUCUNE disposition Git de remédiation
    (add/commit/push/merge/rebase/cherry-pick/stash/reset/checkout) ;
  * possède UNIQUEMENT le cycle de vie *espace de travail* Git :
    `git worktree add` (création) et, symétriquement, `git worktree remove`
    + `git branch -d` (suppression sûre, sans --force) d'un worktree/branche
    que CE module a créés et qui sont prouvablement jetables ;
  * NE PERSISTE AUCUN nouveau modèle d'état — la corrélation prepare<->execute
    passe par les IDs déjà retournés par le driver (batch_execution_id,
    child_execution_id, execution_authority_hash) et les magasins immuables
    existants. `IsolatedWorkUnit` est une poignée en mémoire, jamais écrite.

`decision_authority = KX108_ONLY`. Aucune valeur de confort de l'appelant
n'est jamais traitée comme autorité.

Deux/trois responsabilités distinctes :

  create_isolated_work_unit(...)
    Valide identité dépôt + base_sha + non-conflit de branche + destination
    de worktree vide/absente, PUIS `git worktree add <path> -b <branch>
    <base_sha>` (sans --force), PUIS vérifie les faits Git d'espace de
    travail (enregistré / distinct du main / non-détaché / branche == /
    HEAD == base_sha / arbre propre) via les helpers Git du module PEC
    canonique. En cas d'échec de cette vérification : supprime UNIQUEMENT
    le worktree/branche vides qu'il vient de créer (sans --force).

  prepare_work_unit_execution(...)
    Refuse explicitement toute forme non prouvée (multi-enfant, CREATE,
    DELETE, ARCHIVE, MOVE, RENAME, cible inexistante) AVANT de déléguer.
    Appelle `prepare_governed_execution(...)` — qui produit l'UNIQUE
    évidence d'isolation canonique via `create_pre_execution_context`
    avec la vraie cible — puis renvoie le résultat du driver VERBATIM
    (statut PREPARED_AWAITING_HUMAN_APPROVAL + EAH exact révélé). S'ARRÊTE.

  execute_work_unit_remediation(...)
    Délégation VERBATIM à `execute_governed_remediation(...)` : c'est le
    driver + PEC existants qui rechargent l'enveloppe, recalculent l'EAH,
    revérifient le PEC et échouent fermé sur toute dérive. Aucune
    sémantique de dérive maison ici.

  dispose_isolated_work_unit(...)
    Cycle de vie d'espace de travail uniquement : supprime un worktree +
    branche créés par CE module quand ils sont prouvablement jetables
    (enregistré / bonne identité / rien de stagé / rien de non-suivi /
    HEAD == base_sha). Sans --force.
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_pre_execution_context as _PEC
import obsidia_governed_execution_driver_v0 as _DRV

DECISION_AUTHORITY = "KX108_ONLY"
SUPPORTED_OPERATION = "UPDATE_TARGET_FROM_SOURCE"

# ── Statuts publics (aucune nouvelle autorité — enveloppe de statuts) ──
WORK_UNIT_CREATED = "WORK_UNIT_CREATED"
WORK_UNIT_CREATE_REJECTED = "WORK_UNIT_CREATE_REJECTED"
WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE = "WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE"
WORK_UNIT_PREPARE_REJECTED_DYNAMIC_ACTION_BASE = "WORK_UNIT_PREPARE_REJECTED_DYNAMIC_ACTION_BASE"
WORK_UNIT_DISPOSED = "WORK_UNIT_DISPOSED"
WORK_UNIT_DISPOSE_REFUSED = "WORK_UNIT_DISPOSE_REFUSED"

# Formes explicitement NON supportées à ce checkpoint (jamais substituées).
_UNSUPPORTED_SHAPES = (
    "MULTI_CHILD", "CREATE", "DELETE", "ARCHIVE", "MOVE", "RENAME",
)


def _run_git(args: "list[str]", cwd: "str | Path") -> "tuple[int, str, str]":
    """Lecture / cycle de vie d'espace de travail Git uniquement.
    Réutilise le même invariant que _PEC._run_git (subprocess borné, jamais
    de shell). Les seules sous-commandes mutantes autorisées ici sont
    `worktree add`, `worktree remove`, `branch -d` — cycle de vie d'espace
    de travail, jamais de disposition de remédiation."""
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=60,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except (subprocess.TimeoutExpired, OSError) as exc:
        return 1, "", str(exc)


@dataclass(frozen=True)
class IsolatedWorkUnit:
    """Poignée EN MÉMOIRE — jamais persistée. Toute corrélation durable
    est portée par les magasins immuables existants (via les IDs du driver)."""
    work_unit_id: str
    repo_root: str
    main_worktree_path: str
    base_sha: str
    branch_name: str
    worktree_path: str
    created_by_this_component: bool


def _reject_create(reason: str, **extra) -> dict:
    return {
        "status": WORK_UNIT_CREATE_REJECTED, "reason": reason,
        "authority": "NON_SOVEREIGN", "decision_authority": DECISION_AUTHORITY,
        "work_unit": None, "worktree_created": False, "branch_created": False,
        **extra,
    }


def _is_git_commit_sha(v) -> bool:
    return isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v.lower())


def _safe_remove_created_worktree(repo_root: Path, worktree_path: Path, branch_name: str) -> dict:
    """Supprime UNIQUEMENT un worktree + branche fraîchement créés par ce
    module. Sans --force. Best-effort : renvoie un compte-rendu, ne lève pas."""
    removed_wt = False
    deleted_branch = False
    detail = {}
    rc, out, err = _run_git(["worktree", "remove", str(worktree_path)], cwd=repo_root)
    removed_wt = rc == 0
    detail["worktree_remove_rc"] = rc
    if err.strip():
        detail["worktree_remove_err"] = err.strip()
    # Branche : suppression SÛRE (-d, jamais -D). Échoue si la branche porte
    # du travail non fusionné -> on laisse l'humain trancher.
    rc, out, err = _run_git(["branch", "-d", branch_name], cwd=repo_root)
    deleted_branch = rc == 0
    detail["branch_delete_rc"] = rc
    if err.strip():
        detail["branch_delete_err"] = err.strip()
    return {"worktree_removed": removed_wt, "branch_deleted": deleted_branch, "detail": detail}


# ══════════════════════════════════════════════════════════════════════════
#  1 — CRÉATION du worktree / branche isolés (cycle de vie d'espace de travail)
# ══════════════════════════════════════════════════════════════════════════

def create_isolated_work_unit(
    *,
    repo_root: "str | Path",
    base_sha: str,
    branch_name: str,
    worktree_path: "str | Path",
    work_unit_id: str,
    main_worktree_path: "Optional[str | Path]" = None,
) -> dict:
    """
    Crée UNE branche locale + UN worktree Git enregistré, bornés, à partir
    de paramètres explicitement fournis par l'humain / l'appelant.

    Aucune branche distante. Aucun push. Aucune configuration d'upstream.
    Aucun --force. Aucun nettoyage destructif d'un worktree existant.
    """
    repo_root = Path(repo_root).resolve()
    worktree_path = Path(worktree_path).resolve()
    main_wt = Path(main_worktree_path).resolve() if main_worktree_path is not None else repo_root

    if not (isinstance(work_unit_id, str) and work_unit_id.strip()):
        return _reject_create("WORK_UNIT_ID_REQUIRED")
    if not (isinstance(branch_name, str) and branch_name.strip()):
        return _reject_create("BRANCH_NAME_REQUIRED")
    if not _is_git_commit_sha(base_sha):
        return _reject_create("BASE_SHA_NOT_A_40_HEX_GIT_COMMIT_SHA")

    # 1. Identité de dépôt : repo_root DOIT être un arbre de travail Git.
    ident = _PEC._run_git(["rev-parse", "--git-common-dir"], cwd=repo_root)
    if ident[0] != 0 or not ident[1].strip():
        return _reject_create("REPO_ROOT_NOT_A_GIT_WORKTREE", detail=ident[2].strip())

    # 2. base_sha existe ET résout vers un commit DANS ce dépôt.
    rc, _, err = _run_git(["cat-file", "-e", f"{base_sha}^{{commit}}"], cwd=repo_root)
    if rc != 0:
        return _reject_create("BASE_SHA_NOT_A_COMMIT_IN_THIS_REPOSITORY", detail=err.strip())

    # 3. Non-conflit de branche : refs/heads/<branch> ne doit PAS exister.
    rc, _, _ = _run_git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch_name}"], cwd=repo_root)
    if rc == 0:
        return _reject_create("BRANCH_ALREADY_EXISTS", branch_name=branch_name)

    # 4. Destination : absente, OU répertoire existant vide (jamais de données étrangères).
    if worktree_path.exists():
        if not worktree_path.is_dir():
            return _reject_create("WORKTREE_DESTINATION_NOT_A_DIRECTORY", worktree_path=str(worktree_path))
        if any(worktree_path.iterdir()):
            return _reject_create("WORKTREE_DESTINATION_NOT_EMPTY", worktree_path=str(worktree_path))

    # 5. Création — cycle de vie d'espace de travail (sans --force).
    rc, _, err = _run_git(
        ["worktree", "add", str(worktree_path), "-b", branch_name, base_sha], cwd=repo_root,
    )
    if rc != 0:
        return _reject_create("GIT_WORKTREE_ADD_FAILED", detail=err.strip())

    # 6. Vérification des faits Git d'espace de travail via les helpers PEC
    #    canoniques (jamais un second validateur : l'ÉVIDENCE d'isolation
    #    canonique unique est produite plus tard par create_pre_execution_context
    #    avec la vraie cible, au moment de prepare_work_unit_execution).
    rc, out, err = _PEC._run_git(["worktree", "list", "--porcelain"], cwd=repo_root)
    if rc != 0:
        rb = _safe_remove_created_worktree(repo_root, worktree_path, branch_name)
        return _reject_create("WORKTREE_LIST_FAILED_AFTER_CREATE", detail=err.strip(), rollback=rb)
    entries = _PEC._parse_worktree_list_porcelain(out)
    wt_match = next((e for e in entries if Path(e["worktree"]).resolve() == worktree_path), None)
    main_match = next((e for e in entries if Path(e["worktree"]).resolve() == main_wt), None)

    fail_reason = None
    if wt_match is None:
        fail_reason = "WORKTREE_NOT_REGISTERED_AFTER_CREATE"
    elif main_match is None:
        fail_reason = "MAIN_WORKTREE_NOT_REGISTERED"
    elif worktree_path == main_wt:
        fail_reason = "WORKTREE_NOT_DISTINCT_FROM_MAIN"
    elif wt_match.get("detached") or not wt_match.get("branch"):
        fail_reason = "WORKTREE_DETACHED_OR_UNKNOWN_BRANCH"
    else:
        observed_branch = wt_match["branch"].replace("refs/heads/", "")
        if observed_branch != branch_name:
            fail_reason = f"BRANCH_MISMATCH:{observed_branch}"
        elif (main_match and not main_match.get("detached") and main_match.get("branch")
              and main_match["branch"].replace("refs/heads/", "") == observed_branch):
            fail_reason = "BRANCH_SAME_AS_MAIN_WORKTREE_BRANCH"
    if fail_reason is None:
        rc, head_out, err = _PEC._run_git(["rev-parse", "HEAD"], cwd=worktree_path)
        if rc != 0:
            fail_reason = "HEAD_UNREADABLE_AFTER_CREATE"
        elif head_out.strip() != base_sha:
            fail_reason = "HEAD_NOT_EQUAL_BASE_SHA"
    if fail_reason is None:
        rc, st_out, err = _PEC._run_git(["status", "--short"], cwd=worktree_path)
        if rc != 0:
            fail_reason = "STATUS_UNREADABLE_AFTER_CREATE"
        elif st_out.strip() != "":
            fail_reason = "WORKTREE_DIRTY_AFTER_CREATE"

    if fail_reason is not None:
        rb = _safe_remove_created_worktree(repo_root, worktree_path, branch_name)
        return _reject_create(f"WORKSPACE_FACTS_NOT_VERIFIED:{fail_reason}", rollback=rb)

    wu = IsolatedWorkUnit(
        work_unit_id=work_unit_id, repo_root=str(repo_root),
        main_worktree_path=str(main_wt), base_sha=base_sha,
        branch_name=branch_name, worktree_path=str(worktree_path),
        created_by_this_component=True,
    )
    return {
        "status": WORK_UNIT_CREATED, "reason": None,
        "authority": "NON_SOVEREIGN", "decision_authority": DECISION_AUTHORITY,
        "work_unit": wu, "worktree_created": True, "branch_created": True,
        "verified_branch": branch_name, "verified_head": base_sha,
        "canonical_isolation_evidence": "DEFERRED_TO_PRE_EXECUTION_CONTEXT_AT_PREPARE",
        "next_required_action": "CALL_prepare_work_unit_execution_WITH_TARGET_AND_TEST_CONTRACT",
    }


# ══════════════════════════════════════════════════════════════════════════
#  2 — PREPARE : premier appelant réel du driver générique (aucune autorité)
# ══════════════════════════════════════════════════════════════════════════

def prepare_work_unit_execution(
    *,
    work_unit: IsolatedWorkUnit,
    source_git_commit: str,
    source_historical_path: str,
    target_path: str,
    test_contract: dict,
    ledger_dir: "str | Path",
    selector_dir: "str | Path",
    execution_dir: "str | Path",
    pre_execution_context_dir: "str | Path",
    objective: str = "",
    operation: str = SUPPORTED_OPERATION,
    repository_identity: "Optional[str]" = None,
    expected_action_base_sha: "Optional[str]" = None,
) -> dict:
    """
    Refuse toute forme non prouvée AVANT de déléguer, puis appelle
    `prepare_governed_execution(...)` et renvoie son résultat VERBATIM.
    Ne reproduit AUCUNE étape du driver.

    `expected_action_base_sha` (Stage 3C, additif) : commit Git LOCAL EXPLICITE
    sur lequel CETTE action gouvernée doit démarrer, potentiellement plus récent
    que `work_unit.base_sha` (origine IMMUABLE de l'unité de travail). Vocabulaire
    Git/work-unit générique — ce module n'importe NI ne connaît la mission, le
    mission_tip, un plan d'action ou une autorité. `None` (défaut) ->
    `effective_action_base_sha = work_unit.base_sha` : comportement historique
    strictement inchangé. Fourni -> préflight fail-closed AVANT toute délégation :
    40-hex, commit résolvant dans le dépôt, HEAD observé == cette valeur (jamais
    "HEAD courant" découvert automatiquement), branche == work_unit.branch_name,
    identité de dépôt (git-common-dir) correcte, et DESCEND de work_unit.base_sha
    (sous-commande `merge-base --is-ancestor work_unit.base_sha <valeur>` -> code
    retour 0). PEC reste strict (HEAD == base_sha, worktree propre) — non modifié.
    """
    if not isinstance(work_unit, IsolatedWorkUnit):
        return {"status": WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE,
                "reason": "WORK_UNIT_HANDLE_REQUIRED", "decision_authority": DECISION_AUTHORITY}

    # Forme mono-enfant / UPDATE uniquement — jamais substituée.
    if operation != SUPPORTED_OPERATION:
        return {"status": WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE,
                "reason": f"UNSUPPORTED_OPERATION_SHAPE:{operation}",
                "supported_operation": SUPPORTED_OPERATION,
                "unsupported_shapes": list(_UNSUPPORTED_SHAPES),
                "decision_authority": DECISION_AUTHORITY, "target_mutated": False}
    if not isinstance(test_contract, dict) or not isinstance(test_contract.get("checks"), list):
        return {"status": WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE,
                "reason": "TEST_CONTRACT_MALFORMED", "decision_authority": DECISION_AUTHORITY,
                "target_mutated": False}
    tc_target = test_contract.get("target_path")
    if tc_target is not None and tc_target != target_path:
        return {"status": WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE,
                "reason": "TEST_CONTRACT_TARGET_PATH_MISMATCH",
                "decision_authority": DECISION_AUTHORITY, "target_mutated": False}
    # UPDATE (jamais CREATE) : la cible DOIT préexister dans le worktree.
    target_abs = Path(work_unit.worktree_path) / str(target_path).replace("\\", "/")
    if not target_abs.exists() or not target_abs.is_file():
        return {"status": WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE,
                "reason": "TARGET_MUST_PREEXIST_UPDATE_ONLY_NO_CREATE",
                "target_path": target_path,
                "decision_authority": DECISION_AUTHORITY, "target_mutated": False}

    # ── Stage 3C : base d'action DYNAMIQUE explicite (préflight fail-closed) ──
    # `work_unit.base_sha` reste l'origine IMMUABLE ; on ne la mute jamais.
    effective_action_base_sha = work_unit.base_sha
    if expected_action_base_sha is not None:
        dyn_reject = _preflight_dynamic_action_base(work_unit, expected_action_base_sha)
        if dyn_reject is not None:
            return dyn_reject
        effective_action_base_sha = expected_action_base_sha

    result = _DRV.prepare_governed_execution(
        source_git_commit=source_git_commit,
        source_historical_path=source_historical_path,
        target_path=target_path,
        test_contract=test_contract,
        execution_worktree_path=work_unit.worktree_path,
        main_worktree_path=work_unit.main_worktree_path,
        branch_name=work_unit.branch_name,
        base_sha=effective_action_base_sha,
        repository_identity=repository_identity,
        objective=objective,
        ledger_dir=ledger_dir,
        selector_dir=selector_dir,
        execution_dir=execution_dir,
        pre_execution_context_dir=pre_execution_context_dir,
    )
    out = dict(result)
    out["work_unit_id"] = work_unit.work_unit_id
    out["first_real_driver_caller"] = "obsidia_isolated_work_unit_v0"
    out["effective_action_base_sha"] = effective_action_base_sha
    out["dynamic_action_base_supplied"] = expected_action_base_sha is not None
    return out


def _preflight_dynamic_action_base(work_unit: IsolatedWorkUnit,
                                   expected_action_base_sha: str) -> "Optional[dict]":
    """Vérifie un `expected_action_base_sha` EXPLICITE contre des FAITS Git
    observés. Renvoie un dict de rejet (fail-closed, AVANT toute délégation au
    driver) ou None si tout est vérifié. Aucune mutation Git — lecture seule."""
    def _rej(reason: str, **extra) -> dict:
        return {"status": WORK_UNIT_PREPARE_REJECTED_DYNAMIC_ACTION_BASE, "reason": reason,
                "authority": "NON_SOVEREIGN", "decision_authority": DECISION_AUTHORITY,
                "target_mutated": False, "expected_action_base_sha": expected_action_base_sha,
                "work_unit_immutable_base_sha": work_unit.base_sha, **extra}

    if not _is_git_commit_sha(expected_action_base_sha):
        return _rej("EXPECTED_ACTION_BASE_SHA_NOT_A_40_HEX_GIT_COMMIT_SHA")

    wt = Path(work_unit.worktree_path)
    main = Path(work_unit.main_worktree_path)

    # 1. commit résolvant vers un commit DANS ce dépôt
    rc, _out, err = _run_git(["cat-file", "-e", f"{expected_action_base_sha}^{{commit}}"], cwd=wt)
    if rc != 0:
        return _rej("EXPECTED_ACTION_BASE_SHA_NOT_A_COMMIT_IN_THIS_REPOSITORY", detail=err.strip())

    # 2. identité de dépôt (git-common-dir) worktree == main
    cd_wt = _PEC._run_git(["rev-parse", "--git-common-dir"], cwd=wt)
    cd_main = _PEC._run_git(["rev-parse", "--git-common-dir"], cwd=main)
    if cd_wt[0] != 0 or cd_main[0] != 0:
        return _rej("REPOSITORY_COMMON_DIR_UNREADABLE")
    try:
        if str((wt / cd_wt[1].strip()).resolve()) != str((main / cd_main[1].strip()).resolve()):
            return _rej("REPOSITORY_COMMON_DIR_MISMATCH")
    except OSError:
        return _rej("REPOSITORY_COMMON_DIR_UNRESOLVABLE")

    # 3. branche observée == branche de l'unité de travail
    rc, br_out, _ = _PEC._run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=wt)
    if rc != 0 or br_out.strip() != work_unit.branch_name:
        return _rej(f"BRANCH_MISMATCH:{br_out.strip()}")

    # 4. HEAD observé == valeur EXPLICITE fournie (jamais "HEAD courant" auto-découvert)
    rc, head_out, _ = _PEC._run_git(["rev-parse", "HEAD"], cwd=wt)
    if rc != 0:
        return _rej("HEAD_UNREADABLE")
    if head_out.strip() != expected_action_base_sha:
        return _rej(f"OBSERVED_HEAD_NOT_EQUAL_EXPECTED_ACTION_BASE_SHA:{head_out.strip()}")

    # 5. la base d'action DESCEND de l'origine immuable de l'unité de travail
    #    (`--is-ancestor X X` -> rc 0, donc l'égalité passe aussi).
    rc, _o, _e = _run_git(
        ["merge-base", "--is-ancestor", work_unit.base_sha, expected_action_base_sha], cwd=wt,
    )
    if rc != 0:
        return _rej("EXPECTED_ACTION_BASE_SHA_DOES_NOT_DESCEND_FROM_WORK_UNIT_BASE_SHA")

    return None


# ══════════════════════════════════════════════════════════════════════════
#  3 — EXECUTE : délégation VERBATIM (dérive/reprise = driver + PEC existants)
# ══════════════════════════════════════════════════════════════════════════

def execute_work_unit_remediation(
    *,
    work_unit: IsolatedWorkUnit,
    batch_execution_id: str,
    child_execution_id: str,
    human_authorized_execution_authority_hash: "Optional[str]" = None,
    human_authorization_reference: "Optional[str]" = None,
    execution_dir: "str | Path",
    pre_execution_context_dir: "str | Path",
    selector_dir: "str | Path",
    ledger_dir: "str | Path",
    kx108_pre_decision_dir: "str | Path",
    kx108_post_decision_dir: "str | Path",
    test_contract_results_dir: "str | Path",
    sealed_receipt_dir: "str | Path",
    sealed_rollback_evidence_dir: "str | Path",
    rollback_result_dir: "str | Path",
    approval_dir: "Optional[str | Path]" = None,
    authority_mode: str = _DRV.DEFAULT_AUTHORITY_MODE,
    mission_id: "Optional[str]" = None,
    mission_store_dir: "Optional[str | Path]" = None,
) -> dict:
    """
    Délègue à `execute_governed_remediation(...)` sans rien y ajouter :
    le rechargement d'enveloppe, le recalcul d'EAH, la revérification PEC
    et l'échec fermé sur dérive sont ceux du driver + PEC existants.
    `repo_root` est TOUJOURS le worktree isolé de l'unité de travail.

    STAGE 4G — passe-plat additif : `authority_mode` / `mission_id` /
    `mission_store_dir` sont transmis TELS QUELS au driver. En mode
    `PER_ACTION_HUMAN_EAH` (défaut) le comportement est INCHANGÉ ; en mode
    `BOUNDED_MISSION_AUTHORITY` le driver exige mission_id + mission_store_dir
    et n'accepte AUCUN EAH humain par action (dispatch + fail-closed dans le
    driver Stage 4F, jamais ici).
    """
    if not isinstance(work_unit, IsolatedWorkUnit):
        return _DRV._pre_exec_reject("WORK_UNIT_HANDLE_REQUIRED")
    result = _DRV.execute_governed_remediation(
        batch_execution_id, child_execution_id,
        human_authorized_execution_authority_hash, human_authorization_reference,
        execution_dir=execution_dir, pre_execution_context_dir=pre_execution_context_dir,
        selector_dir=selector_dir, ledger_dir=ledger_dir,
        kx108_pre_decision_dir=kx108_pre_decision_dir,
        kx108_post_decision_dir=kx108_post_decision_dir,
        test_contract_results_dir=test_contract_results_dir,
        sealed_receipt_dir=sealed_receipt_dir,
        sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
        rollback_result_dir=rollback_result_dir,
        repo_root=work_unit.worktree_path,
        approval_dir=approval_dir,
        authority_mode=authority_mode,
        mission_id=mission_id,
        mission_store_dir=mission_store_dir,
    )
    out = dict(result)
    out["work_unit_id"] = work_unit.work_unit_id
    return out


# ══════════════════════════════════════════════════════════════════════════
#  4 — DISPOSE : cycle de vie d'espace de travail uniquement (sans --force)
# ══════════════════════════════════════════════════════════════════════════

def dispose_isolated_work_unit(
    *,
    work_unit: IsolatedWorkUnit,
    require_branch_disposition_done: bool = True,
) -> dict:
    """
    Supprime un worktree + branche créés par CE module quand ils sont
    prouvablement jetables : enregistré sous la bonne identité, rien de
    stagé, rien de non-suivi/non-committé, HEAD toujours == base_sha
    (aucun commit de travail conservé sur la branche). Sans --force.

    `require_branch_disposition_done=True` : refuse si la branche a avancé
    (HEAD != base_sha) — l'humain doit d'abord trancher la disposition Git.
    Un worktree jetable de fixture de test peut passer
    `require_branch_disposition_done=False`.
    """
    if not isinstance(work_unit, IsolatedWorkUnit) or not work_unit.created_by_this_component:
        return {"status": WORK_UNIT_DISPOSE_REFUSED, "reason": "NOT_CREATED_BY_THIS_COMPONENT",
                "decision_authority": DECISION_AUTHORITY}
    repo_root = Path(work_unit.repo_root)
    worktree_path = Path(work_unit.worktree_path)

    rc, out, err = _PEC._run_git(["worktree", "list", "--porcelain"], cwd=repo_root)
    if rc != 0:
        return {"status": WORK_UNIT_DISPOSE_REFUSED, "reason": "WORKTREE_LIST_FAILED",
                "detail": err.strip(), "decision_authority": DECISION_AUTHORITY}
    entries = _PEC._parse_worktree_list_porcelain(out)
    wt_match = next((e for e in entries if Path(e["worktree"]).resolve() == worktree_path.resolve()), None)
    if wt_match is None:
        return {"status": WORK_UNIT_DISPOSE_REFUSED, "reason": "WORKTREE_NOT_REGISTERED",
                "decision_authority": DECISION_AUTHORITY}
    observed_branch = (wt_match.get("branch") or "").replace("refs/heads/", "")
    if observed_branch != work_unit.branch_name:
        return {"status": WORK_UNIT_DISPOSE_REFUSED, "reason": "WORKTREE_IDENTITY_MISMATCH",
                "observed_branch": observed_branch, "decision_authority": DECISION_AUTHORITY}

    rc, st_out, _ = _PEC._run_git(["status", "--porcelain"], cwd=worktree_path)
    if rc != 0 or st_out.strip() != "":
        return {"status": WORK_UNIT_DISPOSE_REFUSED, "reason": "WORKTREE_NOT_CLEAN",
                "detail": st_out.strip(), "decision_authority": DECISION_AUTHORITY}

    rc, head_out, _ = _PEC._run_git(["rev-parse", "HEAD"], cwd=worktree_path)
    head_now = head_out.strip()
    if require_branch_disposition_done and head_now != work_unit.base_sha:
        return {"status": WORK_UNIT_DISPOSE_REFUSED,
                "reason": "BRANCH_HAS_ADVANCED_HUMAN_GIT_DISPOSITION_REQUIRED_FIRST",
                "head": head_now, "base_sha": work_unit.base_sha,
                "decision_authority": DECISION_AUTHORITY}

    rb = _safe_remove_created_worktree(repo_root, worktree_path, work_unit.branch_name)
    disposed = rb["worktree_removed"] and rb["branch_deleted"]
    return {
        "status": WORK_UNIT_DISPOSED if disposed else WORK_UNIT_DISPOSE_REFUSED,
        "reason": None if disposed else "SAFE_REMOVAL_INCOMPLETE",
        "worktree_removed": rb["worktree_removed"],
        "branch_deleted": rb["branch_deleted"],
        "detail": rb["detail"],
        "decision_authority": DECISION_AUTHORITY,
    }
