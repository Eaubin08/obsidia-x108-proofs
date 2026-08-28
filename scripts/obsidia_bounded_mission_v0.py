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

DECISION_AUTHORITY = "KX108_ONLY"
SEMANTIC_DECISION_AUTHORITY = "NON_SOVEREIGN"
SUPPORTED_OPERATION = "UPDATE_TARGET_FROM_SOURCE"

GENESIS_SCHEMA_VERSION = 1
REVISION_SCHEMA_VERSION = 1
HOLD_SCHEMA_VERSION = 1
HUMAN_MISSION_DECISION_SCHEMA_VERSION = 1
RESUME_REFERENCE_SCHEMA_VERSION = 1

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
                                     main_worktree_path: Path, *, require_clean: bool) -> "tuple[bool, Optional[str]]":
    """Revérifie le lien mission<->worktree à partir de FAITS Git observés
    (helpers PEC), jamais d'assertions. Aucune seconde implémentation
    d'isolation Git."""
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
    # Stage 2 : aucune disposition Git, HEAD reste == canonical_base_sha.
    if head_out.strip() != genesis["canonical_base_sha"]:
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
            linked_execution_ids.append({
                "batch_execution_id": ev.get("batch_execution_id"),
                "child_execution_id": ev.get("child_execution_id"),
                "execution_authority_hash": ev.get("execution_authority_hash"),
                "outcome_status": ev.get("driver_status"),
                "approval_id": ev.get("approval_id"),
                "kx108_pre_decision_record_id": ev.get("kx108_pre_decision_record_id"),
                "kx108_pre_gate": ev.get("kx108_pre_gate"),
                "kx108_post_gate": ev.get("kx108_post_gate"),
                "rollback_result_id": ev.get("rollback_result_id"),
            })
        elif event == E_MISSION_ABORTED:
            aborted_from_state = rev.get("from_state")
            for h in holds.values():
                if h["resolution_state"] == "OPEN":
                    h["resolution_state"] = "SUPERSEDED"
            active_hold_id = None

        state = to_state
        prev_hash = rev["mission_revision_record_hash"]

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
        "unknowns": unknowns,
    }


def _proj_invalid(mission_id: str, reason: str) -> dict:
    return {"status": STATUS_MISSION_PROJECTION_INVALID, "mission_id": mission_id, "reason": reason}


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

    # 2. Faits Git observés (helpers PEC — jamais une seconde implémentation)
    ok, reason = _verify_mission_worktree_binding(
        genesis, Path(work_unit.worktree_path), Path(work_unit.main_worktree_path),
        require_clean=True,
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
                           repository_identity: "Optional[str]" = None) -> dict:
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

    # Délégation VERBATIM au pont Checkpoint 1 (aucune étape du driver reproduite)
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
                           human_authorized_execution_authority_hash: str,
                           human_authorization_reference: str,
                           execution_dir: "str | Path", pre_execution_context_dir: "str | Path",
                           selector_dir: "str | Path", ledger_dir: "str | Path",
                           kx108_pre_decision_dir: "str | Path", kx108_post_decision_dir: "str | Path",
                           test_contract_results_dir: "str | Path", sealed_receipt_dir: "str | Path",
                           sealed_rollback_evidence_dir: "str | Path", rollback_result_dir: "str | Path",
                           mission_store_dir: "str | Path",
                           approval_dir: "Optional[str | Path]" = None) -> dict:
    store_dir = Path(mission_store_dir)
    proj = project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != STATUS_PROJECTION_OK:
        return _rej(STATUS_EXECUTE_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if proj["current_state"] != S_ACTION_PREPARED:
        return _rej(STATUS_EXECUTE_REJECTED, f"MISSION_NOT_IN_ACTION_PREPARED_STATE:{proj['current_state']}")

    prepared = proj.get("last_prepared_evidence") or {}
    if prepared.get("batch_execution_id") != batch_execution_id or \
       prepared.get("child_execution_id") != child_execution_id:
        return _rej(STATUS_EXECUTE_REJECTED, "EXECUTE_IDS_DO_NOT_MATCH_PREPARED_ACTION")

    # Délégation VERBATIM au pont Checkpoint 1 : c'est LUI (+ driver + PEC) qui
    # recharge l'enveloppe, recalcule l'EAH, exige recomputed == stored == humain,
    # persiste la HumanApproval, invoque KX108 PRE/POST, C2, D1/D2. La couche
    # mission ne fabrique RIEN de tout cela.
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

    ev = {
        "driver_status": dstatus,
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child_execution_id,
        "execution_authority_hash": driver_result.get("execution_authority_hash"),
        "approval_id": driver_result.get("approval_id"),
        "human_authorization_reference": human_authorization_reference,
        "kx108_pre_decision_record_id": driver_result.get("kx108_pre_decision_record_id"),
        "kx108_pre_gate": driver_result.get("kx108_pre_gate"),
        "kx108_post_gate": driver_result.get("kx108_post_gate"),
        "rollback_result_id": driver_result.get("rollback_result_id"),
        "sealed_apply_receipt_id": driver_result.get("sealed_apply_receipt_id"),
        "sealed_rollback_evidence_id": driver_result.get("sealed_rollback_evidence_id"),
        "target_mutated": bool(driver_result.get("target_mutated")) if "target_mutated" in driver_result else None,
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
        "expected_head_relationship": {"ref": "canonical_base_sha", "relation": "EQUAL"},
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
    # Dérive du worktree / branche (helpers PEC — pas de sémantique concurrente)
    ok_wt, reason_wt = _verify_mission_worktree_binding(
        genesis, Path(work_unit.worktree_path), Path(work_unit.main_worktree_path),
        require_clean=True,
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
    if rc2 != 0 or head_out.strip() != projection["canonical_base_sha"]:
        return {"eligible": False, "reason": "HEAD_NOT_AT_CANONICAL_BASE_SHA"}
    return {"eligible": True, "reason": None,
            "note": "delegate actual removal to obsidia_isolated_work_unit_v0.dispose_isolated_work_unit"}


# ══════════════════════════════════════════════════════════════════════════
#  util
# ══════════════════════════════════════════════════════════════════════════

def _rej(status: str, reason: str, **extra) -> dict:
    return {"status": status, "reason": reason, "authority": "NON_SOVEREIGN",
            "decision_authority": DECISION_AUTHORITY,
            "mission_object_is_execution_authority": False, **extra}
