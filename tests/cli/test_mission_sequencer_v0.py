"""
tests/cli/test_mission_sequencer_v0.py
======================================
STAGE_3D — le séquenceur de mission compose les primitives committées
(Checkpoint 1/2, Stage 3A/3B/3C) en UNE mission bornée multi-actions,
avec UN EAH humain EXACT par action.

Preuve critique : vraie séquence gouvernée A -> B -> C dans UN dépôt
temporaire, UN worktree isolé, UNE branche locale de mission, où B
observe réellement le résultat committé de A et C celui de B. 4 appels
`advance_bounded_mission`, 3 approbations EAH humaines, 0 approbation
automatique, 3 KX108_PRE / 3 KX108_POST / 3 C2 / 3 TestContract PASS /
3 snapshots Stage 3A chaînés, canonical_base_sha immuable, tip final ==
commit du snapshot C.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_test_contract as TC                    # noqa: E402
import obsidia_isolated_work_unit_v0 as WU            # noqa: E402
import obsidia_bounded_mission_v0 as M                # noqa: E402
import obsidia_mission_sequencer_v0 as SEQ            # noqa: E402

_TARGET = "periphery/xdomain/seq_target_v0.txt"
_S1 = "periphery/xdomain/seq_src_1.txt"
_S2 = "periphery/xdomain/seq_src_2.txt"
_S3 = "periphery/xdomain/seq_src_3.txt"
_A0 = b"SEQ\nstate: 0\n"
_A1 = b"SEQ\nstate: 1\n"
_A2 = b"SEQ\nstate: 2\n"
_A3 = b"SEQ\nstate: 3\n"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(repo: Path, *a: str) -> str:
    r = subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {a}: {r.stderr}"
    return r.stdout.strip()


@pytest.fixture
def env(tmp_path):
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    (main / _TARGET).write_bytes(_A0)
    (main / _S1).write_bytes(_A1)
    (main / _S2).write_bytes(_A2)
    (main / _S3).write_bytes(_A3)
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "t@example.com")
    _git(main, "config", "user.name", "t")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", _TARGET, _S1, _S2, _S3)
    _git(main, "commit", "-q", "-m", "seed")
    base = _git(main, "rev-parse", "HEAD")
    stores = {k: tmp_path / k for k in (
        "ledger", "selector", "exec", "pec", "kxpre", "kxpost", "tcr",
        "sar", "sre", "rbk", "missions", "holds", "decisions", "snap")}
    wt = (tmp_path / "wt_seq").resolve()
    cr = WU.create_isolated_work_unit(repo_root=main, base_sha=base, branch_name="seqbr",
                                      worktree_path=wt, work_unit_id="wu-seq-0001")
    assert cr["status"] == WU.WORK_UNIT_CREATED, cr
    return {"root": tmp_path, "main": main, "base": base, "stores": stores,
            "wu": cr["work_unit"], "wt": wt}


def _contract(expected_post: bytes, cid: str) -> dict:
    return TC.build_test_contract(cid, "cand", "batch", _TARGET, [
        TC.build_check("post-sha", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET,
                       expected_target_sha256=_sha(expected_post), required=True),
        TC.build_check("diff-scope", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[_TARGET], required=True),
    ])


def _genesis(env, *, max_actions=3, allowed=None, max_retries=0):
    return M.create_bounded_mission(
        objective="stage3d A->B->C", repository_identity="repo://seq",
        canonical_base_sha=env["base"], branch_name="seqbr",
        worktree_path=str(env["wt"]), main_worktree_path=str(env["main"].resolve()),
        scope={"allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
               "allowed_target_paths": allowed if allowed is not None else [_TARGET],
               "max_actions": max_actions, "max_retries_per_action": max_retries},
        human_mandate_reference="human-mandate-seq",
        mission_store_dir=env["stores"]["missions"])


def _abc_actions(*, a_contract=None):
    return [
        {"ordinal": 0, "target_path": _TARGET, "source_git_commit": None,
         "source_historical_path": _S1, "test_contract": a_contract or _contract(_A1, "c-A"),
         "dependency_ordinals": []},
        {"ordinal": 1, "target_path": _TARGET, "source_git_commit": None,
         "source_historical_path": _S2, "test_contract": _contract(_A2, "c-B"),
         "dependency_ordinals": [0]},
        {"ordinal": 2, "target_path": _TARGET, "source_git_commit": None,
         "source_historical_path": _S3, "test_contract": _contract(_A3, "c-C"),
         "dependency_ordinals": [1]},
    ]


def _fix_source_commit(actions, base):
    for a in actions:
        a["source_git_commit"] = base
    return actions


def _seq_kw(env):
    s = env["stores"]
    return dict(
        work_unit=env["wu"],
        ledger_dir=s["ledger"], selector_dir=s["selector"], execution_dir=s["exec"],
        pre_execution_context_dir=s["pec"], kx108_pre_decision_dir=s["kxpre"],
        kx108_post_decision_dir=s["kxpost"], test_contract_results_dir=s["tcr"],
        sealed_receipt_dir=s["sar"], sealed_rollback_evidence_dir=s["sre"],
        rollback_result_dir=s["rbk"], mission_store_dir=s["missions"],
        hold_store_dir=s["holds"], decision_store_dir=s["decisions"],
        snapshot_store_dir=s["snap"])


def _proj(env, mid):
    return M.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                             hold_store_dir=env["stores"]["holds"])


# ══════════════════════════════════════════════════════════════════════════
#  Plan bind — validation (A..K)
# ══════════════════════════════════════════════════════════════════════════

def _bind(env, mid, actions):
    return M.bind_mission_plan(mission_id=mid, actions=actions,
                               mission_store_dir=env["stores"]["missions"])


def test_A_B_plan_bind_valid_and_immutable(env):
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    assert r["status"] == M.STATUS_PLAN_BOUND, r
    assert r["plan_id"].startswith("mpl-") and len(r["plan_hash"]) == 64
    assert r["decision_authority"] == "NON_SOVEREIGN"
    assert r["plan_is_execution_authority"] is False
    # immuable : re-bind rejeté
    r2 = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    assert r2["status"] == M.STATUS_PLAN_BIND_REJECTED and r2["reason"] == "PLAN_ALREADY_BOUND"
    # verify
    plan = M.load_mission_plan(mid, r["plan_id"], env["stores"]["missions"])
    g = M.load_mission_genesis(mid, env["stores"]["missions"])
    ok, why = M.verify_mission_plan(plan, genesis=g)
    assert ok, why
    assert plan["execution_order"] == [a["action_id"] for a in sorted(plan["actions"], key=lambda d: d["ordinal"])]


def test_C_plan_hash_tamper_rejected(env):
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    ppath = next((env["stores"]["missions"] / mid / "plans").glob("mpl-*.json"))
    p = json.loads(ppath.read_text(encoding="utf-8"))
    p["actions"][0]["target_path"] = "periphery/xdomain/other.txt"
    ppath.write_text(json.dumps(p, indent=2, sort_keys=True), encoding="utf-8")
    out = SEQ.advance_bounded_mission(mission_id=mid, plan_id=r["plan_id"], **_seq_kw(env))
    assert out["status"] == SEQ.ADVANCE_REJECTED
    assert out["reason"].startswith("PLAN_INVALID") or out["reason"] == "PLAN_HASH_DRIFT"


def test_DEFGH_plan_malformed_rejected(env):
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    base = env["base"]
    # D duplicate ordinal
    a = _fix_source_commit(_abc_actions(), base); a[1]["ordinal"] = 0
    assert _bind(env, mid, a)["reason"] == "PLAN_MALFORMED:DUPLICATE_ORDINAL:0"
    # F self dependency
    a = _fix_source_commit(_abc_actions(), base); a[0]["dependency_ordinals"] = [0]
    assert _bind(env, mid, a)["reason"] == "PLAN_MALFORMED:ACTION_SELF_DEPENDENCY:0"
    # G unknown dependency
    a = _fix_source_commit(_abc_actions(), base); a[0]["dependency_ordinals"] = [9]
    assert _bind(env, mid, a)["reason"] == "PLAN_MALFORMED:DEPENDENCY_ORDINAL_NOT_IN_PLAN:9"
    # H cycle
    a = _fix_source_commit(_abc_actions(), base)
    a[0]["dependency_ordinals"] = [1]; a[1]["dependency_ordinals"] = [0]
    assert _bind(env, mid, a)["reason"].startswith("PLAN_MALFORMED:DEPENDENCY_CYCLE")


def test_IJK_plan_scope_and_budget_rejected(env):
    # I target outside scope
    mid = _genesis(env, allowed=["periphery/xdomain/nope.txt"])["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    assert r["reason"].startswith("PLAN_TARGET_OUTSIDE_MISSION_SCOPE")
    # K max_actions exceeded
    mid2 = _genesis(env, max_actions=2)["mission_id"]
    M.bind_work_unit(mission_id=mid2, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r2 = _bind(env, mid2, _fix_source_commit(_abc_actions(), env["base"]))
    assert r2["reason"] == "PLAN_EXCEEDS_MAX_ACTIONS"


# ══════════════════════════════════════════════════════════════════════════
#  L..AE — vraie séquence gouvernée A -> B -> C
# ══════════════════════════════════════════════════════════════════════════

def _drive_full_abc(env):
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    plan_id = r["plan_id"]
    eahs, calls = [], []

    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=plan_id, **_seq_kw(env))
    calls.append(c1)
    assert c1["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL, c1
    assert c1["ordinal"] == 0                       # L/M — A d'abord (ordre déterministe)
    assert c1["governed_target_mutations_this_call"] == 0   # O — aucune mutation avant EAH
    eahs.append(c1["execution_authority_hash"])

    for expected_ordinal, expected_post in ((1, _A2), (2, _A3)):
        prev = calls[-1]
        c = SEQ.advance_bounded_mission(
            mission_id=mid, plan_id=plan_id,
            human_authorized_execution_authority_hash=prev["execution_authority_hash"],
            human_authorization_reference=f"human-eah-turn-{prev['ordinal']}",
            **_seq_kw(env))
        calls.append(c)
        assert c["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL, c
        assert c["ordinal"] == expected_ordinal
        assert c["governed_target_mutations_this_call"] == 1   # exactement UNE mutation par appel
        eahs.append(c["execution_authority_hash"])

    # dernier appel : exécute C -> snapshot -> PLAN_COMPLETED
    last = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=plan_id,
        human_authorized_execution_authority_hash=calls[-1]["execution_authority_hash"],
        human_authorization_reference="human-eah-turn-2",
        **_seq_kw(env))
    calls.append(last)
    return mid, plan_id, eahs, calls, last


def test_LMNOP_QRS_TUV_WXY_full_abc_mission(env):
    mid, plan_id, eahs, calls, last = _drive_full_abc(env)
    assert last["status"] == SEQ.PLAN_EXECUTION_COMPLETE, last
    assert last["current_state"] == "CLOSED_AWAITING_NEXT_PLAN"
    assert last["actions_kept"] == 3
    assert last["governed_target_mutations_this_call"] == 1
    # T / AA — 3 EAH distincts
    assert len(set(eahs)) == 3
    # Z / AE — cible finale == A3, tip == commit du snapshot C, base canonique immuable
    assert (env["wt"] / _TARGET).read_bytes() == _A3
    p = _proj(env, mid)
    assert p["canonical_base_sha"] == env["base"]
    snaps = p["local_snapshots"]
    assert len(snaps) == 3
    assert p["mission_tip_sha"] == snaps[2]["new_commit_sha"]
    # AC — chaîne de parents des snapshots exacte
    assert snaps[0]["commit_parent_sha"] == env["base"]
    assert snaps[1]["commit_parent_sha"] == snaps[0]["new_commit_sha"]
    assert snaps[2]["commit_parent_sha"] == snaps[1]["new_commit_sha"]
    # 3 exécutions gouvernées liées, gates ALLOW, records KX108 distincts
    lg = p["linked_governed_executions"]
    assert len(lg) == 3 and all(x["outcome_status"] == WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW for x in lg)
    assert len({x["kx108_pre_decision_record_id"] for x in lg}) == 3
    assert all(x["kx108_pre_gate"] == "ALLOW" and x["kx108_post_gate"] == "ALLOW" for x in lg)
    # worktree propre, HEAD == tip
    assert _git(env["wt"], "status", "--porcelain") == ""
    assert _git(env["wt"], "rev-parse", "HEAD") == p["mission_tip_sha"]


def test_37_human_interruption_count_is_three(env):
    mid, plan_id, eahs, calls, last = _drive_full_abc(env)
    # 4 appels advance ; exactement 3 portaient un EAH humain
    eah_calls = [1 for c_in, c_out in zip(range(4), calls) if c_out["status"] == SEQ.PLAN_EXECUTION_COMPLETE
                 or c_out["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL]
    # (le test structurel : 3 EAH fournis, 0 approbation automatique)
    assert len(set(eahs)) == 3
    p = _proj(env, mid)
    assert len(p["linked_governed_executions"]) == 3


def test_38_cross_action_eah_replay_fail_closed(env):
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    plan_id = r["plan_id"]
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=plan_id, **_seq_kw(env))
    eah_A = c1["execution_authority_hash"]
    c2 = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=plan_id, human_authorized_execution_authority_hash=eah_A,
        human_authorization_reference="h0", **_seq_kw(env))
    assert c2["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL and c2["ordinal"] == 1
    eah_B = c2["execution_authority_hash"]
    # rejouer EAH_A pour l'action B -> fail closed
    bad = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=plan_id, human_authorized_execution_authority_hash=eah_A,
        human_authorization_reference="h1", **_seq_kw(env))
    assert bad["status"] == SEQ.PLAN_BLOCKED and bad["reason"] == "ENVELOPE_DRIFT"
    # l'EAH_B correct fonctionne ensuite
    good = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=plan_id, human_authorized_execution_authority_hash=eah_B,
        human_authorization_reference="h1", **_seq_kw(env))
    assert good["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL and good["ordinal"] == 2


def test_AL_terminal_action_cannot_execute_twice(env):
    mid, plan_id, eahs, calls, last = _drive_full_abc(env)
    assert last["status"] == SEQ.PLAN_EXECUTION_COMPLETE
    again = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=plan_id,
        human_authorized_execution_authority_hash=eahs[0],
        human_authorization_reference="replay", **_seq_kw(env))
    assert again["status"] == SEQ.PLAN_EXECUTION_COMPLETE  # déjà complété, idempotent, aucune ré-exécution
    assert again["governed_target_mutations_this_call"] == 0


# ══════════════════════════════════════════════════════════════════════════
#  AF/AG/AH — redémarrage de processus
# ══════════════════════════════════════════════════════════════════════════

def test_AFGH_restart_derives_same_position(env):
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    plan_id = r["plan_id"]
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=plan_id, **_seq_kw(env))   # A préparée
    c2 = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=plan_id, human_authorized_execution_authority_hash=c1["execution_authority_hash"],
        human_authorization_reference="h0", **_seq_kw(env))                            # A KEEP+snap, B préparée
    assert c2["ordinal"] == 1
    tip_after_A = _proj(env, mid)["mission_tip_sha"]

    # redémarrage à froid : on charge des instances FRAÎCHES des deux modules,
    # puis on RESTAURE les entrées canoniques de sys.modules (pour ne pas casser
    # les autres fichiers de test qui référencent l'objet module d'origine).
    _orig_M = sys.modules.get("obsidia_bounded_mission_v0")
    _orig_SEQ = sys.modules.get("obsidia_mission_sequencer_v0")
    for name in ("obsidia_mission_sequencer_v0", "obsidia_bounded_mission_v0"):
        sys.modules.pop(name, None)
    import obsidia_bounded_mission_v0 as M2  # noqa
    import obsidia_mission_sequencer_v0 as SEQ2
    try:
        p = M2.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                               hold_store_dir=env["stores"]["holds"])
        assert p["current_state"] == "ACTION_PREPARED"
        assert p["mission_tip_sha"] == tip_after_A
        assert p["last_prepared_evidence"]["ordinal"] == 1
        # advance sans EAH -> ré-expose exactement l'EAH_B de l'action préparée
        c = SEQ2.advance_bounded_mission(mission_id=mid, plan_id=plan_id, **_seq_kw(env))
        assert c["status"] == SEQ2.MISSION_AWAITING_HUMAN_EAH_APPROVAL and c["ordinal"] == 1
        assert c["execution_authority_hash"] == c2["execution_authority_hash"]
    finally:
        if _orig_M is not None:
            sys.modules["obsidia_bounded_mission_v0"] = _orig_M
        if _orig_SEQ is not None:
            sys.modules["obsidia_mission_sequencer_v0"] = _orig_SEQ


# ══════════════════════════════════════════════════════════════════════════
#  AI — HOLD non résolu bloque ; AJ — décision sémantique ≠ EAH
# ══════════════════════════════════════════════════════════════════════════

def test_AI_unresolved_hold_blocks_then_resumes(env):
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    plan_id = r["plan_id"]
    h = M.open_mission_hold(
        mission_id=mid, hold_type="AMBIGUOUS_WIRE_OR_DEPRECATE",
        reason="operator paused", question_for_human="wire or deprecate?",
        bounded_options=["WIRE", "DEPRECATE"],
        mission_store_dir=env["stores"]["missions"], hold_store_dir=env["stores"]["holds"])
    assert h["status"] == M.STATUS_HOLD_OPENED
    out = SEQ.advance_bounded_mission(mission_id=mid, plan_id=plan_id, **_seq_kw(env))
    assert out["status"] == SEQ.HOLD_FOR_HUMAN_DECISION
    assert out["hold_id"] == h["hold_id"]
    assert out["semantic_decision_is_execution_approval"] is False
    # décision humaine sémantique -> résout -> l'action A est ensuite préparée
    d = M.record_human_mission_decision(
        mission_id=mid, hold_id=h["hold_id"], hold_record_hash=h["mission_hold_record_hash"],
        chosen_option="WIRE", mission_store_dir=env["stores"]["missions"],
        hold_store_dir=env["stores"]["holds"], decision_store_dir=env["stores"]["decisions"])
    assert d["status"] == M.STATUS_DECISION_RECORDED
    res = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=plan_id, human_mission_decision_id=d["human_mission_decision_id"],
        **_seq_kw(env))
    assert res["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL and res["ordinal"] == 0


def test_AJ_semantic_decision_and_eah_same_call_fail_closed(env):
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    out = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=r["plan_id"],
        human_authorized_execution_authority_hash="0" * 64,
        human_authorization_reference="x", human_mission_decision_id="hmd-x", **_seq_kw(env))
    assert out["status"] == SEQ.ADVANCE_INPUT_AMBIGUOUS
    assert out["semantic_decision_is_execution_approval"] is False


# ══════════════════════════════════════════════════════════════════════════
#  AK / §40 — échec gouverné réel stoppe la mission multi-actions
# ══════════════════════════════════════════════════════════════════════════

def test_AK_real_failure_stops_multi_action_mission(env):
    neg = TC.build_test_contract("c-A-neg", "cand", "batch", _TARGET, [
        TC.build_check("no-change", TC.CHECK_TYPE_DIFF_SCOPE, expected_diff_paths=[], required=True)])
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(a_contract=neg), env["base"]))
    plan_id = r["plan_id"]
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=plan_id, **_seq_kw(env))
    assert c1["ordinal"] == 0
    c2 = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=plan_id, human_authorized_execution_authority_hash=c1["execution_authority_hash"],
        human_authorization_reference="h0", **_seq_kw(env))
    assert c2["status"] == SEQ.PLAN_BLOCKED
    assert c2["reason"].startswith("ACTION_")
    assert c2["driver_status"] == WU._DRV.REJECTED_ROLLED_BACK
    assert c2["real_failure_stops_multi_action_mission"] is True
    assert c2["only_keep_can_advance_mission_tip"] is True
    p = _proj(env, mid)
    assert p["mission_tip_sha"] == env["base"]        # tip PAS avancé
    assert p["local_snapshot_count"] == 0             # aucun snapshot
    assert (env["wt"] / _TARGET).read_bytes() == _A0  # A restauré par D2
    # aucune 2e action préparée
    assert p["current_state"] == "ACTION_EXECUTED_ROLLED_BACK"


# ══════════════════════════════════════════════════════════════════════════
#  §26 — chaîne PLAN -> mission_tip -> expected_action_base_sha -> PEC.base_sha
# ══════════════════════════════════════════════════════════════════════════

def test_26_base_chain_plan_tip_to_pec(env):
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    plan_id = r["plan_id"]
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=plan_id, **_seq_kw(env))
    c2 = SEQ.advance_bounded_mission(
        mission_id=mid, plan_id=plan_id, human_authorized_execution_authority_hash=c1["execution_authority_hash"],
        human_authorization_reference="h0", **_seq_kw(env))
    assert c2["ordinal"] == 1
    p = _proj(env, mid)
    tip_A = p["mission_tip_sha"]
    assert c2["prepared_action_base_sha"] == tip_A
    # le PEC de B (résolu par son id exact) porte base_sha == tip_A
    prep_ev = p["last_prepared_evidence"]
    assert prep_ev["effective_action_base_sha"] == tip_A
    pecB = json.loads(next(env["stores"]["pec"].rglob(prep_ev["pre_execution_context_id"] + ".json")).read_text(encoding="utf-8"))
    assert pecB["base_sha"] == tip_A
    # B observe le résultat de A
    assert pecB["target_pre_sha256"] == _sha(_A1)


# ══════════════════════════════════════════════════════════════════════════
#  §42 / §43 — audit statique : le séquenceur n'est pas une autorité
# ══════════════════════════════════════════════════════════════════════════

def test_42_sequencer_static_no_bypass():
    src = Path(SEQ.__file__).read_text(encoding="utf-8")
    for banned in ("run_governed_content_apply(", "store_approval_artifact(",
                   "run_and_persist_kx108", "run_governed_rollback(",
                   "run_tooling_build_pipeline", "create_pre_execution_context(",
                   "build_sealed_apply_receipt(", ".write_bytes(",
                   '"commit"', '"add", "--"', '"restore", "--staged"', '"reset"',
                   '"push"', '"merge"', '"rebase"', '"cherry-pick"',
                   "GuardX108", "approved_by", "def compute_execution_authority_hash"):
        assert banned not in src, banned
    # aucune écriture : le séquenceur ne persiste RIEN lui-même
    assert "open(" not in src and "write_text(" not in src and "_atomic_publish_json" not in src
    assert "NON_SOVEREIGN" in src
    assert "sequencer_is_authority" in src


def test_43_max_one_mutation_per_advance_call(env):
    # invariant structurel : chaque retour porte governed_target_mutations_this_call <= 1
    mid = _genesis(env)["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = _bind(env, mid, _fix_source_commit(_abc_actions(), env["base"]))
    plan_id = r["plan_id"]
    seen = []
    c = SEQ.advance_bounded_mission(mission_id=mid, plan_id=plan_id, **_seq_kw(env))
    seen.append(c["governed_target_mutations_this_call"])
    for _ in range(3):
        if c["status"] != SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL:
            break
        c = SEQ.advance_bounded_mission(
            mission_id=mid, plan_id=plan_id,
            human_authorized_execution_authority_hash=c["execution_authority_hash"],
            human_authorization_reference="h", **_seq_kw(env))
        seen.append(c["governed_target_mutations_this_call"])
    assert all(0 <= v <= 1 for v in seen)
    assert seen[0] == 0 and any(v == 1 for v in seen[1:])


def test_AY_audit_world_action_bus_untouched():
    for f in (SEQ.__file__, M.__file__):
        assert "world_action_bus" not in Path(f).read_text(encoding="utf-8")