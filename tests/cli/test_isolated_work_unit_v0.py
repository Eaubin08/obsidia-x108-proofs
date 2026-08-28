"""
tests/cli/test_isolated_work_unit_v0.py
=======================================
MINIMAL_AUTONOMOUS_WORK_WIRING_CHECKPOINT_1

Prouve, sur des dépôts / worktrees / magasins TEMPORAIRES et isolés
(kernel sigma canonique RÉEL pour PRE et POST), que
obsidia_isolated_work_unit_v0 :

  * crée une branche locale + un worktree Git enregistré depuis un
    base_sha explicite, et vérifie les faits Git d'espace de travail ;
  * refuse : branche en conflit, destination non vide, mauvaise
    identité de dépôt / base_sha ;
  * PREPARE est le PREMIER APPELANT RÉEL de prepare_governed_execution
    (ne duplique pas sa logique) et s'arrête à
    PREPARED_AWAITING_HUMAN_APPROVAL en révélant l'EAH exact — sans
    HumanApproval, sans KX108, sans mutation ;
  * un mauvais EAH humain est rejeté AVANT toute mutation ;
  * l'EAH exact atteint le driver d'exécution existant (KEEP réel) ;
  * une dérive entre prepare et execute échoue fermé (driver + PEC) ;
  * aucune opération Git distante, aucun commit automatique, aucune
    mutation de audit/world_action_bus ;
  * les formes multi-enfant / CREATE / DELETE échouent explicitement.

AUCUNE mutation canonique. AUCUN artefact Event-2 canonique.
"""
from __future__ import annotations

import hashlib
import inspect
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

import obsidia_test_contract as TC                 # noqa: E402
import obsidia_isolated_work_unit_v0 as WU         # noqa: E402
import obsidia_governed_execution_driver_v0 as DRV # noqa: E402
import obsidia_sealed_evidence_v0 as SEV           # noqa: E402
import obsidia_mission_local_snapshot_v0 as LS     # noqa: E402  (Stage 3C — advanced-base proof)

_TARGET_REL = "periphery/xdomain/wu_target_v0.txt"
_SOURCE_REL = "periphery/xdomain/wu_source_v0.txt"
_A = b"ISOLATED_WORK_UNIT_FIXTURE\nstate: BEFORE\n"
_B = b"ISOLATED_WORK_UNIT_FIXTURE\nstate: AFTER_GOVERNED_APPLY\n"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {args}: {r.stderr}"
    return r.stdout.strip()


@pytest.fixture
def repo(tmp_path):
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    (main / _TARGET_REL).write_bytes(_A)
    (main / _SOURCE_REL).write_bytes(_B)
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "t@example.com")
    _git(main, "config", "user.name", "t")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", _TARGET_REL, _SOURCE_REL)
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    stores = {k: tmp_path / k for k in (
        "ledger", "selector", "exec", "pec", "kxpre", "kxpost", "tcr",
        "sar", "sre", "rbk")}
    return {"root": tmp_path, "main": main, "base_sha": base_sha, "stores": stores}


def _create(repo, *, branch="wubr", dest=None, base=None, wid="wu-0001", repo_root=None):
    return WU.create_isolated_work_unit(
        repo_root=repo_root or repo["main"],
        base_sha=base or repo["base_sha"],
        branch_name=branch,
        worktree_path=dest or (repo["root"] / "wt_wubr"),
        work_unit_id=wid,
    )


def _positive_contract() -> dict:
    checks = [
        TC.build_check("post-sha", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET_REL,
                       expected_target_sha256=_sha(_B), required=True),
        TC.build_check("diff-scope", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[_TARGET_REL], required=True),
        TC.build_check("marker", TC.CHECK_TYPE_SUBPROCESS,
                       argv=[sys.executable, "-c",
                             "import pathlib,sys;"
                             "c=pathlib.Path('" + _TARGET_REL + "').read_text();"
                             "sys.exit(0 if 'AFTER_GOVERNED_APPLY' in c and 'state: BEFORE' not in c else 1)"],
                       expected_exit_code=0, required=True),
    ]
    return TC.build_test_contract("wu-positive-v0", "cand", "batch", _TARGET_REL, checks)


def _negative_contract() -> dict:
    checks = [
        TC.build_check("no-change-expected", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[], required=True),
    ]
    return TC.build_test_contract("wu-negative-v0", "cand", "batch", _TARGET_REL, checks)


def _prepare(repo, wu, contract=None, **over):
    kw = dict(
        work_unit=wu,
        source_git_commit=repo["base_sha"],
        source_historical_path=_SOURCE_REL,
        target_path=_TARGET_REL,
        test_contract=contract or _positive_contract(),
        ledger_dir=repo["stores"]["ledger"],
        selector_dir=repo["stores"]["selector"],
        execution_dir=repo["stores"]["exec"],
        pre_execution_context_dir=repo["stores"]["pec"],
        objective="checkpoint-1 conformance",
    )
    kw.update(over)
    return WU.prepare_work_unit_execution(**kw)


def _execute(repo, wu, prep, eah=None, ref="human-turn-ref-0001"):
    s = repo["stores"]
    return WU.execute_work_unit_remediation(
        work_unit=wu,
        batch_execution_id=prep["batch_execution_id"],
        child_execution_id=prep["child_execution_id"],
        human_authorized_execution_authority_hash=eah if eah is not None else prep["execution_authority_hash"],
        human_authorization_reference=ref,
        execution_dir=s["exec"], pre_execution_context_dir=s["pec"],
        selector_dir=s["selector"], ledger_dir=s["ledger"],
        kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
        test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
        sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"],
    )


# ── A / B — création worktree + branche depuis base_sha explicite ────────

def test_A_B_creates_isolated_worktree_and_branch(repo):
    r = _create(repo)
    assert r["status"] == WU.WORK_UNIT_CREATED, r
    wu = r["work_unit"]
    assert wu.branch_name == "wubr" and wu.base_sha == repo["base_sha"]
    assert Path(wu.worktree_path).is_dir()
    assert _git(Path(wu.worktree_path), "rev-parse", "HEAD") == repo["base_sha"]
    assert _git(Path(wu.worktree_path), "rev-parse", "--abbrev-ref", "HEAD") == "wubr"
    assert (Path(wu.worktree_path) / _TARGET_REL).read_bytes() == _A
    # branche enregistrée dans le dépôt
    assert _git(repo["main"], "rev-parse", "--verify", "refs/heads/wubr") == repo["base_sha"]


# ── C — PEC accepte l'isolation (via prepare -> driver -> create_pre_execution_context)

def test_C_pec_accepts_isolation_at_prepare(repo):
    wu = _create(repo)["work_unit"]
    p = _prepare(repo, wu)
    assert p["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL, p
    pec_files = list(repo["stores"]["pec"].rglob("pec-*.json"))
    assert len(pec_files) == 1
    rec = json.loads(pec_files[0].read_text(encoding="utf-8"))
    assert rec["worktree_isolated"] is True and rec["branch_isolated"] is True
    assert rec["base_sha"] == repo["base_sha"] and rec["branch_name"] == "wubr"


# ── D — refuse une branche déjà existante ───────────────────────────────

def test_D_refuses_existing_branch(repo):
    _git(repo["main"], "branch", "taken")
    r = _create(repo, branch="taken", dest=repo["root"] / "wt_taken")
    assert r["status"] == WU.WORK_UNIT_CREATE_REJECTED
    assert r["reason"] == "BRANCH_ALREADY_EXISTS"
    assert not (repo["root"] / "wt_taken").exists()


# ── E — refuse une destination non vide ────────────────────────────────

def test_E_refuses_nonempty_destination(repo):
    dest = repo["root"] / "wt_dirty"
    dest.mkdir()
    (dest / "stranger.txt").write_text("unrelated")
    r = _create(repo, branch="wubr2", dest=dest)
    assert r["status"] == WU.WORK_UNIT_CREATE_REJECTED
    assert r["reason"] == "WORKTREE_DESTINATION_NOT_EMPTY"
    assert (dest / "stranger.txt").read_text() == "unrelated"   # rien touché


# ── F — refuse mauvaise identité de dépôt / base_sha ───────────────────

def test_F_refuses_non_git_repo_root(repo, tmp_path):
    non_git = tmp_path / "not_a_repo"
    non_git.mkdir()
    r = _create(repo, repo_root=non_git, dest=repo["root"] / "wt_x")
    assert r["status"] == WU.WORK_UNIT_CREATE_REJECTED
    assert r["reason"] == "REPO_ROOT_NOT_A_GIT_WORKTREE"


def test_F_refuses_unknown_base_sha(repo):
    r = _create(repo, base="0" * 40, dest=repo["root"] / "wt_bad_base")
    assert r["status"] == WU.WORK_UNIT_CREATE_REJECTED
    assert r["reason"] == "BASE_SHA_NOT_A_COMMIT_IN_THIS_REPOSITORY"


def test_F_refuses_malformed_base_sha(repo):
    r = _create(repo, base="deadbeef", dest=repo["root"] / "wt_bad_base2")
    assert r["status"] == WU.WORK_UNIT_CREATE_REJECTED
    assert r["reason"] == "BASE_SHA_NOT_A_40_HEX_GIT_COMMIT_SHA"


# ── G — PREPARE appelle le driver générique, ne le duplique pas ────────

def test_G_prepare_is_real_caller_not_duplicate():
    src = Path(WU.__file__).read_text(encoding="utf-8")
    # appelle bien le driver
    assert "prepare_governed_execution" in src
    assert "execute_governed_remediation" in src
    # ne reproduit AUCUNE étape du rail
    for banned in ("register_git_blob_source", "propose_batch", "prepare_execution(",
                   "compute_execution_authority_hash", "store_approval_artifact",
                   "run_and_persist_kx108", "run_governed_content_apply(",
                   "run_governed_rollback", "run_tooling_build_pipeline",
                   "compute_pre_execution_context", "create_pre_execution_context("):
        assert banned not in src, f"work-unit module must not reproduce {banned}"
    # exactement un site d'appel de chaque phase du driver
    assert src.count("_DRV.prepare_governed_execution(") == 1
    assert src.count("_DRV.execute_governed_remediation(") == 1


# ── H / I / J — PREPARE révèle l'EAH exact et s'arrête ─────────────────

def test_H_I_J_prepare_reveals_exact_eah_and_stops(repo):
    wu = _create(repo)["work_unit"]
    p = _prepare(repo, wu)
    assert p["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL
    assert len(p["execution_authority_hash"]) == 64
    assert p["work_unit_id"] == "wu-0001"
    assert p["first_real_driver_caller"] == "obsidia_isolated_work_unit_v0"
    # I — aucune HumanApproval créée
    assert p["human_approval_created"] is False
    assert not list(repo["stores"]["exec"].rglob("approval.json"))
    # J — aucun KX108 invoqué
    assert p["kx108_invocations"] == 0
    assert not list(repo["stores"]["kxpre"].rglob("*.json"))
    assert not list(repo["stores"]["kxpost"].rglob("*.json"))
    # cible intacte
    assert (Path(wu.worktree_path) / _TARGET_REL).read_bytes() == _A
    assert not list(repo["stores"]["sar"].rglob("*.json"))
    assert not list(repo["stores"]["sre"].rglob("*.json"))


# ── K — mauvais EAH humain rejeté AVANT mutation ──────────────────────

def test_K_wrong_human_eah_rejected_before_mutation(repo):
    wu = _create(repo)["work_unit"]
    p = _prepare(repo, wu)
    r = _execute(repo, wu, p, eah="0" * 64)
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"].startswith("HUMAN_AUTHORIZED_EAH_MISMATCH")
    assert (Path(wu.worktree_path) / _TARGET_REL).read_bytes() == _A
    assert not list(repo["stores"]["kxpre"].rglob("*.json"))


# ── L — EAH exact atteint le driver d'exécution existant (KEEP réel) ───

def test_L_correct_exact_eah_reaches_execute_driver_keep(repo):
    wu = _create(repo)["work_unit"]
    p = _prepare(repo, wu)
    r = _execute(repo, wu, p)
    assert r["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, r
    assert r["kx108_pre_gate"] == "ALLOW" and r["kx108_post_gate"] == "ALLOW"
    assert r["work_unit_id"] == "wu-0001"
    assert (Path(wu.worktree_path) / _TARGET_REL).read_bytes() == _B
    sre = SEV.load_sealed_rollback_evidence(r["sealed_rollback_evidence_id"], repo["stores"]["sre"])
    sar = SEV.load_sealed_apply_receipt(r["sealed_apply_receipt_id"], repo["stores"]["sar"])
    assert SEV.verify_sealed_rollback_evidence(sre)[0]
    assert SEV.verify_sealed_apply_receipt(sar)[0]
    # aucune disposition Git : HEAD inchangé, diff = [target] seulement
    assert _git(Path(wu.worktree_path), "rev-parse", "HEAD") == repo["base_sha"]
    assert _git(Path(wu.worktree_path), "diff", "--name-only") == _TARGET_REL
    assert r["driver_git_disposition"] is False


# ── M — dérive entre prepare et execute échoue fermé (driver + PEC) ────

def test_M_drift_between_prepare_and_execute_fails_closed(repo):
    wu = _create(repo)["work_unit"]
    p = _prepare(repo, wu)
    ep = repo["stores"]["exec"] / "executions" / p["batch_execution_id"] / "execution.json"
    env = json.loads(ep.read_text())
    env["execution_authority_hash"] = "9" * 64
    ep.write_text(json.dumps(env))
    r = _execute(repo, wu, p, eah=p["execution_authority_hash"])
    assert r["status"] == DRV.PRE_EXECUTION_REJECTED
    assert r["reason"] in ("ENVELOPE_EAH_DRIFT", "HUMAN_AUTHORIZED_EAH_MISMATCH")
    assert (Path(wu.worktree_path) / _TARGET_REL).read_bytes() == _A
    assert not list(repo["stores"]["kxpre"].rglob("*.json"))


# ── N / O — aucune opération Git distante, aucun commit automatique ────

def test_N_O_no_remote_no_autocommit_static():
    src = Path(WU.__file__).read_text(encoding="utf-8")
    for banned in ("git push", "git fetch", "git pull", "git remote", "set-upstream",
                   "--set-upstream", "git commit", "git add", "git merge", "git rebase",
                   "git cherry-pick", "git stash", "git reset", "git checkout",
                   "gh pr", "pull request"):
        assert banned not in src, banned
    # les seules sous-commandes Git mutantes sont le cycle de vie d'espace de travail
    assert '"worktree", "add"' in src
    assert '"worktree", "remove"' in src
    assert '"branch", "-d"' in src
    assert '"-D"' not in src and "'-D'" not in src        # jamais de suppression forcée


def test_O_execute_does_not_change_head_after_keep(repo):
    wu = _create(repo)["work_unit"]
    p = _prepare(repo, wu)
    r = _execute(repo, wu, p)
    assert r["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    assert _git(Path(wu.worktree_path), "rev-parse", "HEAD") == repo["base_sha"]
    assert _git(repo["main"], "rev-parse", "HEAD") == repo["base_sha"]


# ── P — aucune mutation de audit/world_action_bus ─────────────────────

def test_P_no_audit_world_action_bus_reference():
    src = Path(WU.__file__).read_text(encoding="utf-8")
    assert "world_action_bus" not in src
    assert "audit/" not in src


# ── Q — formes non supportées échouent explicitement ──────────────────

def test_Q_multichild_create_delete_shapes_fail_explicitly(repo):
    wu = _create(repo)["work_unit"]
    # opération non-UPDATE
    for op in ("CREATE", "DELETE", "ARCHIVE", "MOVE", "RENAME", "MULTI_CHILD"):
        r = _prepare(repo, wu, operation=op)
        assert r["status"] == WU.WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE
        assert r["reason"] == f"UNSUPPORTED_OPERATION_SHAPE:{op}"
        assert (Path(wu.worktree_path) / _TARGET_REL).read_bytes() == _A
    # cible inexistante -> pas de CREATE implicite (contrat aligné sur la cible absente)
    missing = "periphery/xdomain/does_not_exist.txt"
    absent_contract = TC.build_test_contract(
        "wu-absent-v0", "cand", "batch", missing,
        [TC.build_check("diff-scope", TC.CHECK_TYPE_DIFF_SCOPE,
                        expected_diff_paths=[missing], required=True)],
    )
    r = _prepare(repo, wu, target_path=missing, test_contract=absent_contract)
    assert r["status"] == WU.WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE
    assert r["reason"] == "TARGET_MUST_PREEXIST_UPDATE_ONLY_NO_CREATE"
    # test_contract malformé
    r = _prepare(repo, wu, test_contract={"checks": "nope"})
    assert r["status"] == WU.WORK_UNIT_PREPARE_REJECTED_UNSUPPORTED_SHAPE
    assert r["reason"] == "TEST_CONTRACT_MALFORMED"


# ── negative real-stack rollback via the work-unit caller ─────────────

def test_negative_real_stack_rollback_to_A(repo):
    wu = _create(repo)["work_unit"]
    p = _prepare(repo, wu, contract=_negative_contract())
    r = _execute(repo, wu, p)
    assert r["status"] == DRV.REJECTED_ROLLED_BACK, r
    assert r["kx108_post_gate"] in ("HOLD", "BLOCK")
    assert (Path(wu.worktree_path) / _TARGET_REL).read_bytes() == _A
    assert _git(Path(wu.worktree_path), "diff", "--name-only") == ""
    assert r["driver_authored_rollback"] is False


# ── dispose : cycle de vie d'espace de travail, sans --force ──────────

def test_dispose_removes_only_own_clean_worktree(repo):
    r = _create(repo)
    wu = r["work_unit"]
    d = WU.dispose_isolated_work_unit(work_unit=wu)
    assert d["status"] == WU.WORK_UNIT_DISPOSED, d
    assert d["worktree_removed"] and d["branch_deleted"]
    assert not Path(wu.worktree_path).exists()
    r2 = subprocess.run(["git", "rev-parse", "--verify", "refs/heads/wubr"],
                        cwd=str(repo["main"]), capture_output=True, text=True)
    assert r2.returncode != 0            # branche supprimée (suppression sûre -d)


def test_dispose_refused_when_not_created_by_component(repo):
    fake = WU.IsolatedWorkUnit(
        work_unit_id="x", repo_root=str(repo["main"]), main_worktree_path=str(repo["main"]),
        base_sha=repo["base_sha"], branch_name="nope", worktree_path=str(repo["root"] / "nope"),
        created_by_this_component=False,
    )
    d = WU.dispose_isolated_work_unit(work_unit=fake)
    assert d["status"] == WU.WORK_UNIT_DISPOSE_REFUSED
    assert d["reason"] == "NOT_CREATED_BY_THIS_COMPONENT"


def test_dispose_refused_after_branch_advanced(repo):
    wu = _create(repo)["work_unit"]
    wt = Path(wu.worktree_path)
    (wt / "new.txt").write_text("x")
    _git(wt, "add", "new.txt")
    _git(wt, "commit", "-q", "-m", "advance")
    d = WU.dispose_isolated_work_unit(work_unit=wu)
    assert d["status"] == WU.WORK_UNIT_DISPOSE_REFUSED
    assert d["reason"] == "BRANCH_HAS_ADVANCED_HUMAN_GIT_DISPOSITION_REQUIRED_FIRST"
    assert wt.exists()


# ── static: no new authority, no mission semantics ──────────────────

def test_static_no_bounded_mission_authority_no_preapproval():
    src = Path(WU.__file__).read_text(encoding="utf-8")
    # aucune IMPLÉMENTATION d'autorité de mission / pré-approbation
    # (le docstring peut nommer ces concepts pour dire qu'il ne les fait PAS)
    for banned in ("class BoundedMissionAuthority", "class MissionAuthority",
                   "def preapprove", "def pre_approve", "APPROVED_FOR_MISSION",
                   "approved_by", "def synthesize_approval", "store_approval_artifact("):
        assert banned not in src, banned
    assert "KX108_ONLY" in src
    # exécution : les paramètres d'autorité humaine restent requis (via délégation)
    sig = inspect.signature(WU.execute_work_unit_remediation)
    for pn in ("human_authorized_execution_authority_hash", "human_authorization_reference"):
        assert pn in sig.parameters
        assert sig.parameters[pn].default is inspect.Parameter.empty


# ══════════════════════════════════════════════════════════════════════════
#  STAGE 3C — base d'action DYNAMIQUE explicite (expected_action_base_sha)
# ══════════════════════════════════════════════════════════════════════════

_SOURCE_B_REL = "periphery/xdomain/wu_source_b_v0.txt"
_C = b"ISOLATED_WORK_UNIT_FIXTURE\nstate: AFTER_SECOND_GOVERNED_APPLY\n"


@pytest.fixture
def repo3c(tmp_path):
    main = tmp_path / "main"
    (main / "periphery" / "xdomain").mkdir(parents=True)
    (main / _TARGET_REL).write_bytes(_A)
    (main / _SOURCE_REL).write_bytes(_B)
    (main / _SOURCE_B_REL).write_bytes(_C)
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "t@example.com")
    _git(main, "config", "user.name", "t")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", _TARGET_REL, _SOURCE_REL, _SOURCE_B_REL)
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    stores = {k: tmp_path / k for k in (
        "ledger", "selector", "exec", "pec", "kxpre", "kxpost", "tcr",
        "sar", "sre", "rbk", "snap")}
    return {"root": tmp_path, "main": main, "base_sha": base_sha, "stores": stores}


def _contract(target_rel, expected_post):
    return TC.build_test_contract("wu-3c", "cand", "batch", target_rel, [
        TC.build_check("post-sha", TC.CHECK_TYPE_TARGET_SHA256, target_path=target_rel,
                       expected_target_sha256=_sha(expected_post), required=True),
        TC.build_check("diff-scope", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[target_rel], required=True),
    ])


def _prep3c(env, wu, *, source_rel, expected_post, base=None):
    s = env["stores"]
    kw = dict(
        work_unit=wu, source_git_commit=env["base_sha"], source_historical_path=source_rel,
        target_path=_TARGET_REL, test_contract=_contract(_TARGET_REL, expected_post),
        ledger_dir=s["ledger"], selector_dir=s["selector"], execution_dir=s["exec"],
        pre_execution_context_dir=s["pec"], objective="stage3c")
    if base is not None:
        kw["expected_action_base_sha"] = base
    return WU.prepare_work_unit_execution(**kw)


def _exec3c(env, wu, prep):
    s = env["stores"]
    return WU.execute_work_unit_remediation(
        work_unit=wu, batch_execution_id=prep["batch_execution_id"],
        child_execution_id=prep["child_execution_id"],
        human_authorized_execution_authority_hash=prep["execution_authority_hash"],
        human_authorization_reference="human-3c",
        execution_dir=s["exec"], pre_execution_context_dir=s["pec"], selector_dir=s["selector"],
        ledger_dir=s["ledger"], kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
        test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
        sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"])


def _snapshot_A(env, wu, prepA, exA):
    s = env["stores"]
    return LS.create_local_snapshot(
        mission_id="msn-3c", action_id="act-A", ordinal=0,
        expected_branch_name="wubr", expected_worktree_path=wu.worktree_path,
        expected_previous_mission_tip_sha=env["base_sha"],
        batch_execution_id=prepA["batch_execution_id"], child_execution_id=prepA["child_execution_id"],
        execution_authority_hash=exA["execution_authority_hash"], approval_id=exA["approval_id"],
        kx108_pre_decision_record_id=exA["kx108_pre_decision_record_id"],
        kx108_post_decision_record_id=exA["kx108_post_decision_record_id"],
        test_contract_result_id=exA["test_contract_result_id"],
        sealed_apply_receipt_id=exA["sealed_apply_receipt_id"],
        sealed_rollback_evidence_id=exA["sealed_rollback_evidence_id"],
        target_path=_TARGET_REL,
        execution_dir=s["exec"], kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
        test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
        sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"],
        snapshot_store_dir=s["snap"])


def _wu3c(env):
    r = WU.create_isolated_work_unit(
        repo_root=env["main"], base_sha=env["base_sha"], branch_name="wubr",
        worktree_path=env["root"] / "wt_3c", work_unit_id="wu-3c-0001")
    assert r["status"] == WU.WORK_UNIT_CREATED, r
    return r["work_unit"]


# ── A / B — compat historique ──────────────────────────────────────────

def test_3c_A_historical_prepare_no_param(repo3c):
    wu = _wu3c(repo3c)
    p = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B)
    assert p["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL
    assert p["dynamic_action_base_supplied"] is False
    assert p["effective_action_base_sha"] == repo3c["base_sha"] == wu.base_sha


def test_3c_B_explicit_base_equals_work_unit_base(repo3c):
    wu = _wu3c(repo3c)
    p = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B, base=repo3c["base_sha"])
    assert p["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL
    assert p["dynamic_action_base_supplied"] is True
    assert p["effective_action_base_sha"] == repo3c["base_sha"]


# ── C..H — vraie 2e action gouvernée depuis une base LOCALE avancée ────

def test_3c_CDEFGH_real_second_action_from_advanced_base(repo3c):
    wu = _wu3c(repo3c)
    # action A : cible _A -> _B, KEEP
    pA = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B)
    exA = _exec3c(repo3c, wu, pA)
    assert exA["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    eah_A = exA["execution_authority_hash"]
    # snapshot A -> HEAD avance
    snap = _snapshot_A(repo3c, wu, pA, exA)
    assert snap["status"] == LS.SNAPSHOT_COMMITTED
    advanced = snap["new_commit_sha"]
    assert _git(Path(wu.worktree_path), "rev-parse", "HEAD") == advanced
    assert _git(Path(wu.worktree_path), "status", "--porcelain") == ""
    # C — action B préparée depuis la base avancée
    pB = _prep3c(repo3c, wu, source_rel=_SOURCE_B_REL, expected_post=_C, base=advanced)
    assert pB["status"] == DRV.PREPARED_AWAITING_HUMAN_APPROVAL, pB
    assert pB["effective_action_base_sha"] == advanced
    # D — le PEC de B (résolu par son id EXACT) porte bien la base avancée
    pecB_path = next(repo3c["stores"]["pec"].rglob(pB["pre_execution_context_id"] + ".json"))
    pecB = json.loads(pecB_path.read_text(encoding="utf-8"))
    assert pecB["base_sha"] == advanced
    assert pecB["worktree_isolated"] is True and pecB["branch_isolated"] is True
    # H — B observe le résultat committé par A (précondition == _B)
    assert pecB["target_pre_sha256"] == _sha(_B)
    # E / F — enveloppe de B liée, EAH_B != EAH_A
    assert pB["execution_authority_hash"] != eah_A
    assert len(pB["execution_authority_hash"]) == 64
    # G — B s'exécute réellement à travers le rail gouverné
    exB = _exec3c(repo3c, wu, pB)
    assert exB["status"] == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, exB
    assert exB["kx108_pre_gate"] == "ALLOW" and exB["kx108_post_gate"] == "ALLOW"
    assert (Path(wu.worktree_path) / _TARGET_REL).read_bytes() == _C
    # work_unit.base_sha jamais muté
    assert wu.base_sha == repo3c["base_sha"]
    assert _git(Path(wu.worktree_path), "rev-parse", "HEAD") == advanced  # execute ne bouge pas HEAD


# ── I — vieille base canonique après avancée du tip : rejet ───────────

def test_3c_I_stale_canonical_base_after_advance_rejected(repo3c):
    wu = _wu3c(repo3c)
    pA = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B)
    exA = _exec3c(repo3c, wu, pA)
    snap = _snapshot_A(repo3c, wu, pA, exA)
    r = _prep3c(repo3c, wu, source_rel=_SOURCE_B_REL, expected_post=_C, base=repo3c["base_sha"])
    assert r["status"] == WU.WORK_UNIT_PREPARE_REJECTED_DYNAMIC_ACTION_BASE
    assert r["reason"].startswith("OBSERVED_HEAD_NOT_EQUAL_EXPECTED_ACTION_BASE_SHA")
    # aucun artefact de préparation créé au-delà de A
    assert len(sorted(repo3c["stores"]["pec"].rglob("pec-*.json"))) == 1


# ── J / K / L / M / N — cas fail-closed du préflight ─────────────────

def test_3c_J_malformed_base_rejected(repo3c):
    wu = _wu3c(repo3c)
    r = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B, base="deadbeef")
    assert r["status"] == WU.WORK_UNIT_PREPARE_REJECTED_DYNAMIC_ACTION_BASE
    assert r["reason"] == "EXPECTED_ACTION_BASE_SHA_NOT_A_40_HEX_GIT_COMMIT_SHA"


def test_3c_K_nonexistent_base_rejected(repo3c):
    wu = _wu3c(repo3c)
    r = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B, base="0" * 40)
    assert r["status"] == WU.WORK_UNIT_PREPARE_REJECTED_DYNAMIC_ACTION_BASE
    assert r["reason"] == "EXPECTED_ACTION_BASE_SHA_NOT_A_COMMIT_IN_THIS_REPOSITORY"


def test_3c_L_non_descendant_base_rejected(repo3c):
    wu = _wu3c(repo3c)
    wt = Path(wu.worktree_path)
    # commit ORPHELIN (aucune ascendance commune avec base_sha)
    tree = _git(wt, "write-tree")
    orphan = _git(wt, "commit-tree", tree, "-m", "orphan")
    _git(wt, "reset", "--hard", orphan)                 # HEAD == orphan, branche wubr, propre
    r = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B, base=orphan)
    assert r["status"] == WU.WORK_UNIT_PREPARE_REJECTED_DYNAMIC_ACTION_BASE
    assert r["reason"] == "EXPECTED_ACTION_BASE_SHA_DOES_NOT_DESCEND_FROM_WORK_UNIT_BASE_SHA"


def test_3c_M_head_mismatch_rejected(repo3c):
    wu = _wu3c(repo3c)
    pA = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B)
    exA = _exec3c(repo3c, wu, pA)
    snap = _snapshot_A(repo3c, wu, pA, exA)   # HEAD == snap, mais on passe base_sha
    r = _prep3c(repo3c, wu, source_rel=_SOURCE_B_REL, expected_post=_C, base=repo3c["base_sha"])
    assert r["status"] == WU.WORK_UNIT_PREPARE_REJECTED_DYNAMIC_ACTION_BASE
    assert r["reason"].startswith("OBSERVED_HEAD_NOT_EQUAL_EXPECTED_ACTION_BASE_SHA")


def test_3c_N_branch_mismatch_rejected(repo3c):
    wu = _wu3c(repo3c)
    wt = Path(wu.worktree_path)
    _git(wt, "checkout", "-q", "-b", "sidebranch")   # branche != wubr, HEAD inchangé
    r = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B, base=repo3c["base_sha"])
    assert r["status"] == WU.WORK_UNIT_PREPARE_REJECTED_DYNAMIC_ACTION_BASE
    assert r["reason"].startswith("BRANCH_MISMATCH")


# ── O — worktree sale à la bonne base : rejet via PEC (strictness préservée) ──

def test_3c_O_dirty_dynamic_base_worktree_rejected_by_pec(repo3c):
    wu = _wu3c(repo3c)
    pA = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B)
    exA = _exec3c(repo3c, wu, pA)
    snap = _snapshot_A(repo3c, wu, pA, exA)
    advanced = snap["new_commit_sha"]
    # salir le worktree APRÈS le snapshot (contenu non lié)
    (Path(wu.worktree_path) / _SOURCE_B_REL).write_bytes(b"unrelated dirty\n")
    r = _prep3c(repo3c, wu, source_rel=_SOURCE_B_REL, expected_post=_C, base=advanced)
    # préflight dynamique passe (HEAD ok), puis PEC refuse fermé
    assert r["status"] in (DRV.PREPARE_REJECTED,)
    assert "WORKTREE_DIRTY" in (r.get("reason") or "") or "DIRTY" in (r.get("reason") or "")


# ── P — work_unit.base_sha inchangé après prepare dynamique ──────────

def test_3c_P_work_unit_base_sha_immutable(repo3c):
    wu = _wu3c(repo3c)
    before = wu.base_sha
    pA = _prep3c(repo3c, wu, source_rel=_SOURCE_REL, expected_post=_B)
    exA = _exec3c(repo3c, wu, pA)
    snap = _snapshot_A(repo3c, wu, pA, exA)
    _prep3c(repo3c, wu, source_rel=_SOURCE_B_REL, expected_post=_C, base=snap["new_commit_sha"])
    assert wu.base_sha == before == repo3c["base_sha"]


# ── Q / R / S / T — audit statique d'architecture ───────────────────

def test_3c_Q_checkpoint1_remains_mission_agnostic():
    src = Path(WU.__file__).read_text(encoding="utf-8")
    for banned in ("import obsidia_bounded_mission_v0", "obsidia_bounded_mission_v0.",
                   "MissionActionPlan", "class BoundedMissionAuthority",
                   "projection[", "\"mission_tip_sha\"", "record_local_snapshot("):
        assert banned not in src, banned
    sig = inspect.signature(WU.prepare_work_unit_execution)
    assert "expected_action_base_sha" in sig.parameters
    assert sig.parameters["expected_action_base_sha"].default is None


def test_3c_R_S_T_pec_driver_kx108_not_modified():
    r = subprocess.run(["git", "status", "--porcelain",
                        "scripts/obsidia_pre_execution_context.py",
                        "scripts/obsidia_governed_execution_driver_v0.py",
                        "scripts/obsidia_kx108_decision_store.py",
                        "scripts/obsidia_governed_apply_v0.py",
                        "scripts/obsidia_governed_rollback_v0.py",
                        "scripts/obsidia_bounded_mission_v0.py",
                        "scripts/obsidia_mission_local_snapshot_v0.py"],
                       cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"unexpected changes: {r.stdout}"


def test_3c_static_dynamic_base_prepare_no_git_mutation():
    src = Path(WU.__file__).read_text(encoding="utf-8")
    # le préflight n'utilise que des sous-commandes de LECTURE
    assert '"merge-base", "--is-ancestor"' in src
    assert '"cat-file", "-e"' in src
    # aucune mutation Git ajoutée (les seules restent worktree add/remove + branch -d)
    for banned in ("git commit", "git add", "git reset", "git checkout", "git clean",
                   "git merge", "git rebase", "git cherry-pick", "git stash", "git push"):
        assert banned not in src, banned
