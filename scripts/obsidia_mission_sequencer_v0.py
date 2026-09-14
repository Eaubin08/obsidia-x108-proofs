"""
obsidia_mission_sequencer_v0.py
===============================
STAGE_3D — SÉQUENCEUR mince, déterministe, NON SOUVERAIN qui COMPOSE les
primitives déjà committées et prouvées en UNE mission bornée multi-actions :

  Checkpoint 1 (obsidia_isolated_work_unit_v0)   — pont mono-action gouverné
  Checkpoint 2 (obsidia_bounded_mission_v0)      — mission persistante + plan
                                                   borné immuable + tip dérivé
  Stage 3A (obsidia_mission_local_snapshot_v0)   — gel Git local d'un KEEP
  Stage 3B (dans bounded_mission)                — snapshot vérifié -> mission_tip
  Stage 3C (dans isolated_work_unit)             — base d'action dynamique

Ce module :

  * N'EST PAS une autorité d'exécution. Il ne crée AUCUNE HumanApproval,
    n'invoque AUCUN KX108, n'écrit AUCUNE cible, n'appelle NI C2 NI D2,
    ne fait AUCUN `git commit`/push/merge/rebase, ne génère NI source NI
    plan. Il APPELLE les interfaces existantes.
  * NE choisit PAS l'action suivante par heuristique ni par modèle : la
    prochaine action READY est l'unique première dans l'ordre topologique
    DÉTERMINISTE (`obsidia_batch_selector.compute_execution_order`,
    réutilisé), dont toutes les dépendances sont KEEP.
  * exécute AU PLUS UNE mutation de cible gouvernée par appel `advance`.
    Après avoir exécuté l'action N (+ snapshot + record + prepare N+1) il
    S'ARRÊTE en renvoyant `MISSION_AWAITING_HUMAN_EAH_APPROVAL` pour N+1.
  * exige UN EAH humain EXACT par action (jamais wildcard, jamais mission-
    wide, jamais réutilisation d'un EAH d'action précédente, jamais
    génération automatique). `HumanMissionDecision` (résolution de HOLD
    sémantique) et `human_authorized_execution_authority_hash` sont des
    entrées STRUCTURELLEMENT DISJOINTES ; les deux dans un même appel ->
    fail-closed.
  * sur toute issue non-KEEP (ROLLED_BACK / QUARANTINE / dérive
    d'enveloppe / erreur) : AUCUN snapshot, AUCUNE avancée de tip, AUCUNE
    préparation de l'action suivante -> PLAN_BLOCKED global (Stage 3
    HOLD_SCOPE = GLOBAL_MISSION). Aucune réparation autonome, aucune
    boucle de retry.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_bounded_mission_v0 as _M
import obsidia_mission_local_snapshot_v0 as _LS
import obsidia_mission_authority_integration_v0 as _INT   # Stage 4E : dérivation DAAW (ÉVIDENCE, non exécution)

DECISION_AUTHORITY = "NON_SOVEREIGN"

# ── Statuts publics de `advance_bounded_mission` ──
MISSION_AWAITING_HUMAN_EAH_APPROVAL = "MISSION_AWAITING_HUMAN_EAH_APPROVAL"
HOLD_FOR_HUMAN_DECISION = "HOLD_FOR_HUMAN_DECISION"
PLAN_EXECUTION_COMPLETE = "PLAN_EXECUTION_COMPLETE"
PLAN_BLOCKED = "PLAN_BLOCKED"
ADVANCE_REJECTED = "ADVANCE_REJECTED"
MISSION_ADVANCE_LOST_RACE = "MISSION_ADVANCE_LOST_RACE"
ADVANCE_INPUT_AMBIGUOUS = "ADVANCE_INPUT_AMBIGUOUS"
# Stage 4E : routage NON_SOUVERAIN au niveau mission — refus de progresser depuis
# une mission Stage-4-préparée dont la dérivation du DAAW échoue (HMA révoquée /
# invalide / dépendance non satisfaite). N'a AUCUN effet sur PRE/KX108.
MISSION_AUTHORITY_HOLD = "MISSION_AUTHORITY_HOLD"

# Stage 4G : mode BOUNDED_MISSION_AUTHORITY explicite. Après avoir préparé la
# prochaine action (EAH canonique + DAAW dérivé), la mission N'ATTEND AUCUN EAH
# humain par action — l'appel `advance` suivant l'exécute directement via le rail
# Stage 4F. Rythme identique à Stage 3D : ≤1 mutation gouvernée par appel.
MISSION_STAGE4_ACTION_PREPARED = "MISSION_STAGE4_ACTION_PREPARED"

AUTHORITY_MODE_PER_ACTION_HUMAN_EAH = _M._WU._DRV.AUTHORITY_MODE_PER_ACTION_HUMAN_EAH
AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY = _M._WU._DRV.AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY
DEFAULT_AUTHORITY_MODE = _M._WU._DRV.DEFAULT_AUTHORITY_MODE

MAX_GOVERNED_TARGET_MUTATIONS_PER_ADVANCE_CALL = 1

_KEPT = _M._KEPT   # GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW


def _rej(status: str, reason: str, **extra) -> dict:
    return {"status": status, "reason": reason, "authority": "NON_SOVEREIGN",
            "decision_authority": DECISION_AUTHORITY,
            "sequencer_is_authority": False,
            "governed_target_mutations_this_call": extra.pop("_mut", 0), **extra}


def advance_bounded_mission(
    *,
    mission_id: str,
    plan_id: str,
    work_unit: "_M._WU.IsolatedWorkUnit",
    ledger_dir: "str | Path", selector_dir: "str | Path",
    execution_dir: "str | Path", pre_execution_context_dir: "str | Path",
    kx108_pre_decision_dir: "str | Path", kx108_post_decision_dir: "str | Path",
    test_contract_results_dir: "str | Path", sealed_receipt_dir: "str | Path",
    sealed_rollback_evidence_dir: "str | Path", rollback_result_dir: "str | Path",
    mission_store_dir: "str | Path", hold_store_dir: "str | Path",
    decision_store_dir: "str | Path", snapshot_store_dir: "str | Path",
    human_authorized_execution_authority_hash: "Optional[str]" = None,
    human_authorization_reference: "Optional[str]" = None,
    human_mission_decision_id: "Optional[str]" = None,
    authority_mode: str = DEFAULT_AUTHORITY_MODE,
) -> dict:
    """Fait avancer la mission d'AU PLUS une mutation de cible gouvernée.

    STAGE 4G — `authority_mode` :
      * `PER_ACTION_HUMAN_EAH` (défaut) : rythme Stage 3D INCHANGÉ ; chaque
        action préparée s'arrête sur `MISSION_AWAITING_HUMAN_EAH_APPROVAL`
        jusqu'à réception d'un EAH humain exact.
      * `BOUNDED_MISSION_AUTHORITY` (EXPLICITE ; jamais d'auto-upgrade) :
        exige une HumanMissionAuthorization liée à la mission ; aucune
        entrée EAH/référence/décision humaine par action ; une action
        préparée est exécutée par l'appel `advance` suivant via le rail
        Stage 4F (DMAE canonique + KX108_PRE/POST souverains par action).
        Échec de validation Stage 4 → HOLD, JAMAIS de repli vers Stage 3.
    """
    mut = 0
    eah = human_authorized_execution_authority_hash
    ref = human_authorization_reference
    hmd = human_mission_decision_id
    if authority_mode not in (AUTHORITY_MODE_PER_ACTION_HUMAN_EAH,
                              AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY):
        return _rej(ADVANCE_REJECTED, f"UNKNOWN_AUTHORITY_MODE:{authority_mode}")
    _stage4 = (authority_mode == AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY)

    # ── Entrées d'autorité mutuellement exclusives ──
    if (eah is not None) and (hmd is not None):
        return _rej(ADVANCE_INPUT_AMBIGUOUS, "EAH_AND_SEMANTIC_DECISION_IN_SAME_CALL",
                    semantic_decision_is_execution_approval=False)
    if _stage4 and (eah is not None or ref is not None or hmd is not None):
        return _rej(ADVANCE_INPUT_AMBIGUOUS, "STAGE4_MODE_REJECTS_PER_ACTION_HUMAN_INPUT",
                    semantic_decision_is_execution_approval=False)

    proj = _M.project_mission(mission_id=mission_id, mission_store_dir=mission_store_dir,
                              hold_store_dir=hold_store_dir)
    if proj["status"] != _M.STATUS_PROJECTION_OK:
        return _rej(ADVANCE_REJECTED, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}")
    if not proj.get("active_plan_id"):
        return _rej(ADVANCE_REJECTED, "NO_PLAN_BOUND")
    if proj["active_plan_id"] != plan_id:
        return _rej(ADVANCE_REJECTED, f"PLAN_ID_MISMATCH:{proj['active_plan_id']}")

    genesis = _M.load_mission_genesis(mission_id, mission_store_dir)
    plan = _M.load_mission_plan(mission_id, plan_id, mission_store_dir)
    ok_p, why_p = _M.verify_mission_plan(plan, genesis=genesis)
    if not ok_p:
        return _rej(ADVANCE_REJECTED, f"PLAN_INVALID:{why_p}")
    if plan["plan_hash"] != proj["active_plan_hash"]:
        return _rej(ADVANCE_REJECTED, "PLAN_HASH_DRIFT")
    if proj.get("plan_completed"):
        return {"status": PLAN_EXECUTION_COMPLETE, "reason": "PLAN_ALREADY_COMPLETED",
                "mission_id": mission_id, "plan_id": plan_id,
                "current_state": proj["current_state"], "mission_tip_sha": proj["mission_tip_sha"],
                "governed_target_mutations_this_call": 0}

    state = proj["current_state"]

    # ══ HELD : résolution sémantique OU arrêt pour décision humaine ══
    if state == _M.S_HELD:
        if hmd is None:
            ah = proj.get("active_hold") or {}
            return {"status": HOLD_FOR_HUMAN_DECISION, "reason": None,
                    "mission_id": mission_id, "plan_id": plan_id,
                    "hold_id": proj.get("active_hold_id"),
                    "hold_type": ah.get("hold_type"),
                    "question_for_human": ah.get("question_for_human"),
                    "bounded_options": ah.get("bounded_options"),
                    "mission_hold_record_hash": ah.get("mission_hold_record_hash"),
                    "semantic_decision_is_execution_approval": False,
                    "governed_target_mutations_this_call": 0}
        r = _M.resolve_mission_hold(
            mission_id=mission_id, hold_id=proj["active_hold_id"],
            human_mission_decision_id=hmd, work_unit=work_unit,
            mission_store_dir=mission_store_dir, hold_store_dir=hold_store_dir,
            decision_store_dir=decision_store_dir,
            execution_dir=execution_dir, pre_execution_context_dir=pre_execution_context_dir,
        )
        if r["status"] != _M.STATUS_HOLD_RESOLVED:
            return _rej(ADVANCE_REJECTED, f"HOLD_RESOLVE_FAILED:{r.get('reason')}")
        proj = _M.project_mission(mission_id=mission_id, mission_store_dir=mission_store_dir,
                                  hold_store_dir=hold_store_dir)
        if proj["status"] != _M.STATUS_PROJECTION_OK:
            return _rej(ADVANCE_REJECTED, f"MISSION_NOT_PROJECTABLE_AFTER_RESOLVE:{proj.get('reason')}")
        state = proj["current_state"]

    # ══ ACTION_PREPARED : (Stage 3) attend l'EAH humain exact puis exécute
    #    CETTE action ; (Stage 4G) exécute directement CETTE action via le rail
    #    Stage 4F, sans aucun EAH humain par action. ══
    if state == _M.S_ACTION_PREPARED:
        prepared = proj.get("last_prepared_evidence") or {}
        cur_aid = prepared.get("action_id")
        cur_ord = prepared.get("ordinal")
        if (not _stage4) and hmd is not None:
            return _rej(ADVANCE_INPUT_AMBIGUOUS, "SEMANTIC_DECISION_SUPPLIED_BUT_ACTION_AWAITS_EAH")
        if (not _stage4) and eah is None:
            return {"status": MISSION_AWAITING_HUMAN_EAH_APPROVAL, "reason": None,
                    "mission_id": mission_id, "plan_id": plan_id,
                    "action_id": cur_aid, "ordinal": cur_ord,
                    "execution_authority_hash": prepared.get("execution_authority_hash"),
                    "batch_execution_id": prepared.get("batch_execution_id"),
                    "child_execution_id": prepared.get("child_execution_id"),
                    "human_authorization_reference_required": True,
                    "eah_per_action_unchanged": True,
                    "governed_target_mutations_this_call": 0}
        if (not _stage4) and not (isinstance(ref, str) and ref.strip()):
            return _rej(ADVANCE_REJECTED, "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED")

        if _stage4:
            # mission RÉELLEMENT autorisée Stage 4 : HMA liée + DAAW dérivé pour
            # CETTE action préparée. Sinon HOLD — jamais de repli vers Stage 3.
            if not proj.get("active_hma_id"):
                return {"status": MISSION_AUTHORITY_HOLD, "reason": "NO_MISSION_AUTHORITY_BOUND",
                        "mission_id": mission_id, "plan_id": plan_id, "action_id": cur_aid,
                        "ordinal": cur_ord, "stage4_to_stage3_autofallback": False,
                        "governed_target_mutations_this_call": 0}
            _dw = next((w for w in (proj.get("derived_witnesses") or [])
                        if w.get("action_id") == cur_aid), None)
            if _dw is None:
                return {"status": MISSION_AUTHORITY_HOLD, "reason": "NO_DERIVED_WITNESS_FOR_PREPARED_ACTION",
                        "mission_id": mission_id, "plan_id": plan_id, "action_id": cur_aid,
                        "ordinal": cur_ord, "stage4_to_stage3_autofallback": False,
                        "governed_target_mutations_this_call": 0}

        prev_tip = proj["mission_tip_sha"]
        ex = _M.execute_mission_action(
            mission_id=mission_id, work_unit=work_unit,
            batch_execution_id=prepared.get("batch_execution_id"),
            child_execution_id=prepared.get("child_execution_id"),
            human_authorized_execution_authority_hash=(None if _stage4 else eah),
            human_authorization_reference=(None if _stage4 else ref),
            authority_mode=authority_mode,
            execution_dir=execution_dir, pre_execution_context_dir=pre_execution_context_dir,
            selector_dir=selector_dir, ledger_dir=ledger_dir,
            kx108_pre_decision_dir=kx108_pre_decision_dir, kx108_post_decision_dir=kx108_post_decision_dir,
            test_contract_results_dir=test_contract_results_dir, sealed_receipt_dir=sealed_receipt_dir,
            sealed_rollback_evidence_dir=sealed_rollback_evidence_dir, rollback_result_dir=rollback_result_dir,
            mission_store_dir=mission_store_dir,
        )
        estatus = ex.get("status")
        if estatus == _M.STATUS_MISSION_EXECUTE_BLOCKED_ENVELOPE_DRIFT:
            return {"status": PLAN_BLOCKED, "reason": "ENVELOPE_DRIFT",
                    "mission_id": mission_id, "plan_id": plan_id, "action_id": cur_aid,
                    "current_state": _M.S_ACTION_PREPARED, "checkpoint2_result": ex,
                    "governed_target_mutations_this_call": 0}
        if estatus == _M.STATUS_EXECUTE_REJECTED:
            reason = ex.get("reason") or ""
            lost = "IMMUTABILITY" in reason or "REVISION" in reason or "PARENT" in reason
            return _rej(MISSION_ADVANCE_LOST_RACE if lost else ADVANCE_REJECTED,
                        f"EXECUTE_REJECTED:{reason}", action_id=cur_aid,
                        two_advance_calls_cannot_execute_same_action_twice=True)
        if estatus != _M.STATUS_ACTION_RECORDED:
            return _rej(ADVANCE_REJECTED, f"UNEXPECTED_EXECUTE_STATUS:{estatus}", action_id=cur_aid)

        mut = 1  # une (et une seule) mutation de cible gouvernée dans cet appel
        dstatus = ex.get("driver_status")
        if dstatus != _KEPT:
            newp = _M.project_mission(mission_id=mission_id, mission_store_dir=mission_store_dir,
                                      hold_store_dir=hold_store_dir)
            return {"status": PLAN_BLOCKED, "reason": f"ACTION_{dstatus}",
                    "mission_id": mission_id, "plan_id": plan_id,
                    "action_id": cur_aid, "ordinal": cur_ord, "driver_status": dstatus,
                    "mission_state": (newp.get("current_state") if newp["status"] == _M.STATUS_PROJECTION_OK else None),
                    "mission_tip_sha": (newp.get("mission_tip_sha") if newp["status"] == _M.STATUS_PROJECTION_OK else None),
                    "real_failure_stops_multi_action_mission": True,
                    "only_keep_can_advance_mission_tip": True,
                    "autonomous_repair_included": False,
                    "governed_target_mutations_this_call": mut}

        # ── KEEP : Stage 3A snapshot -> Stage 3B record -> tip avance ──
        c1 = ex.get("checkpoint1_result") or {}
        plan_action = next(a for a in plan["actions"] if a["action_id"] == cur_aid)
        snap = _LS.create_local_snapshot(
            mission_id=mission_id, action_id=cur_aid, ordinal=cur_ord,
            expected_branch_name=proj["branch_name"],
            expected_worktree_path=work_unit.worktree_path,
            expected_previous_mission_tip_sha=prev_tip,
            batch_execution_id=prepared.get("batch_execution_id"),
            child_execution_id=prepared.get("child_execution_id"),
            execution_authority_hash=c1.get("execution_authority_hash"),
            approval_id=c1.get("approval_id"),
            kx108_pre_decision_record_id=c1.get("kx108_pre_decision_record_id"),
            kx108_post_decision_record_id=c1.get("kx108_post_decision_record_id"),
            test_contract_result_id=c1.get("test_contract_result_id"),
            sealed_apply_receipt_id=c1.get("sealed_apply_receipt_id"),
            sealed_rollback_evidence_id=c1.get("sealed_rollback_evidence_id"),
            target_path=plan_action["target_path"],
            execution_dir=execution_dir, kx108_pre_decision_dir=kx108_pre_decision_dir,
            kx108_post_decision_dir=kx108_post_decision_dir,
            test_contract_results_dir=test_contract_results_dir,
            sealed_receipt_dir=sealed_receipt_dir, sealed_rollback_evidence_dir=sealed_rollback_evidence_dir,
            rollback_result_dir=rollback_result_dir, snapshot_store_dir=snapshot_store_dir,
        )
        if snap.get("status") not in (_LS.SNAPSHOT_COMMITTED, _LS.SNAPSHOT_IDEMPOTENT_EXISTING_IDENTICAL):
            return _rej(ADVANCE_REJECTED, f"SNAPSHOT_FAILED:{snap.get('status')}:{snap.get('reason')}",
                        action_id=cur_aid, _mut=mut)
        rec = _M.record_local_snapshot(
            mission_id=mission_id, action_id=cur_aid,
            snapshot_receipt_id=snap["snapshot_receipt_id"], work_unit=work_unit,
            snapshot_store_dir=snapshot_store_dir, mission_store_dir=mission_store_dir,
            plan_id=plan_id,
        )
        if rec.get("status") not in (_M.STATUS_LOCAL_SNAPSHOT_RECORDED, _M.STATUS_LOCAL_SNAPSHOT_EVENT_IDEMPOTENT):
            return _rej(ADVANCE_REJECTED, f"RECORD_SNAPSHOT_FAILED:{rec.get('status')}:{rec.get('reason')}",
                        action_id=cur_aid, _mut=mut)

        proj = _M.project_mission(mission_id=mission_id, mission_store_dir=mission_store_dir,
                                  hold_store_dir=hold_store_dir)
        if proj["status"] != _M.STATUS_PROJECTION_OK:
            return _rej(ADVANCE_REJECTED, f"MISSION_NOT_PROJECTABLE_AFTER_SNAPSHOT:{proj.get('reason')}", _mut=mut)
        if proj["mission_tip_sha"] != snap["new_commit_sha"]:
            return _rej(ADVANCE_REJECTED, "MISSION_TIP_NOT_ADVANCED_TO_SNAPSHOT_COMMIT", _mut=mut)
        state = proj["current_state"]   # WORKTREE_BOUND — on enchaîne sur la préparation (0 mutation)

    # ══ WORKTREE_BOUND : préparer la prochaine action READY, ou clôturer le plan ══
    if state == _M.S_WORKTREE_BOUND:
        done = set(proj.get("snapshotted_action_ids") or [])
        all_ids = [a["action_id"] for a in plan["actions"]]
        if all(aid in done for aid in all_ids):
            c = _M.close_plan(mission_id=mission_id, plan_id=plan_id, mission_store_dir=mission_store_dir)
            if c["status"] != _M.STATUS_PLAN_COMPLETED:
                return _rej(ADVANCE_REJECTED, f"PLAN_CLOSE_FAILED:{c.get('reason')}", _mut=mut)
            return {"status": PLAN_EXECUTION_COMPLETE, "reason": None,
                    "mission_id": mission_id, "plan_id": plan_id,
                    "current_state": c["current_state"],
                    "canonical_base_sha": proj["canonical_base_sha"],
                    "mission_tip_sha": proj["mission_tip_sha"],
                    "actions_kept": len(all_ids),
                    "mission_closure_stage_6_still_required": True,
                    "governed_target_mutations_this_call": mut}

        by_aid = {a["action_id"]: a for a in plan["actions"]}
        aid_by_ord = {a["ordinal"]: a["action_id"] for a in plan["actions"]}
        next_action = None
        for aid in plan["execution_order"]:
            if aid in done:
                continue
            a = by_aid.get(aid)
            if a is None:
                return _rej(ADVANCE_REJECTED, f"EXECUTION_ORDER_REFERENCES_UNKNOWN_ACTION:{aid}", _mut=mut)
            deps_ok = all(aid_by_ord.get(d) in done for d in a["dependency_ordinals"])
            if not deps_ok:
                continue
            next_action = a
            break
        if next_action is None:
            return {"status": PLAN_BLOCKED, "reason": "NO_READY_ACTION_DEPENDENCIES_UNSATISFIED",
                    "mission_id": mission_id, "plan_id": plan_id,
                    "dependency_satisfied_by": ["KEPT"],
                    "governed_target_mutations_this_call": mut}

        p = _M.prepare_mission_action(
            mission_id=mission_id, work_unit=work_unit,
            source_git_commit=next_action["source_git_commit"],
            source_historical_path=next_action["source_historical_path"],
            target_path=next_action["target_path"], test_contract=next_action["test_contract"],
            ledger_dir=ledger_dir, selector_dir=selector_dir,
            execution_dir=execution_dir, pre_execution_context_dir=pre_execution_context_dir,
            mission_store_dir=mission_store_dir,
            expected_action_base_sha=proj["mission_tip_sha"],
            plan_id=plan_id, action_id=next_action["action_id"], ordinal=next_action["ordinal"],
        )
        if p["status"] != _M.STATUS_ACTION_PREPARED:
            return _rej(ADVANCE_REJECTED, f"PREPARE_FAILED:{p.get('reason')}",
                        action_id=next_action["action_id"], checkpoint2_result=p, _mut=mut)

        # ── Stage 4E : si une HumanMissionAuthorization est liée à la mission,
        #    dériver + vérifier + persister le DAAW EXACT de cette action APRÈS que
        #    l'EAH canonique existe. ÉVIDENCE UNIQUEMENT — ne satisfait AUCUNE
        #    HumanApproval, ne touche NI le rail PRE NI KX108, n'exécute rien.
        #    (Stage 3) l'EAH humain par action reste requis ensuite ;
        #    (Stage 4G) l'appel `advance` suivant exécute directement. ──
        daaw_refs: dict = {}
        proj2 = _M.project_mission(mission_id=mission_id, mission_store_dir=mission_store_dir,
                                   hold_store_dir=hold_store_dir)
        if _stage4 and not (proj2["status"] == _M.STATUS_PROJECTION_OK and proj2.get("active_hma_id")):
            return {"status": MISSION_AUTHORITY_HOLD, "reason": "NO_MISSION_AUTHORITY_BOUND",
                    "mission_id": mission_id, "plan_id": plan_id,
                    "action_id": next_action["action_id"], "ordinal": next_action["ordinal"],
                    "stage4_to_stage3_autofallback": False,
                    "governed_target_mutations_this_call": mut}
        if proj2["status"] == _M.STATUS_PROJECTION_OK and proj2.get("active_hma_id"):
            dv = _INT.derive_and_record_action_authority_witness(
                mission_id=mission_id, work_unit=work_unit,
                execution_dir=execution_dir, mission_store_dir=mission_store_dir,
                hold_store_dir=hold_store_dir)
            if dv["status"] != _INT.WITNESS_DERIVED_AND_VERIFIED:
                return {"status": MISSION_AUTHORITY_HOLD, "reason": dv.get("reason"),
                        "mission_id": mission_id, "plan_id": plan_id,
                        "action_id": next_action["action_id"], "ordinal": next_action["ordinal"],
                        "witness_status": dv["status"],
                        "execution_authority_hash": p["execution_authority_hash"],
                        "per_action_human_eah_still_required": True,
                        "kx_pre_semantics_changed": False,
                        "daaw_is_execution_authority": False,
                        "governed_target_mutations_this_call": mut}
            daaw_refs = {
                "derived_action_authority_witness_id": dv["derived_action_authority_witness_id"],
                "daaw_record_hash": dv["daaw_record_hash"],
                "mission_authority_mode": "BOUNDED_MISSION_AUTHORITY_PREPARED",
                "daaw_is_execution_authority": False,
                "daaw_can_authorize_pre": False,
            }

        if _stage4:
            # action préparée + DAAW dérivé : l'appel `advance` suivant l'exécute
            # via le rail Stage 4F. AUCUN EAH humain par action.
            return {"status": MISSION_STAGE4_ACTION_PREPARED, "reason": None,
                    "mission_id": mission_id, "plan_id": plan_id,
                    "action_id": next_action["action_id"], "ordinal": next_action["ordinal"],
                    "execution_authority_hash": p["execution_authority_hash"],
                    "batch_execution_id": p["batch_execution_id"],
                    "child_execution_id": p["child_execution_id"],
                    "prepared_action_base_sha": proj["mission_tip_sha"],
                    "authority_mode": AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY,
                    "human_authorization_reference_required": False,
                    "per_action_human_eah_required": False,
                    "next_call_executes_this_action": True,
                    "governed_target_mutations_this_call": mut, **daaw_refs}

        return {"status": MISSION_AWAITING_HUMAN_EAH_APPROVAL, "reason": None,
                "mission_id": mission_id, "plan_id": plan_id,
                "action_id": next_action["action_id"], "ordinal": next_action["ordinal"],
                "execution_authority_hash": p["execution_authority_hash"],
                "batch_execution_id": p["batch_execution_id"],
                "child_execution_id": p["child_execution_id"],
                "prepared_action_base_sha": proj["mission_tip_sha"],
                "human_authorization_reference_required": True,
                "eah_per_action_unchanged": True,
                "governed_target_mutations_this_call": mut, **daaw_refs}

    return _rej(ADVANCE_REJECTED, f"MISSION_STATE_NOT_ADVANCEABLE:{state}", _mut=mut)
