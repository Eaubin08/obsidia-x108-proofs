"""
obsidia_family_wiring.py
=========================
TERMINAL_FAMILY_WIRING_SELF_AUDIT_V0 — lecteur/auditeur GÉNÉRIQUE d'état
de câblage de famille (family wiring state), piloté entièrement par la
registry (scripts/obsidia_registry.yaml#families), jamais par du code
spécifique à une famille donnée.

Ce module NE DÉCIDE RIEN et NE MUTE RIEN — READ_ONLY, NON_SOVEREIGN.
Il ne recommande aucune action corrective : il restitue l'état canonique
déjà persisté et le RECALCULE indépendamment (jamais une confiance
aveugle aux compteurs), pour exposer toute divergence via
consistency_status plutôt que de la masquer.

Aucun littéral "AGENTS"/"MODULES" n'apparaît dans la logique de lecture
ci-dessous — le family_id est un paramètre, et les noms de section
interne à l'état canonique sont dérivés génériquement
(f"{family_id.lower()}_family_reconciliation",
f"{family_id.lower()}_family_status", etc.) avec repli explicite si
absents, jamais une valeur fabriquée.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "NON_SOVEREIGN"

STATUS_OK = "OK"
STATUS_FAMILY_NOT_REGISTERED = "FAMILY_NOT_REGISTERED"
STATUS_STATE_FILE_MISSING = "STATE_FILE_MISSING"
STATUS_STATE_FILE_MALFORMED = "STATE_FILE_MALFORMED"

CONSISTENCY_PASS = "PASS"
CONSISTENCY_FAIL = "FAIL"
CONSISTENCY_HOLD = "HOLD"

RESOLUTION_OPEN = "OPEN"
RESOLUTION_SUPERSEDED = "SUPERSEDED"


def load_family_registration(family_id: str, registry: dict) -> Optional[dict]:
    """Résout l'enregistrement de famille depuis registry['families'][family_id].
    Aucune connaissance de famille spécifique — purement une lecture de config."""
    families = registry.get("families") or {}
    return families.get(family_id)


def _sha256_file(path: Path) -> Optional[str]:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _git_fact(repo_root: Path, args: list) -> Optional[str]:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(repo_root), capture_output=True, text=True, timeout=15,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _resolution_status(blocker: dict) -> str:
    """Règle gelée : resolution_status absent => OPEN (rétrocompatible)."""
    return blocker.get("resolution_status") or RESOLUTION_OPEN


def _blocker_view(b: dict) -> dict:
    return {
        "blocker_id": b.get("blocker_id"),
        "wave": b.get("wave"),
        "path": b.get("path"),
        "blocker_category": b.get("blocker_category"),
        "blocker_type": b.get("blocker_type"),
        "owner": b.get("owner"),
        "reason": b.get("reason"),
        "next_action": b.get("next_action"),
        "source_artifact": b.get("source_artifact"),
        "resolution_status": _resolution_status(b),
        "resolution_reason": b.get("resolution_reason"),
        "resolved_by_provider": b.get("resolved_by_provider"),
    }


def audit_family_wiring(
    family_id: str,
    registry: dict,
    repo_root: Optional[Path] = None,
) -> dict:
    """
    Chemin de production UNIQUE — lecture seule, jamais d'écriture.

    1. résout l'enregistrement de famille depuis la registry (config, pas de code dédié)
    2. charge l'artefact d'état canonique référencé
    3. valide sa structure JSON
    4. RECALCULE indépendamment les compteurs de blockers actifs/historiques
       depuis blocker_matrix_v1.blockers[] (jamais une confiance aveugle
       aux compteurs déjà persistés)
    5. compare recalcul vs persisté -> consistency_status (jamais une
       normalisation silencieuse en cas de divergence)
    6. retourne un résultat structuré déterministe avec provenance complète

    Échoue fermé (status != OK) si la famille n'est pas enregistrée, si
    l'artefact d'état est absent, ou si son JSON est malformé.
    """
    root = repo_root or Path(__file__).resolve().parent.parent

    reg = load_family_registration(family_id, registry)
    if reg is None:
        return {"status": STATUS_FAMILY_NOT_REGISTERED, "family": family_id}

    state_rel = reg.get("canonical_state")
    index_rel = reg.get("artifact_index")
    authority = reg.get("authority", "UNKNOWN")

    state_path = (root / state_rel) if state_rel else None
    if not state_rel or not state_path.is_file():
        return {"status": STATUS_STATE_FILE_MISSING, "family": family_id, "state_source": state_rel}

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": STATUS_STATE_FILE_MALFORMED,
            "family": family_id,
            "state_source": state_rel,
            "reason": str(exc),
        }
    if not isinstance(state, dict):
        return {"status": STATUS_STATE_FILE_MALFORMED, "family": family_id, "state_source": state_rel, "reason": "root is not an object"}

    # --- Blockers : convention générique blocker_matrix_v1 (absente = 0 blockers, honnête) ---
    bm = state.get("blocker_matrix_v1") or {}
    blockers = bm.get("blockers") or []

    file_blockers = [b for b in blockers if b.get("is_file_blocker")]
    global_blockers = [b for b in blockers if b.get("is_global_blocker")]

    active_file = [b for b in file_blockers if _resolution_status(b) == RESOLUTION_OPEN]
    active_global = [b for b in global_blockers if _resolution_status(b) == RESOLUTION_OPEN]
    historical_superseded_global = [b for b in global_blockers if _resolution_status(b) == RESOLUTION_SUPERSEDED]

    recomputed_active_file = len(active_file)
    recomputed_active_global = len(active_global)
    recomputed_active_total = recomputed_active_file + recomputed_active_global
    recomputed_historical_superseded = len(historical_superseded_global)

    # --- Section de réconciliation : dérivée génériquement du family_id, jamais littérale ---
    recon_key = f"{family_id.lower()}_family_reconciliation"
    rec = state.get(recon_key) or {}

    fully_closed_key = f"{family_id.lower()}_family_fully_closed"
    fully_closed = rec.get(fully_closed_key)
    if fully_closed is None:
        fully_closed = rec.get("fully_closed")

    family_status = rec.get("family_status")
    if family_status is None:
        family_status = state.get(f"{family_id.lower()}_family_status")

    persisted_active_file_key = f"{family_id.lower()}_family_file_blockers"
    persisted_active_global_key = f"{family_id.lower()}_family_global_blockers"
    persisted_historical_key = f"{family_id.lower()}_family_historical_superseded_global_blockers"

    persisted_active_file = rec.get(persisted_active_file_key)
    persisted_active_global = rec.get(persisted_active_global_key)
    persisted_historical_superseded = rec.get(persisted_historical_key)
    persisted_active_total = bm.get("total_blockers")

    consistency = CONSISTENCY_PASS
    if bm:
        mismatches = []
        if persisted_active_file is not None and persisted_active_file != recomputed_active_file:
            mismatches.append("active_file_blockers")
        if persisted_active_global is not None and persisted_active_global != recomputed_active_global:
            mismatches.append("active_global_blockers")
        if persisted_active_total is not None and persisted_active_total != recomputed_active_total:
            mismatches.append("active_total_blockers")
        if persisted_historical_superseded is not None and persisted_historical_superseded != recomputed_historical_superseded:
            mismatches.append("historical_superseded")
        consistency = CONSISTENCY_FAIL if mismatches else CONSISTENCY_PASS
    else:
        consistency = CONSISTENCY_HOLD  # pas de blocker_matrix_v1 -> rien à recalculer/comparer

    index_path = (root / index_rel) if index_rel else None
    index_exists = bool(index_path and index_path.is_file())

    provenance = {
        "state_source_path": str(state_path),
        "state_source_sha256": _sha256_file(state_path),
        "artifact_index_source_path": str(index_path) if index_path else None,
        "artifact_index_exists": index_exists,
        "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_branch": _git_fact(root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        "git_head": _git_fact(root, ["rev-parse", "HEAD"]),
        "worktree_root": str(root),
    }

    return {
        "status": STATUS_OK,
        "schema_version": SCHEMA_VERSION,
        "family": family_id,
        "state_source": state_rel,
        "artifact_index_source": index_rel,
        "authority": authority,
        "decision_authority": DECISION_AUTHORITY,

        "family_status": family_status,
        "fully_closed": fully_closed,

        "global_manifest_complete": state.get("global_manifest_complete"),
        "global_relation_graph_complete": state.get("global_relation_graph_complete"),
        "global_registration_blocked": rec.get("global_registration_blocked", state.get("global_registration_blocked")),

        "persisted_active_file_blockers": persisted_active_file,
        "persisted_active_global_blockers": persisted_active_global,
        "persisted_active_total_blockers": persisted_active_total,
        "persisted_historical_superseded": persisted_historical_superseded,

        "recomputed_active_file_blockers": recomputed_active_file,
        "recomputed_active_global_blockers": recomputed_active_global,
        "recomputed_active_total_blockers": recomputed_active_total,
        "recomputed_historical_superseded": recomputed_historical_superseded,

        "consistency_status": consistency,

        "active_blockers": [_blocker_view(b) for b in (active_file + active_global)],
        "historical_superseded_blockers": [_blocker_view(b) for b in historical_superseded_global],

        "provenance": provenance,
    }


# ---------------------------------------------------------------------------
# FAMILY_WIRING_CANDIDATE_ONLY_V0 — Family Wiring active blocker
#   -> deterministic structured FamilyRemediationCandidate
#
# READ_ONLY. NON_SOVEREIGN. write_capability = false. Zero writes, zero
# persisted artefact (this path only calls audit_family_wiring, itself
# read-only). This is OBSERVATION -> STRUCTURED CANDIDATE only: it is NOT
# a KX108 decision, NOT a HumanApproval, NOT an Obsidure proposal, NOT an
# apply/commit authorization. The full governed remediation seam remains
# on HOLD (KX108 + human gate are not proven before the first target
# mutation); this checkpoint does not change that.
#
# An ambiguous canonical next_action (structural disjunction — an
# "..._OR_..." head — or a deferral to a named campaign/effort) is
# preserved verbatim as source_next_action and NEVER collapsed into a
# single action: remediation_intent stays HOLD_FOR_HUMAN_REMEDIATION_CHOICE
# and this function selects nothing.
# ---------------------------------------------------------------------------

CANDIDATE_SCHEMA_VERSION = 1
CANDIDATE_DECISION_AUTHORITY = "KX108_ONLY"

STATUS_CONSISTENCY_HOLD = "CONSISTENCY_HOLD"
STATUS_BLOCKER_NOT_FOUND = "BLOCKER_NOT_FOUND"
STATUS_BLOCKER_NOT_ACTIVE = "BLOCKER_NOT_ACTIVE"
STATUS_BLOCKER_MALFORMED = "BLOCKER_MALFORMED"

REMEDIATION_HOLD_FOR_HUMAN_CHOICE = "HOLD_FOR_HUMAN_REMEDIATION_CHOICE"
CANDIDATE_STATUS_HOLD_FOR_HUMAN_REMEDIATION_CHOICE = "HOLD_FOR_HUMAN_REMEDIATION_CHOICE"
CANDIDATE_STATUS_READY_FOR_HUMAN_REVIEW = "READY_FOR_HUMAN_REVIEW"


def _classify_next_action(next_action: Optional[str]) -> tuple:
    """Structural, generic classification of a canonical blocker next_action.

    No verb whitelist, no family knowledge, no hardcoded token. Returns
    (is_single_deterministic: bool, action_head: Optional[str], reason: str).

    Rules (purely structural — the head is everything before a "_IN_<effort>"
    deferral suffix):
      - absent / non-string                -> (False, None, "next_action_absent")
      - head contains "_OR_"               -> (False, head, "next_action_is_explicit_disjunction")
      - a "_IN_<effort>" suffix is present -> (False, head, "next_action_deferred_to_named_effort")
      - otherwise                          -> (True,  head, "next_action_is_single_token")
    """
    if not isinstance(next_action, str) or not next_action.strip():
        return False, None, "next_action_absent"
    token = next_action.strip()
    head, sep, _effort = token.partition("_IN_")
    if "_OR_" in head:
        return False, head, "next_action_is_explicit_disjunction"
    if sep:
        return False, head, "next_action_deferred_to_named_effort"
    return True, head, "next_action_is_single_token"


def build_family_remediation_candidate(
    family_id: str,
    blocker_id: str,
    registry: dict,
    repo_root: Optional[Path] = None,
) -> dict:
    """
    READ_ONLY production path — a currently active Family Wiring blocker
    becomes a deterministic FamilyRemediationCandidate. Performs ZERO writes
    and creates ZERO persisted artefact.

    Fail-closed (status != OK, no candidate emitted) when:
      - family not registered / canonical state missing / malformed
        (status propagated verbatim from audit_family_wiring)
      - consistency_status != PASS               -> CONSISTENCY_HOLD
      - blocker_id not present at all            -> BLOCKER_NOT_FOUND
      - blocker_id present but non-active
        (SUPERSEDED / historical)                -> BLOCKER_NOT_ACTIVE
      - active blocker without a canonical
        target path                              -> BLOCKER_MALFORMED

    Deterministic: same canonical state (same state_source_sha256) + same
    blocker_id => byte-identical candidate_id. captured_at is provenance
    only and is NOT part of candidate_id. Ambiguity in the canonical
    next_action is preserved, never resolved here.
    """
    root = repo_root or Path(__file__).resolve().parent.parent

    audit = audit_family_wiring(family_id, registry, repo_root=root)
    if audit.get("status") != STATUS_OK:
        return {
            "status": audit.get("status"),
            "schema_version": CANDIDATE_SCHEMA_VERSION,
            "family_id": family_id,
            "source_blocker_id": blocker_id,
        }

    if audit.get("consistency_status") != CONSISTENCY_PASS:
        return {
            "status": STATUS_CONSISTENCY_HOLD,
            "schema_version": CANDIDATE_SCHEMA_VERSION,
            "family_id": family_id,
            "source_blocker_id": blocker_id,
            "consistency_status": audit.get("consistency_status"),
        }

    active = {b.get("blocker_id"): b for b in audit.get("active_blockers", [])}
    historical = {b.get("blocker_id"): b for b in audit.get("historical_superseded_blockers", [])}

    blocker = active.get(blocker_id)
    if blocker is None:
        non_active = blocker_id in historical
        return {
            "status": STATUS_BLOCKER_NOT_ACTIVE if non_active else STATUS_BLOCKER_NOT_FOUND,
            "schema_version": CANDIDATE_SCHEMA_VERSION,
            "family_id": family_id,
            "source_blocker_id": blocker_id,
            "resolution_status": (
                (historical.get(blocker_id) or {}).get("resolution_status") if non_active else None
            ),
        }

    target_path = blocker.get("path")
    if not isinstance(target_path, str) or not target_path.strip():
        return {
            "status": STATUS_BLOCKER_MALFORMED,
            "schema_version": CANDIDATE_SCHEMA_VERSION,
            "family_id": family_id,
            "source_blocker_id": blocker_id,
            "reason": "active_blocker_without_canonical_target_path",
        }
    target_path = target_path.strip()

    prov = audit.get("provenance", {}) or {}
    state_sha = prov.get("state_source_sha256")

    next_action = blocker.get("next_action")
    is_single, action_head, action_reason = _classify_next_action(next_action)
    if is_single:
        candidate_status = CANDIDATE_STATUS_READY_FOR_HUMAN_REVIEW
        remediation_intent = action_head
    else:
        candidate_status = CANDIDATE_STATUS_HOLD_FOR_HUMAN_REMEDIATION_CHOICE
        remediation_intent = REMEDIATION_HOLD_FOR_HUMAN_CHOICE

    id_material = json.dumps(
        {
            "family_id": family_id,
            "source_blocker_id": blocker_id,
            "target_path": target_path,
            "family_wiring_state_sha256": state_sha,
            "source_next_action": next_action,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    candidate_id = "frc-" + hashlib.sha256(id_material.encode("utf-8")).hexdigest()[:32]

    return {
        "status": STATUS_OK,
        "schema_version": CANDIDATE_SCHEMA_VERSION,

        "candidate_id": candidate_id,
        "candidate_status": candidate_status,

        "family_id": family_id,
        "source_blocker_id": blocker_id,
        "target_path": target_path,

        "blocker_category": blocker.get("blocker_category"),
        "blocker_type": blocker.get("blocker_type"),
        "owner": blocker.get("owner"),
        "reason": blocker.get("reason"),

        "source_next_action": next_action,
        "source_next_action_classification": action_reason,

        "remediation_intent": remediation_intent,

        "allowed_scope": [target_path],
        "forbidden_scope": [],

        "finding_provenance": {
            "family_wiring_state_sha256": state_sha,
            "source_artifact": blocker.get("source_artifact"),
            "git_branch": prov.get("git_branch"),
            "git_head": prov.get("git_head"),
            "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },

        "requires_human_review": True,
        "authority": DECISION_AUTHORITY,               # NON_SOVEREIGN
        "write_capability": False,
        "decision_authority": CANDIDATE_DECISION_AUTHORITY,  # KX108_ONLY — decisions are NOT this candidate's
    }
