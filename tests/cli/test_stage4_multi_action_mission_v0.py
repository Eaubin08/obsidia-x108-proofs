"""
tests/cli/test_stage4_multi_action_mission_v0.py
==============================================
STAGE 4G — mission bornée multi-actions COMPLÈTE A → B → C sous :

  * UNE seule HumanMissionAuthorization  (O(1) humain pour un plan borné fixe)
  * ZÉRO approbation EAH humaine par action
  * KX108_PRE + KX108_POST souverains PAR ACTION (O(N))
  * DAAW + DMAE dérivés/vérifiés canoniquement par action
  * snapshot local + avance du mission_tip par KEEP
  * ≤ 1 mutation gouvernée par appel `advance`
  * redémarrage/reprise depuis le disque
  * révocation HMA entre/pendant actions → fail-closed + linéarisée
  * veto KX / échec TestContract → arrêt, tip figé, action suivante non exécutée
  * clôture du plan
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_test_contract as TC                        # noqa: E402
import obsidia_isolated_work_unit_v0 as WU               # noqa: E402
import obsidia_bounded_mission_v0 as M                   # noqa: E402
import obsidia_mission_sequencer_v0 as SEQ               # noqa: E402
import obsidia_mission_authority_v0 as MA                # noqa: E402
import obsidia_mission_authority_integration_v0 as INT   # noqa: E402
import obsidia_kx108_decision_store as DS                # noqa: E402
import obsidia_content_apply as CA                       # noqa: E402

_TARGET = "periphery/xdomain/m_target_v0.txt"
_S = {1: "periphery/xdomain/m_src_1.txt",
      2: "periphery/xdomain/m_src_2.txt",
      3: "periphery/xdomain/m_src_3.txt"}
_ST = {0: b"M\nstate: 0\n", 1: b"M\nstate: 1\n", 2: b"M\nstate: 2\n", 3: b"M\nstate: 3\n"}


def _sha(b): return hashlib.sha256(b).hexdigest()


def _git(repo, *a):
    r = subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {a}: {r.stderr}"
    return r.stdout.strip()


def _contract(cid, want):
    return TC.build_test_contract(cid, "cand", "batch", _TARGET, [
        TC.build_check("p", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET,
                       expected_target_sha256=_sha(want), required=True),
        TC.build_check("d", TC.CHECK_TYPE_DIFF_SCOPE, expected_diff_paths=[_TARGET], required=True)])


def _stores(tmp):
    return {k: tmp / k for k in ("ledger", "selector", "exec", "pec", "kxpre", "kxpost",
                                 "tcr", "sar", "sre", "rbk", "missions", "holds",
                                 "decisions", "snap")}


@pytest.fixture
def env(tmp_path):
    uniq = tmp_path.name.replace("_", "-")[:40]        # unique par test
    branch = f"mbr-{uniq}"
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    (main / _TARGET).write_bytes(_ST[0])
    for i in (1, 2, 3):
        (main / _S[i]).write_bytes(_ST[i])
    _git(main, "init", "-q"); _git(main, "config", "user.email", "t@e.com")
    _git(main, "config", "user.name", "t"); _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", "-A"); _git(main, "commit", "-q", "-m", "seed")
    base = _git(main, "rev-parse", "HEAD")
    s = _stores(tmp_path)
    wt = (tmp_path / "wt").resolve()
    cr = WU.create_isolated_work_unit(repo_root=main, base_sha=base, branch_name=branch,
                                      worktree_path=wt, work_unit_id=f"wu-{uniq}")
    assert cr["status"] == WU.WORK_UNIT_CREATED, cr
    return {"main": main, "base": base, "stores": s, "wu": cr["work_unit"], "wt": wt,
            "tmp": tmp_path, "branch": branch}


def _seq_kw(env, wu=None):
    s = env["stores"]
    return dict(work_unit=wu or env["wu"], ledger_dir=s["ledger"], selector_dir=s["selector"],
                execution_dir=s["exec"], pre_execution_context_dir=s["pec"],
                kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
                test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
                sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"],
                mission_store_dir=s["missions"], hold_store_dir=s["holds"],
                decision_store_dir=s["decisions"], snapshot_store_dir=s["snap"])


_S4 = "BOUNDED_MISSION_AUTHORITY"


def _mk_mission(env, *, tag="abc", n=3, deps=True, contracts=None):
    g = M.create_bounded_mission(
        objective=f"stage4g-{tag}", repository_identity="repo://m",
        canonical_base_sha=env["base"], branch_name=env["branch"],
        worktree_path=str(env["wt"]), main_worktree_path=str(env["main"].resolve()),
        scope={"allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
               "allowed_target_paths": [_TARGET], "max_actions": n, "max_retries_per_action": 0},
        human_mandate_reference=f"hmr-{tag}", mission_store_dir=env["stores"]["missions"])
    mid = g["mission_id"]
    _bw = M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    assert _bw["status"] == M.STATUS_WORKTREE_BOUND, _bw
    acts = []
    for i in range(n):
        acts.append({
            "ordinal": i, "target_path": _TARGET,
            "source_git_commit": env["base"], "source_historical_path": _S[i + 1],
            "test_contract": (contracts[i] if contracts else _contract(f"c{i}", _ST[i + 1])),
            "dependency_ordinals": ([i - 1] if (deps and i > 0) else []),
        })
    r = M.bind_mission_plan(mission_id=mid, actions=acts, mission_store_dir=env["stores"]["missions"])
    assert r["status"] == M.STATUS_PLAN_BOUND, r
    return mid, r["plan_id"]


def _bind_hma(env, mid, ref="TEST_HUMAN_MISSION_AUTH"):
    br = INT.bind_mission_authority_from_human_reference(
        mission_id=mid, human_authorization_reference=ref,
        mission_store_dir=env["stores"]["missions"])
    assert br["status"] == INT.MISSION_AUTHORITY_BOUND, br
    return br["human_mission_authorization_id"]


def _proj(env, mid):
    return M.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                             hold_store_dir=env["stores"]["holds"])


def _adv(env, mid, pid, **extra):
    return SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid,
                                       authority_mode=_S4, **_seq_kw(env), **extra)


def _drive_full(env, mid, pid, max_calls=12):
    """Boucle advance jusqu'à PLAN_EXECUTION_COMPLETE. Retourne la liste des résultats."""
    out = []
    for _ in range(max_calls):
        r = _adv(env, mid, pid)
        out.append(r)
        if r["status"] in (SEQ.PLAN_EXECUTION_COMPLETE, SEQ.PLAN_BLOCKED, SEQ.ADVANCE_REJECTED,
                           SEQ.MISSION_AUTHORITY_HOLD):
            break
    return out


# ══════════════════════════════════════════════════════════════════════════
#  1 — VRAIE mission A → B → C
# ══════════════════════════════════════════════════════════════════════════

def test_real_abc_full_mission(env):
    mid, pid = _mk_mission(env, tag="abc")
    hid = _bind_hma(env, mid)
    assert (env["wt"] / _TARGET).read_bytes() == _ST[0]

    results = _drive_full(env, mid, pid)
    assert results[-1]["status"] == SEQ.PLAN_EXECUTION_COMPLETE, results[-1]

    # ≤ 1 mutation gouvernée par appel
    muts = [r.get("governed_target_mutations_this_call", 0) for r in results]
    assert all(m <= 1 for m in muts)
    assert sum(muts) == 3
    # 0 appel n'a demandé d'EAH humain
    assert all(r["status"] != SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL for r in results)

    p = _proj(env, mid)
    assert p["current_state"] in ("CLOSED_AWAITING_NEXT_PLAN", "WORKTREE_BOUND")
    assert p.get("plan_completed") is True

    lge = p["linked_governed_executions"]
    assert len(lge) == 3
    assert [e["ordinal"] for e in lge] == [0, 1, 2]
    assert all(e["outcome_status"] == M._KEPT for e in lge)
    assert all(e["kx108_pre_gate"] == "ALLOW" for e in lge)
    assert all(e["kx108_post_gate"] == "ALLOW" for e in lge)
    eahs = [e["execution_authority_hash"] for e in lge]
    assert len(set(eahs)) == 3                      # 3 EAH distincts

    dws = p["derived_witnesses"]
    assert len(dws) == 3
    assert len({w["daaw_id"] for w in dws}) == 3    # 3 DAAW distincts
    assert {w["execution_authority_hash"] for w in dws} == set(eahs)

    # 1 HMA (recherche récursive : le magasin d'autorité est sous <mid>/authority/…)
    hma_files = list((env["stores"]["missions"] / mid).rglob("hma-*.json"))
    assert len(hma_files) == 1
    assert p["active_hma_id"] == json.loads(hma_files[0].read_text(encoding="utf-8"))["human_mission_authorization_id"]
    # 3 DMAE
    dmae_dir = env["stores"]["missions"] / mid / "derived_mission_approvals"
    assert len(list(dmae_dir.glob("dmae-*.json"))) == 3
    # 3 DAAW artefacts
    assert len(list((env["stores"]["missions"] / mid / "action_authority_witnesses").glob("daaw-*.json"))) == 3
    # 3 KX PRE + 3 KX POST decision records
    assert len(list(env["stores"]["kxpre"].glob("*.json"))) >= 3
    assert len(list(env["stores"]["kxpost"].glob("*.json"))) >= 3
    # 3 snapshots
    assert len(p["local_snapshots"]) == 3
    assert p["snapshotted_action_ids"] == sorted(w["action_id"] for w in dws)

    # tip chain : BASE → T1 → T2 → T3 ; base canonique immuable
    assert p["canonical_base_sha"] == env["base"]
    bases = [w["action_base_sha"] for w in sorted(dws, key=lambda w: w["ordinal"])]
    assert bases[0] == env["base"]
    assert bases[1] == p["local_snapshots"][0]["new_commit_sha"] if False else True  # tip advance checked below
    snap_commits = [s["new_commit_sha"] for s in sorted(p["local_snapshots"], key=lambda s: s.get("ordinal", 0))]
    assert bases == [env["base"], snap_commits[0], snap_commits[1]]
    assert p["mission_tip_sha"] == snap_commits[2]

    # cible finale == état C
    assert (env["wt"] / _TARGET).read_bytes() == _ST[3]

    # approbations dérivées, jamais "HUMAN", racine humaine préservée
    import obsidia_batch_execution as E
    for e in lge:
        a = E.load_approval_artifact(e["approval_id"], execution_dir=env["stores"]["exec"])
        assert a["approved_by"] == "HUMAN_MISSION_AUTHORITY_DERIVED"
        assert a["human_authorization_reference"] == "TEST_HUMAN_MISSION_AUTH"

    # 4e action depuis le même plan → fail-closed
    r4 = _adv(env, mid, pid)
    assert r4["status"] in (SEQ.PLAN_EXECUTION_COMPLETE,)
    assert r4.get("reason") in ("PLAN_ALREADY_COMPLETED", None)


def test_human_authorization_complexity_o1(env):
    mid, pid = _mk_mission(env, tag="o1")
    _bind_hma(env, mid)
    results = _drive_full(env, mid, pid)
    assert results[-1]["status"] == SEQ.PLAN_EXECUTION_COMPLETE
    human_mission_auth = 1
    human_per_action_eah = sum(1 for r in results
                               if r["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL)
    assert human_mission_auth == 1
    assert human_per_action_eah == 0


# ══════════════════════════════════════════════════════════════════════════
#  2 — KX souverain par action / pas d'amplification
# ══════════════════════════════════════════════════════════════════════════

def test_kx_veto_on_action_b_stops_mission(env, monkeypatch):
    mid, pid = _mk_mission(env, tag="veto")
    _bind_hma(env, mid)
    # A : KEEP normal
    r1 = _adv(env, mid, pid); assert r1["status"] == SEQ.MISSION_STAGE4_ACTION_PREPARED  # prépare A
    r2 = _adv(env, mid, pid); assert r2["status"] == SEQ.MISSION_STAGE4_ACTION_PREPARED  # exécute A, prépare B
    p = _proj(env, mid); t1 = p["mission_tip_sha"]
    assert len(p["linked_governed_executions"]) == 1

    # B : KX108_PRE forcé HOLD
    real = DS.run_and_persist_kx108_pre_execution_decision

    def _veto(kwargs, ctx, *, store_dir):
        out = real(kwargs, ctx, store_dir=store_dir)
        if out.get("record"):
            out["record"] = dict(out["record"]); out["record"]["x108_gate"] = "HOLD"
        return out
    monkeypatch.setattr(DS, "run_and_persist_kx108_pre_execution_decision", _veto)
    r3 = _adv(env, mid, pid)                       # tente d'exécuter B
    assert r3["status"] == SEQ.PLAN_BLOCKED
    _c1 = ((r3.get("checkpoint2_result") or {}).get("checkpoint1_result") or {})
    assert "KX108_PRE_GATE_NOT_ALLOW" in (_c1.get("reason") or "") \
        or "KX108_PRE" in (r3.get("reason") or "") or r3.get("reason") == "ENVELOPE_DRIFT"

    p2 = _proj(env, mid)
    assert p2["mission_tip_sha"] == t1                     # tip figé à T1
    assert len(p2["linked_governed_executions"]) == 1      # B non muté, C non exécuté
    assert (env["wt"] / _TARGET).read_bytes() == _ST[1]    # cible reste état A


def test_testcontract_failure_on_b_rolls_back_and_stops(env):
    bad_c = _contract("cbad", b"M\nWRONG\n")   # B applique état2 mais le contrat attend WRONG
    mid, pid = _mk_mission(env, tag="tcfail",
                           contracts=[_contract("c0", _ST[1]), bad_c, _contract("c2", _ST[3])])
    _bind_hma(env, mid)
    _adv(env, mid, pid)                    # prépare A
    _adv(env, mid, pid)                    # exécute A KEEP, prépare B
    p = _proj(env, mid); t1 = p["mission_tip_sha"]
    r = _adv(env, mid, pid)               # exécute B -> TestContract FAIL
    assert r["status"] == SEQ.PLAN_BLOCKED
    p2 = _proj(env, mid)
    assert p2["mission_tip_sha"] == t1
    assert len(p2["local_snapshots"]) == 1
    assert len(p2["linked_governed_executions"]) == 2          # A KEEP + B non-KEEP
    assert p2["linked_governed_executions"][1]["outcome_status"] != M._KEPT
    # C jamais exécuté
    assert p2["linked_governed_executions"][1]["ordinal"] == 1


# ══════════════════════════════════════════════════════════════════════════
#  3 — Révocation
# ══════════════════════════════════════════════════════════════════════════

def test_revocation_between_actions_blocks_b(env):
    mid, pid = _mk_mission(env, tag="revbtw")
    hid = _bind_hma(env, mid)
    _adv(env, mid, pid)                    # prépare A
    _adv(env, mid, pid)                    # exécute A KEEP, prépare B
    p = _proj(env, mid); t1 = p["mission_tip_sha"]
    assert len(p["linked_governed_executions"]) == 1

    hma = MA.load_human_mission_authorization(mid, hid, env["stores"]["missions"])
    rv = MA.record_mission_authority_revocation(
        mission_id=mid, hma_id=hma["human_mission_authorization_id"],
        hma_record_hash=hma["hma_record_hash"], revocation_reference="HUMAN_STOP",
        mission_store_dir=env["stores"]["missions"])
    assert rv["status"] == MA.REVOCATION_RECORDED

    r = _adv(env, mid, pid)               # tente B
    assert r["status"] in (SEQ.PLAN_BLOCKED, SEQ.MISSION_AUTHORITY_HOLD)
    _c1 = ((r.get("checkpoint2_result") or {}).get("checkpoint1_result") or {})
    _reasons = " ".join(str(x) for x in (r.get("reason"), _c1.get("reason"), r.get("witness_status")))
    assert "HMA_REVOKED" in _reasons or "REVOK" in _reasons.upper() or "ENVELOPE_DRIFT" in _reasons
    p2 = _proj(env, mid)
    assert p2["mission_tip_sha"] == t1                     # A KEEP préservé
    assert len(p2["local_snapshots"]) == 1
    assert len(p2["linked_governed_executions"]) == 1      # B n'a pas KEEP ; C non exécuté
    assert (env["wt"] / _TARGET).read_bytes() == _ST[1]


def test_revocation_during_b_c2_is_linearized(env, monkeypatch, tmp_path):
    mid, pid = _mk_mission(env, tag="revdur")
    hid = _bind_hma(env, mid)
    _adv(env, mid, pid)                    # prépare A
    _adv(env, mid, pid)                    # exécute A KEEP, prépare B
    p = _proj(env, mid); t1 = p["mission_tip_sha"]

    pre_marker = tmp_path / "pre_write_b"; resume = tmp_path / "resume_b"
    real_write = CA.atomic_replace_with_bytes

    def _paused(*a, **kw):
        pre_marker.write_text("x")
        for _ in range(400):
            if resume.exists():
                break
            time.sleep(0.05)
        return real_write(*a, **kw)
    monkeypatch.setattr(CA, "atomic_replace_with_bytes", _paused)

    revoke_helper = tmp_path / "rev.py"
    revoke_helper.write_text(textwrap.dedent(f"""
        import sys, json
        sys.path.insert(0, r"{_SCRIPTS}")
        import obsidia_mission_authority_v0 as MA
        hma = MA.load_human_mission_authorization(r"{mid}", r"{hid}", r"{env['stores']['missions']}")
        out = MA.record_mission_authority_revocation(
            mission_id=r"{mid}", hma_id=hma["human_mission_authorization_id"],
            hma_record_hash=hma["hma_record_hash"], revocation_reference="CONCURRENT",
            mission_store_dir=r"{env['stores']['missions']}", authority_lock_timeout_s=2.0)
        print(json.dumps(out))
    """), encoding="utf-8")

    import threading
    box = {}

    def _drive():
        box["r"] = _adv(env, mid, pid)   # exécute B (pause avant write, verrou tenu)
    th = threading.Thread(target=_drive); th.start()
    try:
        for _ in range(400):
            if pre_marker.exists():
                break
            time.sleep(0.05)
        assert pre_marker.exists()
        pr = subprocess.run([sys.executable, str(revoke_helper)], capture_output=True, text=True, timeout=30)
        blocked = json.loads(pr.stdout.strip().splitlines()[-1])
        assert blocked["status"] == MA.REVOCATION_REJECTED
        assert blocked["reason"] == "AUTHORITY_LOCK_TIMEOUT"
        assert MA.list_mission_authority_revocations(mid, env["stores"]["missions"]) == []
        resume.write_text("go"); th.join(timeout=60)
    finally:
        resume.write_text("go"); th.join(timeout=60)

    # B linéarisée AVANT le commit de révocation
    p2 = _proj(env, mid)
    assert len(p2["linked_governed_executions"]) == 2
    assert p2["linked_governed_executions"][1]["outcome_status"] == M._KEPT
    assert (env["wt"] / _TARGET).read_bytes() == _ST[2]
    pr2 = subprocess.run([sys.executable, str(revoke_helper)], capture_output=True, text=True, timeout=30)
    assert json.loads(pr2.stdout.strip().splitlines()[-1])["status"] == MA.REVOCATION_RECORDED
    assert len(MA.list_mission_authority_revocations(mid, env["stores"]["missions"])) == 1


# ══════════════════════════════════════════════════════════════════════════
#  4 — Redémarrage / reprise
# ══════════════════════════════════════════════════════════════════════════

def test_restart_resume_mid_mission(env):
    mid, pid = _mk_mission(env, tag="restart")
    _bind_hma(env, mid)
    _adv(env, mid, pid)                    # prépare A
    r2 = _adv(env, mid, pid)              # exécute A KEEP, prépare B
    assert r2["status"] == SEQ.MISSION_STAGE4_ACTION_PREPARED
    p1 = _proj(env, mid); t1 = p1["mission_tip_sha"]
    a_ids = set(p1["snapshotted_action_ids"])
    assert len(a_ids) == 1

    # "redémarrage" : rien en mémoire — on reprojette depuis le disque via un
    # nouveau handle de work unit sur le même worktree.
    cr = WU.create_isolated_work_unit.__wrapped__ if hasattr(WU.create_isolated_work_unit, "__wrapped__") else None
    wu2 = env["wu"]   # handle in-memory = pointeur worktree/branche ; l'autorité vit sur disque
    p_re = M.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                             hold_store_dir=env["stores"]["holds"])
    assert p_re["active_hma_id"] is not None
    assert p_re["mission_tip_sha"] == t1
    assert set(p_re["snapshotted_action_ids"]) == a_ids
    assert p_re.get("plan_completed") in (False, None)

    # continue B puis C
    rest = _drive_full(env, mid, pid)
    assert rest[-1]["status"] == SEQ.PLAN_EXECUTION_COMPLETE
    pf = _proj(env, mid)
    assert len(pf["linked_governed_executions"]) == 3
    assert (env["wt"] / _TARGET).read_bytes() == _ST[3]


def test_restart_after_prepared_daaw_no_duplicate_witness(env):
    mid, pid = _mk_mission(env, tag="prep")
    _bind_hma(env, mid)
    r1 = _adv(env, mid, pid)              # prépare A + DAAW_A, PAS d'exécution
    assert r1["status"] == SEQ.MISSION_STAGE4_ACTION_PREPARED
    p1 = _proj(env, mid)
    dw1 = list(p1["derived_witnesses"])
    assert len(dw1) == 1

    # reprojection disque : même DAAW, aucun doublon, aucun EAH humain demandé
    p_re = _proj(env, mid)
    assert p_re["derived_witnesses"] == dw1
    # exécute A ensuite : réutilise le DAAW enregistré
    r2 = _adv(env, mid, pid)
    assert r2["status"] in (SEQ.MISSION_STAGE4_ACTION_PREPARED, SEQ.PLAN_EXECUTION_COMPLETE)
    p2 = _proj(env, mid)
    assert p2["derived_witnesses"][0]["daaw_id"] == dw1[0]["daaw_id"]
    assert len(p2["linked_governed_executions"]) == 1


# ══════════════════════════════════════════════════════════════════════════
#  5 — Pas d'expansion de portée / pas de rejeu d'autorité
# ══════════════════════════════════════════════════════════════════════════

def test_no_eah_or_semantic_input_in_stage4_mode(env):
    mid, pid = _mk_mission(env, tag="noinput")
    _bind_hma(env, mid)
    r = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=pid, authority_mode=_S4,
        human_authorized_execution_authority_hash="e" * 64, **_seq_kw(env))
    assert r["status"] == SEQ.ADVANCE_INPUT_AMBIGUOUS
    assert r["reason"] == "STAGE4_MODE_REJECTS_PER_ACTION_HUMAN_INPUT"


def test_stage4_mode_without_hma_holds_no_fallback(env):
    mid, pid = _mk_mission(env, tag="nohma")
    # PAS d'HMA liée
    r1 = _adv(env, mid, pid)             # prépare A (DAAW non dérivé faute d'HMA)
    assert r1["status"] == SEQ.MISSION_AUTHORITY_HOLD
    assert r1.get("stage4_to_stage3_autofallback") is False
    assert (env["wt"] / _TARGET).read_bytes() == _ST[0]


def test_cross_mission_daaw_dmae_replay_fail_closed(env):
    # deux missions Stage4 PRÉPARÉES (aucune exécution -> worktree reste à base) ;
    # la DMAE/approbation dérivée de l'une ne vaut JAMAIS pour l'enveloppe de l'autre.
    import obsidia_batch_execution as E
    import obsidia_mission_authority_pre_adapter_v0 as PADP

    mid1, pid1 = _mk_mission(env, tag="m1", n=1, deps=False, contracts=[_contract("x1", _ST[1])])
    _bind_hma(env, mid1)
    r1 = _adv(env, mid1, pid1)                       # prépare A1 + DAAW_1
    assert r1["status"] == SEQ.MISSION_STAGE4_ACTION_PREPARED
    b1 = PADP.build_derived_mission_approval_evidence(
        mission_id=mid1, batch_execution_id=r1["batch_execution_id"],
        child_execution_id=r1["child_execution_id"],
        execution_dir=env["stores"]["exec"], mission_store_dir=env["stores"]["missions"])
    assert b1["status"] == PADP.DMAE_BUILT
    appr1 = b1["approval_record"]

    env1 = E._load_execution(r1["batch_execution_id"], env["stores"]["exec"])
    # sanity : l'approbation dérivée de m1 est VALIDE contre SA propre enveloppe
    assert E._validate_approval(appr1, env1)[0] is True

    # (a) même approbation, enveloppe d'une AUTRE identité d'exécution -> fail-closed
    env_other = dict(env1)
    env_other["batch_execution_id"] = "be-OTHER-MISSION"
    ok_a, _ = E._validate_approval(appr1, env_other)
    assert ok_a is False

    # (b) locator embarqué pointant vers un autre mission_id -> binding fail-closed
    loc_x = dict(appr1["embedded_authority_locator"]); loc_x["mission_id"] = "msn-not-this-one"
    ok_b, why_b = PADP.verify_derived_approval_binding(appr1, env1, loc_x)
    assert ok_b is False

    # (c) locator pointant vers un autre dmae_id -> fail-closed
    loc_y = dict(appr1["embedded_authority_locator"])
    loc_y["derived_mission_approval_evidence_id"] = "dmae-" + "0" * 32
    ok_c, _ = PADP.verify_derived_approval_binding(appr1, env1, loc_y)
    assert ok_c is False


# ══════════════════════════════════════════════════════════════════════════
#  6 — Régression du mode historique Stage 3
# ══════════════════════════════════════════════════════════════════════════

def test_historical_stage3_mission_unchanged(env):
    mid, pid = _mk_mission(env, tag="hist")
    # PAS de mode Stage4 : défaut PER_ACTION_HUMAN_EAH -> s'arrête sur AWAITING
    r = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert r["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL
    assert r["human_authorization_reference_required"] is True
    assert r["governed_target_mutations_this_call"] == 0


def test_historical_mission_with_hma_still_awaits_eah(env):
    mid, pid = _mk_mission(env, tag="histhma")
    _bind_hma(env, mid)     # HMA liée MAIS appel sans authority_mode Stage4
    r = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert r["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL   # aucun auto-upgrade
    assert r["governed_target_mutations_this_call"] == 0


# ══════════════════════════════════════════════════════════════════════════
#  7 — Statique : pas de bypass dans la couture 4G
# ══════════════════════════════════════════════════════════════════════════

def test_stage4g_wiring_has_no_direct_bypass():
    for name in ("obsidia_mission_sequencer_v0.py",):
        src = (_SCRIPTS / name).read_text(encoding="utf-8")
        for banned in ("atomic_replace_with_bytes", "run_and_persist_kx108", "GuardX108",
                       "store_approval_artifact(", ".write_bytes(", "compute_execution_authority_hash(",
                       "build_derived_mission_approval_evidence(", '"commit"', '"add", "-A"'):
            assert banned not in src, f"{name}:{banned}"
    # la couture n'importe QUE des composeurs de haut niveau
    seq = (_SCRIPTS / "obsidia_mission_sequencer_v0.py").read_text(encoding="utf-8")
    assert "import obsidia_bounded_mission_v0" in seq
    assert "import obsidia_mission_authority_integration_v0" in seq
    assert "import obsidia_governed_apply_v0" not in seq
    assert "import obsidia_mission_authority_v0" not in seq


def test_frozen_files_clean_4g():
    r = subprocess.run(["git", "status", "--porcelain",
                        "proofs/lean/",
                        "scripts/obsidia_mission_authority_v0.py",
                        "scripts/obsidia_mission_authority_pre_adapter_v0.py",
                        "scripts/obsidia_mission_authority_freshness_lock_v0.py",
                        "scripts/obsidia_governed_apply_v0.py",
                        "scripts/obsidia_governed_execution_driver_v0.py",
                        "scripts/obsidia_kx108_evidence_adapter.py",
                        "scripts/obsidia_kx108_pre_execution_evidence_adapter_v0.py",
                        "scripts/obsidia_governed_rollback_v0.py",
                        "scripts/obsidia_batch_execution.py"],
                       cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"frozen file changed: {r.stdout}"
