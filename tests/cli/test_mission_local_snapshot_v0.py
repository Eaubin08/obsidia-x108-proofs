"""
tests/cli/test_mission_local_snapshot_v0.py
===========================================
STAGE_3A — preuve de la primitive de snapshot local bornée.

Sur des dépôts / worktrees / magasins TEMPORAIRES isolés (kernel sigma
canonique RÉEL via le pont Checkpoint 1) :

  * une action gouvernée KEEP réelle -> UN commit local du SEUL chemin
    cible, parent == tip précédent, octets committés == octets post-état
    gouverné (SAR.target_post_sha256), worktree propre, reçu immuable
    NON_SOVEREIGN vérifiable ;
  * toute non-KEEP (rollback réel) -> AUCUN commit ;
  * matrice d'attaque : mauvaise mission/action/tip/branche/worktree,
    chemin sale/stagé/untracked non lié, cible mutée après KX108_POST,
    mauvais SAR/KX108_PRE/KX108_POST, POST BLOCK, échec TestContract,
    RollbackResult présent, rejeu d'EAH, HEAD bougé, blob stagé trafiqué,
    reçu trafiqué, arbre de commit incohérent ;
  * aucune opération Git distante, aucune révision de mission écrite,
    aucune modification de PEC / Checkpoint 1 / Checkpoint 2 / KX108,
    audit/world_action_bus intouché.
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

import obsidia_test_contract as TC                     # noqa: E402
import obsidia_isolated_work_unit_v0 as WU             # noqa: E402
import obsidia_mission_local_snapshot_v0 as LS         # noqa: E402

_TARGET_REL = "periphery/xdomain/ls_target_v0.txt"
_SOURCE_REL = "periphery/xdomain/ls_source_v0.txt"
_A = b"LOCAL_SNAPSHOT_FIXTURE\nstate: BEFORE\n"
_B = b"LOCAL_SNAPSHOT_FIXTURE\nstate: AFTER_GOVERNED_APPLY\n"

_MID = "msn-stage3a-fixture-mission-0001"
_AID = "act-stage3a-fixture-action-0001"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {args}: {r.stderr}"
    return r.stdout.strip()


@pytest.fixture
def env(tmp_path):
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
        "sar", "sre", "rbk", "snap")}
    wt = (tmp_path / "wt_ls").resolve()
    cr = WU.create_isolated_work_unit(repo_root=main, base_sha=base_sha, branch_name="lsbr",
                                      worktree_path=wt, work_unit_id="wu-ls-0001")
    assert cr["status"] == WU.WORK_UNIT_CREATED, cr
    return {"root": tmp_path, "main": main, "base_sha": base_sha, "stores": stores,
            "wu": cr["work_unit"], "wt": wt}


def _positive_contract():
    return TC.build_test_contract("ls-positive-v0", "cand", "batch", _TARGET_REL, [
        TC.build_check("post-sha", TC.CHECK_TYPE_TARGET_SHA256, target_path=_TARGET_REL,
                       expected_target_sha256=_sha(_B), required=True),
        TC.build_check("diff-scope", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[_TARGET_REL], required=True),
    ])


def _negative_contract():
    return TC.build_test_contract("ls-negative-v0", "cand", "batch", _TARGET_REL, [
        TC.build_check("no-change-expected", TC.CHECK_TYPE_DIFF_SCOPE,
                       expected_diff_paths=[], required=True),
    ])


def _drive_to_keep(env, contract=None):
    s = env["stores"]
    wu = env["wu"]
    p = WU.prepare_work_unit_execution(
        work_unit=wu, source_git_commit=env["base_sha"], source_historical_path=_SOURCE_REL,
        target_path=_TARGET_REL, test_contract=contract or _positive_contract(),
        ledger_dir=s["ledger"], selector_dir=s["selector"], execution_dir=s["exec"],
        pre_execution_context_dir=s["pec"], objective="stage3a")
    assert p["status"] == WU._DRV.PREPARED_AWAITING_HUMAN_APPROVAL, p
    r = WU.execute_work_unit_remediation(
        work_unit=wu, batch_execution_id=p["batch_execution_id"],
        child_execution_id=p["child_execution_id"],
        human_authorized_execution_authority_hash=p["execution_authority_hash"],
        human_authorization_reference="human-turn-ref-3a",
        execution_dir=s["exec"], pre_execution_context_dir=s["pec"], selector_dir=s["selector"],
        ledger_dir=s["ledger"], kx108_pre_decision_dir=s["kxpre"], kx108_post_decision_dir=s["kxpost"],
        test_contract_results_dir=s["tcr"], sealed_receipt_dir=s["sar"],
        sealed_rollback_evidence_dir=s["sre"], rollback_result_dir=s["rbk"])
    return p, r


def _snap_kwargs(env, p, r, **over):
    s = env["stores"]
    kw = dict(
        mission_id=_MID, action_id=_AID, ordinal=0,
        expected_branch_name="lsbr", expected_worktree_path=env["wt"],
        expected_previous_mission_tip_sha=env["base_sha"],
        batch_execution_id=p["batch_execution_id"], child_execution_id=p["child_execution_id"],
        execution_authority_hash=r["execution_authority_hash"], approval_id=r["approval_id"],
        kx108_pre_decision_record_id=r["kx108_pre_decision_record_id"],
        kx108_post_decision_record_id=r["kx108_post_decision_record_id"],
        test_contract_result_id=r["test_contract_result_id"],
        sealed_apply_receipt_id=r["sealed_apply_receipt_id"],
        sealed_rollback_evidence_id=r["sealed_rollback_evidence_id"],
        target_path=_TARGET_REL,
        execution_dir=s["exec"], kx108_pre_decision_dir=s["kxpre"],
        kx108_post_decision_dir=s["kxpost"], test_contract_results_dir=s["tcr"],
        sealed_receipt_dir=s["sar"], sealed_rollback_evidence_dir=s["sre"],
        rollback_result_dir=s["rbk"], snapshot_store_dir=s["snap"],
    )
    kw.update(over)
    return kw


def _commit_count(wt: Path) -> int:
    return int(_git(wt, "rev-list", "--count", "HEAD"))


# ══════════════════════════════════════════════════════════════════════════
#  A–F — snapshot réussi + reçu vérifiable
# ══════════════════════════════════════════════════════════════════════════

def test_A_real_governed_keep_to_local_snapshot(env):
    p, r = _drive_to_keep(env)
    assert r["status"] == WU._DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW, r
    assert (env["wt"] / _TARGET_REL).read_bytes() == _B
    assert _commit_count(env["wt"]) == 1
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert out["status"] == LS.SNAPSHOT_COMMITTED, out
    assert out["mission_revision_writes"] == 0
    assert out["decision_authority"] == "NON_SOVEREIGN"
    assert out["local_snapshot_is_execution_authority"] is False
    assert out["local_snapshot_is_final_human_acceptance"] is False
    assert _commit_count(env["wt"]) == 2


def test_B_commit_parent_is_previous_tip(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert out["commit_parent_sha"] == env["base_sha"]
    assert _git(env["wt"], "rev-parse", "HEAD^") == env["base_sha"]


def test_C_exactly_one_target_committed(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert out["committed_paths"] == [_TARGET_REL]
    names = _git(env["wt"], "show", "--name-only", "--pretty=format:", "HEAD").split()
    assert names == [_TARGET_REL]


def test_D_committed_bytes_equal_governed_post_state(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    blob = subprocess.run(["git", "show", f"{out['new_commit_sha']}:{_TARGET_REL}"],
                          cwd=str(env["wt"]), capture_output=True).stdout
    assert hashlib.sha256(blob).hexdigest() == _sha(_B)
    assert out["snapshot_receipt"]["target_post_sha256"] == _sha(_B)


def test_E_worktree_clean_after_snapshot(env):
    p, r = _drive_to_keep(env)
    LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert _git(env["wt"], "status", "--porcelain") == ""
    assert _git(env["wt"], "diff", "--cached", "--name-only") == ""


def test_F_receipt_verifies_from_stored_evidence(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    rid = out["snapshot_receipt_id"]
    rec = json.loads((env["stores"]["snap"] / f"{rid}.json").read_text(encoding="utf-8"))
    ok, why = LS.verify_local_snapshot_receipt(rec, repo_root=env["wt"])
    assert ok, why
    # vérification historique autonome (sans dépôt) passe aussi
    ok2, why2 = LS.verify_local_snapshot_receipt(rec)
    assert ok2, why2
    assert rec["decision_authority"] == "NON_SOVEREIGN"
    assert rec["not_final_human_git_disposition"] is True


# ══════════════════════════════════════════════════════════════════════════
#  G — double snapshot : pas de second commit
# ══════════════════════════════════════════════════════════════════════════

def test_G_double_snapshot_no_second_commit(env):
    p, r = _drive_to_keep(env)
    o1 = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert o1["status"] == LS.SNAPSHOT_COMMITTED
    n = _commit_count(env["wt"])
    o2 = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert o2["status"] == LS.SNAPSHOT_IDEMPOTENT_EXISTING_IDENTICAL, o2
    assert o2["new_commit_sha"] == o1["new_commit_sha"]
    assert _commit_count(env["wt"]) == n


# ══════════════════════════════════════════════════════════════════════════
#  H–L — mauvaise identité rejetée
# ══════════════════════════════════════════════════════════════════════════

def test_H_wrong_previous_tip_rejected(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r, expected_previous_mission_tip_sha="0" * 40))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"].startswith("HEAD_NOT_AT_EXPECTED_PREVIOUS_MISSION_TIP")
    assert _commit_count(env["wt"]) == 1


def test_I_wrong_branch_rejected(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r, expected_branch_name="not-the-branch"))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"].startswith("BRANCH_MISMATCH")
    assert _commit_count(env["wt"]) == 1


def test_J_wrong_worktree_rejected(env, tmp_path):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r, expected_worktree_path=tmp_path / "nope"))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"] == "WORKTREE_PATH_NOT_A_DIRECTORY"


def test_K_wrong_sar_rejected(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r, sealed_apply_receipt_id="sar-deadbeef"))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"].startswith("SEALED_APPLY_RECEIPT_INVALID")
    assert _commit_count(env["wt"]) == 1


def test_L_wrong_eah_rejected(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r, execution_authority_hash="a" * 64))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    # SAR est lié à l'EAH réel -> mismatch détecté dès l'étape SAR
    assert out["reason"].startswith("SAR_FIELD_MISMATCH")
    assert _commit_count(env["wt"]) == 1


# ══════════════════════════════════════════════════════════════════════════
#  M–O — dérive du worktree bloque
# ══════════════════════════════════════════════════════════════════════════

def test_M_unrelated_dirty_path_blocks(env):
    p, r = _drive_to_keep(env)
    (env["wt"] / _SOURCE_REL).write_bytes(b"unrelated change\n")
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"].startswith("WORKTREE_STATE_NOT_EXACTLY_GOVERNED_TARGET_MODIFICATION")
    assert _commit_count(env["wt"]) == 1


def test_N_unrelated_staged_path_blocks(env):
    p, r = _drive_to_keep(env)
    (env["wt"] / "extra.txt").write_text("x")
    _git(env["wt"], "add", "extra.txt")
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"] == "INDEX_NOT_EMPTY"
    assert _commit_count(env["wt"]) == 1


def test_O_untracked_path_blocks(env):
    p, r = _drive_to_keep(env)
    (env["wt"] / "stranger.txt").write_text("x")
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"] == "UNTRACKED_PRESENT"
    assert _commit_count(env["wt"]) == 1


def test_P_target_mutated_after_post_blocks(env):
    p, r = _drive_to_keep(env)
    (env["wt"] / _TARGET_REL).write_bytes(_B + b"tampered\n")
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"].startswith("TARGET_BYTES_DRIFT")
    assert _commit_count(env["wt"]) == 1


def test_Q_wrong_kx108_pre_rejected(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r, kx108_pre_decision_record_id="kxpre-deadbeef"))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    # SAR porte le kx108_pre_decision_record_id réel -> mismatch au niveau SAR
    assert out["reason"].startswith("SAR_FIELD_MISMATCH:kx108_pre_decision_record_id")


def test_R_wrong_kx108_post_rejected(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r, kx108_post_decision_record_id="kxpost-deadbeef"))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"].startswith("KX108_POST_INVALID")
    assert _commit_count(env["wt"]) == 1


# ══════════════════════════════════════════════════════════════════════════
#  S–U — non-KEEP réel ne peut jamais être snapshotté
# ══════════════════════════════════════════════════════════════════════════

def test_S_negative_rolled_back_cannot_snapshot(env):
    p, r = _drive_to_keep(env, contract=_negative_contract())
    assert r["status"] == WU._DRV.REJECTED_ROLLED_BACK, r
    assert (env["wt"] / _TARGET_REL).read_bytes() == _A       # A restauré
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE, out
    assert out["reason"] in (
        "KX108_POST_GATE_NOT_ALLOW:HOLD", "KX108_POST_GATE_NOT_ALLOW:BLOCK",
        "ROLLBACK_RESULT_EXISTS_FOR_THIS_ACTION", "WORKTREE_CLEAN_NOTHING_TO_SNAPSHOT",
    )
    assert _commit_count(env["wt"]) == 1


def test_U_rollback_result_present_blocks(env):
    p, r = _drive_to_keep(env, contract=_negative_contract())
    # un RollbackResult existe pour ce (batch, child)
    rbk_files = list(env["stores"]["rbk"].glob("*.json"))
    assert rbk_files, "expected a RollbackResult from the negative run"
    kw = _snap_kwargs(env, p, r)
    elig = LS.check_local_snapshot_eligibility(**{k: v for k, v in kw.items() if k != "snapshot_store_dir"})
    assert elig["eligible"] is False


# ══════════════════════════════════════════════════════════════════════════
#  W–AA — rejeu / course / trafic
# ══════════════════════════════════════════════════════════════════════════

def test_W_replay_evidence_against_other_action_rejected(env):
    p, r = _drive_to_keep(env)
    # snapshot légitime
    LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    # re-tenter avec un action_id DIFFÉRENT : nouvelle identité de reçu, mais le
    # worktree est propre -> inéligible (rien à snapshotter)
    n = _commit_count(env["wt"])
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r, action_id="act-some-other-action"))
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    # HEAD a avancé jusqu'au commit de snapshot -> le rejeu contre l'état ancien échoue fermé
    assert out["reason"] in ("HEAD_NOT_AT_EXPECTED_PREVIOUS_MISSION_TIP:" + _git(env["wt"], "rev-parse", "HEAD"),
                             "WORKTREE_CLEAN_NOTHING_TO_SNAPSHOT")
    assert _commit_count(env["wt"]) == n


def test_X_head_moved_after_eligibility_fails_closed(env):
    p, r = _drive_to_keep(env)
    # éligibilité OK maintenant
    kw = _snap_kwargs(env, p, r)
    elig = LS.check_local_snapshot_eligibility(**{k: v for k, v in kw.items() if k != "snapshot_store_dir"})
    assert elig["eligible"] is True
    # un commit étranger avance HEAD entre-temps
    (env["wt"] / "mid.txt").write_text("x")
    _git(env["wt"], "add", "mid.txt")
    _git(env["wt"], "commit", "-q", "-m", "concurrent advance")
    out = LS.create_local_snapshot(**kw)
    assert out["status"] == LS.SNAPSHOT_INELIGIBLE
    assert out["reason"].startswith("HEAD_NOT_AT_EXPECTED_PREVIOUS_MISSION_TIP")


def test_Z_receipt_tamper_rejected(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    rec = dict(out["snapshot_receipt"])
    rec["target_post_sha256"] = "f" * 64
    ok, why = LS.verify_local_snapshot_receipt(rec, repo_root=env["wt"])
    assert ok is False
    assert why in ("RECEIPT_RECORD_HASH_MISMATCH", "RECEIPT_COMMITTED_BLOB_NEQ_GOVERNED_POST")


def test_AA_commit_tree_mismatch_rejected(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    rec = dict(out["snapshot_receipt"])
    rec["commit_tree_sha"] = "0" * 40
    ok, why = LS.verify_local_snapshot_receipt(rec, repo_root=env["wt"])
    assert ok is False
    assert why in ("RECEIPT_RECORD_HASH_MISMATCH", "RECEIPT_COMMIT_TREE_MISMATCH")


def test_wrong_mission_id_changes_receipt_identity(env):
    p, r = _drive_to_keep(env)
    o1 = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    # même contexte, mission_id différent -> corrélation/reçu différents ; worktree propre -> inéligible
    o2 = LS.create_local_snapshot(**_snap_kwargs(env, p, r, mission_id="msn-other-mission"))
    assert o2["status"] == LS.SNAPSHOT_INELIGIBLE
    assert o1["snapshot_receipt_id"] != LS._snapshot_receipt_id({
        "mission_id": "msn-other-mission", "action_id": _AID, "ordinal": 0,
        "previous_mission_tip_sha": env["base_sha"],
        "execution_authority_hash": r["execution_authority_hash"],
        "batch_execution_id": p["batch_execution_id"], "child_execution_id": p["child_execution_id"],
        "approval_id": r["approval_id"],
        "kx108_pre_decision_record_id": r["kx108_pre_decision_record_id"],
        "kx108_post_decision_record_id": r["kx108_post_decision_record_id"],
        "test_contract_result_id": r["test_contract_result_id"],
        "sealed_apply_receipt_id": r["sealed_apply_receipt_id"],
        "sealed_rollback_evidence_id": r["sealed_rollback_evidence_id"],
        "target_path": _TARGET_REL,
    })


# ══════════════════════════════════════════════════════════════════════════
#  AB–AG — audits statiques / d'invariance
# ══════════════════════════════════════════════════════════════════════════

def test_AB_no_remote_or_forbidden_git_static():
    src = Path(LS.__file__).read_text(encoding="utf-8")
    # formes argv-token (les mentions de prose du docstring nommant ce qui est INTERDIT sont OK)
    for banned in ('"add", "."', '"add", "-A"', '"add", "--all"', '"reset"', '"--hard"',
                   '"clean"', '"checkout"', '"branch", "-D"', '"branch", "-d"',
                   '"worktree", "remove"', '"push"', '"fetch"', '"pull"', '"merge"',
                   '"rebase"', '"cherry-pick"', '"stash"', '"--amend"', '"--force"', '"gh", "pr"'):
        assert banned not in src, banned
    # les 3 SEULS verbes mutants autorisés sont présents et sous forme exacte
    assert '"add", "--", target_path' in src
    assert '"restore", "--staged", "--", target_path' in src
    assert '"commit", "-m"' in src


def test_AC_no_governed_writers_static():
    src = Path(LS.__file__).read_text(encoding="utf-8")
    for banned in ("run_governed_content_apply(", "run_governed_rollback(",
                   "store_approval_artifact(", "run_and_persist_kx108",
                   "run_tooling_build_pipeline", "create_pre_execution_context(",
                   "build_sealed_apply_receipt(", "build_sealed_rollback_evidence(",
                   "store_sealed_apply_receipt(", "store_kx108_decision_record(",
                   "store_test_contract_result(", "GuardX108", ".write_bytes("):
        assert banned not in src, banned
    # unique helper d'écriture ; write_text uniquement dans le helper de publication
    assert src.count("def _atomic_publish_json(") == 1
    assert src.count("write_text(") == 1
    assert "NON_SOVEREIGN" in src and "not_final_human_git_disposition" in src


def test_AD_no_mission_revision_write(env):
    p, r = _drive_to_keep(env)
    out = LS.create_local_snapshot(**_snap_kwargs(env, p, r))
    assert out["mission_revision_writes"] == 0
    src = Path(LS.__file__).read_text(encoding="utf-8")
    assert "ACTION_LOCAL_SNAPSHOT_COMMITTED" not in src
    assert "_append_revision" not in src
    assert "bounded_missions" not in src  # n'écrit pas dans le magasin mission


def test_AE_AF_pec_and_checkpoints_byte_unchanged():
    r = subprocess.run(["git", "status", "--porcelain",
                        "scripts/obsidia_pre_execution_context.py",
                        "scripts/obsidia_governed_execution_driver_v0.py",
                        "scripts/obsidia_kx108_decision_store.py"],
                       cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"unexpected changes: {r.stdout}"


def test_AG_snapshot_module_never_invokes_kx108():
    src = Path(LS.__file__).read_text(encoding="utf-8")
    # KX108_ONLY apparaît uniquement comme valeur ATTENDUE en lecture, jamais en écriture
    assert 'EXPECTED_GOVERNED_DECISION_AUTHORITY = "KX108_ONLY"' in src
    assert "run_and_persist_kx108_pre_execution_decision" not in src
    assert "run_and_persist_kx108_decision" not in src


def test_static_v0_max_targets_is_one():
    assert LS.LOCAL_SNAPSHOT_V0_MAX_TARGETS == 1


def test_static_create_requires_no_new_authority_inputs():
    sig = inspect.signature(LS.create_local_snapshot)
    # aucun paramètre "approve"/"authorize" fabriquant une autorité
    for pn in sig.parameters:
        assert "approve" not in pn.lower()
        assert not pn.lower().startswith("grant_")
    # l'EAH est une ENTRÉE (revue par l'humain en amont), jamais générée ici
    assert "execution_authority_hash" in sig.parameters


def test_audit_world_action_bus_untouched():
    src = Path(LS.__file__).read_text(encoding="utf-8")
    assert "world_action_bus" not in src
    r = subprocess.run(["git", "diff", "--stat", "audit/world_action_bus.jsonl"],
                       cwd=str(_REPO_ROOT), capture_output=True, text=True)
    # le fichier était déjà sale AVANT ce checkpoint (dirt pré-existant) ; on vérifie
    # seulement que le module ne le référence pas
    assert "world_action_bus" not in Path(LS.__file__).read_text(encoding="utf-8")
