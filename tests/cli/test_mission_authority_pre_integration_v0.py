"""
tests/cli/test_mission_authority_pre_integration_v0.py
=====================================================
STAGE 4F — le rail PRE accepte une `DerivedMissionApprovalEvidence` comme
ÉVIDENCE D'AUTORISATION HUMAINE dans le mode `BOUNDED_MISSION_AUTHORITY`,
KX108_PRE conservant son veto souverain indépendant.

Preuve : vraie action gouvernée A exécutée avec 1 HMA humaine, 1 DAAW
dérivé, 0 approbation EAH humaine par action, 1 DMAE, 1 KX108_PRE ALLOW,
1 governed apply, 1 KX108_POST ALLOW, KEEP. Puis : le mode historique est
byte-compatible ; KX veto -> aucune mutation ; HMA révoquée avant mutation
-> aucune mutation.
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
import obsidia_mission_authority_pre_adapter_v0 as PADP # noqa: E402
import obsidia_governed_execution_driver_v0 as DRV      # noqa: E402
import obsidia_kx108_decision_store as DS               # noqa: E402
import obsidia_batch_execution as E                     # noqa: E402

_TARGET = "periphery/xdomain/f_target_v0.txt"
_S1 = "periphery/xdomain/f_src_1.txt"
_A0, _A1 = (b"F\nstate: 0\n", b"F\nstate: 1\n")


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
    (main / _S1).write_bytes(_A1)
    _git(main, "init", "-q"); _git(main, "config", "user.email", "t@e.com")
    _git(main, "config", "user.name", "t"); _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", _TARGET, _S1); _git(main, "commit", "-q", "-m", "seed")
    base = _git(main, "rev-parse", "HEAD")
    s = {k: tmp_path / k for k in ("ledger", "selector", "exec", "pec", "kxpre", "kxpost",
                                   "tcr", "sar", "sre", "rbk", "missions", "holds",
                                   "decisions", "snap")}
    wt = (tmp_path / "wt").resolve()
    cr = WU.create_isolated_work_unit(repo_root=main, base_sha=base, branch_name="fbr",
                                      worktree_path=wt, work_unit_id="wu-f-0001")
    assert cr["status"] == WU.WORK_UNIT_CREATED
    return {"main": main, "base": base, "stores": s, "wu": cr["work_unit"], "wt": wt}


def _contract(cid):
    return TC.build_test_contract(cid, "cand", "batch", _TARGET, [
        TC.build_check("p", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET,
                       expected_target_sha256=_sha(_A1), required=True),
        TC.build_check("d", TC.CHECK_TYPE_DIFF_SCOPE, expected_diff_paths=[_TARGET], required=True)])


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


def _proj(env, mid):
    return M.project_mission(mission_id=mid, mission_store_dir=env["stores"]["missions"],
                             hold_store_dir=env["stores"]["holds"])


def _setup(env, *, bind_hma=True, tag="a"):
    g = M.create_bounded_mission(
        objective=f"stage4f-{tag}", repository_identity="repo://f",
        canonical_base_sha=env["base"], branch_name="fbr",
        worktree_path=str(env["wt"]), main_worktree_path=str(env["main"].resolve()),
        scope={"allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
               "allowed_target_paths": [_TARGET], "max_actions": 1, "max_retries_per_action": 0},
        human_mandate_reference=f"hmr-{tag}", mission_store_dir=env["stores"]["missions"])
    mid = g["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    r = M.bind_mission_plan(mission_id=mid, actions=[
        {"ordinal": 0, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S1, "test_contract": _contract("cA"),
         "dependency_ordinals": []}], mission_store_dir=env["stores"]["missions"])
    assert r["status"] == M.STATUS_PLAN_BOUND
    pid = r["plan_id"]
    hma_ref = None
    if bind_hma:
        br = INT.bind_mission_authority_from_human_reference(
            mission_id=mid, human_authorization_reference="TEST_HUMAN_MISSION_AUTH",
            mission_store_dir=env["stores"]["missions"])
        assert br["status"] == INT.MISSION_AUTHORITY_BOUND
        hma_ref = br["human_mission_authorization_id"]
    c1 = SEQ.advance_bounded_mission(mission_id=mid, plan_id=pid, **_seq_kw(env))
    assert c1["status"] == SEQ.MISSION_AWAITING_HUMAN_EAH_APPROVAL, c1
    pe = _proj(env, mid)["last_prepared_evidence"]
    return dict(mid=mid, pid=pid, hma_id=hma_ref, c1=c1,
                beid=pe["batch_execution_id"], cheid=pe["child_execution_id"],
                eah=c1["execution_authority_hash"])


# ══════════════════════════════════════════════════════════════════════════
#  Statique / bornes
# ══════════════════════════════════════════════════════════════════════════

def test_default_mode_and_allowed_approved_by():
    assert DRV.DEFAULT_AUTHORITY_MODE == "PER_ACTION_HUMAN_EAH"
    assert E.APPROVED_BY_ALLOWED_VALUES == ("HUMAN", "HUMAN_MISSION_AUTHORITY_DERIVED")


def test_adapter_no_bypass_static():
    src = Path(PADP.__file__).read_text(encoding="utf-8")
    for banned in ("run_governed_content_apply(", "run_governed_rollback(",
                   "run_and_persist_kx108", "GuardX108", ".write_bytes(", '"commit"',
                   '"add"', '"push"', "atomic_replace_with_bytes"):
        assert banned not in src, banned
    # EAH réutilisé, jamais réimplémenté
    assert "compute_execution_authority_hash" in src
    assert "def compute_execution_authority_hash" not in src


def test_formal_files_frozen():
    # Le modèle formel Lean reste gelé. (`obsidia_mission_authority_v0.py` est
    # modifié par la réparation 4F — verrou de linéarisation partagé — donc plus
    # gelé ; la sémantique DAAW/HMA/révocation y est inchangée, cf.
    # test_mission_authority_v0.py.)
    r = subprocess.run(["git", "status", "--porcelain",
                        "proofs/lean/Obsidia/MissionAuthority/"],
                       cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"frozen file changed: {r.stdout}"


# ══════════════════════════════════════════════════════════════════════════
#  DMAE build — positifs / négatifs
# ══════════════════════════════════════════════════════════════════════════

def test_dmae_build_positive_non_sovereign(env):
    d = _setup(env)
    bd = PADP.build_derived_mission_approval_evidence(
        mission_id=d["mid"], batch_execution_id=d["beid"], child_execution_id=d["cheid"],
        execution_dir=env["stores"]["exec"], mission_store_dir=env["stores"]["missions"])
    assert bd["status"] == PADP.DMAE_BUILT, bd
    assert bd["dmae"]["sovereignty"] == "NON_SOVEREIGN"
    assert bd["dmae"]["is_execution_authority"] is False
    assert bd["dmae"]["bypasses_kx_pre"] is False
    assert bd["approval_record"]["approved_by"] == "HUMAN_MISSION_AUTHORITY_DERIVED"
    assert bd["approval_record"]["approval_kind"] == "DERIVED_MISSION_AUTHORITY_EVIDENCE_V0"
    # racine humaine préservée
    assert bd["approval_record"]["human_authorization_reference"] == "TEST_HUMAN_MISSION_AUTH"
    ok, why = PADP.verify_derived_mission_approval_evidence(bd["dmae"])
    assert ok, why
    # write-once
    bd2 = PADP.build_derived_mission_approval_evidence(
        mission_id=d["mid"], batch_execution_id=d["beid"], child_execution_id=d["cheid"],
        execution_dir=env["stores"]["exec"], mission_store_dir=env["stores"]["missions"])
    assert bd2["dmae"]["derived_mission_approval_evidence_id"] == bd["dmae"]["derived_mission_approval_evidence_id"]


def test_dmae_build_no_hma_fail_closed(env):
    d = _setup(env, bind_hma=False)
    bd = PADP.build_derived_mission_approval_evidence(
        mission_id=d["mid"], batch_execution_id=d["beid"], child_execution_id=d["cheid"],
        execution_dir=env["stores"]["exec"], mission_store_dir=env["stores"]["missions"])
    assert bd["status"] == PADP.DMAE_BUILD_REJECTED
    assert bd["reason"] == "NO_MISSION_AUTHORITY_BOUND"


def test_dmae_build_revoked_hma_fail_closed(env):
    d = _setup(env)
    hma = MA.load_human_mission_authorization(d["mid"], d["hma_id"], env["stores"]["missions"])
    MA.record_mission_authority_revocation(
        mission_id=d["mid"], hma_id=hma["human_mission_authorization_id"],
        hma_record_hash=hma["hma_record_hash"], revocation_reference="STOP",
        mission_store_dir=env["stores"]["missions"])
    bd = PADP.build_derived_mission_approval_evidence(
        mission_id=d["mid"], batch_execution_id=d["beid"], child_execution_id=d["cheid"],
        execution_dir=env["stores"]["exec"], mission_store_dir=env["stores"]["missions"])
    assert bd["status"] == PADP.DMAE_BUILD_REJECTED
    assert bd["reason"].startswith("HMA_INVALID:HMA_REVOKED")


# ══════════════════════════════════════════════════════════════════════════
#  VRAIE exécution Stage 4F — action unique
# ══════════════════════════════════════════════════════════════════════════

def test_real_stage4_single_action_positive(env):
    d = _setup(env)
    assert (env["wt"] / _TARGET).read_bytes() == _A0
    r = DRV.execute_governed_remediation(
        d["beid"], d["cheid"], None, None,
        authority_mode="BOUNDED_MISSION_AUTHORITY",
        mission_id=d["mid"], mission_store_dir=env["stores"]["missions"], **_drv_kw(env))
    assert r["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, r
    assert r["authority_mode"] == "BOUNDED_MISSION_AUTHORITY"
    assert r["kx108_pre_gate"] == "ALLOW"
    assert r.get("kx108_post_gate") == "ALLOW"
    assert r["derived_mission_approval_evidence_id"].startswith("dmae-")
    assert (env["wt"] / _TARGET).read_bytes() == _A1     # 1 mutation de cible
    # l'approbation persistée porte approved_by dérivé, racine humaine présente
    appr = E.load_approval_artifact(r["approval_id"], execution_dir=env["stores"]["exec"])
    assert appr["approved_by"] == "HUMAN_MISSION_AUTHORITY_DERIVED"
    assert appr["human_authorization_reference"] == "TEST_HUMAN_MISSION_AUTH"
    ok, why = E._validate_approval(appr, E._load_execution(d["beid"], env["stores"]["exec"]))
    assert ok, why


def test_historical_single_action_unchanged(env):
    d = _setup(env, bind_hma=False, tag="hist")
    r = DRV.execute_governed_remediation(
        d["beid"], d["cheid"], d["eah"], "human-eah-turn-0", **_drv_kw(env))
    assert r["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, r
    assert r["authority_mode"] == "PER_ACTION_HUMAN_EAH"
    assert r["derived_mission_approval_evidence_id"] is None
    appr = E.load_approval_artifact(r["approval_id"], execution_dir=env["stores"]["exec"])
    assert appr["approved_by"] == "HUMAN"
    assert "approval_kind" not in appr           # byte-compatible : aucun champ additif
    assert (env["wt"] / _TARGET).read_bytes() == _A1


# ══════════════════════════════════════════════════════════════════════════
#  No-fallback / mutual exclusivity
# ══════════════════════════════════════════════════════════════════════════

def test_ambiguous_stage4_plus_human_eah_fail_closed(env):
    d = _setup(env)
    r = DRV.execute_governed_remediation(
        d["beid"], d["cheid"], d["eah"], None,
        authority_mode="BOUNDED_MISSION_AUTHORITY",
        mission_id=d["mid"], mission_store_dir=env["stores"]["missions"], **_drv_kw(env))
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"] == "AMBIGUOUS_DUAL_AUTHORITY_INPUT"
    assert (env["wt"] / _TARGET).read_bytes() == _A0


def test_ambiguous_historical_plus_mission_ref_fail_closed(env):
    d = _setup(env)
    r = DRV.execute_governed_remediation(
        d["beid"], d["cheid"], d["eah"], "ref",
        mission_id=d["mid"], mission_store_dir=env["stores"]["missions"], **_drv_kw(env))
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"] == "AMBIGUOUS_DUAL_AUTHORITY_INPUT"


def test_stage4_invalid_does_not_autofallback_to_historical(env):
    d = _setup(env, bind_hma=False)     # pas d'HMA -> Stage4 doit ÉCHOUER, pas basculer
    r = DRV.execute_governed_remediation(
        d["beid"], d["cheid"], None, None,
        authority_mode="BOUNDED_MISSION_AUTHORITY",
        mission_id=d["mid"], mission_store_dir=env["stores"]["missions"], **_drv_kw(env))
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"].startswith("DERIVED_MISSION_APPROVAL_REJECTED")
    assert (env["wt"] / _TARGET).read_bytes() == _A0    # aucune mutation, aucun repli


# ══════════════════════════════════════════════════════════════════════════
#  KX108_PRE garde son veto indépendant
# ══════════════════════════════════════════════════════════════════════════

def test_valid_mission_authority_plus_kx_veto_no_mutation(env, monkeypatch):
    d = _setup(env)
    real = DS.run_and_persist_kx108_pre_execution_decision

    def _veto(kwargs, ctx, *, store_dir):
        out = real(kwargs, ctx, store_dir=store_dir)
        if out.get("record"):
            out["record"] = dict(out["record"]); out["record"]["x108_gate"] = "HOLD"
        return out
    monkeypatch.setattr(DS, "run_and_persist_kx108_pre_execution_decision", _veto)
    r = DRV.execute_governed_remediation(
        d["beid"], d["cheid"], None, None,
        authority_mode="BOUNDED_MISSION_AUTHORITY",
        mission_id=d["mid"], mission_store_dir=env["stores"]["missions"], **_drv_kw(env))
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"].startswith("KX108_PRE_GATE_NOT_ALLOW")
    assert (env["wt"] / _TARGET).read_bytes() == _A0    # HMA+DAAW+DMAE valides mais KX veto -> 0 mutation


# ══════════════════════════════════════════════════════════════════════════
#  Fraîcheur de révocation — fenêtre fermée à la frontière driver
# ══════════════════════════════════════════════════════════════════════════

def test_revoked_between_dmae_build_and_mutation_no_mutation(env, monkeypatch):
    d = _setup(env)
    real_build = PADP.build_derived_mission_approval_evidence

    def _build_then_revoke(**kw):
        bd = real_build(**kw)
        # simule une révocation humaine survenant APRÈS la construction de la DMAE
        # mais AVANT la mutation : la re-vérification de fraîcheur doit la capter.
        hma = MA.load_human_mission_authorization(d["mid"], d["hma_id"], env["stores"]["missions"])
        MA.record_mission_authority_revocation(
            mission_id=d["mid"], hma_id=hma["human_mission_authorization_id"],
            hma_record_hash=hma["hma_record_hash"], revocation_reference="HUMAN_STOP_MIDFLIGHT",
            mission_store_dir=env["stores"]["missions"])
        return bd
    monkeypatch.setattr(PADP, "build_derived_mission_approval_evidence", _build_then_revoke)
    r = DRV.execute_governed_remediation(
        d["beid"], d["cheid"], None, None,
        authority_mode="BOUNDED_MISSION_AUTHORITY",
        mission_id=d["mid"], mission_store_dir=env["stores"]["missions"], **_drv_kw(env))
    # Après la réparation 4F, la révocation est captée par le premier gate
    # canonique pré-mutation atteint (adaptateur d'évidence KX108_PRE, 4bis du
    # driver, ou re-vérif sous verrou C2) — toujours PRE_EXECUTION_REJECTED,
    # toujours HMA_REVOKED, toujours 0 mutation.
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert "HMA_REVOKED" in r["reason"] or "HMA_INVALID" in r["reason"]
    assert (env["wt"] / _TARGET).read_bytes() == _A0     # révoquée avant mutation -> aucune mutation


def test_fresh_check_passes_when_nothing_changed(env):
    d = _setup(env)
    bd = PADP.build_derived_mission_approval_evidence(
        mission_id=d["mid"], batch_execution_id=d["beid"], child_execution_id=d["cheid"],
        execution_dir=env["stores"]["exec"], mission_store_dir=env["stores"]["missions"])
    fr = PADP.verify_derived_mission_approval_evidence_fresh(
        mission_id=d["mid"], derived_mission_approval_evidence_id=bd["derived_mission_approval_evidence_id"],
        batch_execution_id=d["beid"], child_execution_id=d["cheid"],
        execution_dir=env["stores"]["exec"], mission_store_dir=env["stores"]["missions"])
    assert fr["status"] == PADP.DMAE_FRESH


def test_mission_not_action_prepared_dmae_build_fail_closed(env):
    # plan lié mais mission NON avancée -> aucune évidence préparée -> _verify_chain
    # refuse de construire une DMAE (fail-closed sur l'état de mission).
    g = M.create_bounded_mission(
        objective="stage4f-noprep", repository_identity="repo://f",
        canonical_base_sha=env["base"], branch_name="fbr",
        worktree_path=str(env["wt"]), main_worktree_path=str(env["main"].resolve()),
        scope={"allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
               "allowed_target_paths": [_TARGET], "max_actions": 1, "max_retries_per_action": 0},
        human_mandate_reference="hmr-noprep", mission_store_dir=env["stores"]["missions"])
    mid = g["mission_id"]
    M.bind_work_unit(mission_id=mid, work_unit=env["wu"], mission_store_dir=env["stores"]["missions"])
    M.bind_mission_plan(mission_id=mid, actions=[
        {"ordinal": 0, "target_path": _TARGET, "source_git_commit": env["base"],
         "source_historical_path": _S1, "test_contract": _contract("cN"),
         "dependency_ordinals": []}], mission_store_dir=env["stores"]["missions"])
    INT.bind_mission_authority_from_human_reference(
        mission_id=mid, human_authorization_reference="TEST_HUMAN_MISSION_AUTH",
        mission_store_dir=env["stores"]["missions"])
    bd = PADP.build_derived_mission_approval_evidence(
        mission_id=mid, batch_execution_id="be-none", child_execution_id="ch-none",
        execution_dir=env["stores"]["exec"], mission_store_dir=env["stores"]["missions"])
    assert bd["status"] == PADP.DMAE_BUILD_REJECTED


# ══════════════════════════════════════════════════════════════════════════
#  Sequencer NON activé en Stage 4F
# ══════════════════════════════════════════════════════════════════════════

def test_sequencer_no_authority_fabrication():
    # Le séquenceur est modifié par Stage 4G (intégration d'exécution mission) mais
    # ne fabrique JAMAIS d'autorité : ni approbation, ni décision KX, ni EAH, ni
    # DAAW/DMAE, ni écriture de cible. Il ne fait QUE composer des appels de haut
    # niveau (execute_mission_action / derive_and_record_action_authority_witness).
    src = (_SCRIPTS / "obsidia_mission_sequencer_v0.py").read_text(encoding="utf-8")
    for banned in ("store_approval_artifact(", "run_and_persist_kx108", "GuardX108",
                   "run_governed_content_apply(", "atomic_replace_with_bytes",
                   "build_derived_mission_approval_evidence(",
                   "compute_execution_authority_hash(", ".write_bytes(",
                   "approved_by", '"commit"'):
        assert banned not in src, banned
    assert "import obsidia_governed_apply_v0" not in src
    assert "import obsidia_mission_authority_v0" not in src
