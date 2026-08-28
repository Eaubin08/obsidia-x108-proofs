"""
obsidia_mission_authority_integration_v0.py
===========================================
STAGE 4E — couture MINCE entre le cycle de vie de la mission bornée (Stage 3)
et le sous-système d'autorité de mission Stage 4C.

Elle fait DEUX choses, toutes deux NON_SOUVERAINES :

  1. bind_mission_authority_from_human_reference(...) — construit + persiste
     write-once UNE HumanMissionAuthorization (via l'humain qui FOURNIT la
     `human_authorization_reference` — jamais synthétisée), la vérifie, puis
     lie sa référence à la mission (`MISSION_AUTHORITY_BOUND`).

  2. derive_and_record_action_authority_witness(...) — pour l'action COURANTE
     déjà préparée par le rail Stage 3 (donc l'EAH canonique EXISTE) :
       recharge l'HMA -> revérifie (révocations incluses) -> recharge la
       projection + l'ExecutionEnvelope canonique -> derive_action_authority_witness
       (Stage 4C, réutilisé) -> verify_derived_action_authority_witness
       (Stage 4C, réutilisé) -> persistance write-once du DAAW EXACT ->
       événement mission `ACTION_AUTHORITY_WITNESS_DERIVED`.

CE QU'ELLE NE FAIT JAMAIS :
  * rendre HMA/DAAW acceptable par le rail PRE / KX108 / HumanApproval ;
  * exécuter une action, muter une cible, faire un `git`, créer une
    HumanApproval ou une décision KX ;
  * changer `approved_by`, le schéma HumanApproval, ou la sémantique KX108 ;
  * retirer l'EAH humain par action.

Le mode d'exécution runtime demeure PER_ACTION_HUMAN_EAH. Le DAAW est
ÉVIDENCE UNIQUEMENT.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_bounded_mission_v0 as _M
import obsidia_mission_authority_v0 as _MA        # HMA/DAAW build+verify COMMITTÉS (réutilisés)
import obsidia_batch_execution as _E              # _load_execution + compute_execution_authority_hash

RUNTIME_AUTHORITY_ACTIVE = False
STAGE4_EXECUTION_INTEGRATION = False
PER_ACTION_HUMAN_EAH_STILL_REQUIRED = True

MISSION_AUTHORITY_BOUND = "MISSION_AUTHORITY_BOUND"
MISSION_AUTHORITY_BIND_REJECTED = "MISSION_AUTHORITY_BIND_REJECTED"
WITNESS_DERIVED_AND_VERIFIED = "ACTION_AUTHORITY_WITNESS_DERIVED_AND_VERIFIED"
WITNESS_DERIVATION_HOLD = "ACTION_AUTHORITY_WITNESS_DERIVATION_HOLD"
WITNESS_DERIVATION_REJECTED = "ACTION_AUTHORITY_WITNESS_DERIVATION_REJECTED"


def _witness_dir(mission_id: str, mission_store_dir: "str | Path") -> Path:
    return _M._mission_dir(mission_id, Path(mission_store_dir)) / "action_authority_witnesses"


def _hold(reason: str, **extra) -> dict:
    return {"status": WITNESS_DERIVATION_HOLD, "reason": reason,
            "per_action_human_eah_still_required": True,
            "kx_pre_semantics_changed": False,
            "daaw_is_execution_authority": False, **extra}


def _rej(reason: str, **extra) -> dict:
    return {"status": WITNESS_DERIVATION_REJECTED, "reason": reason,
            "per_action_human_eah_still_required": True,
            "kx_pre_semantics_changed": False,
            "daaw_is_execution_authority": False, **extra}


# ══════════════════════════════════════════════════════════════════════════
#  1 — Liaison d'UNE HumanMissionAuthorization à la mission
# ══════════════════════════════════════════════════════════════════════════

def bind_mission_authority_from_human_reference(
    *, mission_id: str, human_authorization_reference: str,
    mission_store_dir: "str | Path",
    revocation_policy: str = _MA.DEFAULT_REVOCATION_POLICY,
) -> dict:
    """L'humain FOURNIT `human_authorization_reference`. Le stack ne la
    synthétise JAMAIS — `_MA.build_human_mission_authorization` échoue fermé
    (`HUMAN_AUTHORIZATION_REFERENCE_REQUIRED`) si elle est vide."""
    proj = _M.project_mission(mission_id=mission_id, mission_store_dir=mission_store_dir)
    if proj["status"] != _M.STATUS_PROJECTION_OK:
        return {"status": MISSION_AUTHORITY_BIND_REJECTED,
                "reason": f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}"}
    if proj["current_state"] != _M.S_WORKTREE_BOUND:
        return {"status": MISSION_AUTHORITY_BIND_REJECTED,
                "reason": f"MISSION_NOT_IN_WORKTREE_BOUND_STATE:{proj['current_state']}"}
    plan_id = proj.get("active_plan_id")
    if not plan_id:
        return {"status": MISSION_AUTHORITY_BIND_REJECTED, "reason": "NO_PLAN_BOUND"}

    br = _MA.bind_human_mission_authorization(
        mission_id=mission_id, plan_id=plan_id,
        human_authorization_reference=human_authorization_reference,
        mission_store_dir=mission_store_dir, revocation_policy=revocation_policy)
    if br["status"] != _MA.HMA_BOUND:
        return {"status": MISSION_AUTHORITY_BIND_REJECTED, "reason": f"HMA_BIND_REJECTED:{br.get('reason')}"}

    genesis = _M.load_mission_genesis(mission_id, mission_store_dir)
    plan = _M.load_mission_plan(mission_id, plan_id, mission_store_dir)
    hma = _MA.load_human_mission_authorization(mission_id, br["human_mission_authorization_id"], mission_store_dir)
    ok, why = _MA.verify_human_mission_authorization(
        hma, genesis=genesis, plan=plan,
        revocations=_MA.list_mission_authority_revocations(mission_id, mission_store_dir))
    if not ok:
        return {"status": MISSION_AUTHORITY_BIND_REJECTED, "reason": f"HMA_VERIFY_REJECTED:{why}"}

    mb = _M.bind_mission_authority(
        mission_id=mission_id, hma_id=hma["human_mission_authorization_id"],
        hma_record_hash=hma["hma_record_hash"], plan_id=plan["plan_id"],
        plan_hash=plan["plan_hash"], mission_store_dir=mission_store_dir)
    if mb["status"] != _M.STATUS_MISSION_AUTHORITY_BOUND:
        return {"status": MISSION_AUTHORITY_BIND_REJECTED, "reason": f"MISSION_BIND_REJECTED:{mb.get('reason')}"}
    return {"status": MISSION_AUTHORITY_BOUND, "reason": None, "mission_id": mission_id,
            "human_mission_authorization_id": hma["human_mission_authorization_id"],
            "hma_record_hash": hma["hma_record_hash"], "plan_id": plan["plan_id"],
            "plan_hash": plan["plan_hash"],
            "mission_authority_mode": "BOUNDED_MISSION_AUTHORITY_PREPARED",
            "hma_issuer": "HUMAN", "is_execution_authority": False,
            "hma_can_authorize_pre": False, "hma_can_satisfy_human_approval": False}


# ══════════════════════════════════════════════════════════════════════════
#  2 — Dérivation + vérification + persistance du DAAW de l'action courante
# ══════════════════════════════════════════════════════════════════════════

def derive_and_record_action_authority_witness(
    *, mission_id: str, work_unit, execution_dir: "str | Path",
    mission_store_dir: "str | Path", hold_store_dir: "Optional[str | Path]" = None,
) -> dict:
    """À appeler APRÈS que le rail Stage 3 a préparé l'action courante (l'EAH
    canonique existe). Ne dérive JAMAIS avant l'enveloppe ; ne prédit / ne
    patche JAMAIS l'EAH."""
    proj = _M.project_mission(mission_id=mission_id, mission_store_dir=mission_store_dir,
                              hold_store_dir=hold_store_dir)
    if proj["status"] != _M.STATUS_PROJECTION_OK:
        return _rej(f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if not proj.get("active_hma_id"):
        return _hold("NO_MISSION_AUTHORITY_BOUND")
    if proj["current_state"] != _M.S_ACTION_PREPARED:
        return _hold(f"MISSION_NOT_IN_ACTION_PREPARED_STATE:{proj['current_state']}")
    if proj.get("plan_completed"):
        return _hold("MISSION_PLAN_COMPLETED")

    pe = proj.get("last_prepared_evidence") or {}
    action_id = pe.get("action_id")
    ordinal = pe.get("ordinal")
    beid = pe.get("batch_execution_id")
    prepared_eah = pe.get("execution_authority_hash")
    if not (action_id and beid and _M._is_64_hex(prepared_eah or "")):
        return _rej("PREPARED_EVIDENCE_INCOMPLETE")

    # Témoin déjà consigné pour cette action : on NE renvoie PAS aveuglément
    # l'existant. On dérive à nouveau depuis la préparation COURANTE puis on
    # exige l'égalité EXACTE (daaw_id / record_hash / EAH / action_base) avec le
    # témoin enregistré ; toute divergence -> HOLD (jamais un 2e témoin, jamais
    # un rebinding silencieux).
    _recorded = next((w for w in (proj.get("derived_witnesses") or [])
                      if w.get("action_id") == action_id), None)

    genesis = _M.load_mission_genesis(mission_id, mission_store_dir)
    plan = _M.load_mission_plan(mission_id, proj["active_hma_plan_id"], mission_store_dir)
    hma = _MA.load_human_mission_authorization(mission_id, proj["active_hma_id"], mission_store_dir)
    if hma is None or plan is None or genesis is None:
        return _rej("HMA_OR_PLAN_OR_GENESIS_NOT_LOADABLE")

    revocations = _MA.list_mission_authority_revocations(mission_id, mission_store_dir)
    ok_h, why_h = _MA.verify_human_mission_authorization(
        hma, genesis=genesis, plan=plan, revocations=revocations)
    if not ok_h:
        # Routage NON_SOUVERAIN au niveau mission : refus de progresser depuis une
        # mission Stage-4-préparée dont l'HMA est révoquée/invalide. AUCUN changement
        # de sémantique PRE/KX108 — l'application de la révocation comme veto
        # d'exécution appartient à 4F.
        return _hold(f"HMA_INVALID_ROUTING_HOLD:{why_h}", hma_invalid=True,
                     revocation_enforcement_belongs_to="STAGE_4F")

    env = _E._load_execution(beid, Path(execution_dir))
    if env is None:
        return _rej(f"EXECUTION_ENVELOPE_NOT_FOUND:{beid}")

    daaw, why_d = _MA.derive_action_authority_witness(
        hma=hma, plan=plan, action_id=action_id, projection=proj, execution_envelope=env)
    if daaw is None:
        return _rej(f"DAAW_DERIVE_REJECTED:{why_d}")

    # L'EAH lié DOIT être l'EAH canonique de la préparation (jamais prédit/patché).
    if daaw["execution_authority_hash"] != prepared_eah:
        return _rej("DAAW_EAH_NOT_PREPARED_CANONICAL_EAH")

    ok_v, why_v = _MA.verify_derived_action_authority_witness(
        daaw=daaw, hma=hma, plan=plan, genesis=genesis, projection=proj,
        execution_envelope=env, revocations=revocations)
    if not ok_v:
        return _rej(f"DAAW_VERIFY_REJECTED:{why_v}")

    fresh = {"daaw_id": daaw["derived_action_authority_witness_id"],
             "daaw_record_hash": daaw["daaw_record_hash"],
             "execution_authority_hash": daaw["execution_authority_hash"],
             "action_base_sha": daaw["action_base_sha"]}

    # ── Idempotence liée au MATÉRIEL EXACT du témoin ──
    if _recorded is not None:
        rec = {k: _recorded.get(k) for k in fresh}
        if fresh != rec:
            return _hold("WITNESS_MATERIAL_DIVERGES_FROM_RECORDED",
                         recorded_daaw_id=_recorded.get("daaw_id"),
                         fresh_daaw_id=fresh["daaw_id"])
        # évidence canonique : l'artefact write-once doit exister et concorder
        art = load_action_authority_witness(mission_id, _recorded.get("daaw_id"), mission_store_dir)
        if not (isinstance(art, dict)
                and art.get("derived_action_authority_witness_id") == _recorded.get("daaw_id")
                and art.get("daaw_record_hash") == _recorded.get("daaw_record_hash")
                and art.get("execution_authority_hash") == _recorded.get("execution_authority_hash")
                and art.get("action_base_sha") == _recorded.get("action_base_sha")
                and art.get("human_mission_authorization_id") == _recorded.get("hma_id")):
            return _rej("WITNESS_ARTIFACT_DISAGREES_WITH_EVENT")
        return {"status": WITNESS_DERIVED_AND_VERIFIED, "reason": None,
                "mission_id": mission_id, "action_id": action_id, "ordinal": ordinal,
                "derived_action_authority_witness_id": _recorded.get("daaw_id"),
                "daaw_record_hash": _recorded.get("daaw_record_hash"),
                "execution_authority_hash": _recorded.get("execution_authority_hash"),
                "action_base_sha": _recorded.get("action_base_sha"),
                "idempotent": True, "per_action_human_eah_still_required": True,
                "daaw_is_execution_authority": False, "daaw_can_authorize_pre": False,
                "daaw_can_satisfy_human_approval": False}

    # Persistance write-once.
    try:
        p = _M._safe_id_path(_witness_dir(mission_id, mission_store_dir),
                             daaw["derived_action_authority_witness_id"])
    except ValueError:
        return _rej("INVALID_DAAW_ID")
    st = _M._atomic_publish_json(p, daaw)
    if st == "IMMUTABILITY_VIOLATION":
        return _rej("DAAW_IMMUTABILITY_VIOLATION")

    rr = _M.record_action_authority_witness(
        mission_id=mission_id, action_id=action_id, ordinal=ordinal,
        daaw_id=daaw["derived_action_authority_witness_id"],
        daaw_record_hash=daaw["daaw_record_hash"],
        execution_authority_hash=daaw["execution_authority_hash"],
        action_base_sha=daaw["action_base_sha"],
        hma_id=hma["human_mission_authorization_id"], mission_store_dir=mission_store_dir)
    if rr["status"] not in (_M.STATUS_ACTION_AUTHORITY_WITNESS_RECORDED,
                            _M.STATUS_ACTION_AUTHORITY_WITNESS_EVENT_IDEMPOTENT):
        return _rej(f"WITNESS_EVENT_REJECTED:{rr.get('reason')}")

    return {"status": WITNESS_DERIVED_AND_VERIFIED, "reason": None,
            "mission_id": mission_id, "action_id": action_id, "ordinal": ordinal,
            "derived_action_authority_witness_id": daaw["derived_action_authority_witness_id"],
            "daaw_record_hash": daaw["daaw_record_hash"],
            "execution_authority_hash": daaw["execution_authority_hash"],
            "action_base_sha": daaw["action_base_sha"],
            "daaw_store_status": st, "mission_event_status": rr["status"],
            "per_action_human_eah_still_required": True,
            "daaw_is_execution_authority": False, "daaw_can_authorize_pre": False,
            "daaw_can_satisfy_human_approval": False}


def load_action_authority_witness(mission_id: str, daaw_id: str,
                                  mission_store_dir: "str | Path") -> Optional[dict]:
    import json
    try:
        p = _M._safe_id_path(_witness_dir(mission_id, mission_store_dir), daaw_id)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
