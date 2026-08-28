"""
tests/cli/test_mission_authority_seam_repair_v0.py
================================================
STAGE 4F MINIMAL AUTHORITY SEAM REPAIR — deux coutures fermées :

  A. Consommation d'approbation dérivée CONTEXTUELLE : `approved_by =
     HUMAN_MISSION_AUTHORITY_DERIVED` + structure + self-hash NE SUFFISENT
     PLUS. Chaque consommateur privilégié exige un locator canonique
     (paramètre explicite OU champ `embedded_authority_locator` LIÉ AU HASH)
     puis RECHARGE + VÉRIFIE l'artefact DMAE canonique et sa liaison exacte.

  B. Révocation HMA committée et mutation gouvernée Stage 4 LINÉARISÉES par
     un verrou inter-processus réel du SE (`msvcrt`/`fcntl`), indexé par
     `mission_id`. Il devient impossible d'obtenir « révocation committée
     AVANT la mutation » ET « la mutation réussit quand même ».
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
import obsidia_mission_authority_pre_adapter_v0 as PADP  # noqa: E402
import obsidia_mission_authority_freshness_lock_v0 as LK # noqa: E402
import obsidia_governed_execution_driver_v0 as DRV       # noqa: E402
import obsidia_governed_apply_v0 as GA                   # noqa: E402
import obsidia_kx108_pre_execution_evidence_adapter_v0 as PRE  # noqa: E402
import obsidia_kx108_decision_store as DS                # noqa: E402
import obsidia_batch_execution as E                      # noqa: E402
import obsidia_content_apply as CA                       # noqa: E402

_TARGET = "periphery/xdomain/g_target_v0.txt"
_S1 = "periphery/xdomain/g_src_1.txt"
_A0, _A1 = (b"G\nstate: 0\n", b"G\nstate: 1\n")


def _sha(b): return hashlib.sha256(b).hexdigest()


def _git(repo, *a):
    r = subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {a}: {r.stderr}"
    return r.stdout.strip()


def _contract(cid, want=_A1):
    return TC.build_test_contract(cid, "cand", "batch", _TARGET, [
        TC.build_check("p", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET,
                       expected_target_sha256=_sha(want), required=True),
        TC.build_check("d", TC.CHECK_TYPE_DIFF_SCOPE, expected_diff_paths=[_TARGET], required=True)])


@pytest.fixture
def env(tmp_path):
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    (main / _TARGET).write_bytes(_A0)
    (main / _S1).write_bytes(_A1)
    _git(main, "init", "-q"); _git(main, "config", "user.email", "t@e.com")
    _git(main, "config", "user.name", "t"); _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", _TARGET, _S1); _git(main, "commit", "-q", "-m", "seed")
    base = _git(main, "rev-parse", "HEAD")
    s = {k: tmp_path / k for k in ("ledger", "selector", "exec", "pec", "kxpre", "kxpost",
                                   "tcr", "sar", "sre", "rbk", "missions", "holds",
                                   "decisions", "snap")}
    wt = (tmp_path / "wt").resolve()
    cr = WU.create_isolated_work_unit(repo_root=main, base_sha=base, branch_name="gbr",
                                      worktree_path=wt, work_unit_id="wu-g-0001")
    assert cr["status"] == WU.WORK_UNIT_CREATED
    return {"main": main, "base": base, "stores": s, "wu": cr["work_unit"], "wt": wt,
            "tmp": tmp_path}


def _seq_kw(env):
    s = env["stores"]
    return dict(work_unit=env["wu"], ledger_dir=s["ledger"], selector_dir=s["selector"],
                execution_dir=s["exec"], pre_execution_context_dir=s["pec"],
                kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
                test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
                sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"],
                mission_store_dir=s["missions"], hold_store_dir=s["holds"],
                decision_store_dir=s["decisions"], snapshot_store_dir=s["snap"])


def _drv_kw(env):
    s = env["stores"]
    return dict(execution_dir=s["exec"], pre_execution_context_dir=s["pec"],
                selector_dir=s["selector"], ledger_dir=s["ledger"],
                kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
                test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
                sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"],
                repo_root=env["wt"])


def _setup(env, *, bind_hma=True, tag="a", want=_A1):
    g = M.create_bounded_mission(
        objective=f"seam-repair-{tag}", repository_identity="repo://g",
        canonical_base_sha=env["base"], branch_name="gbr",
        worktree_path=str(env["wt"]), main_worktree_path=str(env["main"].resolve()),
        scope={"allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
               "allowed_target_paths": [_TARGET], "max_actions": 1, "max_retries_per_action": 0},
        human_mandate_reference=f"hmr-{tag}", mission_store_dir=env["stores"]["missions"])
    mid = g["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = M.bind_mission_plan(mission_id=mid, actions=[
        {"ordinal": 0, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S1, "test_contract": _contract("cA", want),
         "dependency_ordinals": []}], mission_store_dir=env["stores"]["missions"])
    pid = r["plan_id"]
    hid = None
    if bind_hma:
        br = INT.bind_mission_authority_from_human_reference(
            mission_id=mid, human_authorization_reference="TEST_HUMAN_MISSION_AUTH",
            mission_store_dir=env["stores"]["missions"])
        assert br["status"] == INT.MISSION_AUTHORITY_BOUND
        hid = br["human_mission_authorization_id"]
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert c1["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL, c1
    pe = M.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"])["last_prepared_evidence"]
    return dict(mid=mid, pid=pid, hid=hid, beid=pe["batch_execution_id"],
                cheid=pe["child_execution_id"], eah=c1["execution_authority_hash"])


def _run_stage4(env, d):
    return DRV.execute_governed_remediation(
        d["beid"], d["cheid"], None, None,
        authority_mode="BOUNDED_MISSION_AUTHORITY",
        mission_id=d["mid"], mission_store_dir=env["stores"]["missions"], **_drv_kw(env))


# ══════════════════════════════════════════════════════════════════════════
#  STATIQUE / GEL
# ══════════════════════════════════════════════════════════════════════════

def test_frozen_files_clean():
    r = subprocess.run(["git", "status", "--porcelain",
                        "proofs/lean/",
                        "scripts/obsidia_mission_sequencer_v0.py",
                        "scripts/obsidia_governed_rollback_v0.py",
                        "scripts/obsidia_kx108_evidence_adapter.py",
                        "scripts/obsidia_post_execution_disposition_v0.py",
                        "scripts/obsidia_mission_authority_integration_v0.py"],
                       cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"frozen file changed: {r.stdout}"


def test_4e_idempotence_key_preserved():
    src = (_SCRIPTS / "obsidia_bounded_mission_v0.py").read_text(encoding="utf-8")
    assert '_WITNESS_IDEMPOTENCE_KEY_FIELDS = (' in src
    for f in ("ordinal", "daaw_id", "daaw_record_hash",
              "execution_authority_hash", "action_base_sha", "hma_id"):
        assert f'"{f}"' in src


def test_revocation_writer_uses_shared_lock_static():
    src = (_SCRIPTS / "obsidia_mission_authority_v0.py").read_text(encoding="utf-8")
    assert "obsidia_mission_authority_freshness_lock_v0" in src
    assert "mission_authority_lock(" in src


def test_c2_stage4_mutation_uses_shared_lock_static():
    src = (_SCRIPTS / "obsidia_governed_apply_v0.py").read_text(encoding="utf-8")
    assert "obsidia_mission_authority_freshness_lock_v0" in src
    # le verrou entoure la re-vérif finale + atomic_replace_with_bytes
    i_lock = src.index("mission_authority_lock(")
    i_verify = src.index("verify_derived_approval_with_context", i_lock)
    i_write = src.index("atomic_replace_with_bytes", i_verify)
    assert i_lock < i_verify < i_write


def test_validate_approval_has_context_param():
    import inspect
    assert "derived_authority_context" in inspect.signature(E._validate_approval).parameters
    assert "embedded_authority_locator" in E._DERIVED_APPROVAL_EXTRA_BOUND_FIELDS


# ══════════════════════════════════════════════════════════════════════════
#  FIX A — l'approbation dérivée FORGÉE ne passe plus
# ══════════════════════════════════════════════════════════════════════════

_FORGED_ENV = {
    "batch_execution_id": "be-REAL", "batch_id": "batch-REAL",
    "batch_hash": "b" * 64, "candidate_scope_hash": "c" * 64,
    "execution_authority_hash": "e" * 64,
}


def _forged_derived(locator=None):
    rec = {
        "approval_id": "appr-" + "0" * 32,
        "approval_schema_version": E.SCHEMA_VERSION,
        "created_at": "2026-08-28T00:00:00+00:00",
        "batch_execution_id": _FORGED_ENV["batch_execution_id"],
        "batch_id": _FORGED_ENV["batch_id"], "batch_hash": _FORGED_ENV["batch_hash"],
        "candidate_scope_hash": _FORGED_ENV["candidate_scope_hash"],
        "execution_authority_hash": _FORGED_ENV["execution_authority_hash"],
        "approved_by": "HUMAN_MISSION_AUTHORITY_DERIVED",
        "approval_status": E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": E.DECISION_AUTHORITY,
        "human_authorization_reference": "ATTACKER",
        "approval_kind": "DERIVED_MISSION_AUTHORITY_EVIDENCE_V0",
        "derived_mission_approval_evidence_id": "dmae-" + "f" * 32,
    }
    if locator is not None:
        rec["embedded_authority_locator"] = locator
    rec["approval_record_hash"] = E.compute_approval_record_hash(rec)
    return rec


def test_forged_derived_no_locator_fail_closed():
    f = _forged_derived(locator=None)
    ok_s, _ = E.verify_approval_artifact(f)
    ok_v, why = E._validate_approval(f, _FORGED_ENV)
    assert ok_v is False
    assert "DERIVED_APPROVAL_REQUIRES_CANONICAL_CONTEXT" in why or "embedded_authority_locator" in why
    assert ok_s is False  # champ lié manquant


def test_forged_derived_bogus_locator_fail_closed(tmp_path):
    loc = {"context_domain_tag": "x", "is_authority": False, "requires_canonical_reload": True,
           "mission_id": "mid-bogus", "mission_store_dir": str(tmp_path / "nope"),
           "execution_dir": str(tmp_path / "nope2"),
           "derived_mission_approval_evidence_id": "dmae-" + "f" * 32,
           "batch_execution_id": _FORGED_ENV["batch_execution_id"],
           "child_execution_id": "ch-bogus", "authority_lock_root": str(tmp_path / "lk")}
    f = _forged_derived(locator=loc)
    ok_v, why = E._validate_approval(f, _FORGED_ENV)
    assert ok_v is False
    assert why.startswith("DERIVED_APPROVAL_CANONICAL_BINDING_FAILED")


def test_real_dmae_forged_approval_substitution_fail_closed(env):
    d = _setup(env, tag="sub")
    bd = PADP.build_derived_mission_approval_evidence(
        mission_id=d["mid"], batch_execution_id=d["beid"], child_execution_id=d["cheid"],
        execution_dir=env["stores"]["exec"], mission_store_dir=env["stores"]["missions"])
    assert bd["status"] == PADP.DMAE_BUILT
    good = dict(bd["approval_record"])
    envelope = E._load_execution(d["beid"], env["stores"]["exec"])
    # sanity : l'approbation légitime passe
    assert E._validate_approval(good, envelope)[0] is True
    # approbation contrefaite : VRAI dmae_id + locator, mais approval_id trafiqué
    bad = dict(good)
    bad["approval_id"] = "appr-" + "9" * 32
    bad["approval_record_hash"] = E.compute_approval_record_hash(bad)
    ok_v, why = E._validate_approval(bad, envelope)
    assert ok_v is False and "APPROVAL_ID_NOT_DERIVED_FROM_DMAE" in why
    # EAH trafiqué
    bad2 = dict(good)
    bad2["execution_authority_hash"] = "a" * 64
    bad2["approval_record_hash"] = E.compute_approval_record_hash(bad2)
    ok_v2, _ = E._validate_approval(bad2, envelope)
    assert ok_v2 is False
    # locator retiré -> échec fermé
    bad3 = {k: v for k, v in good.items() if k != "embedded_authority_locator"}
    bad3["approval_record_hash"] = E.compute_approval_record_hash(bad3)
    ok_v3, why3 = E._validate_approval(bad3, envelope)
    assert ok_v3 is False


def test_historical_validate_approval_unchanged(env):
    # approbation historique approved_by=HUMAN : aucun paramètre, aucun champ additif,
    # hash inchangé, validation identique.
    d = _setup(env, bind_hma=False, tag="hist")
    r = DRV.execute_governed_remediation(
        d["beid"], d["cheid"], d["eah"], "human-eah-0", **_drv_kw(env))
    assert r["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, r
    appr = E.load_approval_artifact(r["approval_id"], execution_dir=env["stores"]["exec"])
    assert appr["approved_by"] == "HUMAN"
    assert "approval_kind" not in appr and "embedded_authority_locator" not in appr
    # hash recomputé sur les seuls champs historiques
    h_now = E.compute_approval_record_hash({k: v for k, v in appr.items()
                                            if k != "approval_record_hash"})
    assert h_now == appr["approval_record_hash"]
    ok_v, _ = E._validate_approval(appr, E._load_execution(d["beid"], env["stores"]["exec"]))
    assert ok_v is True


def test_forged_derived_cannot_reach_kx_pre(env):
    d = _setup(env, tag="kxpre")
    f = _forged_derived(locator=None)
    f["batch_execution_id"] = d["beid"]
    f["approval_record_hash"] = E.compute_approval_record_hash(f)
    E.store_approval_artifact(f, execution_dir=env["stores"]["exec"])
    tr = PRE.translate_pre_execution_evidence_to_tooling_build_state(
        d["beid"], d["cheid"], f["approval_id"],
        execution_dir=env["stores"]["exec"],
        pre_execution_context_dir=env["stores"]["pec"], repo_root=env["wt"])
    assert tr["status"] == PRE.STATUS_NOT_READY


def test_forged_derived_cannot_reach_governed_apply(env):
    d = _setup(env, tag="capply")
    f = _forged_derived(locator=None)
    f["batch_execution_id"] = d["beid"]
    f["approval_record_hash"] = E.compute_approval_record_hash(f)
    E.store_approval_artifact(f, execution_dir=env["stores"]["exec"])
    r = GA.run_governed_content_apply(
        d["beid"], d["cheid"], f["approval_id"], "kxpre-nonexistent",
        execution_dir=env["stores"]["exec"], pre_execution_context_dir=env["stores"]["pec"],
        kx108_decision_dir=env["stores"]["kxpre"], post_decision_store_dir=env["stores"]["kxpost"],
        selector_dir=env["stores"]["selector"], ledger_dir=env["stores"]["ledger"],
        test_contract_results_dir=env["stores"]["tcr"], sealed_receipt_dir=env["stores"]["sar"],
        sealed_rollback_evidence_dir=env["stores"]["sre"], rollback_result_dir=env["stores"]["rbk"],
        repo_root=env["wt"])
    assert r["status"] == GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION
    assert (env["wt"] / _TARGET).read_bytes() == _A0


# ══════════════════════════════════════════════════════════════════════════
#  FIX A — positif inchangé + veto KX
# ══════════════════════════════════════════════════════════════════════════

def test_real_stage4_positive_keep(env):
    d = _setup(env, tag="pos")
    assert (env["wt"] / _TARGET).read_bytes() == _A0
    r = _run_stage4(env, d)
    assert r["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, r
    assert r["kx108_pre_gate"] == "ALLOW"
    assert r.get("kx108_post_gate") == "ALLOW"
    assert r["derived_mission_approval_evidence_id"].startswith("dmae-")
    assert (env["wt"] / _TARGET).read_bytes() == _A1
    appr = E.load_approval_artifact(r["approval_id"], execution_dir=env["stores"]["exec"])
    assert appr["approved_by"] == "HUMAN_MISSION_AUTHORITY_DERIVED"
    assert appr["human_authorization_reference"] == "TEST_HUMAN_MISSION_AUTH"


def test_stage4_kx_veto_no_mutation(env, monkeypatch):
    d = _setup(env, tag="veto")
    real = DS.run_and_persist_kx108_pre_execution_decision

    def _veto(kwargs, ctx, *, store_dir):
        out = real(kwargs, ctx, store_dir=store_dir)
        if out.get("record"):
            out["record"] = dict(out["record"]); out["record"]["x108_gate"] = "HOLD"
        return out
    monkeypatch.setattr(DS, "run_and_persist_kx108_pre_execution_decision", _veto)
    r = _run_stage4(env, d)
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert "KX108_PRE_GATE_NOT_ALLOW" in r["reason"]
    assert (env["wt"] / _TARGET).read_bytes() == _A0


# ══════════════════════════════════════════════════════════════════════════
#  FIX B — primitive de verrou inter-processus
# ══════════════════════════════════════════════════════════════════════════

def test_lock_mutual_exclusion(tmp_path):
    root = tmp_path / "lk"
    with LK.mission_authority_lock("mid-x", lock_root=root, timeout_s=5):
        with pytest.raises(LK.MissionAuthorityLockTimeout):
            with LK.mission_authority_lock("mid-x", lock_root=root, timeout_s=1):
                pass
    # relâché : réacquisition immédiate OK
    with LK.mission_authority_lock("mid-x", lock_root=root, timeout_s=2):
        pass


def test_lock_released_on_exception(tmp_path):
    root = tmp_path / "lk"
    with pytest.raises(RuntimeError):
        with LK.mission_authority_lock("mid-y", lock_root=root, timeout_s=2):
            raise RuntimeError("boom")
    with LK.mission_authority_lock("mid-y", lock_root=root, timeout_s=2):
        pass


def test_lock_crash_releases(tmp_path):
    root = tmp_path / "lk"
    helper = tmp_path / "hold_and_die.py"
    helper.write_text(textwrap.dedent(f"""
        import sys, os, time
        sys.path.insert(0, r"{_SCRIPTS}")
        import obsidia_mission_authority_freshness_lock_v0 as LK
        cm = LK.mission_authority_lock("mid-crash", lock_root=r"{root}", timeout_s=5)
        cm.__enter__()
        open(r"{tmp_path / 'held'}", "w").close()
        time.sleep(30)
    """), encoding="utf-8")
    proc = subprocess.Popen([sys.executable, str(helper)])
    try:
        for _ in range(100):
            if (tmp_path / "held").exists():
                break
            time.sleep(0.05)
        assert (tmp_path / "held").exists()
        with pytest.raises(LK.MissionAuthorityLockTimeout):
            with LK.mission_authority_lock("mid-crash", lock_root=root, timeout_s=1):
                pass
        proc.kill(); proc.wait(timeout=10)
        # le SE a libéré le verrou à la mort du processus
        with LK.mission_authority_lock("mid-crash", lock_root=root, timeout_s=5):
            pass
    finally:
        if proc.poll() is None:
            proc.kill()


# ══════════════════════════════════════════════════════════════════════════
#  FIX B — linéarisation révocation ↔ mutation
# ══════════════════════════════════════════════════════════════════════════

def test_revocation_first_no_mutation(env):
    d = _setup(env, tag="revfirst")
    hma = MA.load_human_mission_authorization(d["mid"], d["hid"], env["stores"]["missions"])
    rv = MA.record_mission_authority_revocation(
        mission_id=d["mid"], hma_id=hma["human_mission_authorization_id"],
        hma_record_hash=hma["hma_record_hash"], revocation_reference="HUMAN_STOP",
        mission_store_dir=env["stores"]["missions"])
    assert rv["status"] == MA.REVOCATION_RECORDED
    r = _run_stage4(env, d)
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert "HMA_REVOKED" in r["reason"] or "HMA_INVALID" in r["reason"]
    assert (env["wt"] / _TARGET).read_bytes() == _A0


def test_executor_first_mutation_linearized_before_revocation(env, monkeypatch, tmp_path):
    """Exécuteur : acquiert le verrou, se met en pause JUSTE avant l'écriture
    physique (verrou tenu). Second PROCESSUS : tente une révocation canonique →
    doit ÉCHOUER sur timeout de verrou tant que l'exécuteur tient. Puis
    l'exécuteur reprend et écrit ; la révocation ne peut committer qu'APRÈS."""
    d = _setup(env, tag="execfirst")
    pre_marker = tmp_path / "pre_write"
    resume = tmp_path / "resume"
    real_write = CA.atomic_replace_with_bytes

    def _paused_write(*a, **kw):
        pre_marker.write_text("x")
        for _ in range(400):
            if resume.exists():
                break
            time.sleep(0.05)
        return real_write(*a, **kw)
    monkeypatch.setattr(CA, "atomic_replace_with_bytes", _paused_write)

    revoke_helper = tmp_path / "revoke.py"
    revoke_helper.write_text(textwrap.dedent(f"""
        import sys, json
        sys.path.insert(0, r"{_SCRIPTS}")
        import obsidia_mission_authority_v0 as MA
        hma = MA.load_human_mission_authorization(
            r"{d['mid']}", r"{d['hid']}", r"{env['stores']['missions']}")
        out = MA.record_mission_authority_revocation(
            mission_id=r"{d['mid']}", hma_id=hma["human_mission_authorization_id"],
            hma_record_hash=hma["hma_record_hash"], revocation_reference="CONCURRENT_STOP",
            mission_store_dir=r"{env['stores']['missions']}",
            authority_lock_timeout_s=2.0)
        print(json.dumps(out))
    """), encoding="utf-8")

    import threading
    box = {}

    def _drive():
        box["r"] = _run_stage4(env, d)
    th = threading.Thread(target=_drive)
    th.start()
    try:
        for _ in range(400):
            if pre_marker.exists():
                break
            time.sleep(0.05)
        assert pre_marker.exists(), "executor did not reach pre-write pause"
        # exécuteur tient le verrou -> la révocation concurrente doit ÉCHOUER
        p = subprocess.run([sys.executable, str(revoke_helper)],
                           capture_output=True, text=True, timeout=30)
        blocked = json.loads(p.stdout.strip().splitlines()[-1])
        assert blocked["status"] == MA.REVOCATION_REJECTED
        assert blocked["reason"] == "AUTHORITY_LOCK_TIMEOUT"
        assert MA.list_mission_authority_revocations(d["mid"], env["stores"]["missions"]) == []
        # laisse l'exécuteur finir
        resume.write_text("go")
        th.join(timeout=60)
    finally:
        resume.write_text("go")
        th.join(timeout=60)

    r = box["r"]
    assert r["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, r
    assert (env["wt"] / _TARGET).read_bytes() == _A1     # mutation linéarisée
    # révocation possible seulement APRÈS que l'exécuteur a relâché
    p2 = subprocess.run([sys.executable, str(revoke_helper)],
                        capture_output=True, text=True, timeout=30)
    after = json.loads(p2.stdout.strip().splitlines()[-1])
    assert after["status"] == MA.REVOCATION_RECORDED
    # ordre sérialisé : mutation AVANT commit de révocation
    assert len(MA.list_mission_authority_revocations(d["mid"], env["stores"]["missions"])) == 1


def test_original_race_closed(env, monkeypatch, tmp_path):
    """Reproduction de l'expérience d'audit : injection d'une révocation
    concurrente PENDANT C2. Résultat interdit = révocation committée AVANT la
    mutation ET cible mutée."""
    d = _setup(env, tag="origrace")
    # injection au moment du sceau SRE (dans run_governed_content_apply, avant write)
    import obsidia_sealed_evidence_v0 as SEV
    real_sre = SEV.build_sealed_rollback_evidence
    state = {"rev_before_write": None}

    def _spy_sre(*a, **kw):
        hma = MA.load_human_mission_authorization(d["mid"], d["hid"], env["stores"]["missions"])
        rv = MA.record_mission_authority_revocation(
            mission_id=d["mid"], hma_id=hma["human_mission_authorization_id"],
            hma_record_hash=hma["hma_record_hash"], revocation_reference="RACE",
            mission_store_dir=env["stores"]["missions"], authority_lock_timeout_s=3.0)
        state["rev_before_write"] = rv["status"]
        return real_sre(*a, **kw)
    monkeypatch.setattr(SEV, "build_sealed_rollback_evidence", _spy_sre)

    r = _run_stage4(env, d)
    mutated = (env["wt"] / _TARGET).read_bytes() == _A1
    revs = MA.list_mission_authority_revocations(d["mid"], env["stores"]["missions"])
    # la révocation à ce point s'exécute AVANT que l'exécuteur ait pris le verrou
    # (le spy est en amont du bloc verrouillé) -> elle committe, puis la re-vérif
    # sous verrou la voit -> AUCUNE mutation.
    assert state["rev_before_write"] == MA.REVOCATION_RECORDED
    assert len(revs) == 1
    assert mutated is False
    assert r["status"] in (DRV.PRE_EXECUTION_REJECTED,
                           GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION)
    # INTERDIT : révocation committée avant la mutation ET cible mutée
    assert not (len(revs) == 1 and mutated)


# ══════════════════════════════════════════════════════════════════════════
#  HISTORIQUE / DEADLOCK
# ══════════════════════════════════════════════════════════════════════════

def test_historical_path_uses_no_lock(env):
    d = _setup(env, bind_hma=False, tag="nolock")
    r = DRV.execute_governed_remediation(
        d["beid"], d["cheid"], d["eah"], "human-eah-0", **_drv_kw(env))
    assert r["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    assert r["authority_mode"] == "PER_ACTION_HUMAN_EAH"
    locks = list(env["tmp"].rglob("mission-authority-*.lock"))
    assert locks == [], f"historical path created a lock file: {locks}"


def test_deadlock_exception_in_c2_releases_lock(env, monkeypatch):
    # Exception pendant l'écriture C2 (SOUS verrou) -> le verrou est relâché en
    # finally : une révocation ultérieure sur la même mission l'acquiert sans
    # timeout. Pas de deadlock.
    d = _setup(env, tag="dlx")

    def _raise(*a, **kw):
        raise OSError("disk gone")
    monkeypatch.setattr(CA, "atomic_replace_with_bytes", _raise)
    r = _run_stage4(env, d)
    assert r["status"] in (
        GA.GOVERNED_REMEDIATION_APPLY_STATE_UNKNOWN_QUARANTINE,
        GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION,
        DRV.PRE_EXECUTION_REJECTED,
        "GOVERNED_REMEDIATION_ROLLBACK_FAILED_QUARANTINE")
    monkeypatch.undo()
    hma = MA.load_human_mission_authorization(d["mid"], d["hid"], env["stores"]["missions"])
    rv = MA.record_mission_authority_revocation(
        mission_id=d["mid"], hma_id=hma["human_mission_authorization_id"],
        hma_record_hash=hma["hma_record_hash"], revocation_reference="AFTER",
        mission_store_dir=env["stores"]["missions"], authority_lock_timeout_s=3.0)
    assert rv["status"] == MA.REVOCATION_RECORDED   # verrou libre -> pas de deadlock


def test_deadlock_normal_revocation_then_reacquire(env):
    # Révocation normale : verrou pris puis relâché ; ré-acquisition immédiate OK.
    d = _setup(env, tag="dln")
    hma = MA.load_human_mission_authorization(d["mid"], d["hid"], env["stores"]["missions"])
    for ref in ("R1", "R2"):   # 2e = idempotent, ré-acquiert le verrou sans souci
        out = MA.record_mission_authority_revocation(
            mission_id=d["mid"], hma_id=hma["human_mission_authorization_id"],
            hma_record_hash=hma["hma_record_hash"], revocation_reference=ref,
            mission_store_dir=env["stores"]["missions"], authority_lock_timeout_s=3.0)
        assert out["status"] == MA.REVOCATION_RECORDED
