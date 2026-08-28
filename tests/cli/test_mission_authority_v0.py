"""
tests/cli/test_mission_authority_v0.py
======================================
STAGE 4C — sous-système runtime d'autorité de mission bornée, INERTE.

Vérifie la représentation + la vérification runtime de HumanMissionAuthorization,
MissionAuthorityRevocation et DerivedActionAuthorityWitness contre le modèle
formel Lean committé (Stage 4A/4B). Positifs + négatifs (rejeu cross-action,
cross-mission, substitution de plan, expansion de portée, révocation, plan clos,
dérive EAH, budget, dépendances).

Aucun de ces objets n'est accepté par un rail d'exécution : ce module n'a AUCUN
appelant de production.
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

import obsidia_test_contract as TC                 # noqa: E402
import obsidia_isolated_work_unit_v0 as WU         # noqa: E402
import obsidia_bounded_mission_v0 as M             # noqa: E402
import obsidia_batch_execution as E                # noqa: E402
import obsidia_mission_authority_v0 as MA          # noqa: E402

_TARGET = "periphery/xdomain/ma_target_v0.txt"
_S1 = "periphery/xdomain/ma_src_1.txt"
_S2 = "periphery/xdomain/ma_src_2.txt"
_S3 = "periphery/xdomain/ma_src_3.txt"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(repo: Path, *a: str) -> str:
    r = subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {a}: {r.stderr}"
    return r.stdout.strip()


def _contract(cid: str) -> dict:
    return TC.build_test_contract(cid, "cand", "batch", _TARGET, [
        TC.build_check("post", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET,
                       expected_target_sha256=_sha(b"x"), required=True),
        TC.build_check("scope", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[_TARGET], required=True),
    ])


@pytest.fixture
def env(tmp_path):
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    for f in (_TARGET, _S1, _S2, _S3):
        (main / f).write_bytes(f.encode())
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "t@example.com")
    _git(main, "config", "user.name", "t")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base = _git(main, "rev-parse", "HEAD")
    stores = tmp_path / "missions"
    wt = (tmp_path / "wt").resolve()
    cr = WU.create_isolated_work_unit(repo_root=main, base_sha=base, branch_name="mabr",
                                      worktree_path=wt, work_unit_id="wu-ma-0001")
    assert cr["status"] == WU.WORK_UNIT_CREATED, cr
    return {"root": tmp_path, "main": main, "base": base, "stores": stores,
            "wu": cr["work_unit"], "wt": wt}


def _mk_mission(env, *, max_actions=3, allowed=None, max_retries=0, brn="mabr", tag="a"):
    g = M.create_bounded_mission(
        objective=f"stage4c-{tag}", repository_identity="repo://ma",
        canonical_base_sha=env["base"], branch_name=brn,
        worktree_path=str(env["wt"]), main_worktree_path=str(env["main"].resolve()),
        scope={"allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
               "allowed_target_paths": allowed if allowed is not None else [_TARGET],
               "max_actions": max_actions, "max_retries_per_action": max_retries},
        human_mandate_reference=f"human-mandate-ma-{tag}",
        mission_store_dir=env["stores"])
    mid = g["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"])
    return mid


def _abc(env):
    return [
        {"ordinal": 0, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S1, "test_contract": _contract("c-A"),
         "dependency_ordinals": []},
        {"ordinal": 1, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S2, "test_contract": _contract("c-B"),
         "dependency_ordinals": [0]},
        {"ordinal": 2, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S3, "test_contract": _contract("c-C"),
         "dependency_ordinals": [1]},
    ]


def _bind_plan(env, mid, actions=None):
    r = M.bind_mission_plan(mission_id=mid, actions=actions or _abc(env),
                            mission_store_dir=env["stores"])
    assert r["status"] == M.STATUS_PLAN_BOUND, r
    return r["plan_id"]


def _load(env, mid, plan_id):
    genesis = M.load_mission_genesis(mid, env["stores"])
    plan = M.load_mission_plan(mid, plan_id, env["stores"])
    return genesis, plan


def _proj(*, tip, snapshotted=(), completed=False, state="WORKTREE_BOUND"):
    return {"mission_tip_sha": tip, "snapshotted_action_ids": list(snapshotted),
            "plan_completed": completed, "current_state": state}


def _envelope(target=_TARGET, tch="e" * 64, *, beid="be-1", tp_override=None):
    return {
        "batch_execution_id": beid,
        "test_contract_hash": tch,
        "decision_authority": "KX108_ONLY",
        "children": [{
            "candidate_entry_id": "ce-1", "child_execution_id": "ch-1",
            "source_kind": "GIT_BLOB", "source_content_sha256": "d" * 64,
            "source_git_commit_sha": "c" * 40,
            "source_git_historical_path": "periphery/xdomain/x.txt",
            "target_path": tp_override or target,
            "operation_type": "UPDATE_TARGET_FROM_SOURCE",
        }],
    }


def _hma(env, mid, plan_id, *, ref="TEST_HUMAN_REFERENCE"):
    return MA.build_human_mission_authorization(
        mission_id=mid, plan_id=plan_id, human_authorization_reference=ref,
        mission_store_dir=env["stores"])[0]


# ══════════════════════════════════════════════════════════════════════════
#  Bornes statiques
# ══════════════════════════════════════════════════════════════════════════

def test_static_boundary_flags():
    assert MA.RUNTIME_AUTHORITY_ACTIVE is False
    assert MA.STAGE4_AUTHORITY_EXECUTION_INTEGRATION is False
    assert MA.DECISION_AUTHORITY == "KX108_ONLY"
    assert MA.MISSION_AUTHORIZATION_PLAN_BINDING == "EXACT_PLAN_HASH"
    assert MA.DAAW_SOVEREIGNTY == "NON_SOVEREIGN"


def test_static_no_bypass_or_kx_or_pre():
    src = Path(MA.__file__).read_text(encoding="utf-8")
    for banned in ("store_approval_artifact(", "_validate_approval(",
                   "run_and_persist_kx108", "run_governed_content_apply(",
                   "run_governed_rollback(", "GuardX108", "approved_by",
                   ".write_bytes(", '"commit"', '"add"', '"push"', '"merge"',
                   "import obsidia_mission_sequencer_v0",
                   "import obsidia_governed_apply_v0",
                   "import obsidia_kx108_decision_store"):
        assert banned not in src, banned
    # EAH réutilisé, jamais réimplémenté
    assert "compute_execution_authority_hash" in src
    assert "def compute_execution_authority_hash" not in src


def test_no_production_callers():
    hits = []
    for p in _SCRIPTS.glob("*.py"):
        if p.name == "obsidia_mission_authority_v0.py":
            continue
        if "obsidia_mission_authority_v0" in p.read_text(encoding="utf-8"):
            hits.append(p.name)
    assert hits == [], f"unexpected production callers: {hits}"


def test_semantic_decision_is_not_mission_authorization():
    assert MA.semantic_decision_is_mission_authorization({"holdId": 1, "chosenOption": 0}) is False


# ══════════════════════════════════════════════════════════════════════════
#  HMA — positifs
# ══════════════════════════════════════════════════════════════════════════

def test_hma_build_valid_1_action(env):
    mid = _mk_mission(env, max_actions=1)
    pid = _bind_plan(env, mid, actions=[_abc(env)[0]])
    rec, why = MA.build_human_mission_authorization(
        mission_id=mid, plan_id=pid, human_authorization_reference="TEST_HUMAN_REFERENCE",
        mission_store_dir=env["stores"])
    assert why is None and rec is not None
    assert rec["issuer"] == "HUMAN"
    assert rec["domain_tag"] == MA.HMA_DOMAIN_TAG
    assert rec["is_kx_authority"] is False and rec["plan_is_execution_authority"] is False
    assert rec["human_mission_authorization_id"] == "hma-" + rec["hma_record_hash"][:32]
    g, plan = _load(env, mid, pid)
    ok, r = MA.verify_human_mission_authorization(rec, genesis=g, plan=plan)
    assert ok, r


def test_hma_build_valid_3_actions_and_verify(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    ok, r = MA.verify_human_mission_authorization(rec, genesis=g, plan=plan)
    assert ok, r
    assert rec["plan_hash"] == plan["plan_hash"]


def test_hma_write_once_and_idempotent(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    r1 = MA.bind_human_mission_authorization(
        mission_id=mid, plan_id=pid, human_authorization_reference="TEST_HUMAN_REFERENCE",
        mission_store_dir=env["stores"])
    assert r1["status"] == MA.HMA_BOUND and r1["store_status"] == "STORED"
    r2 = MA.bind_human_mission_authorization(
        mission_id=mid, plan_id=pid, human_authorization_reference="TEST_HUMAN_REFERENCE",
        mission_store_dir=env["stores"])
    assert r2["status"] == MA.HMA_BOUND and r2["store_status"] == "IDEMPOTENT_EXISTING_IDENTICAL"
    loaded = MA.load_human_mission_authorization(mid, r1["human_mission_authorization_id"], env["stores"])
    assert loaded["hma_record_hash"] == r1["hma_record_hash"]


def test_hma_divergent_same_id_is_immutability_violation(env, monkeypatch):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    r1 = MA.bind_human_mission_authorization(
        mission_id=mid, plan_id=pid, human_authorization_reference="TEST_HUMAN_REFERENCE",
        mission_store_dir=env["stores"])
    hid = r1["human_mission_authorization_id"]
    # écrase manuellement le fichier avec un contenu divergent de même id
    p = env["stores"] / mid / "mission_authority" / "authorizations" / f"{hid}.json"
    rec = json.loads(p.read_text(encoding="utf-8"))
    rec["revocation_policy"] = "TAMPERED"
    p.write_text(json.dumps(rec), encoding="utf-8")
    loaded = MA.load_human_mission_authorization(mid, hid, env["stores"])
    g, plan = _load(env, mid, pid)
    ok, why = MA.verify_human_mission_authorization(loaded, genesis=g, plan=plan)
    assert ok is False and why == "HMA_RECORD_HASH_MISMATCH"


def test_hma_requires_external_human_reference(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    rec, why = MA.build_human_mission_authorization(
        mission_id=mid, plan_id=pid, human_authorization_reference="   ",
        mission_store_dir=env["stores"])
    assert rec is None and why == "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED"


# ══════════════════════════════════════════════════════════════════════════
#  HMA — négatifs (tamper / mismatch / expansion)
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("mut,expect", [
    (lambda r: r.__setitem__("issuer", "STACK"), "HMA_ISSUER_NOT_HUMAN"),
    (lambda r: r.__setitem__("domain_tag", "OTHER"), "HMA_DOMAIN_TAG_MISMATCH"),
    (lambda r: r.__setitem__("authority_schema_version", 99), "HMA_SCHEMA_UNSUPPORTED"),
    (lambda r: r.__setitem__("mission_id", "mis-other"), "HMA_RECORD_HASH_MISMATCH"),
    (lambda r: r.__setitem__("hma_record_hash", "0" * 64), "HMA_RECORD_HASH_MISMATCH"),
])
def test_hma_negative_structural(env, mut, expect):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    mut(rec)
    ok, why = MA.verify_human_mission_authorization(rec, genesis=g, plan=plan)
    assert ok is False and why == expect


def test_hma_wrong_genesis_hash(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    g2 = dict(g); g2["mission_genesis_record_hash"] = "f" * 64
    ok, why = MA.verify_human_mission_authorization(rec, genesis=g2, plan=plan)
    assert ok is False and why in ("GENESIS_INVALID:MISSION_GENESIS_RECORD_HASH_MISMATCH",
                                   "HMA_GENESIS_HASH_MISMATCH")


def test_hma_plan_substitution_fails_even_if_shapes_equal(env):
    mid = _mk_mission(env)
    pid1 = _bind_plan(env, mid)
    rec = _hma(env, mid, pid1)             # HMA liée au plan 1
    # 2e mission identique en forme -> plan_hash différent (mission_id différent dans le matériel)
    mid2 = _mk_mission(env, tag="b")
    pid2 = _bind_plan(env, mid2)
    g2, plan2 = _load(env, mid2, pid2)
    ok, why = MA.verify_human_mission_authorization(rec, genesis=g2, plan=plan2)
    assert ok is False and why in ("HMA_MISSION_MISMATCH", "HMA_PLAN_HASH_MISMATCH", "HMA_PLAN_ID_MISMATCH")


def test_hma_scope_expansion_max_actions(env):
    mid = _mk_mission(env, max_actions=3)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    rec["max_actions"] = 99
    # hash recomputé pour isoler la sémantique de portée (sinon HMA_RECORD_HASH_MISMATCH)
    rec["hma_record_hash"] = MA._sha256_hex(MA._canon({k: rec[k] for k in MA._HMA_BOUND_FIELDS}))
    rec["human_mission_authorization_id"] = "hma-" + rec["hma_record_hash"][:32]
    ok, why = MA.verify_human_mission_authorization(rec, genesis=g, plan=plan)
    assert ok is False and why == "HMA_MAX_ACTIONS_EXCEEDS_GENESIS"


def test_hma_scope_expansion_target_added(env):
    mid = _mk_mission(env, allowed=[_TARGET])
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    rec["allowed_target_paths"] = [_TARGET, "periphery/xdomain/extra.txt"]
    rec["hma_record_hash"] = MA._sha256_hex(MA._canon({k: rec[k] for k in MA._HMA_BOUND_FIELDS}))
    rec["human_mission_authorization_id"] = "hma-" + rec["hma_record_hash"][:32]
    ok, why = MA.verify_human_mission_authorization(rec, genesis=g, plan=plan)
    assert ok is False and why == "HMA_TARGETS_NOT_SUBSET_OF_GENESIS"


def test_hma_dependency_commitment_mismatch(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    rec["dependency_commitment"] = "a" * 64
    rec["hma_record_hash"] = MA._sha256_hex(MA._canon({k: rec[k] for k in MA._HMA_BOUND_FIELDS}))
    rec["human_mission_authorization_id"] = "hma-" + rec["hma_record_hash"][:32]
    ok, why = MA.verify_human_mission_authorization(rec, genesis=g, plan=plan)
    assert ok is False and why == "HMA_DEPENDENCY_COMMITMENT_MISMATCH"


# ══════════════════════════════════════════════════════════════════════════
#  Révocation
# ══════════════════════════════════════════════════════════════════════════

def test_revocation_append_only_and_invalidates_future(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    ok, _r = MA.verify_human_mission_authorization(rec, genesis=g, plan=plan, revocations=[])
    assert ok
    rv = MA.record_mission_authority_revocation(
        mission_id=mid, hma_id=rec["human_mission_authorization_id"],
        hma_record_hash=rec["hma_record_hash"], revocation_reference="TEST_HUMAN_STOP",
        mission_store_dir=env["stores"])
    assert rv["status"] == MA.REVOCATION_RECORDED and rv["history_rewritten"] is False
    revs = MA.list_mission_authority_revocations(mid, env["stores"])
    assert len(revs) == 1
    ok2, why2 = MA.verify_human_mission_authorization(rec, genesis=g, plan=plan, revocations=revs)
    assert ok2 is False and why2 == "HMA_REVOKED"
    # ré-révocation identique -> idempotent (aucune réécriture d'histoire)
    rv2 = MA.record_mission_authority_revocation(
        mission_id=mid, hma_id=rec["human_mission_authorization_id"],
        hma_record_hash=rec["hma_record_hash"], revocation_reference="TEST_HUMAN_STOP",
        mission_store_dir=env["stores"])
    assert rv2["status"] == MA.REVOCATION_RECORDED
    assert len(MA.list_mission_authority_revocations(mid, env["stores"])) == 1


def test_revocation_actor_must_be_human(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    rec = _hma(env, mid, pid)
    rv = MA.record_mission_authority_revocation(
        mission_id=mid, hma_id=rec["human_mission_authorization_id"],
        hma_record_hash=rec["hma_record_hash"], revocation_reference="x",
        mission_store_dir=env["stores"], actor="STACK")
    assert rv["status"] == MA.REVOCATION_REJECTED and rv["reason"] == "REVOCATION_ACTOR_NOT_HUMAN"


# ══════════════════════════════════════════════════════════════════════════
#  DAAW — positifs
# ══════════════════════════════════════════════════════════════════════════

def test_daaw_derive_and_verify_first_action(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    a0 = plan["actions"][0]["action_id"]
    proj = _proj(tip=env["base"], snapshotted=[])
    envl = _envelope()
    daaw, why = MA.derive_action_authority_witness(
        hma=rec, plan=plan, action_id=a0, projection=proj, execution_envelope=envl)
    assert why is None and daaw is not None
    assert daaw["sovereignty"] == "NON_SOVEREIGN"
    assert daaw["derived_action_authority_witness_id"] == "daaw-" + daaw["daaw_record_hash"][:32]
    ok, r = MA.verify_derived_action_authority_witness(
        daaw=daaw, hma=rec, plan=plan, genesis=g, projection=proj,
        execution_envelope=envl, revocations=[])
    assert ok, r


def test_daaw_verify_second_action_after_tip_advance(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    a0 = plan["actions"][0]["action_id"]
    a1 = plan["actions"][1]["action_id"]
    proj = _proj(tip="a" * 40, snapshotted=[a0])   # A snapshotée, tip avancé
    envl = _envelope(beid="be-2")
    daaw, why = MA.derive_action_authority_witness(
        hma=rec, plan=plan, action_id=a1, projection=proj, execution_envelope=envl)
    assert why is None, why
    ok, r = MA.verify_derived_action_authority_witness(
        daaw=daaw, hma=rec, plan=plan, genesis=g, projection=proj,
        execution_envelope=envl, revocations=[])
    assert ok, r
    assert daaw["executed_action_index"] == 1
    assert daaw["action_base_sha"] == "a" * 40


def test_daaw_eah_reused_not_reimplemented(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    _g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    envl = _envelope()
    daaw, _w = MA.derive_action_authority_witness(
        hma=rec, plan=plan, action_id=plan["actions"][0]["action_id"],
        projection=_proj(tip=env["base"]), execution_envelope=envl)
    assert daaw["execution_authority_hash"] == E.compute_execution_authority_hash(envl)


# ══════════════════════════════════════════════════════════════════════════
#  DAAW — négatifs
# ══════════════════════════════════════════════════════════════════════════

def _valid_daaw(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    a0 = plan["actions"][0]["action_id"]
    proj = _proj(tip=env["base"], snapshotted=[])
    envl = _envelope()
    daaw, why = MA.derive_action_authority_witness(
        hma=rec, plan=plan, action_id=a0, projection=proj, execution_envelope=envl)
    assert why is None
    return dict(mid=mid, pid=pid, g=g, plan=plan, hma=rec, daaw=daaw, proj=proj, envl=envl)


def test_daaw_hash_tamper(env):
    d = _valid_daaw(env)
    d["daaw"]["target_path"] = "periphery/xdomain/other.txt"
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=d["daaw"], hma=d["hma"], plan=d["plan"], genesis=d["g"],
        projection=d["proj"], execution_envelope=d["envl"])
    assert ok is False and why == "DAAW_RECORD_HASH_MISMATCH"


def test_daaw_eah_drift_fail_closed(env):
    d = _valid_daaw(env)
    drifted = _envelope(beid="DIFFERENT")     # composant d'enveloppe modifié -> EAH change
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=d["daaw"], hma=d["hma"], plan=d["plan"], genesis=d["g"],
        projection=d["proj"], execution_envelope=drifted)
    assert ok is False and why == "EAH_MISMATCH"


def test_daaw_stale_base_fail_closed(env):
    d = _valid_daaw(env)
    stale = _proj(tip="b" * 40, snapshotted=[])
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=d["daaw"], hma=d["hma"], plan=d["plan"], genesis=d["g"],
        projection=stale, execution_envelope=d["envl"])
    assert ok is False and why == "DAAW_ACTION_BASE_NOT_CURRENT_MISSION_TIP"


def test_daaw_dependency_unsatisfied_fail_closed(env):
    mid = _mk_mission(env)
    pid = _bind_plan(env, mid)
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    a1 = plan["actions"][1]["action_id"]       # dépend de l'ordinal 0
    proj = _proj(tip=env["base"], snapshotted=[])   # rien de snapshoté
    envl = _envelope()
    daaw, why = MA.derive_action_authority_witness(
        hma=rec, plan=plan, action_id=a1, projection=proj, execution_envelope=envl)
    assert daaw is None and why.startswith("DEPENDENCY_ORDINAL_NOT_SNAPSHOTTED")


def test_daaw_budget_exceeded_fail_closed(env):
    mid = _mk_mission(env, max_actions=1)
    pid = _bind_plan(env, mid, actions=[_abc(env)[0]])
    g, plan = _load(env, mid, pid)
    rec = _hma(env, mid, pid)
    a0 = plan["actions"][0]["action_id"]
    proj = _proj(tip="z" * 40, snapshotted=[a0])   # index 1, max_actions 1 -> dépassé
    envl = _envelope()
    daaw, _w = MA.derive_action_authority_witness(
        hma=rec, plan=plan, action_id=a0, projection=proj, execution_envelope=envl)
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=daaw, hma=rec, plan=plan, genesis=g, projection=proj, execution_envelope=envl)
    assert ok is False and why == "DAAW_BUDGET_EXCEEDED"


def test_daaw_closed_mission_fail_closed(env):
    d = _valid_daaw(env)
    closed = _proj(tip=env["base"], snapshotted=[], completed=True,
                   state="CLOSED_AWAITING_NEXT_PLAN")
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=d["daaw"], hma=d["hma"], plan=d["plan"], genesis=d["g"],
        projection=closed, execution_envelope=d["envl"])
    assert ok is False and why == "MISSION_PLAN_COMPLETED"


def test_daaw_revoked_hma_fail_closed(env):
    d = _valid_daaw(env)
    rv = MA.record_mission_authority_revocation(
        mission_id=d["mid"], hma_id=d["hma"]["human_mission_authorization_id"],
        hma_record_hash=d["hma"]["hma_record_hash"], revocation_reference="STOP",
        mission_store_dir=env["stores"])
    assert rv["status"] == MA.REVOCATION_RECORDED
    revs = MA.list_mission_authority_revocations(d["mid"], env["stores"])
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=d["daaw"], hma=d["hma"], plan=d["plan"], genesis=d["g"],
        projection=d["proj"], execution_envelope=d["envl"], revocations=revs)
    assert ok is False and why.startswith("HMA_INVALID:HMA_REVOKED")


def test_daaw_cross_action_replay_fail_closed(env):
    d = _valid_daaw(env)
    # DAAW pour l'action 0 présenté avec action_id de l'action 1
    a1 = d["plan"]["actions"][1]["action_id"]
    tampered = dict(d["daaw"]); tampered["action_id"] = a1
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=tampered, hma=d["hma"], plan=d["plan"], genesis=d["g"],
        projection=d["proj"], execution_envelope=d["envl"])
    assert ok is False and why == "DAAW_RECORD_HASH_MISMATCH"


def test_daaw_cross_mission_replay_fail_closed(env):
    d = _valid_daaw(env)
    mid2 = _mk_mission(env, tag="b")
    pid2 = _bind_plan(env, mid2)
    g2, plan2 = _load(env, mid2, pid2)
    rec2 = _hma(env, mid2, pid2)
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=d["daaw"], hma=rec2, plan=plan2, genesis=g2,
        projection=d["proj"], execution_envelope=d["envl"])
    assert ok is False and why in ("DAAW_HMA_ID_MISMATCH", "DAAW_MISSION_MISMATCH",
                                   "DAAW_PLAN_ID_MISMATCH", "DAAW_PLAN_HASH_MISMATCH")


def test_daaw_scope_amplification_fail_closed(env):
    d = _valid_daaw(env)
    t = dict(d["daaw"])
    t["max_actions"] = 999
    t["daaw_record_hash"] = MA._sha256_hex(MA._canon({k: t.get(k) for k in MA._DAAW_BOUND_FIELDS}))
    t["derived_action_authority_witness_id"] = "daaw-" + t["daaw_record_hash"][:32]
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=t, hma=d["hma"], plan=d["plan"], genesis=d["g"],
        projection=d["proj"], execution_envelope=d["envl"])
    assert ok is False and why == "DAAW_SCOPE_AMPLIFICATION"


def test_daaw_envelope_target_mismatch_fail_closed(env):
    d = _valid_daaw(env)
    other = _envelope(tp_override="periphery/xdomain/nope.txt")
    ok, why = MA.verify_derived_action_authority_witness(
        daaw=d["daaw"], hma=d["hma"], plan=d["plan"], genesis=d["g"],
        projection=d["proj"], execution_envelope=other)
    assert ok is False and why in ("EAH_MISMATCH", "ENVELOPE_TARGET_MISMATCH")
