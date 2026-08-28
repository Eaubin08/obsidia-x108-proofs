"""
obsidia_mission_authority_v0.py
===============================
STAGE 4C — REPRÉSENTATION + VÉRIFICATION runtime, INERTE, du modèle formel
d'autorité de mission bornée (Lean : proofs/lean/Obsidia/MissionAuthority/,
Stage 4A/4B, 16 invariants + second théorème central machine-vérifiés).

CE MODULE N'ACTIVE RIEN.

  * Il ne rend AUCUNE HumanMissionAuthorization ni DerivedActionAuthorityWitness
    acceptable par le rail PRE / KX108 / le séquenceur.
  * Il n'a AUCUN appelant de production (cf. tests/cli/test_mission_authority_v0.py
    — seul consommateur). `RUNTIME_AUTHORITY_ACTIVE = False`.
  * Il ne modifie NI PRE, NI HumanApproval, NI KX108, NI le séquenceur, NI
    obsidia_governed_apply / rollback. Il n'écrit AUCUNE cible, ne fait AUCUN
    `git`, ne crée AUCUN artefact d'approbation ni décision KX.
  * `decision_authority` reste `KX108_ONLY` — ce module l'AFFIRME, ne le fixe jamais.

Il fournit :

  HumanMissionAuthorization (HMA)   — autorité humaine RACINE, borne supérieure,
                                      immuable, write-once, liée EXACTEMENT à
                                      un `plan_hash` (jamais une famille de plans).
  MissionAuthorityRevocation        — évidence append-only ; n'efface pas l'histoire.
  DerivedActionAuthorityWitness (DAAW) — témoin machine NON_SOUVERAIN, par action,
                                      lié EXACTEMENT à l'EAH (via la fonction
                                      canonique réutilisée `compute_execution_authority_hash`).
  + vérificateurs déterministes, locaux, sans inférence de modèle.

La consommation d'autorité (index d'action, budget) est DÉRIVÉE de la projection
de mission immuable (Stage 3B) — aucun compteur mutable.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_bounded_mission_v0 as _M      # helpers canoniques + projection/plan/genesis (LECTURE)
import obsidia_batch_execution as _E         # compute_execution_authority_hash CANONIQUE (RÉUTILISÉ, jamais réimplémenté)

# ── Bornes de séparation, explicites et statiques ──
RUNTIME_AUTHORITY_ACTIVE = False
STAGE4_AUTHORITY_EXECUTION_INTEGRATION = False
DECISION_AUTHORITY = "KX108_ONLY"            # affirmé, jamais fixé ici
SEMANTIC_DECISION_AUTHORITY = "NON_SOVEREIGN"

AUTHORITY_SCHEMA_VERSION = 1
REVOCATION_SCHEMA_VERSION = 1
WITNESS_SCHEMA_VERSION = 1

HMA_DOMAIN_TAG = "OBSIDIA_STAGE4_HMA_V0"
DAAW_DOMAIN_TAG = "OBSIDIA_STAGE4_DAAW_V0"
REVOCATION_DOMAIN_TAG = "OBSIDIA_STAGE4_REVOCATION_V0"

HMA_AUTHORITY_LEVEL = "HUMAN_ROOT_UPPER_BOUND"
DAAW_SOVEREIGNTY = "NON_SOVEREIGN"
DEFAULT_REVOCATION_POLICY = "HUMAN_APPEND_ONLY_REVOCATION_V0"

MISSION_AUTHORIZATION_PLAN_BINDING = "EXACT_PLAN_HASH"

# ── Statuts publics ──
HMA_BOUND = "HUMAN_MISSION_AUTHORIZATION_BOUND"
HMA_BIND_REJECTED = "HUMAN_MISSION_AUTHORIZATION_BIND_REJECTED"
HMA_STORE_STORED = "STORED"
HMA_STORE_IDEMPOTENT = "IDEMPOTENT_EXISTING_IDENTICAL"
HMA_STORE_IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
HMA_VERIFIED = "HUMAN_MISSION_AUTHORIZATION_VERIFIED"
HMA_VERIFY_REJECTED = "HUMAN_MISSION_AUTHORIZATION_VERIFY_REJECTED"
REVOCATION_RECORDED = "MISSION_AUTHORITY_REVOCATION_RECORDED"
REVOCATION_REJECTED = "MISSION_AUTHORITY_REVOCATION_REJECTED"
DAAW_DERIVED = "DERIVED_ACTION_AUTHORITY_WITNESS_DERIVED"
DAAW_DERIVE_REJECTED = "DERIVED_ACTION_AUTHORITY_WITNESS_DERIVE_REJECTED"
DAAW_VERIFIED = "DERIVED_ACTION_AUTHORITY_WITNESS_VERIFIED"
DAAW_VERIFY_REJECTED = "DERIVED_ACTION_AUTHORITY_WITNESS_VERIFY_REJECTED"


# ══════════════════════════════════════════════════════════════════════════
#  Helpers canoniques (RÉUTILISÉS depuis obsidia_bounded_mission_v0 — aucune
#  logique de hachage/canonicalisation/store dupliquée).
# ══════════════════════════════════════════════════════════════════════════

_canon = _M._canon
_sha256_hex = _M._sha256_hex


def _authority_dir(mission_id: str, store_dir: "str | Path") -> Path:
    return _M._mission_dir(mission_id, Path(store_dir)) / "mission_authority"


def _authorizations_dir(mission_id: str, store_dir: "str | Path") -> Path:
    return _authority_dir(mission_id, store_dir) / "authorizations"


def _revocations_dir(mission_id: str, store_dir: "str | Path") -> Path:
    return _authority_dir(mission_id, store_dir) / "revocations"


def _dependency_commitment(plan: dict) -> str:
    """Engagement déterministe sur le DAG du plan (arêtes de dépendance
    canoniques Stage 3D)."""
    return _sha256_hex(_canon(plan.get("dependency_edges") or []))


def _dependency_satisfaction_digest(plan: dict, ordinals: "list[int]",
                                    snapshotted: "list[str]") -> str:
    ord_to_aid = {d["ordinal"]: d["action_id"] for d in plan.get("actions", [])}
    entries = []
    for o in sorted(set(ordinals)):
        entries.append({
            "ordinal": o,
            "action_id": ord_to_aid.get(o),
            "snapshotted": ord_to_aid.get(o) in set(snapshotted),
        })
    return _sha256_hex(_canon(entries))


def _subset_or_none(a, b) -> bool:
    """`a ⊆ b` avec None == « non borné ». b non borné -> toujours vrai ;
    a non borné mais b borné -> faux (a serait plus large)."""
    if b is None:
        return True
    if a is None:
        return False
    return set(a) <= set(b)


def scope_le(a: dict, b: dict) -> bool:
    """Miroir runtime EXACT de `Obsidia.MissionAuthority.scopeLE` (Lean 4A) :
    « a n'est pas plus permissif que b »."""
    return (
        _subset_or_none(a.get("allowed_target_paths"), b.get("allowed_target_paths")) and
        _subset_or_none(a.get("allowed_operation_shapes"), b.get("allowed_operation_shapes")) and
        int(a.get("max_actions", 0)) <= int(b.get("max_actions", 0)) and
        int(a.get("max_retries_per_action", 0)) <= int(b.get("max_retries_per_action", 0)) and
        a.get("plan_hash") == b.get("plan_hash") and
        a.get("repository_identity") == b.get("repository_identity") and
        a.get("branch_name") == b.get("branch_name") and
        a.get("canonical_base_sha") == b.get("canonical_base_sha") and
        a.get("dependency_commitment") == b.get("dependency_commitment")
    )


def _rej(status: str, reason: str, **extra) -> dict:
    return {"status": status, "reason": reason,
            "authority": "NON_SOVEREIGN", "runtime_authority_active": False,
            "stage4_authority_execution_integration": False, **extra}


# ══════════════════════════════════════════════════════════════════════════
#  1 — HumanMissionAuthorization (HMA)
# ══════════════════════════════════════════════════════════════════════════

_HMA_BOUND_FIELDS = (
    "authority_schema_version", "domain_tag", "issuer",
    "mission_id", "mission_genesis_record_hash",
    "plan_id", "plan_hash", "canonical_base_sha",
    "repository_identity", "branch_name", "worktree_path",
    "allowed_operation_shapes", "allowed_target_paths",
    "max_actions", "max_retries_per_action",
    "dependency_commitment", "human_authorization_reference",
    "revocation_policy",
)


def _hma_scope(record: dict) -> dict:
    return {
        "allowed_operation_shapes": record.get("allowed_operation_shapes"),
        "allowed_target_paths": record.get("allowed_target_paths"),
        "max_actions": record.get("max_actions"),
        "max_retries_per_action": record.get("max_retries_per_action"),
        "plan_hash": record.get("plan_hash"),
        "repository_identity": record.get("repository_identity"),
        "branch_name": record.get("branch_name"),
        "canonical_base_sha": record.get("canonical_base_sha"),
        "dependency_commitment": record.get("dependency_commitment"),
    }


def _genesis_as_scope(genesis: dict, plan_hash: str, dependency_commitment: str) -> dict:
    gs = genesis["scope"]
    return {
        "allowed_operation_shapes": gs.get("allowed_operation_shapes"),
        "allowed_target_paths": gs.get("allowed_target_paths"),
        "max_actions": gs.get("max_actions"),
        "max_retries_per_action": gs.get("max_retries_per_action"),
        "plan_hash": plan_hash,
        "repository_identity": genesis["repository_identity"],
        "branch_name": genesis["branch_name"],
        "canonical_base_sha": genesis["canonical_base_sha"],
        "dependency_commitment": dependency_commitment,
    }


def build_human_mission_authorization(
    *, mission_id: str, plan_id: str,
    human_authorization_reference: str,
    mission_store_dir: "str | Path",
    revocation_policy: str = DEFAULT_REVOCATION_POLICY,
) -> "tuple[Optional[dict], Optional[str]]":
    """Construit (SANS persister) la HMA immuable. L'humain FOURNIT
    `human_authorization_reference` — le stack ne la synthétise JAMAIS
    (fail-closed `HUMAN_AUTHORIZATION_REFERENCE_REQUIRED`)."""
    if not (isinstance(human_authorization_reference, str) and human_authorization_reference.strip()):
        return None, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED"
    genesis = _M.load_mission_genesis(mission_id, mission_store_dir)
    if genesis is None:
        return None, "MISSION_GENESIS_NOT_FOUND"
    ok_g, why_g = _M._verify_genesis(genesis)
    if not ok_g:
        return None, f"MISSION_GENESIS_INVALID:{why_g}"
    plan = _M.load_mission_plan(mission_id, plan_id, mission_store_dir)
    if plan is None:
        return None, "MISSION_PLAN_NOT_FOUND"
    ok_p, why_p = _M.verify_mission_plan(plan, genesis=genesis)
    if not ok_p:
        return None, f"MISSION_PLAN_INVALID:{why_p}"
    if plan.get("plan_id") != plan_id:
        return None, "PLAN_ID_MISMATCH"

    dep_commitment = _dependency_commitment(plan)
    gs = genesis["scope"]
    record = {
        "authority_schema_version": AUTHORITY_SCHEMA_VERSION,
        "domain_tag": HMA_DOMAIN_TAG,
        "issuer": "HUMAN",
        "mission_id": mission_id,
        "mission_genesis_record_hash": genesis["mission_genesis_record_hash"],
        "plan_id": plan_id,
        "plan_hash": plan["plan_hash"],
        "canonical_base_sha": genesis["canonical_base_sha"],
        "repository_identity": genesis["repository_identity"],
        "branch_name": genesis["branch_name"],
        "worktree_path": genesis["worktree_path"],
        "allowed_operation_shapes": gs.get("allowed_operation_shapes"),
        "allowed_target_paths": gs.get("allowed_target_paths"),
        "max_actions": gs.get("max_actions"),
        "max_retries_per_action": gs.get("max_retries_per_action"),
        "dependency_commitment": dep_commitment,
        "human_authorization_reference": human_authorization_reference,
        "revocation_policy": revocation_policy,
        # champs informationnels (hors matériel d'identité)
        "authority_level": HMA_AUTHORITY_LEVEL,
        "plan_is_execution_authority": False,
        "is_kx_authority": False,
        "plan_action_count": len(plan.get("actions", [])),
        "plan_binding": MISSION_AUTHORIZATION_PLAN_BINDING,
    }
    rh = _sha256_hex(_canon({k: record.get(k) for k in _HMA_BOUND_FIELDS}))
    record["hma_record_hash"] = rh
    record["human_mission_authorization_id"] = "hma-" + rh[:32]
    return record, None


def bind_human_mission_authorization(
    *, mission_id: str, plan_id: str,
    human_authorization_reference: str,
    mission_store_dir: "str | Path",
    revocation_policy: str = DEFAULT_REVOCATION_POLICY,
) -> dict:
    """Construit + persiste write-once. AUCUNE révision de mission appendée
    (le rattachement au cycle de vie de la mission est Stage 4E)."""
    record, reason = build_human_mission_authorization(
        mission_id=mission_id, plan_id=plan_id,
        human_authorization_reference=human_authorization_reference,
        mission_store_dir=mission_store_dir, revocation_policy=revocation_policy)
    if record is None:
        return _rej(HMA_BIND_REJECTED, reason)
    try:
        p = _M._safe_id_path(_authorizations_dir(mission_id, mission_store_dir),
                             record["human_mission_authorization_id"])
    except ValueError:
        return _rej(HMA_BIND_REJECTED, "INVALID_HMA_ID")
    st = _M._atomic_publish_json(p, record)
    if st == "IMMUTABILITY_VIOLATION":
        return _rej(HMA_BIND_REJECTED, "HMA_IMMUTABILITY_VIOLATION",
                    human_mission_authorization_id=record["human_mission_authorization_id"])
    return {
        "status": HMA_BOUND, "reason": None,
        "human_mission_authorization_id": record["human_mission_authorization_id"],
        "hma_record_hash": record["hma_record_hash"],
        "store_status": st, "plan_id": plan_id, "plan_hash": record["plan_hash"],
        "issuer": "HUMAN", "is_kx_authority": False,
        "plan_is_execution_authority": False,
        "plan_binding": MISSION_AUTHORIZATION_PLAN_BINDING,
        "runtime_authority_active": False,
    }


def load_human_mission_authorization(mission_id: str, hma_id: str,
                                     mission_store_dir: "str | Path") -> Optional[dict]:
    try:
        p = _M._safe_id_path(_authorizations_dir(mission_id, mission_store_dir), hma_id)
    except ValueError:
        return None
    if not p.exists():
        return None
    import json
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_human_mission_authorization(
    record: Optional[dict], *, genesis: Optional[dict], plan: Optional[dict],
    revocations: "Optional[list]" = None,
) -> "tuple[bool, Optional[str]]":
    """Fail-closed, déterministe, local, sans inférence."""
    if not isinstance(record, dict):
        return False, "HMA_RECORD_MISSING"
    if record.get("authority_schema_version") != AUTHORITY_SCHEMA_VERSION:
        return False, "HMA_SCHEMA_UNSUPPORTED"
    if record.get("domain_tag") != HMA_DOMAIN_TAG:
        return False, "HMA_DOMAIN_TAG_MISMATCH"
    if record.get("issuer") != "HUMAN":
        return False, "HMA_ISSUER_NOT_HUMAN"
    for f in _HMA_BOUND_FIELDS:
        if f not in record:
            return False, f"HMA_FIELD_MISSING:{f}"
    rh = _sha256_hex(_canon({k: record.get(k) for k in _HMA_BOUND_FIELDS}))
    if record.get("hma_record_hash") != rh:
        return False, "HMA_RECORD_HASH_MISMATCH"
    if record.get("human_mission_authorization_id") != "hma-" + rh[:32]:
        return False, "HMA_ID_NOT_DERIVED"
    if not isinstance(genesis, dict):
        return False, "GENESIS_MISSING"
    ok_g, why_g = _M._verify_genesis(genesis)
    if not ok_g:
        return False, f"GENESIS_INVALID:{why_g}"
    if record.get("mission_id") != genesis.get("mission_id"):
        return False, "HMA_MISSION_MISMATCH"
    if record.get("mission_genesis_record_hash") != genesis.get("mission_genesis_record_hash"):
        return False, "HMA_GENESIS_HASH_MISMATCH"
    if record.get("canonical_base_sha") != genesis.get("canonical_base_sha"):
        return False, "HMA_CANONICAL_BASE_MISMATCH"
    if record.get("repository_identity") != genesis.get("repository_identity"):
        return False, "HMA_REPOSITORY_MISMATCH"
    if record.get("branch_name") != genesis.get("branch_name"):
        return False, "HMA_BRANCH_MISMATCH"
    if record.get("worktree_path") != genesis.get("worktree_path"):
        return False, "HMA_WORKTREE_MISMATCH"
    if not isinstance(plan, dict):
        return False, "PLAN_MISSING"
    ok_p, why_p = _M.verify_mission_plan(plan, genesis=genesis)
    if not ok_p:
        return False, f"PLAN_INVALID:{why_p}"
    if record.get("plan_id") != plan.get("plan_id"):
        return False, "HMA_PLAN_ID_MISMATCH"
    if record.get("plan_hash") != plan.get("plan_hash"):
        return False, "HMA_PLAN_HASH_MISMATCH"                 # EXACT_PLAN_HASH
    dep_commitment = _dependency_commitment(plan)
    if record.get("dependency_commitment") != dep_commitment:
        return False, "HMA_DEPENDENCY_COMMITMENT_MISMATCH"
    gs = genesis["scope"]
    if not _subset_or_none(record.get("allowed_operation_shapes"), gs.get("allowed_operation_shapes")):
        return False, "HMA_OPERATIONS_NOT_SUBSET_OF_GENESIS"
    if not _subset_or_none(record.get("allowed_target_paths"), gs.get("allowed_target_paths")):
        return False, "HMA_TARGETS_NOT_SUBSET_OF_GENESIS"
    if int(record.get("max_actions", 0)) > int(gs.get("max_actions", 0)):
        return False, "HMA_MAX_ACTIONS_EXCEEDS_GENESIS"
    if int(record.get("max_retries_per_action", 0)) > int(gs.get("max_retries_per_action", 0)):
        return False, "HMA_MAX_RETRIES_EXCEEDS_GENESIS"
    if not scope_le(_hma_scope(record), _genesis_as_scope(genesis, record["plan_hash"], dep_commitment)):
        return False, "HMA_SCOPE_NOT_BOUNDED_BY_GENESIS"
    if len(plan.get("actions", [])) > int(record.get("max_actions", 0)):
        return False, "PLAN_ACTIONS_EXCEED_HMA_MAX_ACTIONS"
    for rv in (revocations or []):
        if (isinstance(rv, dict)
                and rv.get("hma_id") == record.get("human_mission_authorization_id")
                and rv.get("hma_record_hash") == record.get("hma_record_hash")):
            ok_r, _ = verify_mission_authority_revocation(rv, hma=record)
            if ok_r:
                return False, "HMA_REVOKED"
    return True, None


# ══════════════════════════════════════════════════════════════════════════
#  2 — MissionAuthorityRevocation (append-only)
# ══════════════════════════════════════════════════════════════════════════

_REVOCATION_BOUND_FIELDS = (
    "revocation_schema_version", "domain_tag",
    "mission_id", "hma_id", "hma_record_hash",
    "revocation_reference", "actor",
)


def record_mission_authority_revocation(
    *, mission_id: str, hma_id: str, hma_record_hash: str,
    revocation_reference: str, mission_store_dir: "str | Path",
    actor: str = "HUMAN",
) -> dict:
    """Évidence de révocation APPEND-ONLY. N'efface AUCUNE histoire ; ne
    touche à AUCUN KEEP passé. Re-révocation identique -> idempotent."""
    if actor != "HUMAN":
        return _rej(REVOCATION_REJECTED, "REVOCATION_ACTOR_NOT_HUMAN")
    if not (isinstance(revocation_reference, str) and revocation_reference.strip()):
        return _rej(REVOCATION_REJECTED, "REVOCATION_REFERENCE_REQUIRED")
    if not _M._is_64_hex(hma_record_hash):
        return _rej(REVOCATION_REJECTED, "HMA_RECORD_HASH_MALFORMED")
    record = {
        "revocation_schema_version": REVOCATION_SCHEMA_VERSION,
        "domain_tag": REVOCATION_DOMAIN_TAG,
        "mission_id": mission_id,
        "hma_id": hma_id,
        "hma_record_hash": hma_record_hash,
        "revocation_reference": revocation_reference,
        "actor": "HUMAN",
    }
    rh = _sha256_hex(_canon({k: record.get(k) for k in _REVOCATION_BOUND_FIELDS}))
    record["revocation_record_hash"] = rh
    record["mission_authority_revocation_id"] = "rev-" + rh[:32]
    try:
        p = _M._safe_id_path(_revocations_dir(mission_id, mission_store_dir),
                             record["mission_authority_revocation_id"])
    except ValueError:
        return _rej(REVOCATION_REJECTED, "INVALID_REVOCATION_ID")
    st = _M._atomic_publish_json(p, record)
    if st == "IMMUTABILITY_VIOLATION":
        return _rej(REVOCATION_REJECTED, "REVOCATION_IMMUTABILITY_VIOLATION")
    return {
        "status": REVOCATION_RECORDED, "reason": None,
        "mission_authority_revocation_id": record["mission_authority_revocation_id"],
        "revocation_record_hash": rh, "store_status": st,
        "hma_id": hma_id, "history_rewritten": False, "actor": "HUMAN",
    }


def verify_mission_authority_revocation(record: Optional[dict], *,
                                       hma: Optional[dict] = None
                                       ) -> "tuple[bool, Optional[str]]":
    if not isinstance(record, dict):
        return False, "REVOCATION_RECORD_MISSING"
    if record.get("revocation_schema_version") != REVOCATION_SCHEMA_VERSION:
        return False, "REVOCATION_SCHEMA_UNSUPPORTED"
    if record.get("domain_tag") != REVOCATION_DOMAIN_TAG:
        return False, "REVOCATION_DOMAIN_TAG_MISMATCH"
    if record.get("actor") != "HUMAN":
        return False, "REVOCATION_ACTOR_NOT_HUMAN"
    for f in _REVOCATION_BOUND_FIELDS:
        if f not in record:
            return False, f"REVOCATION_FIELD_MISSING:{f}"
    rh = _sha256_hex(_canon({k: record.get(k) for k in _REVOCATION_BOUND_FIELDS}))
    if record.get("revocation_record_hash") != rh:
        return False, "REVOCATION_RECORD_HASH_MISMATCH"
    if record.get("mission_authority_revocation_id") != "rev-" + rh[:32]:
        return False, "REVOCATION_ID_NOT_DERIVED"
    if hma is not None:
        if record.get("hma_id") != hma.get("human_mission_authorization_id"):
            return False, "REVOCATION_HMA_ID_MISMATCH"
        if record.get("hma_record_hash") != hma.get("hma_record_hash"):
            return False, "REVOCATION_HMA_HASH_MISMATCH"
    return True, None


def list_mission_authority_revocations(mission_id: str,
                                       mission_store_dir: "str | Path") -> "list[dict]":
    import json
    d = _revocations_dir(mission_id, mission_store_dir)
    if not d.exists():
        return []
    out = []
    for f in sorted(d.glob("rev-*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return out


# ══════════════════════════════════════════════════════════════════════════
#  3 — DerivedActionAuthorityWitness (DAAW) — NON_SOUVERAIN
# ══════════════════════════════════════════════════════════════════════════

_DAAW_BOUND_FIELDS = (
    "witness_schema_version", "domain_tag", "sovereignty",
    "mission_id", "human_mission_authorization_id", "hma_record_hash",
    "plan_id", "plan_hash",
    "action_id", "ordinal", "operation", "target_path",
    "source_git_commit", "source_historical_path", "test_contract_hash",
    "action_base_sha", "dependency_satisfaction_digest",
    "executed_action_index", "execution_authority_hash",
    "allowed_operation_shapes", "allowed_target_paths",
    "max_actions", "max_retries_per_action",
    "canonical_base_sha", "repository_identity", "branch_name",
    "dependency_commitment",
)


def _daaw_scope(record: dict) -> dict:
    return {
        "allowed_operation_shapes": record.get("allowed_operation_shapes"),
        "allowed_target_paths": record.get("allowed_target_paths"),
        "max_actions": record.get("max_actions"),
        "max_retries_per_action": record.get("max_retries_per_action"),
        "plan_hash": record.get("plan_hash"),
        "repository_identity": record.get("repository_identity"),
        "branch_name": record.get("branch_name"),
        "canonical_base_sha": record.get("canonical_base_sha"),
        "dependency_commitment": record.get("dependency_commitment"),
    }


def _find_action(plan: dict, action_id: str) -> Optional[dict]:
    return next((d for d in plan.get("actions", []) if d.get("action_id") == action_id), None)


def derive_action_authority_witness(
    *, hma: dict, plan: dict, action_id: str, projection: dict,
    execution_envelope: dict,
    eah_fn=_E.compute_execution_authority_hash,
) -> "tuple[Optional[dict], Optional[str]]":
    """PRIMITIVE PURE — construit un DAAW candidat depuis des entrées
    explicites. AUCUN workflow de production ne l'invoque (cf. §17 / §41).
    L'EAH est calculé par la fonction CANONIQUE réutilisée."""
    desc = _find_action(plan, action_id)
    if desc is None:
        return None, "ACTION_NOT_IN_PLAN"
    deps = list(desc.get("dependency_ordinals") or [])
    snapshotted = list(projection.get("snapshotted_action_ids") or [])
    ord_to_aid = {d["ordinal"]: d["action_id"] for d in plan.get("actions", [])}
    for o in deps:
        if ord_to_aid.get(o) not in set(snapshotted):
            return None, f"DEPENDENCY_ORDINAL_NOT_SNAPSHOTTED:{o}"
    try:
        eah = eah_fn(execution_envelope)
    except Exception as e:  # noqa: BLE001 — surface propre, pas de fabrication
        return None, f"EAH_COMPUTATION_FAILED:{type(e).__name__}"
    if not _M._is_64_hex(eah):
        return None, "EAH_NOT_64_HEX"
    record = {
        "witness_schema_version": WITNESS_SCHEMA_VERSION,
        "domain_tag": DAAW_DOMAIN_TAG,
        "sovereignty": DAAW_SOVEREIGNTY,
        "mission_id": hma["mission_id"],
        "human_mission_authorization_id": hma["human_mission_authorization_id"],
        "hma_record_hash": hma["hma_record_hash"],
        "plan_id": plan["plan_id"],
        "plan_hash": plan["plan_hash"],
        "action_id": action_id,
        "ordinal": desc["ordinal"],
        "operation": desc["operation"],
        "target_path": desc["target_path"],
        "source_git_commit": desc.get("source_git_commit"),
        "source_historical_path": desc.get("source_historical_path"),
        "test_contract_hash": desc.get("test_contract_hash"),
        "action_base_sha": projection.get("mission_tip_sha"),
        "dependency_satisfaction_digest": _dependency_satisfaction_digest(plan, deps, snapshotted),
        "executed_action_index": len(snapshotted),
        "execution_authority_hash": eah,
        "allowed_operation_shapes": hma.get("allowed_operation_shapes"),
        "allowed_target_paths": hma.get("allowed_target_paths"),
        "max_actions": hma.get("max_actions"),
        "max_retries_per_action": hma.get("max_retries_per_action"),
        "canonical_base_sha": hma.get("canonical_base_sha"),
        "repository_identity": hma.get("repository_identity"),
        "branch_name": hma.get("branch_name"),
        "dependency_commitment": hma.get("dependency_commitment"),
        # informationnel
        "is_kx_authority": False,
        "is_human_approval": False,
        "is_execution_authority": False,
    }
    rh = _sha256_hex(_canon({k: record.get(k) for k in _DAAW_BOUND_FIELDS}))
    record["daaw_record_hash"] = rh
    record["derived_action_authority_witness_id"] = "daaw-" + rh[:32]
    return record, None


def verify_derived_action_authority_witness(
    *, daaw: Optional[dict], hma: Optional[dict], plan: Optional[dict],
    genesis: Optional[dict], projection: Optional[dict],
    execution_envelope: dict,
    revocations: "Optional[list]" = None,
    eah_fn=_E.compute_execution_authority_hash,
) -> "tuple[bool, Optional[str]]":
    """Fail-closed sur toute divergence. NE lève AUCUN gate KX ni ne rend
    quoi que ce soit exécutable."""
    if not isinstance(daaw, dict):
        return False, "DAAW_RECORD_MISSING"
    if daaw.get("witness_schema_version") != WITNESS_SCHEMA_VERSION:
        return False, "DAAW_SCHEMA_UNSUPPORTED"
    if daaw.get("domain_tag") != DAAW_DOMAIN_TAG:
        return False, "DAAW_DOMAIN_TAG_MISMATCH"
    if daaw.get("sovereignty") != DAAW_SOVEREIGNTY:
        return False, "DAAW_NOT_NON_SOVEREIGN"
    for f in _DAAW_BOUND_FIELDS:
        if f not in daaw:
            return False, f"DAAW_FIELD_MISSING:{f}"
    rh = _sha256_hex(_canon({k: daaw.get(k) for k in _DAAW_BOUND_FIELDS}))
    if daaw.get("daaw_record_hash") != rh:
        return False, "DAAW_RECORD_HASH_MISMATCH"
    if daaw.get("derived_action_authority_witness_id") != "daaw-" + rh[:32]:
        return False, "DAAW_ID_NOT_DERIVED"

    ok_h, why_h = verify_human_mission_authorization(
        hma, genesis=genesis, plan=plan, revocations=revocations)
    if not ok_h:
        return False, f"HMA_INVALID:{why_h}"

    if daaw.get("mission_id") != hma.get("mission_id"):
        return False, "DAAW_MISSION_MISMATCH"
    if daaw.get("human_mission_authorization_id") != hma.get("human_mission_authorization_id"):
        return False, "DAAW_HMA_ID_MISMATCH"
    if daaw.get("hma_record_hash") != hma.get("hma_record_hash"):
        return False, "DAAW_HMA_HASH_MISMATCH"
    if daaw.get("plan_id") != hma.get("plan_id") or daaw.get("plan_id") != plan.get("plan_id"):
        return False, "DAAW_PLAN_ID_MISMATCH"
    if daaw.get("plan_hash") != hma.get("plan_hash") or daaw.get("plan_hash") != plan.get("plan_hash"):
        return False, "DAAW_PLAN_HASH_MISMATCH"

    desc = _find_action(plan, daaw.get("action_id"))
    if desc is None:
        return False, "DAAW_ACTION_NOT_IN_PLAN"
    for k in ("ordinal", "operation", "target_path",
              "source_git_commit", "source_historical_path", "test_contract_hash"):
        if daaw.get(k) != desc.get(k):
            return False, f"DAAW_ACTION_FIELD_MISMATCH:{k}"

    if not isinstance(projection, dict):
        return False, "PROJECTION_MISSING"
    if projection.get("plan_completed") or projection.get("current_state") == "CLOSED_AWAITING_NEXT_PLAN":
        return False, "MISSION_PLAN_COMPLETED"
    if daaw.get("action_base_sha") != projection.get("mission_tip_sha"):
        return False, "DAAW_ACTION_BASE_NOT_CURRENT_MISSION_TIP"

    deps = list(desc.get("dependency_ordinals") or [])
    snapshotted = list(projection.get("snapshotted_action_ids") or [])
    ord_to_aid = {d["ordinal"]: d["action_id"] for d in plan.get("actions", [])}
    for o in deps:
        aid = ord_to_aid.get(o)
        if aid is None or aid not in set(snapshotted):
            return False, f"DAAW_DEPENDENCY_UNSATISFIED:{o}"
    if daaw.get("dependency_satisfaction_digest") != _dependency_satisfaction_digest(plan, deps, snapshotted):
        return False, "DAAW_DEPENDENCY_DIGEST_MISMATCH"

    if daaw.get("executed_action_index") != len(snapshotted):
        return False, "DAAW_EXECUTED_INDEX_NOT_DERIVED"
    if int(daaw.get("executed_action_index", -1)) >= int(hma.get("max_actions", 0)):
        return False, "DAAW_BUDGET_EXCEEDED"

    if not scope_le(_daaw_scope(daaw), _hma_scope(hma)):
        return False, "DAAW_SCOPE_AMPLIFICATION"

    try:
        recomputed = eah_fn(execution_envelope)
    except Exception as e:  # noqa: BLE001
        return False, f"EAH_RECOMPUTATION_FAILED:{type(e).__name__}"
    if daaw.get("execution_authority_hash") != recomputed:
        return False, "EAH_MISMATCH"

    # liaison cible ↔ enveloppe (miroir de `env.action = w.action`, Lean 4A)
    children = execution_envelope.get("children") or []
    if len(children) != 1:
        return False, "ENVELOPE_NOT_SINGLE_CHILD"
    if children[0].get("target_path") != daaw.get("target_path"):
        return False, "ENVELOPE_TARGET_MISMATCH"

    return True, None


# ══════════════════════════════════════════════════════════════════════════
#  4 — Séparation sémantique (miroir de `SemanticDecisionNonSovereign`, 4B)
# ══════════════════════════════════════════════════════════════════════════

def semantic_decision_is_mission_authorization(_human_mission_decision) -> bool:
    """Une résolution de HOLD sémantique n'est JAMAIS une autorisation de
    mission. Toujours False."""
    return False
