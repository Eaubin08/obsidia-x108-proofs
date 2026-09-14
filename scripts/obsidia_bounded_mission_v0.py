"""
obsidia_bounded_mission_v0.py
=============================
MINIMAL_AUTONOMOUS_WORK_WIRING_CHECKPOINT_2 — identité de mission bornée
PERSISTANTE + HOLD sémantique structuré + décision humaine sémantique
liée-contenu + reprise fail-closed, au-dessus (jamais à la place) du
rail gouverné committé (A1 -> C1 -> C2 -> D1 -> D2), du driver générique
et du pont d'unité de travail isolée Checkpoint 1.

Ce module :

  * NE DÉFINIT AUCUNE nouvelle autorité. `BoundedMissionRecord` est un
    CONTEXTE DE TRAVAIL / PROVENANCE — jamais une autorité d'exécution.
    Il ne fabrique JAMAIS `approved_by`, `approval_status`,
    `execution_authority_hash`, ni une `human_authorization_reference` ;
    il n'invoque JAMAIS KX108 (ni mock, ni ALLOW forcé, ni BLOCK forcé) ;
    il n'écrit JAMAIS une HumanApproval, un record KX108 PRE/POST, un
    SRE/SAR, un RollbackResult, ni une seule cible de remédiation.
  * N'IMPLÉMENTE AUCUN séquenceur multi-actions : `prepare_mission_action`
    puis `execute_mission_action` traitent UNE action mono-enfant déjà
    prouvée, puis la mission s'arrête honnêtement
    (`CLOSED_AWAITING_NEXT_PLAN`). Aucune boucle prepare->approve->
    execute->select-next.
  * N'IMPLÉMENTE AUCUNE `BoundedMissionAuthority`, aucune pré-approbation
    de mission, aucun budget d'approbation consommé comme HumanApproval,
    aucun retry automatique, aucune boucle de réparation, aucune
    automation de commit local, aucun push / PR / intégration main.
  * NE DUPLIQUE AUCUNE logique du rail : ni Ledger, ni BatchProposal, ni
    ExecutionEnvelope, ni le CALCUL de l'EAH, ni le store HumanApproval,
    ni KX108 PRE/POST, ni C1/C2, ni D1/D2, ni PEC hashing, ni la
    sémantique d'isolation Git, ni la logique de blocker Family Wiring.
    Il RÉUTILISE : le pont Checkpoint 1 (`obsidia_isolated_work_unit_v0`)
    pour prepare/execute mono-action, les helpers Git READ-ONLY de
    `obsidia_pre_execution_context`, et — pour la revérification d'une
    enveloppe déjà préparée après un HOLD — le rechargement d'enveloppe
    et le recalcul d'EAH CANONIQUES de `obsidia_batch_execution` (appelés,
    jamais réécrits).
  * NE FAIT AUCUNE opération Git mutante. Ses seuls appels Git sont des
    lectures de faits (`rev-parse`, `worktree list`, `status`, `cat-file`)
    via `obsidia_pre_execution_context._run_git`. Aucune capacité distante.
  * N'ÉCRIT QUE SES PROPRES magasins immuables append-only, hors dépôt,
    via l'unique helper `_atomic_publish_json` (même primitive `os.link`
    que `obsidia_pre_execution_context` / `obsidia_kx108_decision_store`) :
      bounded_missions/<mission_id>/genesis.json          (write-once)
      bounded_missions/<mission_id>/revisions/NNNNNN-*.json (append-only)
      bounded_mission_holds/<hold_id>.json                 (write-once)
      bounded_mission_decisions/<hmd_id>.json              (write-once)
    La `MissionResumeReference` est un objet DÉRIVÉ lié-contenu, jamais
    persisté (aucun 4e magasin).
  * L'ÉTAT COURANT de mission n'est JAMAIS stocké : il est DÉRIVÉ en
    rejouant la chaîne de révisions immuables hash-chaînée
    (`project_mission`). Aucun fichier `current_state` mutable, aucun
    compteur mutable, aucun `active_hold` stocké.

`decision_authority = KX108_ONLY` pour la mission (inchangé, jamais
consommé comme autorité). `decision_authority = NON_SOVEREIGN` pour la
`HumanMissionDecision` — résolution d'intention sémantique, JAMAIS une
approbation d'exécution.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_pre_execution_context as _PEC          # helpers Git READ-ONLY + verify PEC
import obsidia_isolated_work_unit_v0 as _WU           # pont mono-action Checkpoint 1
import obsidia_batch_execution as _E                  # rechargement enveloppe + recalcul EAH CANONIQUES
import obsidia_mission_local_snapshot_v0 as _LS       # Stage 3A : verify_local_snapshot_receipt (LECTURE SEULE)
import obsidia_batch_selector as _S                   # Stage 3D : detect_cycles + compute_execution_order (RÉUTILISÉS)
import obsidia_test_contract as _TC                   # Stage 3D : compute_test_contract_hash (RÉUTILISÉ)

DECISION_AUTHORITY = "KX108_ONLY"
SEMANTIC_DECISION_AUTHORITY = "NON_SOVEREIGN"
SUPPORTED_OPERATION = "UPDATE_TARGET_FROM_SOURCE"

GENESIS_SCHEMA_VERSION = 1
REVISION_SCHEMA_VERSION = 1
HOLD_SCHEMA_VERSION = 1
HUMAN_MISSION_DECISION_SCHEMA_VERSION = 1
RESUME_REFERENCE_SCHEMA_VERSION = 1
PLAN_SCHEMA_VERSION = 1

_SUPPORTED_GENESIS_SCHEMA_VERSIONS = (1,)
_SUPPORTED_REVISION_SCHEMA_VERSIONS = (1,)

# ── Magasins (défauts production hors dépôt — tests DOIVENT passer des racines temporaires) ──
_BOUNDED_MISSION_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "bounded_missions"
_BOUNDED_MISSION_HOLD_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "bounded_mission_holds"
_BOUNDED_MISSION_DECISION_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "bounded_mission_decisions"

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

# ── États de mission (Stage 2 approuvés — AUCUN état Stage 3 / L4) ──
S_CREATED = "CREATED"
S_WORKTREE_BOUND = "WORKTREE_BOUND"
S_ACTION_PREPARED = "ACTION_PREPARED"
S_HELD = "HELD"
S_ACTION_EXECUTED_KEPT = "ACTION_EXECUTED_KEPT"
S_ACTION_EXECUTED_ROLLED_BACK = "ACTION_EXECUTED_ROLLED_BACK"
S_ACTION_FAILED_QUARANTINE = "ACTION_FAILED_QUARANTINE"
S_CLOSED_AWAITING_NEXT_PLAN = "CLOSED_AWAITING_NEXT_PLAN"
S_ABORTED = "ABORTED"

MISSION_STATES = (
    S_CREATED, S_WORKTREE_BOUND, S_ACTION_PREPARED, S_HELD,
    S_ACTION_EXECUTED_KEPT, S_ACTION_EXECUTED_ROLLED_BACK,
    S_ACTION_FAILED_QUARANTINE, S_CLOSED_AWAITING_NEXT_PLAN, S_ABORTED,
)

# ── Événements ──
E_MISSION_CREATED = "MISSION_CREATED"
E_WORKTREE_CREATED = "WORKTREE_CREATED"
E_ACTION_PREPARE_SUCCEEDED = "ACTION_PREPARE_SUCCEEDED"
E_HOLD_OPENED = "HOLD_OPENED"
E_HOLD_RESOLVED = "HOLD_RESOLVED"
E_ACTION_EXECUTE_KEPT = "ACTION_EXECUTE_KEPT"
E_ACTION_EXECUTE_ROLLED_BACK = "ACTION_EXECUTE_ROLLED_BACK"
E_ACTION_EXECUTE_QUARANTINE = "ACTION_EXECUTE_QUARANTINE"
E_MISSION_CLOSED_NO_PLAN = "MISSION_CLOSED_NO_PLAN"
E_MISSION_ABORTED = "MISSION_ABORTED"
# ── Stage 3B additif : gel Git local d'un résultat gouverné KEEP, lié depuis
#    un LocalSnapshotReceipt Stage 3A VÉRIFIÉ (jamais créé ici). Fait avancer
#    le mission_tip_sha DÉRIVÉ. Ne sélectionne AUCUNE action suivante. ──
E_ACTION_LOCAL_SNAPSHOT_COMMITTED = "ACTION_LOCAL_SNAPSHOT_COMMITTED"
# ── Stage 3D additif : liaison d'UN plan d'action borné immuable / complétion. ──
E_PLAN_BOUND = "PLAN_BOUND"
E_PLAN_COMPLETED = "PLAN_COMPLETED"
# ── Stage 4E additif : liaison d'UNE HumanMissionAuthorization à la mission +
#    dérivation automatique d'un DerivedActionAuthorityWitness par action.
#    ÉVIDENCE STRICTEMENT NON_SOUVERAINE : n'autorise AUCUNE exécution, ne
#    satisfait AUCUNE HumanApproval, ne touche NI le rail PRE NI KX108. Le mode
#    d'exécution runtime demeure PER_ACTION_HUMAN_EAH. Transitions self-loop
#    (aucun changement d'état de mission). ──
E_MISSION_AUTHORITY_BOUND = "MISSION_AUTHORITY_BOUND"
E_ACTION_AUTHORITY_WITNESS_DERIVED = "ACTION_AUTHORITY_WITNESS_DERIVED"

# ── Table de transitions FERMÉE. Clé = (from_state, event) -> to_state.
#    from_state None == genèse. Les cas dépendant du contexte (HOLD_RESOLVED,
#    MISSION_ABORTED) sont validés en plus par le fold contre des ensembles
#    explicites ci-dessous. ──
_TRANSITIONS = {
    (None, E_MISSION_CREATED): S_CREATED,
    (S_CREATED, E_WORKTREE_CREATED): S_WORKTREE_BOUND,
    (S_WORKTREE_BOUND, E_ACTION_PREPARE_SUCCEEDED): S_ACTION_PREPARED,
    (S_WORKTREE_BOUND, E_HOLD_OPENED): S_HELD,
    (S_ACTION_PREPARED, E_HOLD_OPENED): S_HELD,
    (S_ACTION_PREPARED, E_ACTION_EXECUTE_KEPT): S_ACTION_EXECUTED_KEPT,
    (S_ACTION_PREPARED, E_ACTION_EXECUTE_ROLLED_BACK): S_ACTION_EXECUTED_ROLLED_BACK,
    (S_ACTION_PREPARED, E_ACTION_EXECUTE_QUARANTINE): S_ACTION_FAILED_QUARANTINE,
    (S_ACTION_EXECUTED_KEPT, E_MISSION_CLOSED_NO_PLAN): S_CLOSED_AWAITING_NEXT_PLAN,
    # Stage 3B : le résultat KEEP a été gelé en Git local, worktree attendu propre
    # au nouveau tip ; la mission est structurellement prête pour une future action
    # (AUCUNE sélection automatique — c'est Stage 3D).
    (S_ACTION_EXECUTED_KEPT, E_ACTION_LOCAL_SNAPSHOT_COMMITTED): S_WORKTREE_BOUND,
    # Stage 3D : liaison / complétion d'un plan borné (aucun nouvel état mission).
    (S_WORKTREE_BOUND, E_PLAN_BOUND): S_WORKTREE_BOUND,
    (S_WORKTREE_BOUND, E_PLAN_COMPLETED): S_CLOSED_AWAITING_NEXT_PLAN,
    # Stage 4E : évidence NON_SOUVERAINE additive — self-loop, aucun changement d'état.
    (S_WORKTREE_BOUND, E_MISSION_AUTHORITY_BOUND): S_WORKTREE_BOUND,
    (S_ACTION_PREPARED, E_ACTION_AUTHORITY_WITNESS_DERIVED): S_ACTION_PREPARED,
}
# HOLD_RESOLVED : depuis HELD uniquement, vers l'état interrompu (ou repli sûr).
_HOLD_RESOLVE_ALLOWED_TO = (S_WORKTREE_BOUND, S_ACTION_PREPARED)
# MISSION_ABORTED : depuis un état éligible uniquement, toujours vers ABORTED.
_ABORT_ELIGIBLE_STATES = (
    S_CREATED, S_WORKTREE_BOUND, S_ACTION_PREPARED, S_HELD, S_ACTION_EXECUTED_KEPT,
)

# ── Types de HOLD stables (jamais free-form en interne) ──
HOLD_TYPES = (
    "AMBIGUOUS_WIRE_OR_DEPRECATE",
    "ARCHIVE_OR_DELETE",
    "MISSING_OR_UNKNOWN_CONSUMER",
    "SCOPE_EXPANSION_REQUIRED",
    "EXTERNAL_API_DEPENDENCY",
    "UNEXPECTED_TARGET_STATE",
    "AMBIGUOUS_TEST_FAILURE",
    "SECURITY_OR_PROTECTED_BOUNDARY",
    "INSUFFICIENT_EVIDENCE",
    "OPERATION_SHAPE_UNSUPPORTED",
)

# ── Classes d'abort ──
ABORT_CLASSES = (
    "ABORT_BEFORE_MUTATION",
    "ABORT_WITH_LOCAL_WORK_PRESENT",
    "ABORT_AFTER_EXECUTION_KEPT_BEFORE_GIT_DISPOSITION",
    "ABORT_WHILE_HOLD",
)

# ── Statuts publics ──
STATUS_MISSION_CREATED = "MISSION_CREATED"
STATUS_MISSION_CREATE_REJECTED = "MISSION_CREATE_REJECTED"
STATUS_WORKTREE_BOUND = "WORKTREE_BOUND"
STATUS_BIND_REJECTED = "BIND_REJECTED"
STATUS_WORK_UNIT_REHYDRATED = "WORK_UNIT_REHYDRATED"
STATUS_WORK_UNIT_REHYDRATE_REJECTED = "WORK_UNIT_REHYDRATE_REJECTED"
STATUS_ACTION_PREPARED = "ACTION_PREPARED"
STATUS_PREPARE_REJECTED = "PREPARE_REJECTED"
STATUS_ACTION_RECORDED = "ACTION_RECORDED"
STATUS_EXECUTE_REJECTED = "EXECUTE_REJECTED"
STATUS_MISSION_EXECUTE_BLOCKED_ENVELOPE_DRIFT = "MISSION_EXECUTE_BLOCKED_ENVELOPE_DRIFT"
STATUS_HOLD_OPENED = "HOLD_OPENED"
STATUS_HOLD_OPEN_REJECTED = "HOLD_OPEN_REJECTED"
STATUS_DECISION_RECORDED = "DECISION_RECORDED"
STATUS_DECISION_REJECTED = "DECISION_REJECTED"
STATUS_HOLD_RESOLVED = "HOLD_RESOLVED"
STATUS_HOLD_RESOLVE_REJECTED = "HOLD_RESOLVE_REJECTED"
STATUS_MISSION_CLOSED = "MISSION_CLOSED"
STATUS_CLOSE_REJECTED = "CLOSE_REJECTED"
STATUS_MISSION_ABORTED = "MISSION_ABORTED"
STATUS_ABORT_REJECTED = "ABORT_REJECTED"
STATUS_PROJECTION_OK = "PROJECTION_OK"
STATUS_MISSION_NOT_FOUND = "MISSION_NOT_FOUND"
STATUS_MISSION_PROJECTION_INVALID = "MISSION_PROJECTION_INVALID"
STATUS_LOCAL_SNAPSHOT_RECORDED = "LOCAL_SNAPSHOT_RECORDED"
STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED = "LOCAL_SNAPSHOT_RECORD_REJECTED"
STATUS_LOCAL_SNAPSHOT_EVENT_IDEMPOTENT = "LOCAL_SNAPSHOT_EVENT_IDEMPOTENT_EXISTING_IDENTICAL"
STATUS_PLAN_BOUND = "PLAN_BOUND"
STATUS_PLAN_BIND_REJECTED = "PLAN_BIND_REJECTED"
STATUS_PLAN_COMPLETED = "PLAN_COMPLETED"
STATUS_PLAN_CLOSE_REJECTED = "PLAN_CLOSE_REJECTED"
# Stage 4E — évidence NON_SOUVERAINE (autorité de mission bornée PRÉPARÉE, non active)
STATUS_MISSION_AUTHORITY_BOUND = "MISSION_AUTHORITY_BOUND"
STATUS_MISSION_AUTHORITY_BIND_REJECTED = "MISSION_AUTHORITY_BIND_REJECTED"
STATUS_ACTION_AUTHORITY_WITNESS_RECORDED = "ACTION_AUTHORITY_WITNESS_RECORDED"
STATUS_ACTION_AUTHORITY_WITNESS_REJECTED = "ACTION_AUTHORITY_WITNESS_REJECTED"
STATUS_ACTION_AUTHORITY_WITNESS_EVENT_IDEMPOTENT = "ACTION_AUTHORITY_WITNESS_EVENT_IDEMPOTENT"

# Statuts terminaux du pont Checkpoint 1 / driver (ré-exportés, jamais réinterprétés)
_KEPT = _WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
_ROLLED_BACK = _WU._DRV.REJECTED_ROLLED_BACK
_ROLLBACK_FAILED_QUARANTINE = _WU._DRV.ROLLBACK_FAILED_QUARANTINE
_APPLY_STATE_UNKNOWN_QUARANTINE = _WU._DRV.APPLY_STATE_UNKNOWN_QUARANTINE
_APPLY_REJECTED_NO_MUTATION = _WU._DRV.APPLY_REJECTED_NO_MUTATION
_PRE_EXECUTION_REJECTED = _WU._DRV.PRE_EXECUTION_REJECTED


# ══════════════════════════════════════════════════════════════════════════
#  Primitives partagées (identité / hash / magasin immuable)
# ══════════════════════════════════════════════════════════════════════════

def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _record_hash(record: dict, bound_fields: "tuple[str, ...]") -> str:
    return _sha256_hex(_canon({k: record.get(k) for k in bound_fields}))


def _is_40_hex(v) -> bool:
    return isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v.lower())


def _is_64_hex(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v.lower())


def _safe_id_path(base: Path, ident: str, suffix: str = ".json") -> Path:
    """`ident` est un IDENTIFIANT, jamais un chemin. Deux défenses :
    regex lexicale stricte + confinement structurel (relative_to)."""
    if not (isinstance(ident, str) and _ID_RE.match(ident)):
        raise ValueError("INVALID_ID")
    candidate = base / f"{ident}{suffix}"
    try:
        candidate.relative_to(base)
    except ValueError:
        raise ValueError("INVALID_ID")
    return candidate


def _atomic_publish_json(path: Path, record: dict) -> str:
    """Publication ATOMIQUE append-only via os.link (même primitive que
    obsidia_pre_execution_context). Renvoie STORED / IDEMPOTENT_EXISTING_IDENTICAL
    / IMMUTABILITY_VIOLATION. UNIQUE point d'écriture du module."""
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.{os.getpid()}.{_sha256_hex(payload + str(id(record)))[:16]}.tmp"
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, path)
        return "STORED"
    except FileExistsError:
        existing = path.read_text(encoding="utf-8")
        return "IDEMPOTENT_EXISTING_IDENTICAL" if existing == payload else "IMMUTABILITY_VIOLATION"
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


# ══════════════════════════════════════════════════════════════════════════
#  Schémas liés (jeux de champs gelés — hash déterministe)
# ══════════════════════════════════════════════════════════════════════════

# Genesis : identité (déterministe, HORS created_at) ...
_GENESIS_IDENTITY_SEED_FIELDS = (
    "mission_record_schema_version", "objective", "repository_identity",
    "canonical_base_sha", "branch_name", "worktree_path", "main_worktree_path",
    "scope", "human_mandate_reference", "created_by", "decision_authority",
)
# ... et intégrité complète (INCLUT mission_id + created_at)
_GENESIS_BOUND_FIELDS = _GENESIS_IDENTITY_SEED_FIELDS + ("mission_id", "created_at")

_REVISION_BOUND_FIELDS = (
    "mission_record_schema_version", "mission_id", "revision",
    "parent_revision_hash", "event", "from_state", "to_state",
    "evidence_refs", "actor", "created_at",
)

_HOLD_IDENTITY_SEED_FIELDS = (
    "hold_schema_version", "mission_id", "mission_revision_at_open",
    "held_from_state", "action_ref", "hold_type", "reason",
    "evidence_refs", "question_for_human", "bounded_options",
    "free_form_decision_allowed",
)
_HOLD_BOUND_FIELDS = _HOLD_IDENTITY_SEED_FIELDS + ("hold_id", "created_at")

_HMD_IDENTITY_SEED_FIELDS = (
    "human_mission_decision_schema_version", "mission_id", "hold_id",
    "hold_record_hash", "chosen_option", "free_form_answer",
    "human_identity_marker", "decision_authority",
)
_HMD_BOUND_FIELDS = _HMD_IDENTITY_SEED_FIELDS + (
    "human_mission_decision_id", "previous_hold_evidence_hash",
    "not_an_execution_approval", "human_decision_ref", "created_at",
)

_RESUME_REF_FIELDS = (
    "resume_reference_schema_version",
    "mission_id", "mission_revision", "mission_revision_record_hash",
    "hold_id", "hold_record_hash",
    "human_mission_decision_id", "human_mission_decision_record_hash",
    "expected_repository_identity", "expected_branch_name",
    "expected_worktree_path", "expected_head_relationship",
    "next_allowed_transition",
)


# ══════════════════════════════════════════════════════════════════════════
#  Faits Git READ-ONLY (délégués à obsidia_pre_execution_context — jamais dupliqués)
# ══════════════════════════════════════════════════════════════════════════

def _git_common_dir(path: Path) -> Optional[str]:
    rc, out, _ = _PEC._run_git(["rev-parse", "--git-common-dir"], cwd=path)
    if rc != 0 or not out.strip():
        return None
    try:
        return str((path / out.strip()).resolve())
    except OSError:
        return None


def _verify_mission_worktree_binding(genesis: dict, worktree_path: Path,
                                     main_worktree_path: Path, *, require_clean: bool,
                                     expected_head_sha: "Optional[str]" = None) -> "tuple[bool, Optional[str]]":
    """Revérifie le lien mission<->worktree à partir de FAITS Git observés
    (helpers PEC), jamais d'assertions. Aucune seconde implémentation
    d'isolation Git.

    `expected_head_sha` (Stage 3B) : HEAD attendu du worktree. Par défaut ==
    genesis["canonical_base_sha"] (comportement Stage 2 inchangé) ; l'appelant
    passe `projection["mission_tip_sha"]` pour une mission qui a fait avancer
    son tip local via des snapshots gouvernés. `require_clean` INCHANGÉ."""
    expected_head = expected_head_sha or genesis["canonical_base_sha"]
    worktree_path = worktree_path.resolve()
    main_worktree_path = main_worktree_path.resolve()

    cd_wt = _git_common_dir(worktree_path)
    cd_main = _git_common_dir(main_worktree_path)
    if cd_wt is None or cd_main is None or cd_wt != cd_main:
        return False, "MISSION_WORKTREE_BINDING_DRIFT:REPO_IDENTITY"

    rc, out, err = _PEC._run_git(["worktree", "list", "--porcelain"], cwd=main_worktree_path)
    if rc != 0:
        return False, "WORKTREE_DRIFT:LIST_FAILED"
    entries = _PEC._parse_worktree_list_porcelain(out)
    wt = next((e for e in entries if Path(e["worktree"]).resolve() == worktree_path), None)
    if wt is None:
        return False, "WORKTREE_DRIFT:NOT_REGISTERED"
    if worktree_path == main_worktree_path:
        return False, "WORKTREE_DRIFT:NOT_DISTINCT_FROM_MAIN"
    if wt.get("detached") or not wt.get("branch"):
        return False, "WORKTREE_DRIFT:DETACHED_OR_UNKNOWN_BRANCH"
    observed_branch = wt["branch"].replace("refs/heads/", "")
    if observed_branch != genesis["branch_name"]:
        return False, f"WORKTREE_DRIFT:BRANCH:{observed_branch}"

    rc, head_out, _ = _PEC._run_git(["rev-parse", "HEAD"], cwd=worktree_path)
    if rc != 0:
        return False, "WORKTREE_DRIFT:HEAD_UNREADABLE"
    # HEAD attendu == tip de mission (== canonical_base_sha tant qu'aucun snapshot
    # gouverné n'a fait avancer la branche locale).
    if head_out.strip() != expected_head:
        return False, f"WORKTREE_DRIFT:HEAD:{head_out.strip()}"

    if require_clean:
        rc, st_out, _ = _PEC._run_git(["status", "--porcelain"], cwd=worktree_path)
        if rc != 0:
            return False, "WORKTREE_DRIFT:STATUS_UNREADABLE"
        if st_out.strip() != "":
            return False, "WORKTREE_DRIFT:DIRTY"
    return True, None


# ══════════════════════════════════════════════════════════════════════════
#  Scope (BORNE SUPÉRIEURE — la mission peut REFUSER, jamais AUTORISER)
# ══════════════════════════════════════════════════════════════════════════

def _normalize_scope(scope) -> "tuple[Optional[dict], Optional[str]]":
    if not isinstance(scope, dict):
        return None, "SCOPE_NOT_AN_OBJECT"
    shapes = scope.get("allowed_operation_shapes")
    if not isinstance(shapes, list) or not shapes or any(not isinstance(s, str) for s in shapes):
        return None, "SCOPE_ALLOWED_OPERATION_SHAPES_INVALID"
    atp = scope.get("allowed_target_paths")
    if atp is not None and (not isinstance(atp, list) or any(not isinstance(p, str) for p in atp)):
        return None, "SCOPE_ALLOWED_TARGET_PATHS_INVALID"
    ma = scope.get("max_actions")
    if not isinstance(ma, int) or isinstance(ma, bool) or ma < 1:
        return None, "SCOPE_MAX_ACTIONS_INVALID"
    mr = scope.get("max_retries_per_action")
    if not isinstance(mr, int) or isinstance(mr, bool) or mr < 0:
        return None, "SCOPE_MAX_RETRIES_INVALID"
    return {
        "allowed_operation_shapes": sorted(set(shapes)),
        "allowed_target_paths": (sorted(set(atp)) if atp is not None else None),
        "max_actions": ma,
        "max_retries_per_action": mr,
    }, None


def _scope_refuses_action(genesis: dict, projection: dict, *, operation: str,
                          target_path: str) -> Optional[str]:
    scope = genesis["scope"]
    if operation not in scope["allowed_operation_shapes"]:
        return f"MISSION_SCOPE_OPERATION_SHAPE_NOT_ALLOWED:{operation}"
    if operation != SUPPORTED_OPERATION:
        return f"MISSION_SCOPE_OPERATION_SHAPE_NOT_ALLOWED:{operation}"
    atp = scope["allowed_target_paths"]
    if atp is not None and target_path not in atp:
        return f"MISSION_SCOPE_TARGET_PATH_NOT_ALLOWED:{target_path}"
    if projection["actions_completed"] >= scope["max_actions"]:
        return "MISSION_SCOPE_MAX_ACTIONS_EXCEEDED"
    if projection["retries_used"] > scope["max_retries_per_action"]:
        return "MISSION_SCOPE_MAX_RETRIES_EXCEEDED"
    return None


# ══════════════════════════════════════════════════════════════════════════
#  Chargement + projection (état DÉRIVÉ — jamais stocké)
# ══════════════════════════════════════════════════════════════════════════

def _mission_dir(mission_id: str, store_dir: Path) -> Path:
    if not (isinstance(mission_id, str) and _ID_RE.match(mission_id)):
        raise ValueError("INVALID_ID")
    d = (store_dir / mission_id).resolve()
    try:
        d.relative_to(store_dir.resolve())
    except ValueError:
        raise ValueError("INVALID_ID")
    return d


def _load_genesis(mission_id: str, store_dir: Path) -> Optional[dict]:
    try:
        p = _mission_dir(mission_id, store_dir) / "genesis.json"
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_mission_genesis(mission_id: str, mission_store_dir: "str | Path") -> Optional[dict]:
    """Accès LECTURE SEULE au record de genèse (verify via _verify_genesis)."""
    return _load_genesis(mission_id, Path(mission_store_dir))


def _load_revisions(mission_id: str, store_dir: Path) -> "list[dict]":
    try:
        d = _mission_dir(mission_id, store_dir) / "revisions"
    except ValueError:
        return []
    if not d.exists():
        return []
    out = []
    for f in sorted(d.glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            out.append({"__unparseable__": True})
    return out


def _verify_genesis(genesis: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if genesis is None:
        return False, "MISSION_GENESIS_MISSING"
    if genesis.get("mission_record_schema_version") not in _SUPPORTED_GENESIS_SCHEMA_VERSIONS:
        return False, "MISSION_GENESIS_SCHEMA_UNSUPPORTED"
    if genesis.get("decision_authority") != DECISION_AUTHORITY:
        return False, "MISSION_GENESIS_DECISION_AUTHORITY_NOT_KX108_ONLY"
    for f in _GENESIS_BOUND_FIELDS:
        if f not in genesis:
            return False, f"MISSION_GENESIS_FIELD_MISSING:{f}"
    if genesis.get("mission_genesis_record_hash") != _record_hash(genesis, _GENESIS_BOUND_FIELDS):
        return False, "MISSION_GENESIS_RECORD_HASH_MISMATCH"
    # Identité déterministe recalculée
    seed = _canon({k: genesis.get(k) for k in _GENESIS_IDENTITY_SEED_FIELDS})
    if genesis.get("mission_id") != "msn-" + _sha256_hex(seed)[:32]:
        return False, "MISSION_ID_NOT_DERIVED_FROM_GENESIS_IDENTITY"
    return True, None


def project_mission(*, mission_id: str, mission_store_dir: "str | Path",
                    hold_store_dir: "Optional[str | Path]" = None) -> dict:
    """Rejoue la chaîne de révisions immuables et DÉRIVE l'état courant.
    Fail-closed : hash / parent hash / ordre / transition illégale / schéma
    inconnu -> MISSION_PROJECTION_INVALID (aucune projection émise)."""
    store_dir = Path(mission_store_dir)
    genesis = _load_genesis(mission_id, store_dir)
    if genesis is None:
        return {"status": STATUS_MISSION_NOT_FOUND, "mission_id": mission_id}
    ok_g, reason_g = _verify_genesis(genesis)
    if not ok_g:
        return {"status": STATUS_MISSION_PROJECTION_INVALID, "mission_id": mission_id, "reason": reason_g}

    revisions = _load_revisions(mission_id, store_dir)
    if not revisions:
        return {"status": STATUS_MISSION_PROJECTION_INVALID, "mission_id": mission_id,
                "reason": "MISSION_HAS_NO_REVISIONS"}

    state = None
    prev_hash = genesis["mission_genesis_record_hash"]
    linked_execution_ids: "list[dict]" = []
    holds: "dict[str, dict]" = {}          # hold_id -> {opened_at_rev, held_from_state, resolution_state, hold_type}
    resolved_decisions: "list[dict]" = []
    prepare_count = 0
    actions_completed = 0
    actions_failed = 0
    active_hold_id: Optional[str] = None
    last_prepared_evidence: Optional[dict] = None
    aborted_from_state: Optional[str] = None
    # ── Stage 3B : tip de mission DÉRIVÉ (jamais stocké). Chaîne descendant de
    #    canonical_base_sha, avancée UNIQUEMENT par un événement snapshot vérifié. ──
    running_tip = genesis["canonical_base_sha"]
    snapshot_count = 0
    snapshotted_action_ids: "set" = set()
    latest_snapshot_receipt_id: Optional[str] = None
    latest_snapshot_receipt_record_hash: Optional[str] = None
    local_snapshots: "list[dict]" = []
    # ── Stage 3D : plan borné + statut d'action DÉRIVÉ par action_id ──
    active_plan_id: Optional[str] = None
    active_plan_hash: Optional[str] = None
    plan_bound_revision: Optional[int] = None
    plan_completed = False
    prepares_by_action_id: "dict[str, int]" = {}
    kept_action_ids: "set" = set()
    rolled_back_action_ids: "set" = set()
    quarantined_action_ids: "set" = set()
    # ── Stage 4E : mode d'autorité de mission + témoins d'action DÉRIVÉS
    #    (NON_SOUVERAINS, dérivés du journal immuable — jamais stockés mutables). ──
    mission_authority_mode = "PER_ACTION_HUMAN_EAH"
    active_hma_id: Optional[str] = None
    active_hma_record_hash: Optional[str] = None
    active_hma_plan_id: Optional[str] = None
    active_hma_plan_hash: Optional[str] = None
    derived_witnesses: "list[dict]" = []
    derived_witness_action_ids: "set" = set()

    for idx, rev in enumerate(revisions, start=1):
        if rev.get("__unparseable__"):
            return _proj_invalid(mission_id, f"REVISION_UNPARSEABLE:{idx}")
        if rev.get("mission_record_schema_version") not in _SUPPORTED_REVISION_SCHEMA_VERSIONS:
            return _proj_invalid(mission_id, f"REVISION_SCHEMA_UNSUPPORTED:{idx}")
        if rev.get("mission_id") != mission_id:
            return _proj_invalid(mission_id, f"REVISION_MISSION_ID_MISMATCH:{idx}")
        if rev.get("revision") != idx:
            return _proj_invalid(mission_id, f"REVISION_INDEX_NOT_CONTIGUOUS:{idx}:{rev.get('revision')}")
        for f in _REVISION_BOUND_FIELDS:
            if f not in rev:
                return _proj_invalid(mission_id, f"REVISION_FIELD_MISSING:{idx}:{f}")
        if rev.get("mission_revision_record_hash") != _record_hash(rev, _REVISION_BOUND_FIELDS):
            return _proj_invalid(mission_id, f"REVISION_RECORD_HASH_MISMATCH:{idx}")
        if rev.get("parent_revision_hash") != prev_hash:
            return _proj_invalid(mission_id, f"REVISION_CHAIN_BREAK:{idx}")
        if rev.get("from_state") != state:
            return _proj_invalid(mission_id, f"REVISION_FROM_STATE_MISMATCH:{idx}")

        event = rev["event"]
        to_state = rev["to_state"]

        if event == E_HOLD_RESOLVED:
            if state != S_HELD or to_state not in _HOLD_RESOLVE_ALLOWED_TO:
                return _proj_invalid(mission_id, f"MISSION_TRANSITION_ILLEGAL:{idx}:{state}->{event}->{to_state}")
        elif event == E_MISSION_ABORTED:
            if state not in _ABORT_ELIGIBLE_STATES or to_state != S_ABORTED:
                return _proj_invalid(mission_id, f"MISSION_TRANSITION_ILLEGAL:{idx}:{state}->{event}->{to_state}")
        else:
            expected_to = _TRANSITIONS.get((state, event))
            if expected_to is None or expected_to != to_state:
                return _proj_invalid(mission_id, f"MISSION_TRANSITION_ILLEGAL:{idx}:{state}->{event}->{to_state}")

        ev = rev.get("evidence_refs") or {}

        # ── effets sur les accumulateurs (dérivés, jamais stockés) ──
        if event == E_ACTION_PREPARE_SUCCEEDED:
            prepare_count += 1
            last_prepared_evidence = dict(ev)
            _aid = ev.get("action_id")
            if _aid:
                prepares_by_action_id[_aid] = prepares_by_action_id.get(_aid, 0) + 1
        elif event == E_HOLD_OPENED:
            hid = ev.get("hold_id")
            holds[hid] = {"opened_at_rev": idx, "held_from_state": ev.get("held_from_state"),
                          "hold_type": ev.get("hold_type"), "resolution_state": "OPEN"}
            active_hold_id = hid
        elif event == E_HOLD_RESOLVED:
            hid = ev.get("hold_id")
            if hid in holds:
                holds[hid]["resolution_state"] = "RESOLVED"
            resolved_decisions.append({
                "hold_id": hid,
                "human_mission_decision_id": ev.get("human_mission_decision_id"),
                "human_mission_decision_record_hash": ev.get("human_mission_decision_record_hash"),
                "resumed_to_state": to_state,
                "prepared_envelope_stale": bool(ev.get("prepared_envelope_stale")),
            })
            active_hold_id = None
        elif event in (E_ACTION_EXECUTE_KEPT, E_ACTION_EXECUTE_ROLLED_BACK, E_ACTION_EXECUTE_QUARANTINE):
            actions_completed += 1
            if event != E_ACTION_EXECUTE_KEPT:
                actions_failed += 1
            _aid = ev.get("action_id")
            if _aid and event == E_ACTION_EXECUTE_KEPT:
                kept_action_ids.add(_aid)
            elif _aid and event == E_ACTION_EXECUTE_ROLLED_BACK:
                rolled_back_action_ids.add(_aid)
            elif _aid and event == E_ACTION_EXECUTE_QUARANTINE:
                quarantined_action_ids.add(_aid)
            linked_execution_ids.append({
                "batch_execution_id": ev.get("batch_execution_id"),
                "child_execution_id": ev.get("child_execution_id"),
                "execution_authority_hash": ev.get("execution_authority_hash"),
                "outcome_status": ev.get("driver_status"),
                "action_id": _aid,
                "plan_id": ev.get("plan_id"),
                "ordinal": ev.get("ordinal"),
                "approval_id": ev.get("approval_id"),
                "kx108_pre_decision_record_id": ev.get("kx108_pre_decision_record_id"),
                "kx108_pre_gate": ev.get("kx108_pre_gate"),
                "kx108_post_gate": ev.get("kx108_post_gate"),
                "rollback_result_id": ev.get("rollback_result_id"),
            })
        elif event == E_PLAN_BOUND:
            active_plan_id = ev.get("plan_id")
            active_plan_hash = ev.get("plan_hash")
            plan_bound_revision = idx
        elif event == E_PLAN_COMPLETED:
            plan_completed = True
        elif event == E_MISSION_AUTHORITY_BOUND:
            mission_authority_mode = "BOUNDED_MISSION_AUTHORITY_PREPARED"
            active_hma_id = ev.get("hma_id")
            active_hma_record_hash = ev.get("hma_record_hash")
            active_hma_plan_id = ev.get("plan_id")
            active_hma_plan_hash = ev.get("plan_hash")
        elif event == E_ACTION_AUTHORITY_WITNESS_DERIVED:
            _waid = ev.get("action_id")
            if _waid:
                derived_witness_action_ids.add(_waid)
            derived_witnesses.append({
                "action_id": _waid, "ordinal": ev.get("ordinal"),
                "daaw_id": ev.get("daaw_id"), "daaw_record_hash": ev.get("daaw_record_hash"),
                "execution_authority_hash": ev.get("execution_authority_hash"),
                "action_base_sha": ev.get("action_base_sha"),
                "hma_id": ev.get("hma_id"),
            })
        elif event == E_MISSION_ABORTED:
            aborted_from_state = rev.get("from_state")
            for h in holds.values():
                if h["resolution_state"] == "OPEN":
                    h["resolution_state"] = "SUPERSEDED"
            active_hold_id = None
        elif event == E_ACTION_LOCAL_SNAPSHOT_COMMITTED:
            prev_tip = ev.get("previous_mission_tip_sha")
            new_tip = ev.get("new_mission_tip_sha")
            commit_parent = ev.get("commit_parent_sha")
            new_commit = ev.get("new_commit_sha")
            snap_action_id = ev.get("action_id")
            if prev_tip != running_tip:
                return _proj_invalid(mission_id, f"MISSION_PROJECTION_INVALID:SNAPSHOT_TIP_CHAIN_BREAK:{idx}:previous_tip")
            if commit_parent != running_tip:
                return _proj_invalid(mission_id, f"MISSION_PROJECTION_INVALID:SNAPSHOT_TIP_CHAIN_BREAK:{idx}:commit_parent")
            if new_tip != new_commit:
                return _proj_invalid(mission_id, f"MISSION_PROJECTION_INVALID:SNAPSHOT_TIP_CHAIN_BREAK:{idx}:new_tip_neq_commit")
            if not (isinstance(new_commit, str) and len(new_commit) == 40
                    and all(c in "0123456789abcdef" for c in new_commit.lower())):
                return _proj_invalid(mission_id, f"MISSION_PROJECTION_INVALID:SNAPSHOT_MALFORMED_COMMIT_SHA:{idx}")
            if snap_action_id in snapshotted_action_ids:
                return _proj_invalid(mission_id, f"MISSION_PROJECTION_INVALID:SNAPSHOT_ACTION_RECORDED_TWICE:{idx}")
            snapshotted_action_ids.add(snap_action_id)
            running_tip = new_tip
            snapshot_count += 1
            latest_snapshot_receipt_id = ev.get("snapshot_receipt_id")
            latest_snapshot_receipt_record_hash = ev.get("local_snapshot_receipt_record_hash")
            local_snapshots.append({
                "action_id": snap_action_id, "ordinal": ev.get("ordinal"),
                "previous_mission_tip_sha": prev_tip, "new_mission_tip_sha": new_tip,
                "new_commit_sha": new_commit, "commit_parent_sha": commit_parent,
                "committed_paths": ev.get("committed_paths"),
                "snapshot_receipt_id": ev.get("snapshot_receipt_id"),
                "local_snapshot_receipt_record_hash": ev.get("local_snapshot_receipt_record_hash"),
            })

        state = to_state
        prev_hash = rev["mission_revision_record_hash"]

    # retries_used : re-préparations d'UNE MÊME action au-delà de la première.
    # Stage 3D : les révisions de préparation portent action_id -> compte par action_id
    # (une action distincte préparée une fois = 0 retry). Historique sans action_id ->
    # ancienne dérivation `prepare_count - 1` (compat Stage 2).
    if prepares_by_action_id:
        retries_used = sum(max(0, c - 1) for c in prepares_by_action_id.values())
    else:
        retries_used = max(0, prepare_count - 1)
    scope = genesis["scope"]
    active_hold = None
    if active_hold_id is not None:
        hrec = _load_hold(active_hold_id, Path(hold_store_dir)) if hold_store_dir else None
        active_hold = {
            "hold_id": active_hold_id,
            "hold_type": (hrec or {}).get("hold_type") or holds.get(active_hold_id, {}).get("hold_type"),
            "held_from_state": (hrec or {}).get("held_from_state") or holds.get(active_hold_id, {}).get("held_from_state"),
            "question_for_human": (hrec or {}).get("question_for_human"),
            "bounded_options": (hrec or {}).get("bounded_options"),
            "free_form_decision_allowed": (hrec or {}).get("free_form_decision_allowed"),
            "mission_hold_record_hash": (hrec or {}).get("mission_hold_record_hash"),
        }

    unknowns: "list[str]" = []
    if state == S_CLOSED_AWAITING_NEXT_PLAN:
        unknowns += ["NO_SEQUENCER_PLAN", "NEXT_ACTION_NOT_DETERMINED_BY_STACK"]
    if state == S_ACTION_FAILED_QUARANTINE:
        unknowns += ["QUARANTINE_REQUIRES_HUMAN_HANDLING"]

    return {
        "status": STATUS_PROJECTION_OK,
        "mission_id": mission_id,
        "schema_version": genesis["mission_record_schema_version"],
        "objective": genesis["objective"],
        "human_mandate_reference": genesis["human_mandate_reference"],
        "created_at": genesis["created_at"],
        "repository_identity": genesis["repository_identity"],
        "canonical_base_sha": genesis["canonical_base_sha"],
        "mission_tip_sha": running_tip,
        "has_local_mission_snapshots": snapshot_count > 0,
        "local_snapshot_count": snapshot_count,
        "latest_snapshot_receipt_id": latest_snapshot_receipt_id,
        "latest_snapshot_receipt_record_hash": latest_snapshot_receipt_record_hash,
        "local_snapshots": local_snapshots,
        "branch_name": genesis["branch_name"],
        "worktree_path": genesis["worktree_path"],
        "main_worktree_path": genesis["main_worktree_path"],
        "scope": scope,
        "current_state": state,
        "revision": len(revisions),
        "mission_revision_record_hash": prev_hash,
        "mission_genesis_record_hash": genesis["mission_genesis_record_hash"],
        "active_hold_id": active_hold_id,
        "active_hold": active_hold,
        "holds": holds,
        "resolved_semantic_decisions": resolved_decisions,
        "linked_governed_executions": linked_execution_ids,
        "actions_completed": actions_completed,
        "actions_failed": actions_failed,
        "retries_used": retries_used,
        "remaining_action_budget": scope["max_actions"] - actions_completed,
        "last_prepared_evidence": last_prepared_evidence,
        "aborted_from_state": aborted_from_state,
        # ── Stage 3D : métadonnées de plan DÉRIVÉES ──
        "active_plan_id": active_plan_id,
        "active_plan_hash": active_plan_hash,
        "plan_bound_revision": plan_bound_revision,
        "plan_completed": plan_completed,
        "prepared_action_ids": sorted(prepares_by_action_id.keys()),
        "kept_action_ids": sorted(kept_action_ids),
        "rolled_back_action_ids": sorted(rolled_back_action_ids),
        "quarantined_action_ids": sorted(quarantined_action_ids),
        "snapshotted_action_ids": sorted(a for a in snapshotted_action_ids if a),
        # ── Stage 4E : mode d'autorité + témoins d'action DÉRIVÉS (NON_SOUVERAINS) ──
        "mission_authority_mode": mission_authority_mode,
        "active_hma_id": active_hma_id,
        "active_hma_record_hash": active_hma_record_hash,
        "active_hma_plan_id": active_hma_plan_id,
        "active_hma_plan_hash": active_hma_plan_hash,
        "derived_witnesses": derived_witnesses,
        "derived_witness_action_ids": sorted(a for a in derived_witness_action_ids if a),
        "unknowns": unknowns,
    }


def _proj_invalid(mission_id: str, reason: str) -> dict:
    return {"status": STATUS_MISSION_PROJECTION_INVALID, "mission_id": mission_id, "reason": reason}

def rehydrate_bound_work_unit(*, mission_id: str,
                              mission_store_dir: "str | Path",
                              hold_store_dir: "Optional[str | Path]" = None) -> dict:
    """Reconstruit en LECTURE SEULE la poign?e IsolatedWorkUnit ? partir
    de la gen?se et de l'unique ?v?nement WORKTREE_CREATED v?rifi?.

    Aucun worktree n'est cr??, aucune r?vision n'est ?crite, aucun KX108
    ni s?quenceur n'est invoqu?. Le binding Git r?el est rev?rifi? par
    _verify_mission_worktree_binding.
    """
    store_dir = Path(mission_store_dir)

    proj = project_mission(
        mission_id=mission_id,
        mission_store_dir=store_dir,
        hold_store_dir=hold_store_dir,
    )
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}",
            mission_id=mission_id,
            work_unit=None,
        )

    genesis = load_mission_genesis(mission_id, store_dir)
    ok_g, reason_g = _verify_genesis(genesis)
    if not ok_g:
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            f"MISSION_GENESIS_INVALID:{reason_g}",
            mission_id=mission_id,
            work_unit=None,
        )

    revisions = _load_revisions(mission_id, store_dir)
    bindings = [r for r in revisions if r.get("event") == E_WORKTREE_CREATED]
    if len(bindings) != 1:
        reason = (
            "WORKTREE_BINDING_EVIDENCE_MISSING"
            if not bindings
            else f"WORKTREE_BINDING_EVIDENCE_NOT_UNIQUE:{len(bindings)}"
        )
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            reason,
            mission_id=mission_id,
            work_unit=None,
        )

    evidence = bindings[0].get("evidence_refs")
    if not isinstance(evidence, dict):
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            "WORKTREE_BINDING_EVIDENCE_MALFORMED",
            mission_id=mission_id,
            work_unit=None,
        )

    work_unit_id = evidence.get("work_unit_id")
    if not (isinstance(work_unit_id, str) and _ID_RE.match(work_unit_id)):
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            "WORKTREE_BINDING_WORK_UNIT_ID_INVALID",
            mission_id=mission_id,
            work_unit=None,
        )

    if evidence.get("verified_branch") != genesis["branch_name"]:
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            "WORKTREE_BINDING_EVIDENCE_BRANCH_MISMATCH",
            mission_id=mission_id,
            work_unit=None,
        )

    if evidence.get("verified_head") != genesis["canonical_base_sha"]:
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            "WORKTREE_BINDING_EVIDENCE_BASE_MISMATCH",
            mission_id=mission_id,
            work_unit=None,
        )

    if evidence.get("worktree_path") != genesis["worktree_path"]:
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            "WORKTREE_BINDING_EVIDENCE_PATH_MISMATCH",
            mission_id=mission_id,
            work_unit=None,
        )

    created_here = evidence.get("created_by_this_component")
    if type(created_here) is not bool:
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            "WORKTREE_BINDING_CREATED_BY_INVALID",
            mission_id=mission_id,
            work_unit=None,
        )

    state = proj["current_state"]

    if state == S_ACTION_EXECUTED_KEPT:
        require_clean = False
    elif state in (S_WORKTREE_BOUND, S_ACTION_PREPARED):
        require_clean = True
    elif state == S_HELD:
        held_from = (proj.get("active_hold") or {}).get("held_from_state")
        if held_from not in (S_WORKTREE_BOUND, S_ACTION_PREPARED):
            return _rej(
                STATUS_WORK_UNIT_REHYDRATE_REJECTED,
                f"WORK_UNIT_REHYDRATE_HELD_FROM_UNSUPPORTED:{held_from}",
                mission_id=mission_id,
                work_unit=None,
            )
        require_clean = True
    else:
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            f"WORK_UNIT_REHYDRATE_STATE_UNSUPPORTED:{state}",
            mission_id=mission_id,
            work_unit=None,
        )

    work_unit = _WU.IsolatedWorkUnit(
        work_unit_id=work_unit_id,
        repo_root=genesis["main_worktree_path"],
        main_worktree_path=genesis["main_worktree_path"],
        base_sha=genesis["canonical_base_sha"],
        branch_name=genesis["branch_name"],
        worktree_path=genesis["worktree_path"],
        created_by_this_component=created_here,
    )

    ok_wt, reason_wt = _verify_mission_worktree_binding(
        genesis,
        Path(work_unit.worktree_path),
        Path(work_unit.main_worktree_path),
        require_clean=require_clean,
        expected_head_sha=proj["mission_tip_sha"],
    )
    if not ok_wt:
        return _rej(
            STATUS_WORK_UNIT_REHYDRATE_REJECTED,
            reason_wt,
            mission_id=mission_id,
            work_unit=None,
        )

    return {
        "status": STATUS_WORK_UNIT_REHYDRATED,
        "reason": None,
        "mission_id": mission_id,
        "current_state": state,
        "work_unit": work_unit,
    }



# ══════════════════════════════════════════════════════════════════════════
#  Écriture d'une révision (append-only, hash-chaînée)
# ══════════════════════════════════════════════════════════════════════════

def _append_revision(mission_id: str, store_dir: Path, *, revision: int, parent_hash: str,
                     event: str, from_state: Optional[str], to_state: str,
                     evidence_refs: dict, actor: str) -> "tuple[Optional[dict], Optional[str]]":
    rec = {
        "mission_record_schema_version": REVISION_SCHEMA_VERSION,
        "mission_id": mission_id,
        "revision": revision,
        "parent_revision_hash": parent_hash,
        "event": event,
        "from_state": from_state,
        "to_state": to_state,
        "evidence_refs": evidence_refs,
        "actor": actor,
        "created_at": _now(),
    }
    rec["mission_revision_record_hash"] = _record_hash(rec, _REVISION_BOUND_FIELDS)
    d = _mission_dir(mission_id, store_dir) / "revisions"
    short = rec["mission_revision_record_hash"][:12]
    p = d / f"{revision:06d}-{short}.json"
    st = _atomic_publish_json(p, rec)
    if st == "IMMUTABILITY_VIOLATION":
        return None, "REVISION_IMMUTABILITY_VIOLATION"
    return rec, None


# ══════════════════════════════════════════════════════════════════════════
#  1 — CRÉATION de la mission bornée (genesis write-once + révision 1)
# ══════════════════════════════════════════════════════════════════════════

def create_bounded_mission(*, objective: str, repository_identity: str,
                           canonical_base_sha: str, branch_name: str,
                           worktree_path: "str | Path", main_worktree_path: "str | Path",
                           scope: dict, human_mandate_reference: str,
                           mission_store_dir: "str | Path", created_by: str = "HUMAN") -> dict:
    store_dir = Path(mission_store_dir)

    if not (isinstance(objective, str) and objective.strip()):
        return _rej(STATUS_MISSION_CREATE_REJECTED, "OBJECTIVE_REQUIRED")
    if not (isinstance(repository_identity, str) and repository_identity.strip()):
        return _rej(STATUS_MISSION_CREATE_REJECTED, "REPOSITORY_IDENTITY_REQUIRED")
    if not _is_40_hex(canonical_base_sha):
        return _rej(STATUS_MISSION_CREATE_REJECTED, "CANONICAL_BASE_SHA_NOT_A_40_HEX_GIT_COMMIT_SHA")
    if not (isinstance(branch_name, str) and branch_name.strip()):
        return _rej(STATUS_MISSION_CREATE_REJECTED, "BRANCH_NAME_REQUIRED")
    if not (isinstance(human_mandate_reference, str) and human_mandate_reference.strip()):
        return _rej(STATUS_MISSION_CREATE_REJECTED, "HUMAN_MANDATE_REFERENCE_REQUIRED")
    norm_scope, scope_err = _normalize_scope(scope)
    if scope_err:
        return _rej(STATUS_MISSION_CREATE_REJECTED, scope_err)

    genesis = {
        "mission_record_schema_version": GENESIS_SCHEMA_VERSION,
        "objective": objective,
        "repository_identity": repository_identity,
        "canonical_base_sha": canonical_base_sha,
        "branch_name": branch_name,
        "worktree_path": str(Path(worktree_path).resolve()),
        "main_worktree_path": str(Path(main_worktree_path).resolve()),
        "scope": norm_scope,
        "human_mandate_reference": human_mandate_reference,
        "created_by": created_by,
        "decision_authority": DECISION_AUTHORITY,
    }
    seed = _canon({k: genesis.get(k) for k in _GENESIS_IDENTITY_SEED_FIELDS})
    mission_id = "msn-" + _sha256_hex(seed)[:32]

    # Idempotence stricte : une genèse déjà présente pour CETTE identité
    # (seed identique + hash vérifié) -> IDEMPOTENT_EXISTING_IDENTICAL, sans
    # réécriture. Toute genèse présente qui ne re-vérifie pas ou dont le seed
    # d'identité diffère -> IMMUTABILITY_VIOLATION (conflit).
    existing = _load_genesis(mission_id, store_dir)
    if existing is not None:
        ok_e, _reason_e = _verify_genesis(existing)
        existing_seed = _canon({k: existing.get(k) for k in _GENESIS_IDENTITY_SEED_FIELDS})
        if ok_e and existing.get("mission_id") == mission_id and existing_seed == seed:
            proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
            return {"status": STATUS_MISSION_CREATED, "reason": "IDEMPOTENT_EXISTING_IDENTICAL",
                    "mission_id": mission_id,
                    "genesis_record_hash": existing["mission_genesis_record_hash"],
                    "genesis_store_status": "IDEMPOTENT_EXISTING_IDENTICAL",
                    "current_state": proj.get("current_state"),
                    "revision": proj.get("revision"),
                    "mission_revision_record_hash": proj.get("mission_revision_record_hash"),
                    "decision_authority": DECISION_AUTHORITY,
                    "mission_object_is_execution_authority": False}
        return _rej(STATUS_MISSION_CREATE_REJECTED, "MISSION_GENESIS_IMMUTABILITY_VIOLATION",
                    mission_id=mission_id)

    genesis["created_at"] = _now()
    genesis["mission_id"] = mission_id
    genesis["mission_genesis_record_hash"] = _record_hash(genesis, _GENESIS_BOUND_FIELDS)

    gpath = _mission_dir(mission_id, store_dir) / "genesis.json"
    st = _atomic_publish_json(gpath, genesis)
    if st == "IMMUTABILITY_VIOLATION":
        return _rej(STATUS_MISSION_CREATE_REJECTED, "MISSION_GENESIS_IMMUTABILITY_VIOLATION",
                    mission_id=mission_id)

    rec, err = _append_revision(
        mission_id, store_dir, revision=1, parent_hash=genesis["mission_genesis_record_hash"],
        event=E_MISSION_CREATED, from_state=None, to_state=S_CREATED,
        evidence_refs={"mission_genesis_record_hash": genesis["mission_genesis_record_hash"]},
        actor="HUMAN",
    )
    if err:
        return _rej(STATUS_MISSION_CREATE_REJECTED, err, mission_id=mission_id)

    return {
        "status": STATUS_MISSION_CREATED, "reason": None, "mission_id": mission_id,
        "genesis_record_hash": genesis["mission_genesis_record_hash"],
        "genesis_store_status": st, "current_state": S_CREATED,
        "revision": 1, "mission_revision_record_hash": rec["mission_revision_record_hash"],
        "decision_authority": DECISION_AUTHORITY,
        "mission_object_is_execution_authority": False,
    }


# ══════════════════════════════════════════════════════════════════════════
#  2 — LIAISON d'une IsolatedWorkUnit Checkpoint 1 à la mission
# ══════════════════════════════════════════════════════════════════════════

def bind_work_unit(*, mission_id: str, work_unit: "_WU.IsolatedWorkUnit",
                   mission_store_dir: "str | Path") -> dict:
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_BIND_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_CREATED:
        return _rej(STATUS_BIND_REJECTED, f"MISSION_NOT_IN_CREATED_STATE:{proj['current_state']}")
    if not isinstance(work_unit, _WU.IsolatedWorkUnit):
        return _rej(STATUS_BIND_REJECTED, "WORK_UNIT_HANDLE_REQUIRED")

    genesis = _load_genesis(mission_id, store_dir)
    # 1. Coordonnées déclarées == coordonnées de l'unité de travail
    if work_unit.branch_name != genesis["branch_name"]:
        return _rej(STATUS_BIND_REJECTED, "BIND_BRANCH_MISMATCH")
    if work_unit.base_sha != genesis["canonical_base_sha"]:
        return _rej(STATUS_BIND_REJECTED, "BIND_BASE_SHA_MISMATCH")
    if str(Path(work_unit.worktree_path).resolve()) != genesis["worktree_path"]:
        return _rej(STATUS_BIND_REJECTED, "BIND_WORKTREE_PATH_MISMATCH")
    if str(Path(work_unit.main_worktree_path).resolve()) != genesis["main_worktree_path"]:
        return _rej(STATUS_BIND_REJECTED, "BIND_MAIN_WORKTREE_PATH_MISMATCH")

    # 2. Faits Git observés (helpers PEC — jamais une seconde implémentation).
    #    À l'état CREATED le tip == canonical_base_sha ; on le passe explicitement.
    ok, reason = _verify_mission_worktree_binding(
        genesis, Path(work_unit.worktree_path), Path(work_unit.main_worktree_path),
        require_clean=True, expected_head_sha=proj["mission_tip_sha"],
    )
    if not ok:
        return _rej(STATUS_BIND_REJECTED, reason)

    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_WORKTREE_CREATED, from_state=S_CREATED, to_state=S_WORKTREE_BOUND,
        evidence_refs={
            "work_unit_id": work_unit.work_unit_id,
            "verified_branch": genesis["branch_name"],
            "verified_head": genesis["canonical_base_sha"],
            "worktree_path": genesis["worktree_path"],
            "created_by_this_component": bool(work_unit.created_by_this_component),
        },
        actor="STACK",
    )
    if err:
        return _rej(STATUS_BIND_REJECTED, err)
    return {"status": STATUS_WORKTREE_BOUND, "reason": None, "mission_id": mission_id,
            "current_state": S_WORKTREE_BOUND, "revision": rec["revision"],
            "mission_revision_record_hash": rec["mission_revision_record_hash"],
            "mission_worktree_binding_reuses_pec": True}


# ══════════════════════════════════════════════════════════════════════════
#  3 — PREPARE mono-action (wrapper autour du pont Checkpoint 1)
# ══════════════════════════════════════════════════════════════════════════

def prepare_mission_action(*, mission_id: str, work_unit: "_WU.IsolatedWorkUnit",
                           source_git_commit: str, source_historical_path: str,
                           target_path: str, test_contract: dict,
                           ledger_dir: "str | Path", selector_dir: "str | Path",
                           execution_dir: "str | Path", pre_execution_context_dir: "str | Path",
                           mission_store_dir: "str | Path", objective: str = "",
                           operation: str = SUPPORTED_OPERATION,
                           repository_identity: "Optional[str]" = None,
                           expected_action_base_sha: "Optional[str]" = None,
                           plan_id: "Optional[str]" = None,
                           action_id: "Optional[str]" = None,
                           ordinal: "Optional[int]" = None) -> dict:
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_PREPARE_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] == S_ACTION_PREPARED:
        return _rej(STATUS_PREPARE_REJECTED, "ACTION_ALREADY_PREPARED")
    if proj["current_state"] != S_WORKTREE_BOUND:
        return _rej(STATUS_PREPARE_REJECTED, f"MISSION_NOT_IN_WORKTREE_BOUND_STATE:{proj['current_state']}")

    genesis = _load_genesis(mission_id, store_dir)
    # SCOPE : borne supérieure — la mission REFUSE hors périmètre (n'autorise jamais)
    scope_refusal = _scope_refuses_action(genesis, proj, operation=operation, target_path=target_path)
    if scope_refusal:
        return _rej(STATUS_PREPARE_REJECTED, scope_refusal, mission_scope_is_upper_bound=True)

    # Délégation VERBATIM au pont Checkpoint 1 (aucune étape du driver reproduite).
    # Stage 3D : `expected_action_base_sha` (== projection.mission_tip_sha fourni par le
    # séquenceur) est transmis TEL QUEL au préflight de base dynamique Stage 3C.
    driver_result = _WU.prepare_work_unit_execution(
        work_unit=work_unit,
        source_git_commit=source_git_commit,
        source_historical_path=source_historical_path,
        target_path=target_path,
        test_contract=test_contract,
        ledger_dir=ledger_dir, selector_dir=selector_dir,
        execution_dir=execution_dir, pre_execution_context_dir=pre_execution_context_dir,
        objective=objective or genesis["objective"],
        operation=operation,
        repository_identity=repository_identity,
        expected_action_base_sha=expected_action_base_sha,
    )
    if driver_result.get("status") != _WU._DRV.PREPARED_AWAITING_HUMAN_APPROVAL:
        return {"status": STATUS_PREPARE_REJECTED, "reason": "CHECKPOINT1_PREPARE_DID_NOT_SUCCEED",
                "mission_id": mission_id, "current_state": proj["current_state"],
                "checkpoint1_result": driver_result, "human_approval_created_by_mission_layer": False}

    ev = {
        "batch_execution_id": driver_result.get("batch_execution_id"),
        "child_execution_id": driver_result.get("child_execution_id"),
        "execution_authority_hash": driver_result.get("execution_authority_hash"),
        "pre_execution_context_id": driver_result.get("pre_execution_context_id"),
        "pre_execution_context_record_hash": driver_result.get("pre_execution_context_record_hash"),
        "test_contract_hash": driver_result.get("test_contract_hash"),
        "ledger_entry_id": driver_result.get("ledger_entry_id"),
        "target_path": target_path,
        "operation": operation,
        "effective_action_base_sha": driver_result.get("effective_action_base_sha"),
        "plan_id": plan_id,
        "action_id": action_id,
        "ordinal": ordinal,
    }
    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_ACTION_PREPARE_SUCCEEDED, from_state=S_WORKTREE_BOUND, to_state=S_ACTION_PREPARED,
        evidence_refs=ev, actor="STACK",
    )
    if err:
        return _rej(STATUS_PREPARE_REJECTED, err)
    return {
        "status": STATUS_ACTION_PREPARED, "reason": None, "mission_id": mission_id,
        "current_state": S_ACTION_PREPARED, "revision": rec["revision"],
        "mission_revision_record_hash": rec["mission_revision_record_hash"],
        # autorité RÉVÉLÉE pour revue humaine — la couche mission NE l'approuve PAS
        "execution_authority_hash": driver_result.get("execution_authority_hash"),
        "batch_execution_id": driver_result.get("batch_execution_id"),
        "child_execution_id": driver_result.get("child_execution_id"),
        "checkpoint1_result": driver_result,
        "human_approval_created_by_mission_layer": False,
        "next_required_action": "HUMAN_AUTHORIZE_EXACT_EAH_THEN_CALL_execute_mission_action",
        "generic_driver_logic_duplicated": False,
    }


# ══════════════════════════════════════════════════════════════════════════
#  4 — EXECUTE mono-action (délègue l'autorisation humaine EXACTE verbatim)
# ══════════════════════════════════════════════════════════════════════════

def execute_mission_action(*, mission_id: str, work_unit: "_WU.IsolatedWorkUnit",
                           batch_execution_id: str, child_execution_id: str,
                           human_authorized_execution_authority_hash: "Optional[str]" = None,
                           human_authorization_reference: "Optional[str]" = None,
                           execution_dir: "str | Path", pre_execution_context_dir: "str | Path",
                           selector_dir: "str | Path", ledger_dir: "str | Path",
                           kx108_pre_decision_dir: "str | Path", kx108_post_decision_dir: "str | Path",
                           test_contract_results_dir: "str | Path", sealed_receipt_dir: "str | Path",
                           sealed_rollback_evidence_dir: "str | Path", rollback_result_dir: "str | Path",
                           mission_store_dir: "str | Path",
                           approval_dir: "Optional[str | Path]" = None,
                           authority_mode: str = _WU._DRV.DEFAULT_AUTHORITY_MODE) -> dict:
    store_dir = Path(mission_store_dir)
    _stage4 = (authority_mode == _WU._DRV.AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_EXECUTE_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_ACTION_PREPARED:
        return _rej(STATUS_EXECUTE_REJECTED, f"MISSION_NOT_IN_ACTION_PREPARED_STATE:{proj['current_state']}")

    prepared = proj.get("last_prepared_evidence") or {}
    if prepared.get("batch_execution_id") != batch_execution_id or \
       prepared.get("child_execution_id") != child_execution_id:
        return _rej(STATUS_EXECUTE_REJECTED, "EXECUTE_IDS_DO_NOT_MATCH_PREPARED_ACTION")

    if _stage4 and (human_authorized_execution_authority_hash is not None
                    or human_authorization_reference is not None):
        return _rej(STATUS_EXECUTE_REJECTED, "STAGE4_MODE_REJECTS_PER_ACTION_HUMAN_EAH")

    # Délégation VERBATIM au pont Checkpoint 1 : c'est LUI (+ driver + PEC) qui
    # recharge l'enveloppe, recalcule l'EAH, (mode historique) exige recomputed ==
    # stored == humain / (mode Stage 4) construit + revérifie CANONIQUEMENT la
    # DerivedMissionApprovalEvidence, persiste la HumanApproval, invoque KX108
    # PRE/POST, C2, D1/D2. La couche mission ne fabrique RIEN de tout cela ; en
    # mode Stage 4 elle NE FOURNIT AUCUN EAH humain par action.
    driver_result = _WU.execute_work_unit_remediation(
        work_unit=work_unit,
        batch_execution_id=batch_execution_id,
        child_execution_id=child_execution_id,
        human_authorized_execution_authority_hash=human_authorized_execution_authority_hash,
        human_authorization_reference=human_authorization_reference,
        execution_dir=execution_dir, pre_execution_context_dir=pre_execution_context_dir,
        selector_dir=selector_dir, ledger_dir=ledger_dir,
        kx108_pre_decision_dir=kx108_pre_decision_dir, kx108_post_decision_dir=kx108_post_decision_dir,
        test_contract_results_dir=test_contract_results_dir, sealed_receipt_dir=sealed_receipt_dir,
        sealed_rollback_evidence_dir=sealed_rollback_evidence_dir, rollback_result_dir=rollback_result_dir,
        approval_dir=approval_dir,
        authority_mode=authority_mode,
        mission_id=(mission_id if _stage4 else None),
        mission_store_dir=(store_dir if _stage4 else None),
    )
    dstatus = driver_result.get("status")

    if dstatus == _PRE_EXECUTION_REJECTED:
        # Enveloppe préparée dérivée : AUCUNE révision, l'état mission reste ACTION_PREPARED.
        # Recours humain : abort_bounded_mission (cible intacte) OU open_mission_hold->resolve
        # (la résolution détecte l'enveloppe périmée et ramène à WORKTREE_BOUND).
        return {
            "status": STATUS_MISSION_EXECUTE_BLOCKED_ENVELOPE_DRIFT,
            "reason": driver_result.get("reason"),
            "mission_id": mission_id, "current_state": S_ACTION_PREPARED,
            "mission_state_unchanged": True,
            "checkpoint1_result": driver_result,
            "recourse": ["abort_bounded_mission", "open_mission_hold_then_resolve"],
        }

    if dstatus == _KEPT:
        event, to_state = E_ACTION_EXECUTE_KEPT, S_ACTION_EXECUTED_KEPT
    elif dstatus == _ROLLED_BACK:
        event, to_state = E_ACTION_EXECUTE_ROLLED_BACK, S_ACTION_EXECUTED_ROLLED_BACK
    elif dstatus in (_ROLLBACK_FAILED_QUARANTINE, _APPLY_STATE_UNKNOWN_QUARANTINE, _APPLY_REJECTED_NO_MUTATION):
        event, to_state = E_ACTION_EXECUTE_QUARANTINE, S_ACTION_FAILED_QUARANTINE
    else:
        return {"status": STATUS_EXECUTE_REJECTED, "reason": f"UNMAPPED_DRIVER_STATUS:{dstatus}",
                "mission_id": mission_id, "current_state": S_ACTION_PREPARED,
                "checkpoint1_result": driver_result}

    # Stage 3D : l'identité de plan/action est celle de l'action PRÉPARÉE (autoritaire,
    # jamais fournie à l'exécution) — reprise depuis last_prepared_evidence.
    _pe = proj.get("last_prepared_evidence") or {}
    ev = {
        "driver_status": dstatus,
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child_execution_id,
        "execution_authority_hash": driver_result.get("execution_authority_hash"),
        "approval_id": driver_result.get("approval_id"),
        # mode Stage 4 : la référence d'autorisation humaine EFFECTIVE est celle de
        # l'HMA racine, propagée par le driver via la DMAE (jamais un EAH par action).
        "human_authorization_reference": (
            human_authorization_reference if not _stage4
            else driver_result.get("human_authorization_reference")),
        "authority_mode": authority_mode,
        "derived_mission_approval_evidence_id": driver_result.get("derived_mission_approval_evidence_id"),
        "kx108_pre_decision_record_id": driver_result.get("kx108_pre_decision_record_id"),
        "kx108_pre_gate": driver_result.get("kx108_pre_gate"),
        "kx108_post_gate": driver_result.get("kx108_post_gate"),
        "rollback_result_id": driver_result.get("rollback_result_id"),
        "sealed_apply_receipt_id": driver_result.get("sealed_apply_receipt_id"),
        "sealed_rollback_evidence_id": driver_result.get("sealed_rollback_evidence_id"),
        "target_mutated": bool(driver_result.get("target_mutated")) if "target_mutated" in driver_result else None,
        "plan_id": _pe.get("plan_id"),
        "action_id": _pe.get("action_id"),
        "ordinal": _pe.get("ordinal"),
        "test_contract_result_id": driver_result.get("test_contract_result_id"),
        "kx108_post_decision_record_id": driver_result.get("kx108_post_decision_record_id"),
    }
    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=event, from_state=S_ACTION_PREPARED, to_state=to_state,
        evidence_refs=ev, actor="STACK",
    )
    if err:
        return _rej(STATUS_EXECUTE_REJECTED, err)
    return {
        "status": STATUS_ACTION_RECORDED, "reason": None, "mission_id": mission_id,
        "current_state": to_state, "revision": rec["revision"],
        "mission_revision_record_hash": rec["mission_revision_record_hash"],
        "driver_status": dstatus, "checkpoint1_result": driver_result,
        "mission_layer_decided_keep_or_block": False,
        "human_approval_created_by_mission_layer": False,
    }


def close_mission_no_plan(*, mission_id: str, mission_store_dir: "str | Path") -> dict:
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_CLOSE_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_ACTION_EXECUTED_KEPT:
        return _rej(STATUS_CLOSE_REJECTED, f"MISSION_NOT_IN_ACTION_EXECUTED_KEPT_STATE:{proj['current_state']}")
    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_MISSION_CLOSED_NO_PLAN, from_state=S_ACTION_EXECUTED_KEPT,
        to_state=S_CLOSED_AWAITING_NEXT_PLAN,
        evidence_refs={"note": "single governed action recorded; no sequencer exists in Stage 2"},
        actor="STACK",
    )
    if err:
        return _rej(STATUS_CLOSE_REJECTED, err)
    return {"status": STATUS_MISSION_CLOSED, "reason": None, "mission_id": mission_id,
            "current_state": S_CLOSED_AWAITING_NEXT_PLAN, "revision": rec["revision"],
            "mission_revision_record_hash": rec["mission_revision_record_hash"],
            "multi_action_sequencer_included": False}


# ══════════════════════════════════════════════════════════════════════════
#  4bis — Stage 3B : LIER un LocalSnapshotReceipt Stage 3A VÉRIFIÉ à l'histoire
#         de mission -> avance le mission_tip_sha DÉRIVÉ. N'écrit AUCUN commit Git.
# ══════════════════════════════════════════════════════════════════════════

def record_local_snapshot(*, mission_id: str, action_id: str, snapshot_receipt_id: str,
                          work_unit: "_WU.IsolatedWorkUnit",
                          snapshot_store_dir: "str | Path",
                          mission_store_dir: "str | Path",
                          plan_id: "Optional[str]" = None) -> dict:
    """Recharge le LocalSnapshotReceipt Stage 3A, le VÉRIFIE via le vérificateur
    canonique `_LS.verify_local_snapshot_receipt` (jamais dupliqué), le lie à
    l'action KEEP courante de la mission, et append une révision
    ACTION_LOCAL_SNAPSHOT_COMMITTED. La couche mission ne crée AUCUN commit Git —
    Stage 3A en est le seul auteur. `only KEEP` peut faire avancer le tip."""
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED,
                    f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_ACTION_EXECUTED_KEPT:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED,
                    f"ONLY_KEEP_CAN_ADVANCE_MISSION_TIP:STATE_IS:{proj['current_state']}")
    if not isinstance(work_unit, _WU.IsolatedWorkUnit):
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "WORK_UNIT_HANDLE_REQUIRED")

    # ── Idempotence : un événement snapshot pour cet action_id existe déjà ? ──
    for s in proj.get("local_snapshots", []):
        if s.get("action_id") == action_id:
            if s.get("snapshot_receipt_id") == snapshot_receipt_id:
                return {"status": STATUS_LOCAL_SNAPSHOT_EVENT_IDEMPOTENT, "reason": None,
                        "mission_id": mission_id, "current_state": proj["current_state"],
                        "mission_tip_sha": proj["mission_tip_sha"],
                        "new_commit_sha": s.get("new_commit_sha")}
            return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED,
                        "MISSION_TIP_CHAIN_FORK:ACTION_ALREADY_SNAPSHOTTED_WITH_DIFFERENT_RECEIPT")

    # ── Recharge + VÉRIFIE le reçu Stage 3A (canonique, jamais dupliqué) ──
    try:
        rpath = _safe_id_path(Path(snapshot_store_dir), snapshot_receipt_id)
    except ValueError:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_RECEIPT_ID_INVALID")
    if not rpath.exists():
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_RECEIPT_NOT_FOUND")
    try:
        receipt = json.loads(rpath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_RECEIPT_UNPARSEABLE")
    ok_r, why_r = _LS.verify_local_snapshot_receipt(receipt, repo_root=Path(work_unit.worktree_path))
    if not ok_r:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, f"SNAPSHOT_RECEIPT_INVALID:{why_r}")

    # ── Le reçu doit désigner CETTE mission + CETTE action KEEP courante ──
    if receipt.get("snapshot_receipt_id") != snapshot_receipt_id:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_RECEIPT_ID_MISMATCH")
    if receipt.get("mission_id") != mission_id:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_RECEIPT_MISSION_MISMATCH")
    if receipt.get("action_id") != action_id:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_RECEIPT_ACTION_MISMATCH")
    if receipt.get("decision_authority") != SEMANTIC_DECISION_AUTHORITY:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_RECEIPT_NOT_NON_SOVEREIGN")
    if receipt.get("not_final_human_git_disposition") is not True:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_RECEIPT_MISSING_NOT_FINAL_MARKER")
    committed_paths = receipt.get("committed_paths")
    if not (isinstance(committed_paths, list) and len(committed_paths) == 1):
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_RECEIPT_NOT_SINGLE_TARGET")

    last_exec = (proj.get("linked_governed_executions") or [])
    if not last_exec:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "MISSION_HAS_NO_LINKED_GOVERNED_EXECUTION")
    kept = last_exec[-1]
    if kept.get("outcome_status") != _KEPT:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "LAST_LINKED_EXECUTION_NOT_KEEP")
    if receipt.get("batch_execution_id") != kept.get("batch_execution_id") or \
       receipt.get("child_execution_id") != kept.get("child_execution_id") or \
       receipt.get("execution_authority_hash") != kept.get("execution_authority_hash"):
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED,
                    "SNAPSHOT_RECEIPT_NOT_BOUND_TO_MISSION_KEPT_ACTION")

    # ── Chaîne de tip ──
    if receipt.get("previous_mission_tip_sha") != proj["mission_tip_sha"]:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED,
                    f"SNAPSHOT_PREVIOUS_TIP_MISMATCH:{receipt.get('previous_mission_tip_sha')}")
    if receipt.get("commit_parent_sha") != proj["mission_tip_sha"]:
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED,
                    f"SNAPSHOT_COMMIT_PARENT_MISMATCH:{receipt.get('commit_parent_sha')}")
    new_commit_sha = receipt.get("new_commit_sha")
    if not (isinstance(new_commit_sha, str) and len(new_commit_sha) == 40
            and all(c in "0123456789abcdef" for c in new_commit_sha.lower())):
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, "SNAPSHOT_NEW_COMMIT_SHA_MALFORMED")

    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_ACTION_LOCAL_SNAPSHOT_COMMITTED, from_state=S_ACTION_EXECUTED_KEPT,
        to_state=S_WORKTREE_BOUND,
        evidence_refs={
            "mission_id": mission_id,
            "action_id": action_id,
            "plan_id": plan_id,
            "ordinal": receipt.get("ordinal"),
            "previous_mission_tip_sha": proj["mission_tip_sha"],
            "new_mission_tip_sha": new_commit_sha,
            "new_commit_sha": new_commit_sha,
            "commit_parent_sha": receipt.get("commit_parent_sha"),
            "committed_paths": committed_paths,
            "snapshot_receipt_id": snapshot_receipt_id,
            "local_snapshot_receipt_record_hash": receipt.get("local_snapshot_receipt_record_hash"),
        },
        actor="STACK",
    )
    if err:
        # Concurrence : une autre écriture a gagné la course sur ce numéro de révision.
        reproj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
        for s in reproj.get("local_snapshots", []):
            if s.get("action_id") == action_id and s.get("snapshot_receipt_id") == snapshot_receipt_id:
                return {"status": STATUS_LOCAL_SNAPSHOT_EVENT_IDEMPOTENT, "reason": "LOST_RACE_REPROJECTED",
                        "mission_id": mission_id, "current_state": reproj.get("current_state"),
                        "mission_tip_sha": reproj.get("mission_tip_sha"),
                        "new_commit_sha": new_commit_sha}
        return _rej(STATUS_LOCAL_SNAPSHOT_RECORD_REJECTED, f"MISSION_TIP_CHAIN_FORK:{err}")

    new_proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    return {
        "status": STATUS_LOCAL_SNAPSHOT_RECORDED, "reason": None, "mission_id": mission_id,
        "current_state": new_proj["current_state"],
        "revision": rec["revision"],
        "mission_revision_record_hash": rec["mission_revision_record_hash"],
        "mission_tip_sha": new_proj["mission_tip_sha"],
        "canonical_base_sha": new_proj["canonical_base_sha"],
        "previous_mission_tip_sha": proj["mission_tip_sha"],
        "new_commit_sha": new_commit_sha,
        "local_snapshot_count": new_proj["local_snapshot_count"],
        "mission_layer_creates_local_git_commit": False,
        "mission_layer_reuses_stage_3a_receipt": True,
        "only_keep_can_advance_mission_tip": True,
    }


# ══════════════════════════════════════════════════════════════════════════
#  4ter — Stage 3D : MissionActionPlan IMMUTABLE (write-once, lié-contenu,
#         NON_SOVEREIGN). Le séquenceur (obsidia_mission_sequencer_v0) le CONSOMME.
#         Aucune identité circulaire : action_id dérive d'ordinaux+champs propres,
#         plan_id dérive du matériel de plan qui INCLUT les action_id.
# ══════════════════════════════════════════════════════════════════════════

_PLAN_ACTION_MATERIAL_FIELDS = (
    "mission_id", "ordinal", "operation", "target_path",
    "source_git_commit", "source_historical_path",
    "test_contract_hash", "dependency_ordinals",
)


def _plan_action_id(mat: dict) -> str:
    return "act-" + _sha256_hex(_canon({k: mat.get(k) for k in _PLAN_ACTION_MATERIAL_FIELDS}))[:32]


def _plan_material(mission_id: str, genesis: dict, action_descriptors: "list[dict]",
                   dependency_edges: "list[dict]") -> str:
    return _canon({
        "plan_schema_version": PLAN_SCHEMA_VERSION,
        "mission_id": mission_id,
        "mission_genesis_record_hash": genesis["mission_genesis_record_hash"],
        "canonical_base_sha": genesis["canonical_base_sha"],
        "branch_name": genesis["branch_name"],
        "worktree_path": genesis["worktree_path"],
        "actions": action_descriptors,
        "dependency_edges": dependency_edges,
    })


def _plans_dir(mission_id: str, store_dir: Path) -> Path:
    return _mission_dir(mission_id, store_dir) / "plans"


def build_mission_action_plan(*, mission_id: str, genesis: dict,
                              actions: "list[dict]") -> "tuple[Optional[dict], Optional[str]]":
    """Construit (JAMAIS ne persiste) le MissionActionPlan immuable. `actions` :
    liste de {ordinal, target_path, source_git_commit, source_historical_path,
    test_contract, dependency_ordinals?}. Renvoie (plan_dict, None) ou (None, reason)."""
    if not isinstance(actions, list) or not actions:
        return None, "PLAN_HAS_NO_ACTIONS"
    seen_ord: set = set()
    descriptors: "list[dict]" = []
    for a in actions:
        if not isinstance(a, dict):
            return None, "ACTION_DESCRIPTOR_NOT_AN_OBJECT"
        ordv = a.get("ordinal")
        if not (isinstance(ordv, int) and not isinstance(ordv, bool) and ordv >= 0):
            return None, "ACTION_ORDINAL_INVALID"
        if ordv in seen_ord:
            return None, f"DUPLICATE_ORDINAL:{ordv}"
        seen_ord.add(ordv)
        op = a.get("operation", SUPPORTED_OPERATION)
        if op != SUPPORTED_OPERATION:
            return None, f"UNSUPPORTED_OPERATION_SHAPE:{op}"
        tp = a.get("target_path")
        if not (isinstance(tp, str) and tp.strip()):
            return None, "ACTION_TARGET_PATH_REQUIRED"
        sgc = a.get("source_git_commit")
        shp = a.get("source_historical_path")
        if not (isinstance(sgc, str) and sgc.strip() and isinstance(shp, str) and shp.strip()):
            return None, "ACTION_SOURCE_REFERENCE_REQUIRED"
        tc = a.get("test_contract")
        if not isinstance(tc, dict) or not isinstance(tc.get("checks"), list):
            return None, "ACTION_TEST_CONTRACT_MALFORMED"
        tc_hash = _TC.compute_test_contract_hash(tc)
        deps = a.get("dependency_ordinals") or []
        if not isinstance(deps, list) or any(not isinstance(d, int) or isinstance(d, bool) for d in deps):
            return None, "ACTION_DEPENDENCY_ORDINALS_MALFORMED"
        if ordv in deps:
            return None, f"ACTION_SELF_DEPENDENCY:{ordv}"
        mat = {
            "mission_id": mission_id, "ordinal": ordv, "operation": op, "target_path": tp,
            "source_git_commit": sgc, "source_historical_path": shp,
            "test_contract_hash": tc_hash, "dependency_ordinals": sorted(set(deps)),
        }
        descriptors.append({
            "action_id": _plan_action_id(mat), "ordinal": ordv, "operation": op,
            "target_path": tp, "source_git_commit": sgc, "source_historical_path": shp,
            "test_contract": tc, "test_contract_hash": tc_hash,
            "dependency_ordinals": sorted(set(deps)),
        })
    descriptors.sort(key=lambda d: d["ordinal"])
    ord_to_aid = {d["ordinal"]: d["action_id"] for d in descriptors}
    for d in descriptors:
        for dep in d["dependency_ordinals"]:
            if dep not in ord_to_aid:
                return None, f"DEPENDENCY_ORDINAL_NOT_IN_PLAN:{dep}"

    dependency_edges = sorted(
        ({"from": d["action_id"], "to": ord_to_aid[dep], "type": _S.DEPENDENCY_CONFIRMED}
         for d in descriptors for dep in d["dependency_ordinals"]),
        key=lambda e: (e["from"], e["to"]),
    )
    cand = [{"candidate_id": d["action_id"]} for d in descriptors]
    cyclic = _S.detect_cycles(cand, dependency_edges)
    if cyclic:
        return None, f"DEPENDENCY_CYCLE:{sorted(cyclic)}"
    execution_order = _S.compute_execution_order(cand, dependency_edges)

    material = _plan_material(mission_id, genesis, descriptors, dependency_edges)
    plan_id = "mpl-" + _sha256_hex(material)[:32]
    plan_hash = _sha256_hex(material)
    from datetime import datetime, timezone
    plan = {
        "plan_schema_version": PLAN_SCHEMA_VERSION,
        "plan_id": plan_id,
        "mission_id": mission_id,
        "mission_genesis_record_hash": genesis["mission_genesis_record_hash"],
        "canonical_base_sha": genesis["canonical_base_sha"],
        "branch_name": genesis["branch_name"],
        "worktree_path": genesis["worktree_path"],
        "actions": descriptors,
        "dependency_edges": dependency_edges,
        "execution_order": execution_order,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "decision_authority": SEMANTIC_DECISION_AUTHORITY,
        "plan_is_execution_authority": False,
        "plan_hash": plan_hash,
    }
    return plan, None


def verify_mission_plan(record: Optional[dict], *, genesis: "Optional[dict]" = None) -> "tuple[bool, Optional[str]]":
    if not isinstance(record, dict):
        return False, "PLAN_RECORD_MISSING"
    if record.get("plan_schema_version") != PLAN_SCHEMA_VERSION:
        return False, "PLAN_SCHEMA_UNSUPPORTED"
    if record.get("decision_authority") != SEMANTIC_DECISION_AUTHORITY:
        return False, "PLAN_DECISION_AUTHORITY_NOT_NON_SOVEREIGN"
    if record.get("plan_is_execution_authority") is not False:
        return False, "PLAN_MUST_NOT_BE_EXECUTION_AUTHORITY"
    acts = record.get("actions")
    if not isinstance(acts, list) or not acts:
        return False, "PLAN_HAS_NO_ACTIONS"
    for d in acts:
        mat = {k: (d.get("ordinal") if k == "ordinal" else
                   sorted(d.get("dependency_ordinals") or []) if k == "dependency_ordinals" else
                   record["mission_id"] if k == "mission_id" else d.get(k))
               for k in _PLAN_ACTION_MATERIAL_FIELDS}
        if d.get("action_id") != _plan_action_id(mat):
            return False, f"ACTION_ID_NOT_DERIVED:{d.get('ordinal')}"
        if d.get("test_contract_hash") != _TC.compute_test_contract_hash(d.get("test_contract") or {}):
            return False, f"ACTION_TEST_CONTRACT_HASH_MISMATCH:{d.get('ordinal')}"
    if genesis is not None:
        material = _plan_material(record["mission_id"], genesis, acts, record.get("dependency_edges") or [])
        if record.get("plan_id") != "mpl-" + _sha256_hex(material)[:32]:
            return False, "PLAN_ID_NOT_DERIVED"
        if record.get("plan_hash") != _sha256_hex(material):
            return False, "PLAN_HASH_MISMATCH"
    return True, None


def load_mission_plan(mission_id: str, plan_id: str, mission_store_dir: "str | Path") -> Optional[dict]:
    try:
        p = _safe_id_path(_plans_dir(mission_id, Path(mission_store_dir)), plan_id)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def bind_mission_plan(*, mission_id: str, actions: "list[dict]",
                      mission_store_dir: "str | Path") -> dict:
    """Valide UN plan borné contre la portée / le budget / le DAG de la mission,
    le persiste write-once, et append une révision PLAN_BOUND. V0 : un seul plan
    par mission (aucune supersession). Le plan N'EST PAS une autorité."""
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_PLAN_BIND_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_WORKTREE_BOUND:
        return _rej(STATUS_PLAN_BIND_REJECTED, f"MISSION_NOT_IN_WORKTREE_BOUND_STATE:{proj['current_state']}")
    if proj.get("active_plan_id"):
        return _rej(STATUS_PLAN_BIND_REJECTED, "PLAN_ALREADY_BOUND")

    genesis = _load_genesis(mission_id, store_dir)
    plan, reason = build_mission_action_plan(mission_id=mission_id, genesis=genesis, actions=actions)
    if plan is None:
        return _rej(STATUS_PLAN_BIND_REJECTED, f"PLAN_MALFORMED:{reason}")

    scope = genesis["scope"]
    if len(plan["actions"]) > scope["max_actions"]:
        return _rej(STATUS_PLAN_BIND_REJECTED, "PLAN_EXCEEDS_MAX_ACTIONS")
    if len(plan["actions"]) > proj["remaining_action_budget"]:
        return _rej(STATUS_PLAN_BIND_REJECTED, "PLAN_EXCEEDS_REMAINING_ACTION_BUDGET")
    atp = scope["allowed_target_paths"]
    if atp is not None:
        for d in plan["actions"]:
            if d["target_path"] not in atp:
                return _rej(STATUS_PLAN_BIND_REJECTED, f"PLAN_TARGET_OUTSIDE_MISSION_SCOPE:{d['target_path']}")
    for d in plan["actions"]:
        if d["operation"] not in scope["allowed_operation_shapes"]:
            return _rej(STATUS_PLAN_BIND_REJECTED, f"PLAN_OPERATION_OUTSIDE_MISSION_SCOPE:{d['operation']}")

    ppath = _safe_id_path(_plans_dir(mission_id, store_dir), plan["plan_id"])
    st = _atomic_publish_json(ppath, plan)
    if st == "IMMUTABILITY_VIOLATION":
        return _rej(STATUS_PLAN_BIND_REJECTED, "PLAN_IMMUTABILITY_VIOLATION")

    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_PLAN_BOUND, from_state=S_WORKTREE_BOUND, to_state=S_WORKTREE_BOUND,
        evidence_refs={
            "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"],
            "action_count": len(plan["actions"]),
            "execution_order": plan["execution_order"],
        },
        actor="HUMAN",
    )
    if err:
        return _rej(STATUS_PLAN_BIND_REJECTED, err)
    return {
        "status": STATUS_PLAN_BOUND, "reason": None, "mission_id": mission_id,
        "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"],
        "plan_store_status": st, "current_state": S_WORKTREE_BOUND,
        "revision": rec["revision"], "mission_revision_record_hash": rec["mission_revision_record_hash"],
        "execution_order": plan["execution_order"],
        "actions": [{"action_id": d["action_id"], "ordinal": d["ordinal"],
                     "target_path": d["target_path"], "dependency_ordinals": d["dependency_ordinals"]}
                    for d in plan["actions"]],
        "plan_is_execution_authority": False,
        "decision_authority": SEMANTIC_DECISION_AUTHORITY,
    }


def close_plan(*, mission_id: str, plan_id: str, mission_store_dir: "str | Path") -> dict:
    """Append PLAN_COMPLETED -> CLOSED_AWAITING_NEXT_PLAN quand CHAQUE action du
    plan a un événement snapshot vérifié. Aucune disposition Git finale (Stage 6)."""
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_PLAN_CLOSE_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_WORKTREE_BOUND:
        return _rej(STATUS_PLAN_CLOSE_REJECTED, f"MISSION_NOT_IN_WORKTREE_BOUND_STATE:{proj['current_state']}")
    if proj.get("active_plan_id") != plan_id:
        return _rej(STATUS_PLAN_CLOSE_REJECTED, "PLAN_ID_NOT_ACTIVE")
    if proj.get("plan_completed"):
        return _rej(STATUS_PLAN_CLOSE_REJECTED, "PLAN_ALREADY_COMPLETED")

    plan = load_mission_plan(mission_id, plan_id, store_dir)
    genesis = _load_genesis(mission_id, store_dir)
    ok_p, reason_p = verify_mission_plan(plan, genesis=genesis)
    if not ok_p:
        return _rej(STATUS_PLAN_CLOSE_REJECTED, f"PLAN_INVALID:{reason_p}")
    if plan["plan_hash"] != proj["active_plan_hash"]:
        return _rej(STATUS_PLAN_CLOSE_REJECTED, "PLAN_HASH_DRIFT")

    done = set(proj["snapshotted_action_ids"])
    missing = [d["action_id"] for d in plan["actions"] if d["action_id"] not in done]
    if missing:
        return _rej(STATUS_PLAN_CLOSE_REJECTED, f"PLAN_ACTIONS_NOT_ALL_SNAPSHOTTED:{missing}")

    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_PLAN_COMPLETED, from_state=S_WORKTREE_BOUND, to_state=S_CLOSED_AWAITING_NEXT_PLAN,
        evidence_refs={"plan_id": plan_id, "plan_hash": plan["plan_hash"],
                       "action_count": len(plan["actions"])},
        actor="STACK",
    )
    if err:
        return _rej(STATUS_PLAN_CLOSE_REJECTED, err)
    return {"status": STATUS_PLAN_COMPLETED, "reason": None, "mission_id": mission_id,
            "plan_id": plan_id, "current_state": S_CLOSED_AWAITING_NEXT_PLAN,
            "revision": rec["revision"], "mission_revision_record_hash": rec["mission_revision_record_hash"],
            "mission_closure_stage_6_still_required": True}


# ══════════════════════════════════════════════════════════════════════════
#  4quater — Stage 4E : liaison HMA + témoin d'action DÉRIVÉ (NON_SOUVERAIN).
#            ÉVIDENCE UNIQUEMENT : n'autorise AUCUNE exécution, ne satisfait
#            AUCUNE HumanApproval, ne touche NI PRE NI KX108. L'HMA elle-même
#            est construite/vérifiée hors de ce module (sous-système d'autorité
#            de mission Stage 4C + couture d'intégration Stage 4E).
# ══════════════════════════════════════════════════════════════════════════

def bind_mission_authority(*, mission_id: str, hma_id: str, hma_record_hash: str,
                           plan_id: str, plan_hash: str,
                           mission_store_dir: "str | Path") -> dict:
    """Append-only `MISSION_AUTHORITY_BOUND`. Self-loop `WORKTREE_BOUND` :
    aucun changement d'état, aucune autorité d'exécution. V0 : une seule HMA
    par mission ; l'HMA doit être liée EXACTEMENT au plan actif."""
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_MISSION_AUTHORITY_BIND_REJECTED,
                    f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if not (_is_64_hex(hma_record_hash) and isinstance(hma_id, str) and hma_id.startswith("hma-")):
        return _rej(STATUS_MISSION_AUTHORITY_BIND_REJECTED, "HMA_REFERENCE_MALFORMED")
    if proj["current_state"] != S_WORKTREE_BOUND:
        return _rej(STATUS_MISSION_AUTHORITY_BIND_REJECTED,
                    f"MISSION_NOT_IN_WORKTREE_BOUND_STATE:{proj['current_state']}")
    if proj.get("active_hma_id"):
        return _rej(STATUS_MISSION_AUTHORITY_BIND_REJECTED, "MISSION_AUTHORITY_ALREADY_BOUND")
    if not proj.get("active_plan_id"):
        return _rej(STATUS_MISSION_AUTHORITY_BIND_REJECTED, "NO_PLAN_BOUND")
    if proj.get("active_plan_id") != plan_id or proj.get("active_plan_hash") != plan_hash:
        return _rej(STATUS_MISSION_AUTHORITY_BIND_REJECTED, "HMA_PLAN_BINDING_MISMATCH")
    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_MISSION_AUTHORITY_BOUND, from_state=S_WORKTREE_BOUND, to_state=S_WORKTREE_BOUND,
        evidence_refs={"hma_id": hma_id, "hma_record_hash": hma_record_hash,
                       "plan_id": plan_id, "plan_hash": plan_hash,
                       "non_sovereign": True, "is_execution_authority": False},
        actor="HUMAN")
    if err:
        return _rej(STATUS_MISSION_AUTHORITY_BIND_REJECTED, err)
    return {"status": STATUS_MISSION_AUTHORITY_BOUND, "reason": None,
            "mission_id": mission_id, "hma_id": hma_id, "hma_record_hash": hma_record_hash,
            "plan_id": plan_id, "plan_hash": plan_hash,
            "mission_authority_mode": "BOUNDED_MISSION_AUTHORITY_PREPARED",
            "revision": rec["revision"],
            "is_execution_authority": False, "non_sovereign": True}


_WITNESS_IDEMPOTENCE_KEY_FIELDS = (
    "ordinal", "daaw_id", "daaw_record_hash",
    "execution_authority_hash", "action_base_sha", "hma_id",
)


def _witnesses_dir(mission_id: str, store_dir: Path) -> Path:
    return _mission_dir(mission_id, store_dir) / "action_authority_witnesses"


def _load_action_authority_witness_artifact(mission_id: str, daaw_id: "Optional[str]",
                                            store_dir: Path) -> Optional[dict]:
    if not (isinstance(daaw_id, str) and daaw_id):
        return None
    try:
        p = _safe_id_path(_witnesses_dir(mission_id, store_dir), daaw_id)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _verify_witness_event_matches_artifact(event_entry: dict,
                                           art: Optional[dict]) -> "tuple[bool, Optional[str]]":
    """L'événement mission NE SUFFIT PAS : l'artefact DAAW write-once canonique
    doit exister et concorder exactement avec la référence de l'événement."""
    if not isinstance(art, dict):
        return False, "ARTIFACT_MISSING"
    if art.get("derived_action_authority_witness_id") != event_entry.get("daaw_id"):
        return False, "DAAW_ID"
    if art.get("daaw_record_hash") != event_entry.get("daaw_record_hash"):
        return False, "RECORD_HASH"
    if art.get("execution_authority_hash") != event_entry.get("execution_authority_hash"):
        return False, "EAH"
    if art.get("action_base_sha") != event_entry.get("action_base_sha"):
        return False, "ACTION_BASE"
    if art.get("human_mission_authorization_id") != event_entry.get("hma_id"):
        return False, "HMA"
    return True, None


def record_action_authority_witness(*, mission_id: str, action_id: str, ordinal: "Optional[int]",
                                    daaw_id: str, daaw_record_hash: str,
                                    execution_authority_hash: str, action_base_sha: str,
                                    hma_id: str, mission_store_dir: "str | Path") -> dict:
    """Append-only `ACTION_AUTHORITY_WITNESS_DERIVED`. Self-loop `ACTION_PREPARED` :
    évidence NON_SOUVERAINE.

    Idempotence liée au MATÉRIEL EXACT du témoin (jamais au seul action_id) :
    un `action_id` déjà consigné avec un `daaw_id` / `daaw_record_hash` /
    `execution_authority_hash` / `action_base_sha` / `ordinal` / `hma_id`
    DIVERGENT échoue fermé (`WITNESS_MATERIAL_DIVERGES_FROM_RECORDED`) — aucune
    révision appendée. Sur duplicata identique : l'identité CANONIQUE consignée
    est renvoyée (jamais le `daaw_id` fourni par l'appelant)."""
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_ACTION_AUTHORITY_WITNESS_REJECTED,
                    f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_ACTION_PREPARED:
        return _rej(STATUS_ACTION_AUTHORITY_WITNESS_REJECTED,
                    f"MISSION_NOT_IN_ACTION_PREPARED_STATE:{proj['current_state']}")
    if proj.get("active_hma_id") != hma_id:
        return _rej(STATUS_ACTION_AUTHORITY_WITNESS_REJECTED, "HMA_NOT_BOUND_TO_MISSION")
    pe = proj.get("last_prepared_evidence") or {}
    if pe.get("action_id") != action_id:
        return _rej(STATUS_ACTION_AUTHORITY_WITNESS_REJECTED, "WITNESS_ACTION_NOT_CURRENTLY_PREPARED")
    if not (_is_64_hex(daaw_record_hash) and _is_64_hex(execution_authority_hash)):
        return _rej(STATUS_ACTION_AUTHORITY_WITNESS_REJECTED, "WITNESS_HASH_MALFORMED")

    already = next((w for w in (proj.get("derived_witnesses") or [])
                    if w.get("action_id") == action_id), None)
    if already is not None:
        supplied = {"ordinal": ordinal, "daaw_id": daaw_id,
                    "daaw_record_hash": daaw_record_hash,
                    "execution_authority_hash": execution_authority_hash,
                    "action_base_sha": action_base_sha, "hma_id": hma_id}
        recorded = {k: already.get(k) for k in _WITNESS_IDEMPOTENCE_KEY_FIELDS}
        if supplied != recorded:
            # AUCUNE révision appendée sur divergence.
            return _rej(STATUS_ACTION_AUTHORITY_WITNESS_REJECTED,
                        "WITNESS_MATERIAL_DIVERGES_FROM_RECORDED",
                        recorded_daaw_id=already.get("daaw_id"),
                        recorded_daaw_record_hash=already.get("daaw_record_hash"))
        art = _load_action_authority_witness_artifact(mission_id, already.get("daaw_id"), store_dir)
        ok_art, why_art = _verify_witness_event_matches_artifact(already, art)
        if not ok_art:
            return _rej(STATUS_ACTION_AUTHORITY_WITNESS_REJECTED,
                        f"WITNESS_ARTIFACT_DISAGREES_WITH_EVENT:{why_art}")
        return {"status": STATUS_ACTION_AUTHORITY_WITNESS_EVENT_IDEMPOTENT, "reason": None,
                "mission_id": mission_id, "action_id": action_id, "ordinal": already.get("ordinal"),
                "daaw_id": already.get("daaw_id"),
                "daaw_record_hash": already.get("daaw_record_hash"),
                "execution_authority_hash": already.get("execution_authority_hash"),
                "action_base_sha": already.get("action_base_sha"),
                "revision": proj["revision"], "idempotent": True,
                "is_execution_authority": False, "non_sovereign": True}
    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_ACTION_AUTHORITY_WITNESS_DERIVED, from_state=S_ACTION_PREPARED, to_state=S_ACTION_PREPARED,
        evidence_refs={"action_id": action_id, "ordinal": ordinal,
                       "daaw_id": daaw_id, "daaw_record_hash": daaw_record_hash,
                       "execution_authority_hash": execution_authority_hash,
                       "action_base_sha": action_base_sha, "hma_id": hma_id,
                       "non_sovereign": True, "is_execution_authority": False},
        actor="STACK")
    if err:
        return _rej(STATUS_ACTION_AUTHORITY_WITNESS_REJECTED, err)
    return {"status": STATUS_ACTION_AUTHORITY_WITNESS_RECORDED, "reason": None,
            "mission_id": mission_id, "action_id": action_id, "ordinal": ordinal,
            "daaw_id": daaw_id, "daaw_record_hash": daaw_record_hash,
            "revision": rec["revision"], "is_execution_authority": False, "non_sovereign": True}


# ══════════════════════════════════════════════════════════════════════════
#  5 — MissionHold structuré (immuable ; resolution_state DÉRIVÉ, jamais stocké)
# ══════════════════════════════════════════════════════════════════════════

def _load_hold(hold_id: str, store_dir: Path) -> Optional[dict]:
    try:
        p = _safe_id_path(store_dir, hold_id)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_hold_record(record: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if record is None:
        return False, "HOLD_RECORD_MISSING"
    if record.get("hold_schema_version") != HOLD_SCHEMA_VERSION:
        return False, "HOLD_SCHEMA_UNSUPPORTED"
    for f in _HOLD_BOUND_FIELDS:
        if f not in record:
            return False, f"HOLD_FIELD_MISSING:{f}"
    if "resolution_state" in record:
        return False, "HOLD_RECORD_MUST_NOT_STORE_MUTABLE_RESOLUTION_STATE"
    if record.get("mission_hold_record_hash") != _record_hash(record, _HOLD_BOUND_FIELDS):
        return False, "HOLD_RECORD_HASH_MISMATCH"
    return True, None


def open_mission_hold(*, mission_id: str, hold_type: str, reason: str, question_for_human: str,
                      evidence_refs: "Optional[list]" = None, bounded_options: "Optional[list]" = None,
                      free_form_decision_allowed: bool = False, action_ref: "Optional[dict]" = None,
                      mission_store_dir: "str | Path", hold_store_dir: "str | Path") -> dict:
    store_dir = Path(mission_store_dir)
    hstore = Path(hold_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir, hold_store_dir=hstore)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_HOLD_OPEN_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] not in (S_WORKTREE_BOUND, S_ACTION_PREPARED):
        return _rej(STATUS_HOLD_OPEN_REJECTED, f"MISSION_NOT_HOLDABLE_FROM_STATE:{proj['current_state']}")
    if hold_type not in HOLD_TYPES:
        return _rej(STATUS_HOLD_OPEN_REJECTED, f"UNKNOWN_HOLD_TYPE:{hold_type}")
    if not (isinstance(reason, str) and reason.strip()):
        return _rej(STATUS_HOLD_OPEN_REJECTED, "HOLD_REASON_REQUIRED")
    if not (isinstance(question_for_human, str) and question_for_human.strip()):
        return _rej(STATUS_HOLD_OPEN_REJECTED, "HOLD_QUESTION_REQUIRED")
    opts = list(bounded_options) if bounded_options else []
    if any(not isinstance(o, str) or not o.strip() for o in opts):
        return _rej(STATUS_HOLD_OPEN_REJECTED, "HOLD_BOUNDED_OPTIONS_MALFORMED")
    if not opts and not free_form_decision_allowed:
        return _rej(STATUS_HOLD_OPEN_REJECTED, "HOLD_HAS_NO_RESOLUTION_PATH")
    ev = list(evidence_refs) if evidence_refs else []

    hold = {
        "hold_schema_version": HOLD_SCHEMA_VERSION,
        "mission_id": mission_id,
        "mission_revision_at_open": proj["revision"],
        "held_from_state": proj["current_state"],
        "action_ref": action_ref,
        "hold_type": hold_type,
        "reason": reason,
        "evidence_refs": ev,
        "question_for_human": question_for_human,
        "bounded_options": sorted(set(opts)),
        "free_form_decision_allowed": bool(free_form_decision_allowed),
        "created_at": _now(),
    }
    seed = _canon({k: hold.get(k) for k in _HOLD_IDENTITY_SEED_FIELDS})
    hold["hold_id"] = "hld-" + _sha256_hex(f"{mission_id}:{proj['revision']}:{seed}")[:32]
    hold["mission_hold_record_hash"] = _record_hash(hold, _HOLD_BOUND_FIELDS)

    st = _atomic_publish_json(_safe_id_path(hstore, hold["hold_id"]), hold)
    if st == "IMMUTABILITY_VIOLATION":
        return _rej(STATUS_HOLD_OPEN_REJECTED, "HOLD_IMMUTABILITY_VIOLATION")

    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_HOLD_OPENED, from_state=proj["current_state"], to_state=S_HELD,
        evidence_refs={
            "hold_id": hold["hold_id"],
            "mission_hold_record_hash": hold["mission_hold_record_hash"],
            "hold_type": hold_type,
            "held_from_state": proj["current_state"],
        },
        actor="STACK",
    )
    if err:
        return _rej(STATUS_HOLD_OPEN_REJECTED, err)
    return {
        "status": STATUS_HOLD_OPENED, "reason": None, "mission_id": mission_id,
        "hold_id": hold["hold_id"], "mission_hold_record_hash": hold["mission_hold_record_hash"],
        "hold_store_status": st, "current_state": S_HELD, "revision": rec["revision"],
        "mission_revision_record_hash": rec["mission_revision_record_hash"],
        "hold_resolution_cannot_mutate_target": True,
    }


# ══════════════════════════════════════════════════════════════════════════
#  6 — HumanMissionDecision (résolution d'intention sémantique — NON_SOVEREIGN)
# ══════════════════════════════════════════════════════════════════════════

def _load_decision(hmd_id: str, store_dir: Path) -> Optional[dict]:
    try:
        p = _safe_id_path(store_dir, hmd_id)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_human_mission_decision(record: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if record is None:
        return False, "HMD_RECORD_MISSING"
    if record.get("human_mission_decision_schema_version") != HUMAN_MISSION_DECISION_SCHEMA_VERSION:
        return False, "HMD_SCHEMA_UNSUPPORTED"
    for f in _HMD_BOUND_FIELDS:
        if f not in record:
            return False, f"HMD_FIELD_MISSING:{f}"
    if record.get("decision_authority") != SEMANTIC_DECISION_AUTHORITY:
        return False, "HMD_DECISION_AUTHORITY_NOT_NON_SOVEREIGN"
    if record.get("not_an_execution_approval") is not True:
        return False, "HMD_MISSING_NOT_AN_EXECUTION_APPROVAL_MARKER"
    # Une HumanMissionDecision ne DOIT PAS porter la signature structurelle d'une HumanApproval.
    for forbidden in ("approval_schema_version", "approval_status", "approved_by",
                      "execution_authority_hash", "approval_record_hash"):
        if forbidden in record:
            return False, f"HMD_CARRIES_FORBIDDEN_APPROVAL_FIELD:{forbidden}"
    if record.get("human_mission_decision_record_hash") != _record_hash(record, _HMD_BOUND_FIELDS):
        return False, "HMD_RECORD_HASH_MISMATCH"
    return True, None


def record_human_mission_decision(*, mission_id: str, hold_id: str, hold_record_hash: str,
                                  chosen_option: "Optional[str]" = None,
                                  free_form_answer: "Optional[str]" = None,
                                  human_decision_ref: "Optional[str]" = None,
                                  mission_store_dir: "str | Path", hold_store_dir: "str | Path",
                                  decision_store_dir: "str | Path") -> dict:
    store_dir = Path(mission_store_dir)
    hstore = Path(hold_store_dir)
    dstore = Path(decision_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir, hold_store_dir=hstore)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_DECISION_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_HELD or proj["active_hold_id"] != hold_id:
        return _rej(STATUS_DECISION_REJECTED, "HOLD_NOT_ACTIVE")

    hold = _load_hold(hold_id, hstore)
    ok_h, reason_h = verify_hold_record(hold)
    if not ok_h:
        return _rej(STATUS_DECISION_REJECTED, f"HOLD_RECORD_INVALID:{reason_h}")
    if hold["mission_id"] != mission_id:
        return _rej(STATUS_DECISION_REJECTED, "HOLD_BELONGS_TO_ANOTHER_MISSION")
    if hold.get("mission_hold_record_hash") != hold_record_hash:
        return _rej(STATUS_DECISION_REJECTED, "HOLD_RECORD_DRIFT")

    opts = hold["bounded_options"]
    ff_allowed = hold["free_form_decision_allowed"]
    has_opt = isinstance(chosen_option, str) and chosen_option.strip() != ""
    has_ff = isinstance(free_form_answer, str) and free_form_answer.strip() != ""
    if has_opt and has_ff:
        return _rej(STATUS_DECISION_REJECTED, "DECISION_AMBIGUOUS_OPTION_AND_FREEFORM")
    if not has_opt and not has_ff:
        return _rej(STATUS_DECISION_REJECTED, "DECISION_EMPTY")
    if has_opt:
        if not opts or chosen_option not in opts:
            return _rej(STATUS_DECISION_REJECTED, "DECISION_OPTION_OUT_OF_BOUNDS")
    if has_ff:
        if not ff_allowed:
            return _rej(STATUS_DECISION_REJECTED, "DECISION_FREEFORM_NOT_ALLOWED")

    hmd = {
        "human_mission_decision_schema_version": HUMAN_MISSION_DECISION_SCHEMA_VERSION,
        "mission_id": mission_id,
        "hold_id": hold_id,
        "hold_record_hash": hold_record_hash,
        "chosen_option": chosen_option if has_opt else None,
        "free_form_answer": free_form_answer if has_ff else None,
        "human_identity_marker": "HUMAN",
        "decision_authority": SEMANTIC_DECISION_AUTHORITY,
        "previous_hold_evidence_hash": hold_record_hash,
        "not_an_execution_approval": True,
        "human_decision_ref": human_decision_ref,
        "created_at": _now(),
    }
    seed = _canon({k: hmd.get(k) for k in _HMD_IDENTITY_SEED_FIELDS})
    hmd["human_mission_decision_id"] = "hmd-" + _sha256_hex(seed)[:32]
    hmd["human_mission_decision_record_hash"] = _record_hash(hmd, _HMD_BOUND_FIELDS)

    st = _atomic_publish_json(_safe_id_path(dstore, hmd["human_mission_decision_id"]), hmd)
    if st == "IMMUTABILITY_VIOLATION":
        return _rej(STATUS_DECISION_REJECTED, "HMD_IMMUTABILITY_VIOLATION")

    # AUCUNE révision, AUCUN changement d'état ici : la résolution est séparée.
    return {
        "status": STATUS_DECISION_RECORDED, "reason": None, "mission_id": mission_id,
        "hold_id": hold_id,
        "human_mission_decision_id": hmd["human_mission_decision_id"],
        "human_mission_decision_record_hash": hmd["human_mission_decision_record_hash"],
        "decision_store_status": st,
        "decision_authority": SEMANTIC_DECISION_AUTHORITY,
        "semantic_decision_is_execution_approval": False,
        "current_state": S_HELD,
    }


# ══════════════════════════════════════════════════════════════════════════
#  7 — Résolution du HOLD + MissionResumeReference (dérivée, liée-contenu)
# ══════════════════════════════════════════════════════════════════════════

def build_resume_reference(*, mission_id: str, mission_revision: int,
                           mission_revision_record_hash: str, hold_id: str, hold_record_hash: str,
                           human_mission_decision_id: str, human_mission_decision_record_hash: str,
                           expected_repository_identity: str, expected_branch_name: str,
                           expected_worktree_path: str, next_allowed_transition: str) -> dict:
    ref = {
        "resume_reference_schema_version": RESUME_REFERENCE_SCHEMA_VERSION,
        "mission_id": mission_id,
        "mission_revision": mission_revision,
        "mission_revision_record_hash": mission_revision_record_hash,
        "hold_id": hold_id,
        "hold_record_hash": hold_record_hash,
        "human_mission_decision_id": human_mission_decision_id,
        "human_mission_decision_record_hash": human_mission_decision_record_hash,
        "expected_repository_identity": expected_repository_identity,
        "expected_branch_name": expected_branch_name,
        "expected_worktree_path": expected_worktree_path,
        # Stage 3B : la reprise exige HEAD == tip de mission DÉRIVÉ (== canonical_base_sha
        # tant qu'aucun snapshot gouverné n'a fait avancer la branche locale).
        "expected_head_relationship": {"ref": "mission_tip_sha", "relation": "EQUAL"},
        "next_allowed_transition": next_allowed_transition,
    }
    ref["resume_reference_hash"] = _sha256_hex(_canon({k: ref.get(k) for k in _RESUME_REF_FIELDS}))
    return ref


def verify_resume_reference(ref: Optional[dict]) -> "tuple[bool, Optional[str]]":
    if not isinstance(ref, dict):
        return False, "RESUME_REFERENCE_MISSING"
    for f in _RESUME_REF_FIELDS:
        if f not in ref:
            return False, f"RESUME_REFERENCE_FIELD_MISSING:{f}"
    if ref.get("resume_reference_hash") != _sha256_hex(_canon({k: ref.get(k) for k in _RESUME_REF_FIELDS})):
        return False, "RESUME_REFERENCE_TAMPERED"
    return True, None


def _reverify_prepared_envelope(prepared_ev: dict, execution_dir: Path,
                                pre_execution_context_dir: Path) -> "tuple[bool, Optional[str]]":
    """Revérifie une enveloppe déjà préparée en RÉUTILISANT le rechargement +
    le recalcul d'EAH CANONIQUES de obsidia_batch_execution (appelés, jamais
    réécrits). Ne mute rien."""
    beid = prepared_ev.get("batch_execution_id")
    envelope = _E._load_execution(beid, execution_dir)
    if envelope is None:
        return False, "PREPARED_ENVELOPE_NOT_FOUND"
    if not envelope.get("integrity_verified"):
        return False, "PREPARED_ENVELOPE_INTEGRITY_NOT_VERIFIED"
    recomputed = _E.compute_execution_authority_hash(envelope)
    if not recomputed or recomputed != envelope.get("execution_authority_hash"):
        return False, "PREPARED_ENVELOPE_EAH_DRIFT"
    if recomputed != prepared_ev.get("execution_authority_hash"):
        return False, "PREPARED_ENVELOPE_EAH_MISMATCH_VS_MISSION_RECORD"
    pcid = envelope.get("pre_execution_context_id")
    pctx = _PEC.load_pre_execution_context_record(pcid, pre_execution_context_dir)
    ok_c, reason_c = _PEC.verify_pre_execution_context_record(pctx)
    if not ok_c:
        return False, f"PREPARED_ENVELOPE_PEC_INVALID:{reason_c}"
    if pctx.get("context_record_hash") != envelope.get("pre_execution_context_record_hash"):
        return False, "PREPARED_ENVELOPE_PEC_HASH_MISMATCH"
    if pctx.get("context_record_hash") != prepared_ev.get("pre_execution_context_record_hash"):
        return False, "PREPARED_ENVELOPE_PEC_HASH_MISMATCH_VS_MISSION_RECORD"
    return True, None


def resolve_mission_hold(*, mission_id: str, hold_id: str, human_mission_decision_id: str,
                         work_unit: "_WU.IsolatedWorkUnit",
                         mission_store_dir: "str | Path", hold_store_dir: "str | Path",
                         decision_store_dir: "str | Path",
                         execution_dir: "Optional[str | Path]" = None,
                         pre_execution_context_dir: "Optional[str | Path]" = None) -> dict:
    store_dir = Path(mission_store_dir)
    hstore = Path(hold_store_dir)
    dstore = Path(decision_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir, hold_store_dir=hstore)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_HELD:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, "MISSION_NOT_HELD")
    if proj["active_hold_id"] != hold_id:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, "HOLD_NOT_ACTIVE")

    hold = _load_hold(hold_id, hstore)
    ok_h, reason_h = verify_hold_record(hold)
    if not ok_h:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, f"HOLD_RECORD_INVALID:{reason_h}")

    hmd = _load_decision(human_mission_decision_id, dstore)
    ok_d, reason_d = verify_human_mission_decision(hmd)
    if not ok_d:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, f"HMD_RECORD_INVALID:{reason_d}")
    if hmd["mission_id"] != mission_id or hmd["hold_id"] != hold_id:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, "DECISION_NOT_BOUND_TO_THIS_HOLD")
    if hmd["hold_record_hash"] != hold.get("mission_hold_record_hash"):
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, "DECISION_NOT_BOUND_TO_THIS_HOLD")
    # option / free-form encore dans les bornes du HOLD
    if hmd.get("chosen_option") is not None and hmd["chosen_option"] not in hold["bounded_options"]:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, "DECISION_OPTION_OUT_OF_BOUNDS")
    if hmd.get("free_form_answer") is not None and not hold["free_form_decision_allowed"]:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, "DECISION_FREEFORM_NOT_ALLOWED")

    genesis = _load_genesis(mission_id, store_dir)
    # Dérive du worktree / branche (helpers PEC — pas de sémantique concurrente).
    # HEAD attendu == tip de mission DÉRIVÉ (avance avec les snapshots gouvernés).
    ok_wt, reason_wt = _verify_mission_worktree_binding(
        genesis, Path(work_unit.worktree_path), Path(work_unit.main_worktree_path),
        require_clean=True, expected_head_sha=proj["mission_tip_sha"],
    )
    if not ok_wt:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, reason_wt)

    target_state = hold["held_from_state"]
    prepared_stale = False
    if target_state == S_ACTION_PREPARED:
        prepared_ev = proj.get("last_prepared_evidence") or {}
        if execution_dir is None or pre_execution_context_dir is None or not prepared_ev:
            prepared_stale = True
        else:
            ok_env, _reason_env = _reverify_prepared_envelope(
                prepared_ev, Path(execution_dir), Path(pre_execution_context_dir),
            )
            prepared_stale = not ok_env
        if prepared_stale:
            target_state = S_WORKTREE_BOUND   # repli sûr — jamais de réutilisation silencieuse

    next_transition = (E_ACTION_PREPARE_SUCCEEDED if target_state == S_WORKTREE_BOUND
                       else E_ACTION_EXECUTE_KEPT)
    resume_ref = build_resume_reference(
        mission_id=mission_id,
        mission_revision=proj["revision"] + 1,
        mission_revision_record_hash="PENDING",   # remplacé ci-dessous par le hash réel
        hold_id=hold_id, hold_record_hash=hold["mission_hold_record_hash"],
        human_mission_decision_id=human_mission_decision_id,
        human_mission_decision_record_hash=hmd["human_mission_decision_record_hash"],
        expected_repository_identity=genesis["repository_identity"],
        expected_branch_name=genesis["branch_name"],
        expected_worktree_path=genesis["worktree_path"],
        next_allowed_transition=next_transition,
    )

    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_HOLD_RESOLVED, from_state=S_HELD, to_state=target_state,
        evidence_refs={
            "hold_id": hold_id,
            "human_mission_decision_id": human_mission_decision_id,
            "human_mission_decision_record_hash": hmd["human_mission_decision_record_hash"],
            "resume_reference_hash": resume_ref["resume_reference_hash"],
            "resumed_to_state": target_state,
            "prepared_envelope_stale": prepared_stale,
        },
        actor="HUMAN",
    )
    if err:
        return _rej(STATUS_HOLD_RESOLVE_REJECTED, err)

    # Le resume_ref publié à l'appelant porte le hash de révision RÉEL.
    resume_ref = build_resume_reference(
        mission_id=mission_id, mission_revision=rec["revision"],
        mission_revision_record_hash=rec["mission_revision_record_hash"],
        hold_id=hold_id, hold_record_hash=hold["mission_hold_record_hash"],
        human_mission_decision_id=human_mission_decision_id,
        human_mission_decision_record_hash=hmd["human_mission_decision_record_hash"],
        expected_repository_identity=genesis["repository_identity"],
        expected_branch_name=genesis["branch_name"],
        expected_worktree_path=genesis["worktree_path"],
        next_allowed_transition=next_transition,
    )
    return {
        "status": STATUS_HOLD_RESOLVED, "reason": None, "mission_id": mission_id,
        "current_state": target_state, "revision": rec["revision"],
        "mission_revision_record_hash": rec["mission_revision_record_hash"],
        "prepared_envelope_stale": prepared_stale,
        "stale_prepared_execution_reuse": False,
        "resume_reference": resume_ref,
        "no_eah_created_by_hold_resolution": True,
        "no_kx108_required_for_semantic_hold_decision": True,
    }


def check_resume_preconditions(*, resume_reference: dict, mission_id: str,
                               work_unit: "_WU.IsolatedWorkUnit",
                               mission_store_dir: "str | Path", hold_store_dir: "str | Path",
                               decision_store_dir: "str | Path",
                               execution_dir: "Optional[str | Path]" = None,
                               pre_execution_context_dir: "Optional[str | Path]" = None) -> dict:
    """Revalidation fail-closed d'une MissionResumeReference contre l'état
    courant. N'écrit rien. Réutilise PEC + le rechargement d'enveloppe /
    recalcul d'EAH canoniques pour les garanties de dérive existantes."""
    ok_r, reason_r = verify_resume_reference(resume_reference)
    if not ok_r:
        return {"resumable": False, "reason": reason_r}
    if resume_reference["mission_id"] != mission_id:
        return {"resumable": False, "reason": "RESUME_REFERENCE_MISSION_MISMATCH"}

    store_dir = Path(mission_store_dir)
    hstore = Path(hold_store_dir)
    dstore = Path(decision_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir, hold_store_dir=hstore)
    if proj["status"] != STATUS_PROJECTION_OK:
        return {"resumable": False, "reason": f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}"}
    if resume_reference["mission_revision_record_hash"] != proj["mission_revision_record_hash"]:
        return {"resumable": False, "reason": "STALE_MISSION_REVISION"}
    if resume_reference["mission_revision"] != proj["revision"]:
        return {"resumable": False, "reason": "STALE_MISSION_REVISION"}

    hmd = _load_decision(resume_reference["human_mission_decision_id"], dstore)
    ok_d, reason_d = verify_human_mission_decision(hmd)
    if not ok_d:
        return {"resumable": False, "reason": f"HMD_RECORD_INVALID:{reason_d}"}
    if hmd["hold_id"] != resume_reference["hold_id"] or \
       hmd["hold_record_hash"] != resume_reference["hold_record_hash"]:
        return {"resumable": False, "reason": "DECISION_NOT_BOUND_TO_THIS_HOLD"}
    if hmd["human_mission_decision_record_hash"] != resume_reference["human_mission_decision_record_hash"]:
        return {"resumable": False, "reason": "DECISION_NOT_BOUND_TO_THIS_HOLD"}

    genesis = _load_genesis(mission_id, store_dir)
    if resume_reference["expected_branch_name"] != genesis["branch_name"] or \
       resume_reference["expected_worktree_path"] != genesis["worktree_path"] or \
       resume_reference["expected_repository_identity"] != genesis["repository_identity"]:
        return {"resumable": False, "reason": "MISSION_WORKTREE_BINDING_DRIFT:GENESIS"}

    ok_wt, reason_wt = _verify_mission_worktree_binding(
        genesis, Path(work_unit.worktree_path), Path(work_unit.main_worktree_path),
        require_clean=(proj["current_state"] != S_ACTION_PREPARED),
        expected_head_sha=proj["mission_tip_sha"],
    )
    if not ok_wt:
        return {"resumable": False, "reason": reason_wt}

    if proj["current_state"] == S_ACTION_PREPARED and execution_dir and pre_execution_context_dir:
        ok_env, reason_env = _reverify_prepared_envelope(
            proj.get("last_prepared_evidence") or {},
            Path(execution_dir), Path(pre_execution_context_dir),
        )
        if not ok_env:
            return {"resumable": False, "reason": "PREPARED_ENVELOPE_STALE", "detail": reason_env}

    return {"resumable": True, "reason": None, "current_state": proj["current_state"],
            "next_allowed_transition": resume_reference["next_allowed_transition"]}


# ══════════════════════════════════════════════════════════════════════════
#  8 — ABORT (HUMAIN) + éligibilité de nettoyage DÉRIVÉE (jamais destructif ici)
# ══════════════════════════════════════════════════════════════════════════

def abort_bounded_mission(*, mission_id: str, abort_class: str, abort_reference: str,
                          mission_store_dir: "str | Path",
                          work_unit: "Optional[_WU.IsolatedWorkUnit]" = None) -> dict:
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_ABORT_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] not in _ABORT_ELIGIBLE_STATES:
        return _rej(STATUS_ABORT_REJECTED, f"MISSION_NOT_ABORT_ELIGIBLE_FROM_STATE:{proj['current_state']}")
    if abort_class not in ABORT_CLASSES:
        return _rej(STATUS_ABORT_REJECTED, f"UNKNOWN_ABORT_CLASS:{abort_class}")
    if not (isinstance(abort_reference, str) and abort_reference.strip()):
        return _rej(STATUS_ABORT_REJECTED, "ABORT_REFERENCE_REQUIRED")

    rec, err = _append_revision(
        mission_id, store_dir, revision=proj["revision"] + 1,
        parent_hash=proj["mission_revision_record_hash"],
        event=E_MISSION_ABORTED, from_state=proj["current_state"], to_state=S_ABORTED,
        evidence_refs={"abort_class": abort_class, "abort_reference": abort_reference,
                       "aborted_from_state": proj["current_state"]},
        actor="HUMAN",
    )
    if err:
        return _rej(STATUS_ABORT_REJECTED, err)

    cleanup = compute_safe_cleanup_eligibility(
        project_mission(mission_id=mission_id, mission_store_dir=store_dir), work_unit,
    )
    return {"status": STATUS_MISSION_ABORTED, "reason": None, "mission_id": mission_id,
            "current_state": S_ABORTED, "revision": rec["revision"],
            "mission_revision_record_hash": rec["mission_revision_record_hash"],
            "abort_class": abort_class,
            "safe_cleanup_eligibility": cleanup,
            "automatic_destructive_cleanup": False}


def compute_safe_cleanup_eligibility(projection: dict,
                                     work_unit: "Optional[_WU.IsolatedWorkUnit]") -> dict:
    """DÉRIVÉE, fail-closed, ne nettoie JAMAIS. Éligible seulement si les
    préconditions du cycle de vie Checkpoint 1 tiennent ET qu'aucune
    évidence / travail local conservé n'exige une disposition Git humaine."""
    if projection.get("status") != STATUS_PROJECTION_OK:
        return {"eligible": False, "reason": "MISSION_NOT_PROJECTABLE"}
    state = projection["current_state"]
    # Stage 3B : une mission qui a créé des commits de snapshot local N'EST PAS
    # équivalente à une branche intouchée à canonical_base_sha — la disposition
    # Git est une décision humaine, jamais un nettoyage automatique.
    if projection.get("has_local_mission_snapshots"):
        return {"eligible": False, "reason": "SNAPSHOT_MISSION_REQUIRES_HUMAN_GIT_DISPOSITION"}
    if projection["linked_governed_executions"]:
        return {"eligible": False, "reason": "GOVERNED_EXECUTION_EVIDENCE_PRESENT"}
    if state in (S_ACTION_EXECUTED_KEPT, S_ACTION_FAILED_QUARANTINE, S_ACTION_EXECUTED_ROLLED_BACK):
        return {"eligible": False, "reason": f"STATE_REQUIRES_HUMAN_GIT_DISPOSITION:{state}"}
    if projection["last_prepared_evidence"] and state == S_ACTION_PREPARED:
        return {"eligible": False, "reason": "PREPARED_ENVELOPE_EVIDENCE_PRESENT"}
    if not isinstance(work_unit, _WU.IsolatedWorkUnit):
        return {"eligible": False, "reason": "NO_WORK_UNIT_HANDLE"}
    if not work_unit.created_by_this_component:
        return {"eligible": False, "reason": "WORK_UNIT_NOT_CREATED_BY_CHECKPOINT_1"}
    try:
        rc, st_out, _ = _PEC._run_git(["status", "--porcelain"], cwd=Path(work_unit.worktree_path))
        rc2, head_out, _ = _PEC._run_git(["rev-parse", "HEAD"], cwd=Path(work_unit.worktree_path))
    except Exception:
        return {"eligible": False, "reason": "WORKTREE_FACTS_UNREADABLE"}
    if rc != 0 or st_out.strip() != "":
        return {"eligible": False, "reason": "WORKTREE_NOT_CLEAN"}
    if rc2 != 0 or head_out.strip() != projection["mission_tip_sha"]:
        return {"eligible": False, "reason": "HEAD_NOT_AT_MISSION_TIP_SHA"}
    return {"eligible": True, "reason": None,
            "note": "delegate actual removal to obsidia_isolated_work_unit_v0.dispose_isolated_work_unit"}


# ══════════════════════════════════════════════════════════════════════════
#  util
# ══════════════════════════════════════════════════════════════════════════

def _rej(status: str, reason: str, **extra) -> dict:
    return {"status": status, "reason": reason, "authority": "NON_SOVEREIGN",
            "decision_authority": DECISION_AUTHORITY,
            "mission_object_is_execution_authority": False, **extra}
