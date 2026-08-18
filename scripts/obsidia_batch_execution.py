"""
obsidia_batch_execution.py
===========================
BATCH_EXECUTION_ENVELOPE_V0 — pont borné entre un BatchProposal (Selector)
et des sessions de build/Obsidure existantes, UN CHILD PAR CANDIDAT.

Flux :
  BatchProposal (immuable, déjà produit par obsidia_batch_selector)
  → vérification d'intégrité (aucune dérive de hash/ordre/dépendances)
  → BatchExecutionEnvelope (parent, NON-SOUVERAIN)
      → ChildExecutionRecord (un par candidat sélectionné)
          → gate de matérialité (source == target ? aucun delta ?)
          → gate d'opération (transformation définie ou non ?)
          → propagation d'échec de dépendance (à l'exécution)
  → projection d'agrégat (jamais une décision KX108)

AUTORITÉ :
  BATCH_EXECUTION_CAN_PLAN                    = TRUE
  BATCH_EXECUTION_CAN_SEQUENCE                = TRUE
  BATCH_EXECUTION_CAN_PROPAGATE_DEP_FAILURE   = TRUE

  BATCH_EXECUTION_CAN_DECIDE_KX108            = FALSE
  BATCH_EXECUTION_CAN_COMMIT                  = FALSE
  BATCH_EXECUTION_CAN_PUSH                    = FALSE
  BATCH_EXECUTION_CAN_MERGE                   = FALSE

  CHILD_DECISION_AUTHORITY = KX108_ONLY

Le statut agrégat du parent (aggregate_status) est TOUJOURS une simple
PROJECTION des statuts enfants — jamais une décision KX108, jamais une
autorisation de commit.
"""

from __future__ import annotations

import hashlib
import json
import os
import datetime
from pathlib import Path
from typing import Optional, Callable

SCHEMA_VERSION = "V0"
DECISION_AUTHORITY = "KX108_ONLY"
EXECUTION_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "batch_execution"

_REPO_ROOT = Path(__file__).resolve().parent.parent

PROTECTED_PATH_PREFIXES = frozenset([
    "proofs/",
    "formal/",
    "runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs",
    "merkle_seal.json",
])

# ─── Statuts matérialité / opération ──────────────────────────────────────────

NO_MEANINGFUL_DELTA          = "NO_MEANINGFUL_DELTA"
MEANINGFUL_DELTA             = "MEANINGFUL_DELTA"
MATERIALITY_UNKNOWN          = "UNKNOWN"

# ─── Statuts d'exécution d'un enfant ──────────────────────────────────────────

PLANNED                    = "PLANNED"
NOT_READY_NO_DELTA          = "NOT_READY_NO_DELTA"
NOT_READY_UNDEFINED_OPERATION = "NOT_READY_UNDEFINED_OPERATION"
DEPENDENCY_BLOCKED          = "DEPENDENCY_BLOCKED"
REFUSED_PROTECTED_TARGET    = "REFUSED_PROTECTED_TARGET"
SOURCE_INTEGRITY_MISMATCH   = "SOURCE_INTEGRITY_MISMATCH"
TARGET_PRECONDITION_MISMATCH = "TARGET_PRECONDITION_MISMATCH"
EXECUTED_ACT                = "EXECUTED_ACT"
EXECUTED_HOLD               = "EXECUTED_HOLD"
EXECUTED_BLOCK               = "EXECUTED_BLOCK"
EXECUTED_ERROR               = "EXECUTED_ERROR"

_TERMINAL_STATUSES = frozenset([
    NOT_READY_NO_DELTA, NOT_READY_UNDEFINED_OPERATION, DEPENDENCY_BLOCKED,
    REFUSED_PROTECTED_TARGET, SOURCE_INTEGRITY_MISMATCH,
    TARGET_PRECONDITION_MISMATCH, EXECUTED_ACT, EXECUTED_HOLD, EXECUTED_BLOCK,
    EXECUTED_ERROR,
])

# ─── Statuts d'approbation d'exécution (parent) ──────────────────────────────

APPROVED_FOR_BOUNDED_EXECUTION = "APPROVED_FOR_BOUNDED_EXECUTION"
EXECUTION_APPROVAL_VALID        = "EXECUTION_APPROVAL_VALID"
EXECUTION_APPROVAL_INVALID      = "EXECUTION_APPROVAL_INVALID"

# ─── Statuts agrégat (parent) — PROJECTION UNIQUEMENT ────────────────────────

BATCH_EXECUTION_NOT_READY = "BATCH_EXECUTION_NOT_READY"
BATCH_PLANNED              = "BATCH_PLANNED"
BATCH_COMPLETE              = "BATCH_COMPLETE"
BATCH_PARTIAL                = "BATCH_PARTIAL"
BATCH_HOLD                   = "BATCH_HOLD"
BATCH_ERROR                  = "BATCH_ERROR"

# ─── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _content_hash(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _is_protected(path: str) -> bool:
    for prefix in PROTECTED_PATH_PREFIXES:
        if path.startswith(prefix) or path == prefix.rstrip("/"):
            return True
    return False


def _selector_module():
    import sys as _sys
    _scripts = str(Path(__file__).resolve().parent)
    if _scripts not in _sys.path:
        _sys.path.insert(0, _scripts)
    import obsidia_batch_selector as _mod
    return _mod


# ─── Stockage (hors repo, %LOCALAPPDATA%\Obsidia\batch_execution\) ───────────

def _execution_path(batch_execution_id: str, execution_dir: Optional[Path] = None) -> Path:
    d = execution_dir or EXECUTION_DIR
    return d / "executions" / batch_execution_id / "execution.json"


def _save_execution(envelope: dict, execution_dir: Optional[Path] = None) -> Path:
    p = _execution_path(envelope["batch_execution_id"], execution_dir)
    _ensure_dir(p.parent)
    p.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _load_execution(batch_execution_id: str, execution_dir: Optional[Path] = None) -> Optional[dict]:
    p = _execution_path(batch_execution_id, execution_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _list_executions(execution_dir: Optional[Path] = None) -> list:
    d = (execution_dir or EXECUTION_DIR) / "executions"
    if not d.exists():
        return []
    result = []
    for entry in sorted(d.iterdir()):
        if entry.is_dir():
            ep = entry / "execution.json"
            if ep.exists():
                try:
                    result.append(json.loads(ep.read_text(encoding="utf-8")))
                except (json.JSONDecodeError, OSError):
                    pass
    return result


# ─── Enregistrement d'approbation (append-only, distinct de KX108) ───────────

def _approval_path(approval_id: str, execution_dir: Optional[Path] = None) -> Path:
    d = execution_dir or EXECUTION_DIR
    return d / "approvals" / approval_id / "approval.json"


def _save_approval(record: dict, execution_dir: Optional[Path] = None) -> Path:
    p = _approval_path(record["approval_id"], execution_dir)
    _ensure_dir(p.parent)
    p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _load_approval(approval_id: str, execution_dir: Optional[Path] = None) -> Optional[dict]:
    p = _approval_path(approval_id, execution_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def create_approval_record(envelope: dict, execution_dir: Optional[Path] = None) -> dict:
    """
    Enregistrement d'approbation APPEND-ONLY, distinct de
    BatchExecutionEnvelope (jamais réécrit) et distinct de toute décision
    KX108. Signifie UNIQUEMENT « autorisation de TENTER une exécution
    bornée » — jamais ACT, jamais commit/push/merge. decision_authority
    reste KX108_ONLY.
    """
    approval_id = _sha16(f"{envelope['batch_execution_id']}:{_now()}")
    record = {
        "approval_id": approval_id,
        "schema_version": SCHEMA_VERSION,
        "created_at": _now(),
        "batch_execution_id": envelope["batch_execution_id"],
        "batch_id": envelope["batch_id"],
        "batch_hash": envelope["batch_hash"],
        "candidate_scope_hash": envelope["candidate_scope_hash"],
        "approved_by": "HUMAN",
        "status": APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": DECISION_AUTHORITY,
    }
    _save_approval(record, execution_dir)
    return record


def _validate_approval(approval: Optional[dict], envelope: dict) -> tuple[bool, Optional[str]]:
    """
    Fail-closed sur toute divergence. Une approbation valide ouvre
    seulement la porte à une TENTATIVE d'exécution — elle ne peut JAMAIS
    lever un gate de preuve (matérialité, dépendance, intégrité,
    protection).
    """
    if approval is None:
        return False, "APPROVAL_MISSING"
    if approval.get("batch_execution_id") != envelope.get("batch_execution_id"):
        return False, "APPROVAL_WRONG_EXECUTION_ID"
    if approval.get("batch_id") != envelope.get("batch_id"):
        return False, "APPROVAL_WRONG_BATCH_ID"
    if approval.get("batch_hash") != envelope.get("batch_hash"):
        return False, "APPROVAL_WRONG_BATCH_HASH"
    if approval.get("candidate_scope_hash") != envelope.get("candidate_scope_hash"):
        return False, "APPROVAL_WRONG_SCOPE_HASH"
    if approval.get("status") != APPROVED_FOR_BOUNDED_EXECUTION:
        return False, "APPROVAL_STATUS_INVALID"
    if approval.get("approved_by") != "HUMAN":
        return False, "APPROVAL_NOT_HUMAN"
    return True, None


def _resolve_and_hash(path_str: Optional[str], root: Path) -> Optional[str]:
    """Lecture réelle — ne fabrique jamais un hash. None si absent/illisible."""
    if not path_str:
        return None
    p = Path(path_str)
    if not p.is_absolute():
        p = root / path_str
    return _content_hash(p)


# ─── Intégrité : liaison immuable au BatchProposal stocké ────────────────────

def verify_batch_integrity(
    proposal: dict,
    ledger_dir: Optional[Path] = None,
) -> tuple[bool, Optional[str]]:
    """
    Vérifie que le BatchProposal stocké n'a pas dérivé par rapport à l'état
    ACTUEL du Ledger (hash de contenu, target_path, arêtes de dépendance,
    ordre d'exécution recalculé). Ne modifie rien. Ne recalcule PAS une
    sélection différente — vérifie seulement que la sélection immuable
    reste fidèle aux preuves actuelles.
    """
    if proposal.get("candidate_scope_mode") != "EXPLICIT_ENTRY_IDS":
        return False, "GLOBAL_MODE_NOT_VERIFIABLE_FOR_EXECUTION"

    scope_ids = proposal.get("candidate_entry_ids")
    if not scope_ids:
        return False, "MISSING_CANDIDATE_ENTRY_IDS"

    sel = _selector_module()
    universe = sel._load_ledger_universe(ledger_dir)
    by_id = {e.get("ledger_entry_id"): e for e in universe}

    stored_selected = proposal.get("selected_entries") or []
    selected_ids = {c.get("candidate_id") for c in stored_selected}

    for c in stored_selected:
        eid = c.get("candidate_id")
        current = by_id.get(eid)
        if current is None:
            return False, f"CANDIDATE_NO_LONGER_IN_LEDGER:{eid}"
        if current.get("source_hash") != c.get("source_hash"):
            return False, f"SOURCE_HASH_DRIFT:{eid}"
        if current.get("target_path") != c.get("target_path"):
            return False, f"TARGET_PATH_DRIFT:{eid}"

    entry_index = sel.build_entry_index_from_ledger(ledger_dir)
    candidates = sel.build_candidates_from_ledger(ledger_dir, None, scope_ids)
    edges = sel.detect_dependencies(candidates, entry_index)
    selected_candidates = [c for c in candidates if c["candidate_id"] in selected_ids]
    recomputed_order = sel.compute_execution_order(selected_candidates, edges)

    stored_order = proposal.get("execution_order") or []
    if recomputed_order != stored_order:
        return False, "EXECUTION_ORDER_MISMATCH"

    stored_edges = {
        (e.get("from"), e.get("to"), e.get("type"))
        for e in (proposal.get("dependency_edges") or [])
    }
    recomputed_edges = {
        (e.get("from"), e.get("to"), e.get("type"))
        for e in edges
        if e.get("from") in selected_ids or e.get("to") in selected_ids
    }
    if stored_edges != recomputed_edges:
        return False, "DEPENDENCY_EDGES_MISMATCH"

    return True, None


# ─── Gate de matérialité ──────────────────────────────────────────────────────

def assess_materiality(
    source_path: Optional[str],
    target_path: Optional[str],
    source_hash: Optional[str],
    repo_root: Optional[Path] = None,
) -> tuple[str, dict]:
    """
    NO_MEANINGFUL_DELTA : source et cible sont le même fichier physique, OU
                            la cible existe déjà avec un contenu identique.
    MEANINGFUL_DELTA      : la cible existe avec un contenu différent, ou
                            n'existe pas encore.
    UNKNOWN                : target_path absent — impossible à évaluer.
    Ne fabrique jamais de hash — lecture réelle uniquement.
    """
    root = repo_root or _REPO_ROOT
    if not target_path:
        return MATERIALITY_UNKNOWN, {"reason": "target_path_missing"}

    if source_path and source_path == target_path:
        return NO_MEANINGFUL_DELTA, {
            "reason": "source_equals_target_path",
            "target_pre_hash": source_hash,
        }

    tp = Path(target_path)
    if not tp.is_absolute():
        tp = root / target_path
    target_pre_hash = _content_hash(tp)

    if target_pre_hash is None:
        return MEANINGFUL_DELTA, {"reason": "target_does_not_exist_yet", "target_pre_hash": None}
    if target_pre_hash == source_hash:
        return NO_MEANINGFUL_DELTA, {
            "reason": "target_content_equals_source",
            "target_pre_hash": target_pre_hash,
        }
    return MEANINGFUL_DELTA, {"reason": "target_content_differs", "target_pre_hash": target_pre_hash}


# ─── Gate d'opération ──────────────────────────────────────────────────────────

def assess_operation(provenance_refs: Optional[dict]) -> tuple[Optional[str], Optional[str]]:
    """
    Retourne (operation_type, operation_reason) ou (None, None) si aucune
    opération légitime n'est établie. N'invente JAMAIS une opération depuis
    le nom de fichier — seule une preuve explicite enregistrée dans
    provenance_refs (au moment du register_source ou d'un lien ultérieur)
    compte.
    """
    prov = provenance_refs or {}
    op_type = prov.get("operation_type")
    if op_type:
        return op_type, prov.get("operation_reason")
    return None, None


# ─── Préparation (READ-ONLY côté cibles) ──────────────────────────────────────

def prepare_execution(
    batch_id: str,
    ledger_dir: Optional[Path] = None,
    selector_dir: Optional[Path] = None,
    execution_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> dict:
    """
    Charge le BatchProposal stocké, vérifie son intégrité, construit
    l'enveloppe d'exécution (parent non-souverain) + un ChildExecutionRecord
    par candidat sélectionné, applique les gates de matérialité/opération.
    Ne crée AUCUNE session, n'invoque AUCUN Obsidure, AUCUN KX108.
    """
    sel = _selector_module()
    proposal = sel._load_batch(batch_id, selector_dir)

    batch_execution_id = _sha16(f"{batch_id}:{_now()}")

    if proposal is None:
        envelope = _blank_envelope(
            batch_execution_id, batch_id, None, None,
            aggregate_status=BATCH_ERROR,
            integrity_error="BATCH_PROPOSAL_NOT_FOUND",
        )
        _save_execution(envelope, execution_dir)
        return envelope

    ok, err = verify_batch_integrity(proposal, ledger_dir)
    if not ok:
        envelope = _blank_envelope(
            batch_execution_id, batch_id, proposal.get("batch_hash"),
            proposal.get("candidate_scope_hash"),
            aggregate_status=BATCH_HOLD,
            integrity_error=f"BATCH_PROPOSAL_INTEGRITY_MISMATCH:{err}",
        )
        _save_execution(envelope, execution_dir)
        return envelope

    root = repo_root or _REPO_ROOT
    selected = proposal.get("selected_entries") or []
    execution_order = proposal.get("execution_order") or [c["candidate_id"] for c in selected]
    dependency_edges = proposal.get("dependency_edges") or []
    by_id = {c["candidate_id"]: c for c in selected}

    # dépendances CONFIRMED restreintes aux candidats sélectionnés
    deps_by_child: dict[str, list[str]] = {cid: [] for cid in by_id}
    for e in dependency_edges:
        if e.get("type") != "DEPENDENCY_CONFIRMED":
            continue
        frm, to = e.get("from"), e.get("to")
        if frm in by_id and to in by_id:
            deps_by_child[frm].append(to)

    children: list[dict] = []
    for position, cid in enumerate(execution_order):
        c = by_id.get(cid)
        if c is None:
            continue
        source_path = c.get("source_path")
        target_path = c.get("target_path")
        source_hash = c.get("source_hash")

        protected = bool(target_path and _is_protected(target_path))

        materiality_status, materiality_detail = assess_materiality(
            source_path, target_path, source_hash, root,
        )
        operation_type, operation_reason = assess_operation(c.get("provenance_refs"))

        if protected:
            execution_status = REFUSED_PROTECTED_TARGET
        elif materiality_status != MEANINGFUL_DELTA:
            execution_status = NOT_READY_NO_DELTA
        elif operation_type is None:
            execution_status = NOT_READY_UNDEFINED_OPERATION
        else:
            execution_status = PLANNED

        child = {
            "child_execution_id": _sha16(f"{batch_execution_id}:{cid}"),
            "batch_execution_id": batch_execution_id,
            "candidate_entry_id": cid,
            "source_path": source_path,
            "source_hash": source_hash,
            "target_path": target_path,
            "target_pre_hash": materiality_detail.get("target_pre_hash"),
            "operation_type": operation_type,
            "operation_reason": operation_reason,
            "materiality_status": materiality_status,
            "materiality_detail": materiality_detail,
            "dependencies": deps_by_child.get(cid, []),
            "dependency_status": "NOT_APPLICABLE" if not deps_by_child.get(cid) else "PENDING",
            "execution_position": position,
            "session_id": None,
            "proposal_id": None,
            "kx108_decision": None,
            "execution_status": execution_status,
            "decision_authority": DECISION_AUTHORITY,
        }
        children.append(child)

    aggregate_status = _compute_aggregate_status(children)

    envelope = {
        "batch_execution_id": batch_execution_id,
        "schema_version": SCHEMA_VERSION,
        "created_at": _now(),

        "batch_id": batch_id,
        "batch_hash": proposal.get("batch_hash"),
        "candidate_scope_hash": proposal.get("candidate_scope_hash"),

        "human_execution_approved": False,
        "decision_authority": DECISION_AUTHORITY,

        "execution_order": execution_order,
        "dependency_edges": dependency_edges,

        "children": children,
        "aggregate_status": aggregate_status,

        "risk_flags": [],
        "unknowns": [],

        "source_batch_ref": {
            "batch_id": batch_id,
            "batch_hash": proposal.get("batch_hash"),
        },

        "integrity_verified": True,
        "integrity_error": None,

        "execution_approval_status": None,
        "execution_approval_id": None,
    }

    _save_execution(envelope, execution_dir)
    return envelope


def _blank_envelope(
    batch_execution_id: str,
    batch_id: str,
    batch_hash: Optional[str],
    candidate_scope_hash: Optional[str],
    aggregate_status: str,
    integrity_error: str,
) -> dict:
    return {
        "batch_execution_id": batch_execution_id,
        "schema_version": SCHEMA_VERSION,
        "created_at": _now(),
        "batch_id": batch_id,
        "batch_hash": batch_hash,
        "candidate_scope_hash": candidate_scope_hash,
        "human_execution_approved": False,
        "decision_authority": DECISION_AUTHORITY,
        "execution_order": [],
        "dependency_edges": [],
        "children": [],
        "aggregate_status": aggregate_status,
        "risk_flags": [],
        "unknowns": [integrity_error] if integrity_error else [],
        "source_batch_ref": {"batch_id": batch_id, "batch_hash": batch_hash},
        "integrity_verified": False,
        "integrity_error": integrity_error,
        "execution_approval_status": None,
        "execution_approval_id": None,
    }


def executable_candidate_count(envelope: dict) -> int:
    return sum(1 for c in envelope.get("children", []) if c["execution_status"] == PLANNED)


# ─── Agrégat (projection uniquement — jamais une décision KX108) ────────────

def _compute_aggregate_status(children: list[dict]) -> str:
    if not children:
        return BATCH_EXECUTION_NOT_READY

    statuses = [c["execution_status"] for c in children]

    if all(s in (NOT_READY_NO_DELTA, NOT_READY_UNDEFINED_OPERATION, REFUSED_PROTECTED_TARGET) for s in statuses):
        return BATCH_EXECUTION_NOT_READY

    if any(s == PLANNED for s in statuses):
        return BATCH_PLANNED

    executed = [s for s in statuses if s.startswith("EXECUTED_")]
    if not executed:
        return BATCH_HOLD

    attempted = [
        s for s in statuses
        if s not in (NOT_READY_NO_DELTA, NOT_READY_UNDEFINED_OPERATION, REFUSED_PROTECTED_TARGET)
    ]
    if attempted and all(s == EXECUTED_ACT for s in attempted):
        return BATCH_COMPLETE

    return BATCH_PARTIAL


# ─── Bridge réel (lecture seule) vers la planification existante ────────────

def real_session_executor_via_compute_plan(child: dict, repo_root: Optional[Path] = None) -> dict:
    """
    Bridge RÉEL — réutilise obsidia_build.compute_plan (fonction pure,
    aucune écriture) pour vérifier si le pipeline existant peut produire un
    plan dont approved_scope_proposal correspond EXACTEMENT à la cible de
    ce child. compute_plan() découvre les fichiers candidats depuis un
    texte d'objectif (heuristique par mots-clés) — il n'existe PAS de
    primitive acceptant un target_path explicite unique.

    Si la portée découverte ne correspond pas exactement, le bridge échoue
    fermé plutôt que d'halluciner une session à portée erronée. Ce module
    NE CRÉE JAMAIS de session réelle (cmd_execute), N'APPELLE JAMAIS KX108
    — matérialiser une session reste un geste séparé, humain, hors de ce
    palier (NO REAL OBSIDURE RUN / NO REAL KX108 BUILD DECISION).
    """
    import sys as _sys
    _scripts = str(Path(__file__).resolve().parent)
    if _scripts not in _sys.path:
        _sys.path.insert(0, _scripts)
    import obsidia_build as _build

    root = repo_root or _REPO_ROOT
    target_path = child.get("target_path")
    objective = f"periphery {target_path}"
    base_sha = _build.get_base_sha(root)
    plan = _build.compute_plan(objective, base_sha, root)

    if plan.get("approved_scope_proposal") != [target_path]:
        return {
            "kx108_decision": None,
            "session_id": None,
            "bridge_error": "APPROVED_SCOPE_DOES_NOT_MATCH_CHILD_TARGET",
            "plan_candidate_files": plan.get("candidate_files"),
        }

    return {
        "kx108_decision": None,
        "session_id": None,
        "plan_verified": True,
        "manifest_hash": plan.get("manifest_hash"),
        "next_step": "cmd_execute_required_manually_outside_this_mandate",
    }


# ─── Exécution (consomme execution_order, propage les échecs de dépendance) ─

def run_execution(
    batch_execution_id: str,
    approval: Optional[dict],
    session_executor: Callable[[dict], dict],
    execution_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> dict:
    """
    Ordre des gates AVANT tout appel à session_executor, pour CHAQUE
    enfant, dans cet ordre exact :
      1. intégrité de l'enveloppe (déjà vérifiée à prepare_execution) ;
      2. approbation d'exécution humaine VALIDE (append-only, distincte de
         KX108) — sans elle, session_executor n'est JAMAIS invoqué ;
      3. prérequis de dépendance satisfaits (tous les EXECUTED_ACT) ;
      4/5. matérialité/opération déjà garanties par le statut PLANNED ;
      6. hash de la source RE-LU maintenant == hash enregistré ;
      7. hash de la cible RE-LU maintenant == target_pre_hash enregistré
         (garde TOCTOU — y compris le cas où une cible absente apparaît) ;
      8. re-vérification protégée au moment de l'exécution ;
      9. seulement alors, session_executor(child).

    Une approbation valide ouvre la porte à une TENTATIVE — elle ne lève
    JAMAIS un gate de preuve (matérialité, dépendance, intégrité,
    protection). `session_executor` DOIT être fourni explicitement —
    aucun défaut n'exécute réellement une session/KX108 dans ce palier.
    """
    envelope = _load_execution(batch_execution_id, execution_dir)
    if envelope is None:
        return {"error": f"batch_execution inconnu : {batch_execution_id}"}

    root = repo_root or _REPO_ROOT

    # Gate 1 : intégrité de l'enveloppe (défense en profondeur — déjà
    # garantie par prepare_execution, jamais de PLANNED si False).
    if not envelope.get("integrity_verified"):
        envelope["execution_approval_status"] = None
        envelope["aggregate_status"] = BATCH_HOLD
        _save_execution(envelope, execution_dir)
        return envelope

    # Gate 2 : approbation d'exécution humaine valide — AUCUN enfant n'est
    # jamais touché, AUCUN executor jamais appelé, sans elle.
    ok, reason = _validate_approval(approval, envelope)
    if not ok:
        envelope["execution_approval_status"] = f"{EXECUTION_APPROVAL_INVALID}:{reason}"
        envelope["execution_approval_id"] = None
        envelope["aggregate_status"] = BATCH_HOLD
        _save_execution(envelope, execution_dir)
        return envelope

    envelope["execution_approval_status"] = EXECUTION_APPROVAL_VALID
    envelope["execution_approval_id"] = approval.get("approval_id")

    children = envelope["children"]
    by_id = {c["candidate_entry_id"]: c for c in children}

    for child in children:
        if child["execution_status"] != PLANNED:
            continue

        # Gate 3 : dépendances
        deps = child.get("dependencies") or []
        blocked = False
        for dep_id in deps:
            dep_child = by_id.get(dep_id)
            if dep_child is None or dep_child.get("execution_status") != EXECUTED_ACT:
                blocked = True
                break
        if blocked:
            child["execution_status"] = DEPENDENCY_BLOCKED
            child["dependency_status"] = "BLOCKED"
            continue
        if deps:
            child["dependency_status"] = "SATISFIED"

        # Gate 8 (re-vérifié ici, avant tout hash) : protection
        if child.get("target_path") and _is_protected(child["target_path"]):
            child["execution_status"] = REFUSED_PROTECTED_TARGET
            continue

        # Gate 6 : intégrité octet-pour-octet de la source, relue MAINTENANT
        actual_source_hash = _resolve_and_hash(child.get("source_path"), root)
        if actual_source_hash != child.get("source_hash"):
            child["execution_status"] = SOURCE_INTEGRITY_MISMATCH
            child["integrity_detail"] = {
                "expected_source_hash": child.get("source_hash"),
                "actual_source_hash": actual_source_hash,
            }
            continue

        # Gate 7 : précondition de cible (garde TOCTOU) — la cible doit
        # être exactement dans l'état observé à prepare_execution, qu'elle
        # ait existé (même hash) ou non existé (toujours absente).
        actual_target_hash = _resolve_and_hash(child.get("target_path"), root)
        expected_target_pre_hash = child.get("target_pre_hash")
        if actual_target_hash != expected_target_pre_hash:
            child["execution_status"] = TARGET_PRECONDITION_MISMATCH
            child["integrity_detail"] = {
                "expected_target_pre_hash": expected_target_pre_hash,
                "actual_target_hash": actual_target_hash,
            }
            continue

        result = session_executor(child) or {}
        child["session_id"] = result.get("session_id")
        child["kx108_decision"] = result.get("kx108_decision")

        kx = result.get("kx108_decision")
        if kx == "ACT":
            child["execution_status"] = EXECUTED_ACT
        elif kx == "HOLD":
            child["execution_status"] = EXECUTED_HOLD
        elif kx == "BLOCK":
            child["execution_status"] = EXECUTED_BLOCK
        else:
            child["execution_status"] = EXECUTED_ERROR

    envelope["aggregate_status"] = _compute_aggregate_status(children)
    _save_execution(envelope, execution_dir)
    return envelope


# ─── Commandes lecture ───────────────────────────────────────────────────────

def cmd_execution_status(batch_execution_id: str, execution_dir: Optional[Path] = None) -> int:
    envelope = _load_execution(batch_execution_id, execution_dir)
    if envelope is None:
        print(f"  [BATCH_EXECUTION_FAIL] Inconnu : {batch_execution_id}")
        return 2
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  OBSIDIA BATCH EXECUTION -- STATUS : {batch_execution_id}")
    print(f"{sep}\n")
    for f in (
        "batch_id", "batch_hash", "candidate_scope_hash", "aggregate_status",
        "human_execution_approved", "decision_authority",
        "integrity_verified", "integrity_error",
        "execution_approval_status", "execution_approval_id",
    ):
        print(f"  {f:<28}: {envelope.get(f)}")
    print(f"  {'children_count':<28}: {len(envelope.get('children', []))}")
    print(f"  {'executable_candidate_count':<28}: {executable_candidate_count(envelope)}")
    return 0


def cmd_execution_inspect(batch_execution_id: str, execution_dir: Optional[Path] = None) -> int:
    envelope = _load_execution(batch_execution_id, execution_dir)
    if envelope is None:
        print(f"  [BATCH_EXECUTION_FAIL] Inconnu : {batch_execution_id}")
        return 2
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  OBSIDIA BATCH EXECUTION -- INSPECT : {batch_execution_id}")
    print(f"{sep}\n")
    print("  [IDENTITY]")
    for f in ("batch_execution_id", "schema_version", "created_at", "batch_id",
              "batch_hash", "candidate_scope_hash", "aggregate_status",
              "human_execution_approved", "decision_authority",
              "integrity_verified", "integrity_error",
              "execution_approval_status", "execution_approval_id"):
        print(f"  {f:<28}: {envelope.get(f)}")

    print(f"\n  [CHILDREN] ({len(envelope.get('children', []))})")
    for c in envelope.get("children", []):
        print(
            f"  {c['candidate_entry_id']}  {c.get('target_path')}  "
            f"materiality={c.get('materiality_status')}  "
            f"status={c.get('execution_status')}  "
            f"kx108={c.get('kx108_decision')}"
        )
    return 0


def cmd_execution_list(execution_dir: Optional[Path] = None) -> int:
    executions = _list_executions(execution_dir)
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA BATCH EXECUTION -- LIST")
    print(f"{sep}\n")
    if not executions:
        print("  [EMPTY] Aucune execution enregistree.")
        return 0
    for e in executions:
        print(
            f"  {e.get('batch_execution_id')}  {e.get('batch_id')}  "
            f"{e.get('aggregate_status')}"
        )
    print(f"\n  {len(executions)} execution(s) -- decision_authority = {DECISION_AUTHORITY}")
    return 0
