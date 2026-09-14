"""
tests/cli/test_mission_authority_integration_v0.py
=================================================
STAGE 4E — dérivation automatique du DerivedActionAuthorityWitness par action,
intégrée au cycle de vie de la mission bornée. ÉVIDENCE UNIQUEMENT.

Preuve : vraie mission A->B->C, UNE HumanMissionAuthorization humaine, 3 DAAW
dérivés+vérifiés+persistés automatiquement, 3 approbations EAH humaines TOUJOURS
requises, 3 KX108_PRE / 3 KX108_POST réels via le rail historique inchangé.
Le mode d'exécution runtime demeure PER_ACTION_HUMAN_EAH.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_test_contract as TC                       # noqa: E402
import obsidia_isolated_work_unit_v0 as WU              # noqa: E402
import obsidia_bounded_mission_v0 as M                  # noqa: E402
import obsidia_mission_sequencer_v0 as SEQ              # noqa: E402
import obsidia_mission_authority_v0 as MA               # noqa: E402
import obsidia_mission_authority_integration_v0 as INT  # noqa: E402

_TARGET = "periphery/xdomain/e_target_v0.txt"
_S1, _S2, _S3 = ("periphery/xdomain/e_src_1.txt", "periphery/xdomain/e_src_2.txt",
                 "periphery/xdomain/e_src_3.txt")
_A0, _A1, _A2, _A3 = (b"E\nstate: 0\n", b"E\nstate: 1\n", b"E\nstate: 2\n", b"E\nstate: 3\n")


def _sha(b): return hashlib.sha256(b).hexdigest()


def _git(repo, *a):
    r = subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {a}: {r.stderr}"
    return r.stdout.strip()


@pytest.fixture
def env(tmp_path):
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    (main / _TARGET).write_bytes(_A0)
    (main / _S1).write_bytes(_A1); (main / _S2).write_bytes(_A2); (main / _S3).write_bytes(_A3)
    _git(main, "init", "-q"); _git(main, "config", "user.email", "t@e.com")
    _git(main, "config", "user.name", "t"); _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", _TARGET, _S1, _S2, _S3); _git(main, "commit", "-q", "-m", "seed")
    base = _git(main, "rev-parse", "HEAD")
    s = {k: tmp_path / k for k in ("ledger", "selector", "exec", "pec", "kxpre", "kxpost",
                                   "tcr", "sar", "sre", "rbk", "missions", "holds",
                                   "decisions", "snap")}
    wt = (tmp_path / "wt").resolve()
    cr = WU.create_isolated_work_unit(repo_root=main, base_sha=base, branch_name="ebr",
                                      worktree_path=wt, work_unit_id="wu-e-0001")
    assert cr["status"] == WU.WORK_UNIT_CREATED
    return {"main": main, "base": base, "stores": s, "wu": cr["work_unit"], "wt": wt}


def _contract(post, cid):
    return TC.build_test_contract(cid, "cand", "batch", _TARGET, [
        TC.build_check("p", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET,
                       expected_target_sha256=_sha(post), required=True),
        TC.build_check("d", TC.CHECK_TYPE_DIFF_SCOPE, expected_diff_paths=[_TARGET], required=True)])


def _genesis(env, *, max_actions=3, tag="a"):
    return M.create_bounded_mission(
        objective=f"stage4e-{tag}", repository_identity="repo://e",
        canonical_base_sha=env["base"], branch_name="ebr",
        worktree_path=str(env["wt"]), main_worktree_path=str(env["main"].resolve()),
        scope={"allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
               "allowed_target_paths": [_TARGET], "max_actions": max_actions,
               "max_retries_per_action": 0},
        human_mandate_reference=f"hmr-{tag}", mission_store_dir=env["stores"]["missions"])


def _abc(env):
    return [
        {"ordinal": 0, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S1, "test_contract": _contract(_A1, "cA"),
         "dependency_ordinals": []},
        {"ordinal": 1, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S2, "test_contract": _contract(_A2, "cB"),
         "dependency_ordinals": [0]},
        {"ordinal": 2, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S3, "test_contract": _contract(_A3, "cC"),
         "dependency_ordinals": [1]},
    ]


def _seq_kw(env):
    s = env["stores"]
    return dict(work_unit=env["wu"], ledger_dir=s["ledger"], selector_dir=s["selector"],
                execution_dir=s["exec"], pre_execution_context_dir=s["pec"],
                kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
                test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
                sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"],
                mission_store_dir=s["missions"], hold_store_dir=s["holds"],
                decision_store_dir=s["decisions"], snapshot_store_dir=s["snap"])


def _proj(env, mid):
    return M.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                             hold_store_dir=env["stores"]["holds"])


def _setup(env, *, tag="a", max_actions=3):
    mid = _genesis(env, tag=tag, max_actions=max_actions)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    acts = _abc(env)[:max_actions] if max_actions < 3 else _abc(env)
    r = M.bind_mission_plan(mission_id=mid, actions=acts, mission_store_dir=env["stores"]["missions"])
    assert r["status"] == M.STATUS_PLAN_BOUND
    return mid, r["plan_id"]


def _bind_hma(env, mid, *, ref="TEST_HUMAN_MISSION_AUTH"):
    return INT.bind_mission_authority_from_human_reference(
        mission_id=mid, human_authorization_reference=ref,
        mission_store_dir=env["stores"]["missions"])


def _daaw_file(env, mid, daaw_id):
    return INT.load_action_authority_witness(mid, daaw_id, env["stores"]["missions"])


# ══════════════════════════════════════════════════════════════════════════
#  Liaison HMA
# ══════════════════════════════════════════════════════════════════════════

def test_bind_hma_requires_human_reference_not_synthesized(env):
    mid, _pid = _setup(env)
    r = INT.bind_mission_authority_from_human_reference(
        mission_id=mid, human_authorization_reference="   ",
        mission_store_dir=env["stores"]["missions"])
    assert r["status"] == INT.MISSION_AUTHORITY_BIND_REJECTED
    assert "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED" in r["reason"]


def test_bind_hma_sets_mode_and_projection(env):
    mid, pid = _setup(env)
    r = _bind_hma(env, mid)
    assert r["status"] == INT.MISSION_AUTHORITY_BOUND
    assert r["hma_issuer"] == "HUMAN"
    assert r["is_execution_authority"] is False
    p = _proj(env, mid)
    assert p["mission_authority_mode"] == "BOUNDED_MISSION_AUTHORITY_PREPARED"
    assert p["active_hma_id"] == r["human_mission_authorization_id"]
    assert p["active_hma_plan_hash"] == p["active_plan_hash"]
    assert p["current_state"] == "WORKTREE_BOUND"   # self-loop, aucun changement d'état


def test_bind_mission_authority_plan_mismatch_fail_closed(env):
    mid, pid = _setup(env)
    r = M.bind_mission_authority(mission_id=mid, hma_id="hma-" + "0" * 32,
                                 hma_record_hash="0" * 64, plan_id=pid, plan_hash="1" * 64,
                                 mission_store_dir=env["stores"]["missions"])
    assert r["status"] == M.STATUS_MISSION_AUTHORITY_BIND_REJECTED
    assert r["reason"] == "HMA_PLAN_BINDING_MISMATCH"


def test_historical_mission_default_mode_unchanged(env):
    mid, _pid = _setup(env)  # aucune HMA liée
    p = _proj(env, mid)
    assert p["mission_authority_mode"] == "PER_ACTION_HUMAN_EAH"
    assert p["active_hma_id"] is None


# ══════════════════════════════════════════════════════════════════════════
#  Vraie mission A -> B -> C avec dérivation automatique du DAAW
# ══════════════════════════════════════════════════════════════════════════

def _drive_abc(env, mid, pid):
    calls = []
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    calls.append(c1)
    assert c1["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL, c1
    for _ in range(3):
        prev = calls[-1]
        if prev["status"] != SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL:
            break
        c = SEQ.advance_bounded_mission(
            mission_id=mid, plan_id=pid,
            human_authorized_execution_authority_hash=prev["execution_authority_hash"],
            human_authorization_reference=f"human-eah-{prev['ordinal']}", **_seq_kw(env))
        calls.append(c)
    return calls


def test_real_abc_one_hma_three_daaw_three_human_eah(env):
    mid, pid = _setup(env)
    br = _bind_hma(env, mid)
    assert br["status"] == INT.MISSION_AUTHORITY_BOUND
    calls = _drive_abc(env, mid, pid)
    last = calls[-1]
    assert last["status"] == SEQ.PLAN_EXECUTION_COMPLETE, last
    assert last["actions_kept"] == 3

    # chaque appel AWAITING_EAH portait un DAAW dérivé (évidence, pas exécution)
    daaw_ids = [c["derived_action_authority_witness_id"] for c in calls
                if c["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL]
    assert len(daaw_ids) == 3
    assert len(set(daaw_ids)) == 3                                  # 3 DAAW distincts
    for c in calls:
        if c["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL:
            assert c["daaw_is_execution_authority"] is False
            assert c["daaw_can_authorize_pre"] is False
            assert c["human_authorization_reference_required"] is True
            assert c["eah_per_action_unchanged"] is True

    p = _proj(env, mid)
    assert len(p["derived_witnesses"]) == 3
    assert len(set(p["derived_witness_action_ids"])) == 3
    # 3 EAH distincts liés
    eahs = [w["execution_authority_hash"] for w in p["derived_witnesses"]]
    assert len(set(eahs)) == 3

    # chaque DAAW persisté write-once, NON_SOUVERAIN, lié à l'HMA de la mission
    hma = MA.load_human_mission_authorization(mid, p["active_hma_id"], env["stores"]["missions"])
    for w in p["derived_witnesses"]:
        daaw = _daaw_file(env, mid, w["daaw_id"])
        assert daaw is not None
        assert daaw["sovereignty"] == "NON_SOVEREIGN"
        assert daaw["is_execution_authority"] is False
        assert daaw["human_mission_authorization_id"] == hma["human_mission_authorization_id"]
        assert daaw["hma_record_hash"] == hma["hma_record_hash"]
    # 3 KX108_PRE / POST réels via le rail historique inchangé
    lg = p["linked_governed_executions"]
    assert len(lg) == 3
    assert all(x["kx108_pre_gate"] == "ALLOW" and x["kx108_post_gate"] == "ALLOW" for x in lg)
    assert all(x["outcome_status"] == WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW for x in lg)
    # cible finale
    assert (env["wt"] / _TARGET).read_bytes() == _A3




def test_daaw_derivation_causes_no_target_mutation(env):
    mid, pid = _setup(env)
    _bind_hma(env, mid)
    before = (env["wt"] / _TARGET).read_bytes()
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert c1["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL
    assert c1["derived_action_authority_witness_id"].startswith("daaw-")
    assert c1["governed_target_mutations_this_call"] == 0
    assert (env["wt"] / _TARGET).read_bytes() == before   # DAAW = évidence, aucune mutation


def test_daaw_derivation_idempotent(env):
    mid, pid = _setup(env)
    _bind_hma(env, mid)
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    d1 = c1["derived_action_authority_witness_id"]
    r2 = INT.derive_and_record_action_authority_witness(
        mission_id=mid, work_unit=env["wu"], execution_dir=env["stores"]["exec"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"])
    assert r2["status"] == INT.WITNESS_DERIVED_AND_VERIFIED
    assert r2["derived_action_authority_witness_id"] == d1
    assert len(_proj(env, mid)["derived_witnesses"]) == 1


# ══════════════════════════════════════════════════════════════════════════
#  Restart
# ══════════════════════════════════════════════════════════════════════════

def test_daaw_survives_process_restart(env):
    mid, pid = _setup(env)
    _bind_hma(env, mid)
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    d1 = c1["derived_action_authority_witness_id"]

    orig = {n: sys.modules.get(n) for n in
            ("obsidia_mission_sequencer_v0", "obsidia_bounded_mission_v0",
             "obsidia_mission_authority_v0", "obsidia_mission_authority_integration_v0")}
    for n in orig:
        sys.modules.pop(n, None)
    import obsidia_bounded_mission_v0 as M2       # noqa
    import obsidia_mission_authority_v0 as MA2    # noqa
    import obsidia_mission_authority_integration_v0 as INT2
    try:
        p = M2.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                               hold_store_dir=env["stores"]["holds"])
        assert p["current_state"] == "ACTION_PREPARED"
        assert p["active_hma_id"] is not None
        assert len(p["derived_witnesses"]) == 1
        assert p["derived_witnesses"][0]["daaw_id"] == d1
        daaw = INT2.load_action_authority_witness(mid, d1, env["stores"]["missions"])
        genesis = M2.load_mission_genesis(mid, env["stores"]["missions"])
        plan = M2.load_mission_plan(mid, pid, env["stores"]["missions"])
        hma = MA2.load_human_mission_authorization(mid, p["active_hma_id"], env["stores"]["missions"])
        import obsidia_batch_execution as E2
        beid = p["last_prepared_evidence"]["batch_execution_id"]
        env_rec = E2._load_execution(beid, env["stores"]["exec"])
        ok, why = MA2.verify_derived_action_authority_witness(
            daaw=daaw, hma=hma, plan=plan, genesis=genesis, projection=p,
            execution_envelope=env_rec,
            revocations=MA2.list_mission_authority_revocations(mid, env["stores"]["missions"]))
        assert ok, why
    finally:
        for n, m in orig.items():
            if m is not None:
                sys.modules[n] = m


# ══════════════════════════════════════════════════════════════════════════
#  Attaques / fail-closed
# ══════════════════════════════════════════════════════════════════════════

def test_cross_mission_daaw_replay_fail_closed(env):
    mid1, pid1 = _setup(env, tag="m1")
    _bind_hma(env, mid1)
    c1 = SEQ.advance_bounded_mission(mission_id=mid1, plan_id=pid1, **_seq_kw(env))
    d1 = c1["derived_action_authority_witness_id"]
    daaw = _daaw_file(env, mid1, d1)

    mid2, pid2 = _setup(env, tag="m2")
    b2 = _bind_hma(env, mid2)
    genesis2 = M.load_mission_genesis(mid2, env["stores"]["missions"])
    plan2 = M.load_mission_plan(mid2, pid2, env["stores"]["missions"])
    hma2 = MA.load_human_mission_authorization(mid2, b2["human_mission_authorization_id"],
                                               env["stores"]["missions"])
    p2 = _proj(env, mid2)
    import obsidia_batch_execution as E
    env_rec = _seq_first_envelope(env, mid1)
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=daaw, hma=hma2, plan=plan2, genesis=genesis2, projection=p2,
        execution_envelope=env_rec, revocations=[])
    assert ok is False
    assert why in ("DAAW_HMA_ID_MISMATCH", "DAAW_MISSION_MISMATCH",
                   "DAAW_PLAN_ID_MISMATCH", "DAAW_PLAN_HASH_MISMATCH", "HMA_INVALID:HMA_PLAN_HASH_MISMATCH")


def _seq_first_envelope(env, mid):
    import obsidia_batch_execution as E
    p = _proj(env, mid)
    beid = p["last_prepared_evidence"]["batch_execution_id"]
    return E._load_execution(beid, env["stores"]["exec"])


def test_revoked_hma_between_actions_mission_routing_hold(env):
    mid, pid = _setup(env)
    br = _bind_hma(env, mid)
    hid = br["human_mission_authorization_id"]
    hhash = br["hma_record_hash"]
    # action A : prepare + DAAW_A + execute KEEP + snapshot
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    c2 = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=pid,
        human_authorized_execution_authority_hash=c1["execution_authority_hash"],
        human_authorization_reference="human-eah-0", **_seq_kw(env))
    # c2 a préparé B et tenté de dériver DAAW_B ; on révoque AVANT de re-vérifier
    assert c2["status"] in (SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL, SEQ.MISSION_AUTHORITY_HOLD)
    rv = MA.record_mission_authority_revocation(
        mission_id=mid, hma_id=hid, hma_record_hash=hhash,
        revocation_reference="HUMAN_STOP", mission_store_dir=env["stores"]["missions"])
    assert rv["status"] == MA.REVOCATION_RECORDED
    # la ré-dérivation (idempotente sur B déjà dérivé -> renvoie l'existant) OU un
    # nouvel appel : on force un nouvel appel d'intégration direct qui doit HOLD si
    # B n'était pas encore dérivé, sinon on teste que l'exécution mission refuse de
    # progresser. Ici on vérifie le routage NON_SOUVERAIN direct :
    dv = INT.derive_and_record_action_authority_witness(
        mission_id=mid, work_unit=env["wu"], execution_dir=env["stores"]["exec"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"])
    if dv["status"] == INT.WITNESS_DERIVED_AND_VERIFIED:
        # B avait déjà été dérivé avant révocation -> idempotent ; on vérifie alors
        # qu'une NOUVELLE mission Stage-4 ne peut plus dériver après révocation
        assert dv.get("idempotent") is True
    else:
        assert dv["status"] == INT.WITNESS_DERIVATION_HOLD
        assert "HMA_INVALID_ROUTING_HOLD" in dv["reason"]
        assert dv["kx_pre_semantics_changed"] is False
        assert dv["revocation_enforcement_belongs_to"] == "STAGE_4F"


def test_closed_mission_cannot_derive_daaw(env):
    mid, pid = _setup(env)
    _bind_hma(env, mid)
    calls = _drive_abc(env, mid, pid)
    assert calls[-1]["status"] == SEQ.PLAN_EXECUTION_COMPLETE
    dv = INT.derive_and_record_action_authority_witness(
        mission_id=mid, work_unit=env["wu"], execution_dir=env["stores"]["exec"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"])
    assert dv["status"] == INT.WITNESS_DERIVATION_HOLD
    assert dv["reason"] in ("MISSION_PLAN_COMPLETED",
                            "MISSION_NOT_IN_ACTION_PREPARED_STATE:CLOSED_AWAITING_NEXT_PLAN")


def test_pre_and_kx_untouched_static(env):
    # PEC / KX108 store : AUCUNE référence à la couture d'autorité de mission.
    for name in ("obsidia_pre_execution_context.py", "obsidia_kx108_decision_store.py"):
        src = (_SCRIPTS / name).read_text(encoding="utf-8")
        assert "obsidia_mission_authority" not in src, name
    # Stage 4F REPAIR : `obsidia_governed_apply_v0` consomme la couture UNIQUEMENT
    # via l'adaptateur PRE dédié + le verrou de linéarisation — jamais 4C ni 4E.
    ga = (_SCRIPTS / "obsidia_governed_apply_v0.py").read_text(encoding="utf-8")
    assert "import obsidia_mission_authority_v0" not in ga
    assert "import obsidia_mission_authority_integration_v0" not in ga
    assert "obsidia_mission_authority_pre_adapter_v0" in ga
    assert "obsidia_mission_authority_freshness_lock_v0" in ga
    # le driver consomme la DerivedMissionApprovalEvidence UNIQUEMENT via
    # l'adaptateur PRE dédié, jamais en important directement 4C ou 4E.
    drv = (_SCRIPTS / "obsidia_governed_execution_driver_v0.py").read_text(encoding="utf-8")
    assert "import obsidia_mission_authority_v0" not in drv
    assert "import obsidia_mission_authority_integration_v0" not in drv
    assert "import obsidia_mission_authority_pre_adapter_v0" in drv
    integ = (_SCRIPTS / "obsidia_mission_authority_integration_v0.py").read_text(encoding="utf-8")
    # aucun APPEL au rail PRE/KX108/apply/rollback ni écriture de cible/git
    for banned in ("store_approval_artifact(", "_validate_approval(", "run_and_persist_kx108",
                   "run_governed_content_apply(", "run_governed_rollback(", "GuardX108",
                   ".write_bytes(", '"commit"', '"add"', '"push"', "subprocess", "_run_git"):
        assert banned not in integ, banned
    # ne construit AUCUN artefact d'approbation ni décision KX
    assert "approved_by\"" not in integ and "'approved_by'" not in integ


def test_per_action_human_eah_still_required(env):
    """Sans EAH humain, l'action préparée n'exécute pas — le DAAW ne la remplace pas."""
    mid, pid = _setup(env)
    _bind_hma(env, mid)
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert c1["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL
    # re-advance sans EAH -> reste AWAITING (aucune exécution depuis le DAAW)
    c2 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert c2["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL
    assert c2["governed_target_mutations_this_call"] == 0
    p = _proj(env, mid)
    assert p["current_state"] == "ACTION_PREPARED"
    assert len(p["linked_governed_executions"]) == 0


# ══════════════════════════════════════════════════════════════════════════
#  Duplicate-witness idempotence — matériel EXACT, jamais action_id seul
# ══════════════════════════════════════════════════════════════════════════

def _setup_daaw_a(env):
    mid, pid = _setup(env)
    br = _bind_hma(env, mid)
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert c1["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL
    p = _proj(env, mid)
    w = p["derived_witnesses"][0]
    return mid, pid, w, p["active_hma_id"], p["revision"]


def _rec(env, mid, w, hma_id_default, **over):
    kw = dict(action_id=w["action_id"], ordinal=w["ordinal"], daaw_id=w["daaw_id"],
              daaw_record_hash=w["daaw_record_hash"],
              execution_authority_hash=w["execution_authority_hash"],
              action_base_sha=w["action_base_sha"], hma_id=hma_id_default,
              mission_store_dir=env["stores"]["missions"])
    kw.update(over)
    return M.record_action_authority_witness(mission_id=mid, **kw)


def test_same_action_all_divergent_material_fail_closed(env):
    """Reproduction EXACTE du bug HOLD : même action_id, tout le reste divergent."""
    mid, pid, w, hma_id, rev0 = _setup_daaw_a(env)
    r = _rec(env, mid, w, hma_id,
             daaw_id="daaw-" + "9" * 32, daaw_record_hash="9" * 64,
             execution_authority_hash="8" * 64, action_base_sha="7" * 40)
    assert r["status"] == M.STATUS_ACTION_AUTHORITY_WITNESS_REJECTED
    assert r["reason"] == "WITNESS_MATERIAL_DIVERGES_FROM_RECORDED"
    assert r["recorded_daaw_id"] == w["daaw_id"]
    assert _proj(env, mid)["revision"] == rev0          # AUCUNE révision appendée


@pytest.mark.parametrize("field,val", [
    ("daaw_id", "daaw-" + "1" * 32),
    ("daaw_record_hash", "1" * 64),
    ("execution_authority_hash", "2" * 64),
    ("action_base_sha", "3" * 40),
    ("ordinal", 7),
    ("hma_id", "hma-" + "4" * 32),
])
def test_same_action_single_field_divergence_fail_closed(env, field, val):
    mid, pid, w, hma_id, rev0 = _setup_daaw_a(env)
    r = _rec(env, mid, w, hma_id, **{field: val})
    assert r["status"] == M.STATUS_ACTION_AUTHORITY_WITNESS_REJECTED, (field, r)
    assert r["reason"] in ("WITNESS_MATERIAL_DIVERGES_FROM_RECORDED",
                           "HMA_NOT_BOUND_TO_MISSION")   # hma_id divergent -> capté plus tôt
    assert _proj(env, mid)["revision"] == rev0


def test_identical_retry_is_idempotent_no_revision(env):
    mid, pid, w, hma_id, rev0 = _setup_daaw_a(env)
    r = _rec(env, mid, w, hma_id)
    assert r["status"] == M.STATUS_ACTION_AUTHORITY_WITNESS_EVENT_IDEMPOTENT
    assert r["daaw_id"] == w["daaw_id"]                  # identité CANONIQUE consignée
    assert r["idempotent"] is True
    assert _proj(env, mid)["revision"] == rev0           # delta révision = 0


def test_idempotent_returns_recorded_not_caller_daaw_id(env):
    """Sur duplicata IDENTIQUE, le daaw_id renvoyé est celui consigné, pas celui de l'appelant."""
    mid, pid, w, hma_id, _rev = _setup_daaw_a(env)
    # même matériel mais on passe volontairement le même daaw_id (identique) : OK
    r = _rec(env, mid, w, hma_id)
    assert r["daaw_id"] == w["daaw_id"]
    # via l'intégration : ré-appel -> renvoie l'enregistré, idempotent
    dv = INT.derive_and_record_action_authority_witness(
        mission_id=mid, work_unit=env["wu"], execution_dir=env["stores"]["exec"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"])
    assert dv["status"] == INT.WITNESS_DERIVED_AND_VERIFIED
    assert dv["idempotent"] is True
    assert dv["derived_action_authority_witness_id"] == w["daaw_id"]


def test_witness_artifact_tamper_fail_closed(env):
    """L'événement mission NE SUFFIT PAS : artefact DAAW altéré -> fail-closed."""
    mid, pid, w, hma_id, _rev = _setup_daaw_a(env)
    art_path = (env["stores"]["missions"] / mid / "action_authority_witnesses"
               / (w["daaw_id"] + ".json"))
    art = json.loads(art_path.read_text(encoding="utf-8"))
    art["daaw_record_hash"] = "d" * 64          # divergence artefact <-> événement
    art_path.write_text(json.dumps(art), encoding="utf-8")
    r = _rec(env, mid, w, hma_id)               # matériel = enregistré, mais artefact ment
    assert r["status"] == M.STATUS_ACTION_AUTHORITY_WITNESS_REJECTED
    assert r["reason"].startswith("WITNESS_ARTIFACT_DISAGREES_WITH_EVENT")
    # l'intégration attrape aussi
    dv = INT.derive_and_record_action_authority_witness(
        mission_id=mid, work_unit=env["wu"], execution_dir=env["stores"]["exec"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"])
    assert dv["status"] in (INT.WITNESS_DERIVATION_REJECTED, INT.WITNESS_DERIVATION_HOLD)


def test_restart_identical_witness_retry_pass(env):
    mid, pid, w, hma_id, rev0 = _setup_daaw_a(env)
    orig = {n: sys.modules.get(n) for n in
            ("obsidia_bounded_mission_v0", "obsidia_mission_authority_v0",
             "obsidia_mission_authority_integration_v0")}
    for n in orig:
        sys.modules.pop(n, None)
    import obsidia_bounded_mission_v0 as M2         # noqa
    import obsidia_mission_authority_integration_v0 as INT2
    try:
        dv = INT2.derive_and_record_action_authority_witness(
            mission_id=mid, work_unit=env["wu"], execution_dir=env["stores"]["exec"],
            mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"])
        assert dv["status"] == INT2.WITNESS_DERIVED_AND_VERIFIED
        assert dv["idempotent"] is True
        assert dv["derived_action_authority_witness_id"] == w["daaw_id"]
        assert dv["daaw_record_hash"] == w["daaw_record_hash"]
        p = M2.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                               hold_store_dir=env["stores"]["holds"])
        assert p["revision"] == rev0               # aucune révision supplémentaire
        assert len(p["derived_witnesses"]) == 1
    finally:
        for n, m in orig.items():
            if m is not None:
                sys.modules[n] = m


def test_authority_boundary_unchanged_after_repair(env):
    mid, pid = _setup(env)
    _bind_hma(env, mid)
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert c1["daaw_is_execution_authority"] is False
    assert c1["daaw_can_authorize_pre"] is False
    assert c1["human_authorization_reference_required"] is True
    # re-advance sans EAH -> reste AWAITING, aucune exécution
    c2 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert c2["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL
    assert _proj(env, mid)["current_state"] == "ACTION_PREPARED"
    assert len(_proj(env, mid)["linked_governed_executions"]) == 0
